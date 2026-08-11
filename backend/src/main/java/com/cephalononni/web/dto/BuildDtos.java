package com.cephalononni.web.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import java.time.Instant;
import java.util.List;
import java.util.Map;

public final class BuildDtos {

    private BuildDtos() {}

    public record EquippedMod(@NotBlank String uniqueName, @Min(0) @Max(10) Integer level) {
        public EquippedMod {
            if (level == null) {
                level = 0;
            }
        }
    }

    public record WeaponBuild(
            @JsonProperty("weapon_uniqueName") @NotBlank String weaponUniqueName,
            @Valid @Size(max = 9, message = "Weapon can have maximum 9 mods") List<EquippedMod> mods,
            @JsonProperty("arcane_uniqueName") String arcaneUniqueName) {
        public WeaponBuild {
            if (mods == null) {
                mods = List.of();
            }
        }
    }

    public record CreateRequest(
            @NotBlank String name,
            @JsonProperty("warframe_uniqueName") @NotBlank String warframeUniqueName,
            @JsonProperty("warframe_mods")
            @Valid @Size(max = 10, message = "Warframe can have maximum 10 mods") List<EquippedMod> warframeMods,
            @JsonProperty("warframe_arcanes")
            @Size(max = 2, message = "Warframe can have maximum 2 arcanes") List<String> warframeArcanes,
            @JsonProperty("primary_weapon") @Valid WeaponBuild primaryWeapon,
            @JsonProperty("secondary_weapon") @Valid WeaponBuild secondaryWeapon,
            @JsonProperty("melee_weapon") @Valid WeaponBuild meleeWeapon) {
        public CreateRequest {
            if (warframeMods == null) warframeMods = List.of();
            if (warframeArcanes == null) warframeArcanes = List.of();
        }
    }

    /** Every field optional/nullable = "leave as-is"; a WeaponBuild with a blank uniqueName clears that slot. */
    public record UpdateRequest(
            String name,
            @JsonProperty("warframe_uniqueName") String warframeUniqueName,
            @JsonProperty("warframe_mods")
            @Valid @Size(max = 10, message = "Warframe can have maximum 10 mods") List<EquippedMod> warframeMods,
            @JsonProperty("warframe_arcanes")
            @Size(max = 2, message = "Warframe can have maximum 2 arcanes") List<String> warframeArcanes,
            @JsonProperty("primary_weapon") @Valid WeaponBuild primaryWeapon,
            @JsonProperty("secondary_weapon") @Valid WeaponBuild secondaryWeapon,
            @JsonProperty("melee_weapon") @Valid WeaponBuild meleeWeapon) {
    }

    public record Ability(String abilityUniqueName, String abilityName, String description) {
    }

    public record WarframeDetails(
            String uniqueName,
            String name,
            String parentName,
            String description,
            Integer health,
            Integer shield,
            Integer armor,
            Integer stamina,
            Integer power,
            Boolean codexSecret,
            Integer masteryReq,
            Double sprintSpeed,
            String passiveDescription,
            List<String> exalted,
            List<Ability> abilities,
            String productCategory) {
    }

    public record WeaponDetails(
            String uniqueName,
            String name,
            Boolean codexSecret,
            Double criticalChance,
            Double criticalMultiplier,
            List<Integer> damagePerShot,
            String description,
            Double fireRate,
            Integer masteryReq,
            Double omegaAttenuation,
            Double procChance,
            String productCategory,
            Integer totalDamage,
            Double accuracy,
            Integer magazineSize,
            Double reloadTime,
            Integer multishot,
            String noise,
            String trigger) {
    }

    public record ArcaneDetails(
            String uniqueName,
            String name,
            Boolean codexSecret,
            String rarity,
            List<Map<String, Object>> levelStats) {
    }

    /** GET /api/builds (list) item shape - no user_id, warframe enrichment only. */
    public record BuildPublic(
            String id,
            String name,
            @JsonProperty("warframe_uniqueName") String warframeUniqueName,
            @JsonProperty("created_at") Instant createdAt,
            @JsonProperty("updated_at") Instant updatedAt,
            WarframeDetails warframe,
            @JsonProperty("warframe_mods") List<EquippedMod> warframeMods,
            @JsonProperty("warframe_arcanes") List<String> warframeArcanes,
            @JsonProperty("primary_weapon") WeaponBuild primaryWeapon,
            @JsonProperty("secondary_weapon") WeaponBuild secondaryWeapon,
            @JsonProperty("melee_weapon") WeaponBuild meleeWeapon) {
    }

    /** POST /api/builds/ (create) response shape - includes user_id, no enrichment. */
    public record BuildCreated(
            String id,
            String name,
            @JsonProperty("warframe_uniqueName") String warframeUniqueName,
            @JsonProperty("warframe_mods") List<EquippedMod> warframeMods,
            @JsonProperty("warframe_arcanes") List<String> warframeArcanes,
            @JsonProperty("primary_weapon") WeaponBuild primaryWeapon,
            @JsonProperty("secondary_weapon") WeaponBuild secondaryWeapon,
            @JsonProperty("melee_weapon") WeaponBuild meleeWeapon,
            @JsonProperty("user_id") String userId,
            @JsonProperty("created_at") Instant createdAt,
            @JsonProperty("updated_at") Instant updatedAt) {
    }

    /**
     * GET/PUT single-build shape. Unlike the old backend's BuildWithDetails, `warframe` is
     * nullable (there it was non-Optional but could be assigned null, which crashed response
     * serialization) and `warframeArcanes` here is the real List&lt;ArcaneDetails&gt; the model
     * always claimed to be, not the raw uniqueName strings it actually got. Both were live bugs
     * in the old backend - fixed here rather than ported.
     */
    public record BuildWithDetails(
            String id,
            String name,
            @JsonProperty("warframe_uniqueName") String warframeUniqueName,
            @JsonProperty("created_at") Instant createdAt,
            @JsonProperty("updated_at") Instant updatedAt,
            WarframeDetails warframe,
            @JsonProperty("warframe_mods") List<EquippedMod> warframeMods,
            @JsonProperty("warframe_arcanes") List<ArcaneDetails> warframeArcanes,
            @JsonProperty("primary_weapon") WeaponBuild primaryWeapon,
            @JsonProperty("secondary_weapon") WeaponBuild secondaryWeapon,
            @JsonProperty("melee_weapon") WeaponBuild meleeWeapon,
            @JsonProperty("primary_weapon_details") WeaponDetails primaryWeaponDetails,
            @JsonProperty("secondary_weapon_details") WeaponDetails secondaryWeaponDetails,
            @JsonProperty("melee_weapon_details") WeaponDetails meleeWeaponDetails,
            @JsonProperty("primary_arcane_details") ArcaneDetails primaryArcaneDetails,
            @JsonProperty("secondary_arcane_details") ArcaneDetails secondaryArcaneDetails,
            @JsonProperty("melee_arcane_details") ArcaneDetails meleeArcaneDetails) {
    }
}
