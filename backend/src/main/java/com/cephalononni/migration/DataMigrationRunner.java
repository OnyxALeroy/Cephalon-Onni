package com.cephalononni.migration;

import com.cephalononni.model.*;
import com.cephalononni.repository.BuildRepository;
import com.cephalononni.repository.InventoryItemRepository;
import com.cephalononni.repository.UserRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import org.bson.Document;
import org.bson.types.ObjectId;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * One-time Mongo -> Postgres migration for `users`, `inventories`, `builds` (static catalog data
 * is already in Postgres - nothing to copy there, see backend-rework-plan.md Phase 2).
 *
 * Guarded by RUN_MONGO_MIGRATION=true (app.migration.enabled) so it never runs by accident, and
 * additionally refuses to run if the `users` table is already non-empty - this is the "how is
 * run-once enforced" gap called out during planning: the guard is "don't touch a DB that already
 * has migrated users", not a separate migrations-log table. Re-running against an already
 * migrated DB is a deliberate no-op, not a duplicate-insert hazard.
 *
 * Follow the cutover runbook in backend-rework-plan.md Phase 2 before running this for real:
 * freeze writes on the old backend first, run this, verify row counts against the source Mongo
 * collections, smoke-test login with a migrated account (bcrypt hash compatibility), *then* flip
 * traffic - and only after that, tear down Mongo.
 */
@Component
@ConditionalOnProperty(name = "app.migration.enabled", havingValue = "true")
public class DataMigrationRunner implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(DataMigrationRunner.class);

    private final UserRepository userRepository;
    private final BuildRepository buildRepository;
    private final InventoryItemRepository inventoryItemRepository;
    private final ObjectMapper objectMapper;
    private final String mongoUrl;
    private final String mongoDatabase;

    public DataMigrationRunner(UserRepository userRepository, BuildRepository buildRepository,
                                InventoryItemRepository inventoryItemRepository, ObjectMapper objectMapper,
                                org.springframework.core.env.Environment env) {
        this.userRepository = userRepository;
        this.buildRepository = buildRepository;
        this.inventoryItemRepository = inventoryItemRepository;
        this.objectMapper = objectMapper;
        this.mongoUrl = env.getProperty("mongo.url", "mongodb://localhost:27017");
        this.mongoDatabase = env.getProperty("mongo.database", "cephalon_onni");
    }

    @Override
    public void run(ApplicationArguments args) {
        if (userRepository.count() > 0) {
            log.warn("Migration skipped: `users` table already has {} row(s). Delete them first "
                    + "if you really want to re-run this (see class javadoc).", userRepository.count());
            return;
        }

        log.info("Starting Mongo -> Postgres migration from {}", mongoUrl);
        try (MongoClient mongoClient = MongoClients.create(mongoUrl)) {
            MongoDatabase db = mongoClient.getDatabase(mongoDatabase);

            Map<String, Long> mongoIdToUserId = migrateUsers(db.getCollection("users"));
            long buildCount = migrateBuilds(db.getCollection("builds"), mongoIdToUserId);
            long inventoryCount = migrateInventory(db.getCollection("inventories"), mongoIdToUserId);

            log.info("Migration complete: {} users, {} builds, {} inventory items",
                    mongoIdToUserId.size(), buildCount, inventoryCount);
        } catch (Exception e) {
            log.error("Migration failed - Postgres may hold a partial migration. Review before "
                    + "flipping traffic to this backend.", e);
            throw new IllegalStateException("Data migration failed", e);
        }
    }

    @Transactional
    Map<String, Long> migrateUsers(MongoCollection<Document> mongoUsers) {
        Map<String, Long> mongoIdToUserId = new HashMap<>();
        for (Document doc : mongoUsers.find()) {
            String mongoId = doc.getObjectId("_id").toHexString();
            String email = doc.getString("email");
            String username = doc.getString("username");
            String hashedPassword = doc.getString("hashed_password");
            String roleWire = doc.getString("role");

            if (userRepository.existsByEmail(email)) {
                log.warn("Skipping duplicate email during migration: {}", email);
                continue;
            }
            // The old Mongo `users` collection never enforced username uniqueness; Postgres does.
            String finalUsername = username;
            int suffix = 1;
            while (userRepository.existsByUsername(finalUsername)) {
                finalUsername = username + "_" + (suffix++);
            }
            if (!finalUsername.equals(username)) {
                log.warn("Username '{}' collided during migration, renamed to '{}'", username, finalUsername);
            }

            User user = new User();
            user.setEmail(email);
            user.setUsername(finalUsername);
            user.setHashedPassword(hashedPassword); // already bcrypt ($2a$/$2b$) - verify round-trip before cutover
            UserRole role;
            try {
                role = UserRole.fromWireValue(roleWire);
            } catch (Exception e) {
                log.warn("Unknown role '{}' for user {}, defaulting to Tenno", roleWire, email);
                role = UserRole.TENNO;
            }
            user.setRole(role);
            user = userRepository.save(user);
            mongoIdToUserId.put(mongoId, user.getId());
        }
        return mongoIdToUserId;
    }

    @Transactional
    long migrateBuilds(MongoCollection<Document> mongoBuilds, Map<String, Long> mongoIdToUserId) {
        long count = 0;
        for (Document doc : mongoBuilds.find()) {
            // builds.user_id was stored as a plain string (unlike inventories.user_id - see
            // backend-rework-plan.md's "Datastores summary" for this pre-existing inconsistency).
            String userIdStr = doc.getString("user_id");
            Long userId = mongoIdToUserId.get(userIdStr);
            if (userId == null) {
                log.warn("Skipping build '{}': owning user {} was not migrated", doc.get("_id"), userIdStr);
                continue;
            }

            Build build = new Build();
            build.setUserId(userId);
            build.setName(doc.getString("name"));
            build.setWarframeUniqueName(doc.getString("warframe_uniqueName"));
            build.setWarframeMods(toJsonNode(doc.get("warframe_mods")));
            build.setWarframeArcanes(toJsonNode(doc.get("warframe_arcanes")));
            build.setPrimaryWeapon(toJsonNode(doc.get("primary_weapon")));
            build.setSecondaryWeapon(toJsonNode(doc.get("secondary_weapon")));
            build.setMeleeWeapon(toJsonNode(doc.get("melee_weapon")));
            build.setCreatedAt(toInstant(doc.get("created_at")));
            build.setUpdatedAt(toInstant(doc.get("updated_at")));
            buildRepository.save(build);
            count++;
        }
        return count;
    }

    @Transactional
    long migrateInventory(MongoCollection<Document> mongoInventory, Map<String, Long> mongoIdToUserId) {
        long count = 0;
        for (Document doc : mongoInventory.find()) {
            // inventories.user_id was stored as an ObjectId, unlike builds.user_id.
            ObjectId userObjectId = doc.getObjectId("user_id");
            Long userId = userObjectId == null ? null : mongoIdToUserId.get(userObjectId.toHexString());
            if (userId == null) {
                log.warn("Skipping inventory item '{}': owning user was not migrated", doc.get("_id"));
                continue;
            }

            InventoryItem item = new InventoryItem();
            item.setUserId(userId);
            String itemKey = doc.getString("item_key");
            item.setItemKey(itemKey != null ? itemKey : doc.getString("name"));
            item.setName(doc.getString("name"));
            item.setType(doc.getString("type"));
            item.setRarity(doc.getString("rarity"));
            Integer itemCount = doc.getInteger("count");
            item.setCount(itemCount != null ? itemCount : 1);
            item.setRank(doc.getInteger("rank"));
            item.setPolarity(toJsonNode(doc.get("polarity")));
            item.setExtra(toJsonNode(doc.get("extra")));
            item.setCreatedAt(toInstant(doc.get("created_at")));
            inventoryItemRepository.save(item);
            count++;
        }
        return count;
    }

    private JsonNode toJsonNode(Object value) {
        if (value == null) {
            return null;
        }
        return objectMapper.valueToTree(value);
    }

    private Instant toInstant(Object value) {
        if (value instanceof java.util.Date date) {
            return date.toInstant();
        }
        return Instant.now();
    }
}
