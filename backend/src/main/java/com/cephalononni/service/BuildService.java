package com.cephalononni.service;

import com.cephalononni.exception.ApiException;
import com.cephalononni.model.*;
import com.cephalononni.repository.*;
import com.cephalononni.web.dto.BuildDtos.*;
import com.cephalononni.web.dto.WarframeDtos.AvailableArcane;
import com.cephalononni.web.dto.WarframeDtos.AvailableMod;
import com.cephalononni.web.dto.WarframeDtos.AvailableWarframe;
import com.cephalononni.web.dto.WarframeDtos.AvailableWeapon;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.data.domain.Pageable;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

@Service
public class BuildService {

    private static final int MAX_BUILDS_PER_USER = 30;
    private static final int MAX_WARFRAME_MODS = 10;
    private static final int MAX_WARFRAME_ARCANES = 2;
    private static final int MAX_WEAPON_MODS = 9;

    private final BuildRepository buildRepository;
    private final WarframeRepository warframeRepository;
    private final WeaponRepository weaponRepository;
    private final ModRepository modRepository;
    private final ArcaneRepository arcaneRepository;
    private final ObjectMapper objectMapper;

    public BuildService(BuildRepository buildRepository, WarframeRepository warframeRepository,
                         WeaponRepository weaponRepository, ModRepository modRepository,
                         ArcaneRepository arcaneRepository, ObjectMapper objectMapper) {
        this.buildRepository = buildRepository;
        this.warframeRepository = warframeRepository;
        this.weaponRepository = weaponRepository;
        this.modRepository = modRepository;
        this.arcaneRepository = arcaneRepository;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public BuildCreated createBuild(Long userId, CreateRequest req) {
        if (buildRepository.countByUserId(userId) >= MAX_BUILDS_PER_USER) {
            throw ApiException.badRequest("Maximum number of builds (" + MAX_BUILDS_PER_USER + ") reached");
        }
        if (req.warframeMods().size() > MAX_WARFRAME_MODS) {
            throw ApiException.badRequest("Warframe can have maximum " + MAX_WARFRAME_MODS + " mods");
        }
        if (req.warframeArcanes().size() > MAX_WARFRAME_ARCANES) {
            throw ApiException.badRequest("Warframe can have maximum " + MAX_WARFRAME_ARCANES + " arcanes");
        }

        validateWarframe(req.warframeUniqueName());
        req.warframeMods().forEach(m -> validateMod(m.uniqueName()));
        req.warframeArcanes().forEach(this::validateArcane);
        validateWeaponBuild(req.primaryWeapon());
        validateWeaponBuild(req.secondaryWeapon());
        validateWeaponBuild(req.meleeWeapon());

        Build build = new Build();
        build.setUserId(userId);
        build.setName(req.name().trim());
        build.setWarframeUniqueName(req.warframeUniqueName().trim());
        build.setWarframeMods(objectMapper.valueToTree(req.warframeMods()));
        build.setWarframeArcanes(objectMapper.valueToTree(req.warframeArcanes()));
        build.setPrimaryWeapon(toNode(req.primaryWeapon()));
        build.setSecondaryWeapon(toNode(req.secondaryWeapon()));
        build.setMeleeWeapon(toNode(req.meleeWeapon()));
        build.setCreatedAt(Instant.now());
        build.setUpdatedAt(Instant.now());
        build = buildRepository.save(build);

        return new BuildCreated(
                String.valueOf(build.getId()), build.getName(), build.getWarframeUniqueName(),
                readModList(build.getWarframeMods()), readStringList(build.getWarframeArcanes()),
                readWeaponBuild(build.getPrimaryWeapon()), readWeaponBuild(build.getSecondaryWeapon()),
                readWeaponBuild(build.getMeleeWeapon()), String.valueOf(build.getUserId()),
                build.getCreatedAt(), build.getUpdatedAt());
    }

    public List<BuildPublic> listBuilds(Long userId, int skip, int limit, boolean includeDetails) {
        List<Build> builds = buildRepository.findByUserIdOrderByCreatedAtDesc(
                userId, Pageable.unpaged());
        return builds.stream()
                .skip(Math.max(skip, 0))
                .limit(Math.max(limit, 0))
                .map(b -> toBuildPublic(b, includeDetails))
                .toList();
    }

    public BuildWithDetails getBuild(Long userId, Long buildId) {
        Build build = requireBuild(userId, buildId);
        return toBuildWithDetails(build);
    }

    @Transactional
    public BuildWithDetails updateBuild(Long userId, Long buildId, UpdateRequest req) {
        Build build = requireBuild(userId, buildId);

        if (req.name() != null) {
            build.setName(req.name().trim());
        }
        if (req.warframeUniqueName() != null) {
            validateWarframe(req.warframeUniqueName());
            build.setWarframeUniqueName(req.warframeUniqueName().trim());
        }
        if (req.warframeMods() != null) {
            if (req.warframeMods().size() > MAX_WARFRAME_MODS) {
                throw ApiException.badRequest("Warframe can have maximum " + MAX_WARFRAME_MODS + " mods");
            }
            req.warframeMods().forEach(m -> validateMod(m.uniqueName()));
            build.setWarframeMods(objectMapper.valueToTree(req.warframeMods()));
        }
        if (req.warframeArcanes() != null) {
            if (req.warframeArcanes().size() > MAX_WARFRAME_ARCANES) {
                throw ApiException.badRequest("Warframe can have maximum " + MAX_WARFRAME_ARCANES + " arcanes");
            }
            req.warframeArcanes().forEach(this::validateArcane);
            build.setWarframeArcanes(objectMapper.valueToTree(req.warframeArcanes()));
        }
        if (req.primaryWeapon() != null) {
            build.setPrimaryWeapon(applyWeaponSlot(req.primaryWeapon()));
        }
        if (req.secondaryWeapon() != null) {
            build.setSecondaryWeapon(applyWeaponSlot(req.secondaryWeapon()));
        }
        if (req.meleeWeapon() != null) {
            build.setMeleeWeapon(applyWeaponSlot(req.meleeWeapon()));
        }
        build.setUpdatedAt(Instant.now());
        build = buildRepository.save(build);
        return toBuildWithDetails(build);
    }

    @Transactional
    public void deleteBuild(Long userId, Long buildId) {
        if (buildRepository.deleteByIdAndUserId(buildId, userId) == 0) {
            throw ApiException.notFound("Build not found");
        }
    }

    /** Looks up a build owned by {@code userId}, or throws a 404 {@link ApiException}. */
    @NonNull
    private Build requireBuild(Long userId, Long buildId) {
        Build build = buildRepository.findByIdAndUserId(buildId, userId)
                .orElseThrow(() -> ApiException.notFound("Build not found"));
        return Objects.requireNonNull(build);
    }

    public List<AvailableWarframe> availableWarframes() {
        return warframeRepository.findAll().stream()
                .map(w -> new AvailableWarframe(
                        w.getUniqueName(), w.getName(), w.getMasteryReq()))
                .toList();
    }

    public List<AvailableWeapon> availableWeapons() {
        return weaponRepository.findAll().stream()
                .map(w -> new AvailableWeapon(
                        w.getUniqueName(), w.getName(), w.getMasteryReq(), w.getProductCategory()))
                .toList();
    }

    public List<AvailableMod> availableMods() {
        return modRepository.findAll().stream()
                .map(m -> new AvailableMod(
                        m.getUniqueName(), m.getName(), m.getType(), m.getRarity(), m.getPolarity()))
                .toList();
    }

    public List<AvailableArcane> availableArcanes() {
        return arcaneRepository.findAll().stream()
                .map(a -> new AvailableArcane(
                        a.getUniqueName(), a.getName(), a.getRarity()))
                .toList();
    }

    /** Throws a 400 {@link ApiException} if no warframe with this uniqueName exists in the catalog. */
    private void validateWarframe(String uniqueName) {
        if (!warframeRepository.existsByUniqueName(uniqueName)) {
            throw ApiException.badRequest("Warframe with uniqueName '" + uniqueName + "' not found");
        }
    }

    /** Throws a 400 {@link ApiException} if no mod with this uniqueName exists in the catalog. */
    private void validateMod(String uniqueName) {
        if (!modRepository.existsByUniqueName(uniqueName)) {
            throw ApiException.badRequest("Mod with uniqueName '" + uniqueName + "' not found");
        }
    }

    /** Throws a 400 {@link ApiException} if no arcane with this uniqueName exists in the catalog. */
    private void validateArcane(String uniqueName) {
        if (!arcaneRepository.existsByUniqueName(uniqueName)) {
            throw ApiException.badRequest("Arcane with uniqueName '" + uniqueName + "' not found");
        }
    }

    /** Throws a 400 {@link ApiException} if no weapon with this uniqueName exists in the catalog. */
    private void validateWeapon(String uniqueName) {
        if (!weaponRepository.existsByUniqueName(uniqueName)) {
            throw ApiException.badRequest("Weapon with uniqueName '" + uniqueName + "' not found");
        }
    }

    /** Validates a weapon slot's uniqueName, mod count/uniqueNames, and optional arcane, if present. */
    private void validateWeaponBuild(WeaponBuild weaponBuild) {
        if (weaponBuild == null) {
            return;
        }
        if (weaponBuild.mods().size() > MAX_WEAPON_MODS) {
            throw ApiException.badRequest("Weapon can have maximum " + MAX_WEAPON_MODS + " mods");
        }
        validateWeapon(weaponBuild.weaponUniqueName());
        weaponBuild.mods().forEach(m -> validateMod(m.uniqueName()));
        if (weaponBuild.arcaneUniqueName() != null && !weaponBuild.arcaneUniqueName().isBlank()) {
            validateArcane(weaponBuild.arcaneUniqueName());
        }
    }

    /** A weapon slot with a blank weaponUniqueName explicitly clears the slot, same as before. */
    private JsonNode applyWeaponSlot(WeaponBuild weaponBuild) {
        if (weaponBuild.weaponUniqueName() == null || weaponBuild.weaponUniqueName().isBlank()) {
            return null;
        }
        validateWeaponBuild(weaponBuild);
        return toNode(weaponBuild);
    }

    /** Serializes a DTO to the JSON tree stored on the entity, or null if the DTO itself is null. */
    private JsonNode toNode(Object value) {
        return value == null ? null : objectMapper.valueToTree(value);
    }

    /** Deserializes the stored warframe_mods JSON tree back into its DTO list, or an empty list. */
    private List<EquippedMod> readModList(JsonNode node) {
        if (node == null || node.isNull()) {
            return List.of();
        }
        return objectMapper.convertValue(node, new TypeReference<List<EquippedMod>>() {});
    }

    /** Deserializes a stored JSON string-array (e.g. warframe_arcanes) back into a list, or empty. */
    private List<String> readStringList(JsonNode node) {
        if (node == null || node.isNull()) {
            return List.of();
        }
        return objectMapper.convertValue(node, new TypeReference<List<String>>() {});
    }

    /** Deserializes a stored weapon-slot JSON tree back into its DTO, or null if the slot is empty. */
    private WeaponBuild readWeaponBuild(JsonNode node) {
        if (node == null || node.isNull()) {
            return null;
        }
        return objectMapper.convertValue(node, WeaponBuild.class);
    }

    /** Maps a build entity to the list-response DTO, enriching it with warframe details on request. */
    private BuildPublic toBuildPublic(Build build, boolean includeDetails) {
        WarframeDetails warframe = includeDetails ? warframeDetailsOrNull(build.getWarframeUniqueName()) : null;
        return new BuildPublic(
                String.valueOf(build.getId()), build.getName(), build.getWarframeUniqueName(),
                build.getCreatedAt(), build.getUpdatedAt(), warframe,
                readModList(build.getWarframeMods()), readStringList(build.getWarframeArcanes()),
                readWeaponBuild(build.getPrimaryWeapon()), readWeaponBuild(build.getSecondaryWeapon()),
                readWeaponBuild(build.getMeleeWeapon()));
    }

    /** Maps a build entity to the single-build DTO, fully enriched with warframe/weapon/arcane details. */
    private BuildWithDetails toBuildWithDetails(Build build) {
        WeaponBuild primary = readWeaponBuild(build.getPrimaryWeapon());
        WeaponBuild secondary = readWeaponBuild(build.getSecondaryWeapon());
        WeaponBuild melee = readWeaponBuild(build.getMeleeWeapon());

        List<String> arcaneNames = readStringList(build.getWarframeArcanes());
        List<ArcaneDetails> arcaneDetails = new ArrayList<>();
        for (String name : arcaneNames) {
            ArcaneDetails details = arcaneDetailsOrNull(name);
            if (details != null) {
                arcaneDetails.add(details);
            }
        }

        return new BuildWithDetails(
                String.valueOf(build.getId()), build.getName(), build.getWarframeUniqueName(),
                build.getCreatedAt(), build.getUpdatedAt(),
                warframeDetailsOrNull(build.getWarframeUniqueName()),
                readModList(build.getWarframeMods()), arcaneDetails,
                primary, secondary, melee,
                weaponDetailsOrNull(primary), weaponDetailsOrNull(secondary), weaponDetailsOrNull(melee),
                arcaneDetailsOrNull(primary == null ? null : primary.arcaneUniqueName()),
                arcaneDetailsOrNull(secondary == null ? null : secondary.arcaneUniqueName()),
                arcaneDetailsOrNull(melee == null ? null : melee.arcaneUniqueName()));
    }

    /** Looks up a warframe by uniqueName and maps it to its details DTO, or null if not found. */
    private WarframeDetails warframeDetailsOrNull(String uniqueName) {
        Optional<Warframe> found = warframeRepository.findByUniqueName(uniqueName);
        if (found.isEmpty()) {
            return null;
        }
        Warframe w = found.get();
        List<String> exalted = w.getExalted() == null || w.getExalted().isNull()
                ? List.of() : objectMapper.convertValue(w.getExalted(), new TypeReference<List<String>>() {});
        List<Ability> abilities = w.getAbilities() == null || w.getAbilities().isNull()
                ? List.of() : objectMapper.convertValue(w.getAbilities(), new TypeReference<List<Ability>>() {});
        return new WarframeDetails(
                w.getUniqueName(), w.getName(), w.getParentName(), w.getDescription(),
                w.getHealth(), w.getShield(), w.getArmor(), w.getStamina(), w.getPower(),
                w.getCodexSecret(), w.getMasteryReq(), w.getSprintSpeed(), w.getPassiveDescription(),
                exalted, abilities, w.getProductCategory());
    }

    /** Looks up the weapon equipped in this slot and maps it to its details DTO, or null if empty/not found. */
    private WeaponDetails weaponDetailsOrNull(WeaponBuild weaponBuild) {
        if (weaponBuild == null) {
            return null;
        }
        Optional<Weapon> found = weaponRepository.findByUniqueName(weaponBuild.weaponUniqueName());
        if (found.isEmpty()) {
            return null;
        }
        Weapon w = found.get();
        List<Integer> damagePerShot = w.getDamagePerShot() == null || w.getDamagePerShot().isNull()
                ? List.of() : objectMapper.convertValue(w.getDamagePerShot(), new TypeReference<List<Integer>>() {});
        return new WeaponDetails(
                w.getUniqueName(), w.getName(), w.getCodexSecret(), w.getCriticalChance(), w.getCriticalMultiplier(),
                damagePerShot, w.getDescription(), w.getFireRate(), w.getMasteryReq(), w.getOmegaAttenuation(),
                w.getProcChance(), w.getProductCategory(), w.getTotalDamage(), w.getAccuracy(), w.getMagazineSize(),
                w.getReloadTime(), w.getMultishot(), w.getNoise(), w.getTrigger());
    }

    /** Looks up an arcane by uniqueName and maps it to its details DTO, or null if blank/not found. */
    private ArcaneDetails arcaneDetailsOrNull(String uniqueName) {
        if (uniqueName == null || uniqueName.isBlank()) {
            return null;
        }
        return arcaneRepository.findByUniqueName(uniqueName).map(a -> {
            List<Map<String, Object>> levelStats = a.getLevelStats() == null || a.getLevelStats().isNull()
                    ? List.of()
                    : objectMapper.convertValue(a.getLevelStats(), new TypeReference<List<Map<String, Object>>>() {});
            return new ArcaneDetails(a.getUniqueName(), a.getName(), a.getCodexSecret(), a.getRarity(), levelStats);
        }).orElse(null);
    }
}
