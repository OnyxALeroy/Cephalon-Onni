package com.cephalononni.web.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import org.springframework.lang.Nullable;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/**
 * Mirrors backend/app/models/worldstate.py's `WorldState` Pydantic model field-for-field,
 * including its snake_case convention - this is the one endpoint in the old API that wasn't
 * camelCase, and the frontend already expects snake_case here, so we keep it (see
 * backend-rework-plan.md Phase 3). The nested Message/Link records are the one exception: the
 * old model mirrored the upstream Warframe API's own PascalCase field names for those two
 * specifically, so we do too.
 */
public final class WorldstateDtos {

    private WorldstateDtos() {}

    public record Message(@JsonProperty("LanguageCode") String languageCode, @JsonProperty("Message") String message) {
    }

    public record Link(@JsonProperty("LanguageCode") String languageCode, @JsonProperty("Link") String link) {
    }

    public record Event(
            List<Message> messages,
            @JsonProperty("is_mobile_only") boolean isMobileOnly,
            boolean priority,
            String prop,
            boolean community,
            String icon,
            @JsonProperty("image_url") String imageUrl,
            @Nullable Instant date,
            @JsonProperty("start_date") @Nullable Instant startDate,
            @JsonProperty("end_date") @Nullable Instant endDate,
            @JsonProperty("live_url") String liveUrl,
            @JsonProperty("do_hide_end_date_modifier") boolean doHideEndDateModifier,
            List<Link> links) {
    }

    public record MissionInfo(
            String location,
            @JsonProperty("mission_type") String missionType,
            String faction,
            int difficulty,
            @JsonProperty("mission_reward") Map<String, Object> missionReward,
            @JsonProperty("level_override") String levelOverride,
            @JsonProperty("enemy_spec") String enemySpec,
            @JsonProperty("min_enemy_level") int minEnemyLevel,
            @JsonProperty("max_enemy_level") int maxEnemyLevel,
            @JsonProperty("desc_text") String descText,
            @JsonProperty("max_wave_num") int maxWaveNum) {
    }

    public record Alert(
            @Nullable Instant activation,
            @Nullable Instant expiry,
            @JsonProperty("mission_info") MissionInfo missionInfo,
            String tag,
            @JsonProperty("force_unlock") boolean forceUnlock) {
    }

    public record OpenWorldMission(
            String type,
            @JsonProperty("mastery_required") int masteryRequired,
            @JsonProperty("max_enemy_level") int maxEnemyLevel,
            @JsonProperty("min_enemy_level") int minEnemyLevel,
            @JsonProperty("rewards_table") String rewardsTable,
            @JsonProperty("xp_amounts") List<Integer> xpAmounts) {
    }

    public record SyndicateMission(
            @Nullable Instant activation,
            @Nullable Instant expiry,
            @JsonProperty("syndicate_tag") String syndicateTag,
            List<Object> nodes,
            @JsonProperty("open_world_missions") @Nullable List<OpenWorldMission> openWorldMissions) {
    }

    public record VoidFissure(
            @Nullable Instant activation,
            @Nullable Instant expiry,
            @JsonProperty("mission_type") String missionType,
            String node,
            int region,
            long seed,
            String era) {
    }

    public record SortieMission(String type, String modifier, String mission, String tileset) {
    }

    public record Sortie(
            @Nullable Instant activation,
            @Nullable Instant expiry,
            String boss,
            String reward,
            @JsonProperty("extra_drops") List<Object> extraDrops,
            long seed,
            List<SortieMission> missions) {
    }

    public record VoidTrader(@Nullable Instant activation, @Nullable Instant expiry, String node, String character) {
    }

    public record PrimeResurgenceItem(@JsonProperty("item_type") String itemType, int price) {
    }

    public record PrimeResurgenceScheduleInfo(
            @Nullable Instant expiry,
            @JsonProperty("featured_item") String featuredItem,
            @JsonProperty("preview_hidden_until") @Nullable Instant previewHiddenUntil) {
    }

    public record PrimeResurgence(
            @Nullable Instant activation,
            @Nullable Instant expiry,
            String node,
            @JsonProperty("initial_start_date") @Nullable Instant initialStartDate,
            List<PrimeResurgenceItem> manifest,
            @JsonProperty("evergreen_manifest") List<PrimeResurgenceItem> evergreenManifest,
            @JsonProperty("schedule_info") List<PrimeResurgenceScheduleInfo> scheduleInfo) {
    }

    public record DailyDeal(
            @Nullable Instant activation,
            @Nullable Instant expiry,
            @JsonProperty("original_price") int originalPrice,
            @JsonProperty("sale_price") int salePrice,
            String item,
            @JsonProperty("sold_amount") int soldAmount,
            @JsonProperty("total_amount") int totalAmount) {
    }

    public record ConclaveChallenge(
            @Nullable Instant activation,
            @Nullable Instant expiry,
            String category,
            @JsonProperty("pvp_mode") String pvpMode,
            @JsonProperty("challenge_type_id") String challengeTypeId,
            @JsonProperty("challenge_sub_challenges") List<String> challengeSubChallenges) {
    }

    public record FeaturedDojo(
            @JsonProperty("alliance_id") String allianceId,
            @JsonProperty("has_emblem") boolean hasEmblem,
            Map<String, Boolean> platforms,
            @JsonProperty("icon_override") int iconOverride,
            String name,
            int tier) {
    }

    public record MissionChallenge(@Nullable Instant activation, String challenge, boolean daily, @Nullable Instant expiry) {
    }

    public record SeasonInfo(
            @Nullable Instant activation,
            @Nullable Instant expiry,
            @JsonProperty("affiliation_tag") String affiliationTag,
            String parameters,
            int phase,
            int season,
            @JsonProperty("active_challenges") List<MissionChallenge> activeChallenges) {
    }

    public record WorldState(
            @JsonProperty("world_seed") String worldSeed,
            @JsonProperty("api_version") int apiVersion,
            @JsonProperty("mobile_version") String mobileVersion,
            @JsonProperty("build_label") String buildLabel,
            @JsonProperty("current_event") @Nullable Event currentEvent,
            @JsonProperty("current_alerts") List<Alert> currentAlerts,
            Sortie sortie,
            @JsonProperty("syndicate_missions") List<SyndicateMission> syndicateMissions,
            @JsonProperty("void_fissures") List<VoidFissure> voidFissures,
            @JsonProperty("global_boosts") List<String> globalBoosts,
            @JsonProperty("void_traders") List<VoidTrader> voidTraders,
            @JsonProperty("prime_resurgence") @Nullable PrimeResurgence primeResurgence,
            @JsonProperty("prime_token_availability") boolean primeTokenAvailability,
            @JsonProperty("daily_deals") List<DailyDeal> dailyDeals,
            @JsonProperty("pvp_alternative_modes") List<ConclaveChallenge> pvpAlternativeModes,
            @JsonProperty("invasion_construction_statuses") List<Double> invasionConstructionStatuses,
            @JsonProperty("feature_dojos") List<FeaturedDojo> featureDojos,
            @JsonProperty("season_info") SeasonInfo seasonInfo) {
    }
}
