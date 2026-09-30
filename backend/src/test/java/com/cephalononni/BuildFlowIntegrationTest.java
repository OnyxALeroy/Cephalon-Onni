package com.cephalononni;

import com.cephalononni.model.Arcane;
import com.cephalononni.model.Mod;
import com.cephalononni.model.Warframe;
import com.cephalononni.model.Weapon;
import com.cephalononni.repository.ArcaneRepository;
import com.cephalononni.repository.ModRepository;
import com.cephalononni.repository.WarframeRepository;
import com.cephalononni.repository.WeaponRepository;
import jakarta.servlet.http.Cookie;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * End-to-end build CRUD through the real filter chain: the ported business rules (30-build cap,
 * mod/arcane limits, catalog existence checks), user isolation (cross-user access must be 404,
 * not 403 - no existence oracle), and the update-context weapon-slot clearing.
 */
@Testcontainers
@SpringBootTest
@AutoConfigureMockMvc
class BuildFlowIntegrationTest {

    private static final String WARFRAME_UNIQUE_NAME = "/Lotus/Powersuits/Test/TestWarframe";
    private static final String WEAPON_UNIQUE_NAME = "/Lotus/Weapons/Test/TestWeapon";
    private static final String MOD_UNIQUE_NAME = "/Lotus/Mods/Test/TestMod";
    private static final String ARCANE_UNIQUE_NAME = "/Lotus/Mods/Test/TestArcane";

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @Autowired
    private MockMvc mockMvc;
    @Autowired
    private WarframeRepository warframeRepository;
    @Autowired
    private WeaponRepository weaponRepository;
    @Autowired
    private ModRepository modRepository;
    @Autowired
    private ArcaneRepository arcaneRepository;

    @BeforeEach
    void seedCatalog() {
        if (!warframeRepository.existsByUniqueName(WARFRAME_UNIQUE_NAME)) {
            Warframe warframe = new Warframe();
            warframe.setUniqueName(WARFRAME_UNIQUE_NAME);
            warframe.setName("TestWarframe");
            warframe.setMasteryReq(0);
            warframeRepository.save(warframe);
        }
        if (!weaponRepository.existsByUniqueName(WEAPON_UNIQUE_NAME)) {
            Weapon weapon = new Weapon();
            weapon.setUniqueName(WEAPON_UNIQUE_NAME);
            weapon.setName("TestWeapon");
            weapon.setProductCategory("Primary");
            weaponRepository.save(weapon);
        }
        if (!modRepository.existsByUniqueName(MOD_UNIQUE_NAME)) {
            Mod mod = new Mod();
            mod.setUniqueName(MOD_UNIQUE_NAME);
            mod.setName("TestMod");
            mod.setType("Warframe");
            mod.setRarity("Common");
            mod.setPolarity("Madurai");
            modRepository.save(mod);
        }
        if (!arcaneRepository.existsByUniqueName(ARCANE_UNIQUE_NAME)) {
            Arcane arcane = new Arcane();
            arcane.setUniqueName(ARCANE_UNIQUE_NAME);
            arcane.setName("TestArcane");
            arcane.setRarity("Rare");
            arcaneRepository.save(arcane);
        }
    }

    private Cookie registerAndLogin(String email, String username) throws Exception {
        mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"" + email + "\",\"username\":\"" + username
                                + "\",\"password\":\"hunter2\"}"))
                .andExpect(status().isOk());
        MvcResult login = mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"" + email + "\",\"password\":\"hunter2\"}"))
                .andExpect(status().isOk())
                .andReturn();
        for (Cookie cookie : login.getResponse().getCookies()) {
            if ("access_token".equals(cookie.getName())) {
                return cookie;
            }
        }
        throw new AssertionError("login did not set the access_token cookie");
    }

    /** A minimal valid create body: the given warframe, no mods/arcanes/weapons. */
    private String createBody(String name) {
        return "{\"name\":\"" + name + "\",\"warframe_uniqueName\":\"" + WARFRAME_UNIQUE_NAME
                + "\",\"warframe_mods\":[],\"warframe_arcanes\":[]}";
    }

    private String createBuild(Cookie cookie, String name) throws Exception {
        MvcResult result = mockMvc.perform(post("/api/builds/")
                        .cookie(cookie)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(createBody(name)))
                .andExpect(status().isCreated())
                .andReturn();
        return new com.fasterxml.jackson.databind.ObjectMapper()
                .readTree(result.getResponse().getContentAsString())
                .get("id")
                .asText();
    }

    @Test
    void createGetUpdateDeleteRoundTrip() throws Exception {
        Cookie cookie = registerAndLogin("build-rt@example.com", "buildrt");

        String buildId = createBuild(cookie, "My build");

        mockMvc.perform(get("/api/builds/" + buildId).cookie(cookie))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("My build"))
                .andExpect(jsonPath("$.warframe.name").value("TestWarframe"));

        mockMvc.perform(put("/api/builds/" + buildId).cookie(cookie)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"Renamed\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Renamed"));

        mockMvc.perform(get("/api/builds").cookie(cookie))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].name").value("Renamed"));

        mockMvc.perform(delete("/api/builds/" + buildId).cookie(cookie))
                .andExpect(status().isNoContent());

        mockMvc.perform(get("/api/builds/" + buildId).cookie(cookie))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.detail").value("Build not found"));
    }

    @Test
    void createValidatesTheCatalog() throws Exception {
        Cookie cookie = registerAndLogin("build-cat@example.com", "buildcat");

        mockMvc.perform(post("/api/builds/").cookie(cookie)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"Bad\",\"warframe_uniqueName\":\"/Does/Not/Exist\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.detail").value(
                        "Warframe with uniqueName '/Does/Not/Exist' not found"));

        mockMvc.perform(post("/api/builds/").cookie(cookie)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"Bad mods\",\"warframe_uniqueName\":\"" + WARFRAME_UNIQUE_NAME
                                + "\",\"warframe_mods\":[{\"uniqueName\":\"/Does/Not/Exist\",\"level\":3}],"
                                + "\"warframe_arcanes\":[]}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.detail").value(
                        "Mod with uniqueName '/Does/Not/Exist' not found"));
    }

    @Test
    void createEnforcesTheModAndArcaneLimits() throws Exception {
        Cookie cookie = registerAndLogin("build-limits@example.com", "buildlimits");

        String oneMod = "{\"uniqueName\":\"" + MOD_UNIQUE_NAME + "\",\"level\":0}";
        String elevenMods = String.join(",", java.util.Collections.nCopies(11, oneMod));
        mockMvc.perform(post("/api/builds/").cookie(cookie)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"Too many\",\"warframe_uniqueName\":\"" + WARFRAME_UNIQUE_NAME
                                + "\",\"warframe_mods\":[" + elevenMods
                                + "],\"warframe_arcanes\":[]}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.detail").value(
                        "warframeMods: Warframe can have maximum 10 mods"));

        String threeArcanes = String.join(",", java.util.Collections.nCopies(3, "\"" + ARCANE_UNIQUE_NAME + "\""));
        mockMvc.perform(post("/api/builds/").cookie(cookie)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"Too many\",\"warframe_uniqueName\":\"" + WARFRAME_UNIQUE_NAME
                                + "\",\"warframe_mods\":[],\"warframe_arcanes\":["
                                + threeArcanes + "]}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.detail").value(
                        "warframeArcanes: Warframe can have maximum 2 arcanes"));

        String tenWeaponMods = String.join(",", java.util.Collections.nCopies(10, oneMod));
        mockMvc.perform(post("/api/builds/").cookie(cookie)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"Too many\",\"warframe_uniqueName\":\"" + WARFRAME_UNIQUE_NAME
                                + "\",\"warframe_mods\":[],\"warframe_arcanes\":[],\"primary_weapon\":{"
                                + "\"weapon_uniqueName\":\"" + WEAPON_UNIQUE_NAME + "\",\"mods\":["
                                + tenWeaponMods + "]}}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.detail").value(
                        "primaryWeapon.mods: Weapon can have maximum 9 mods"));

        // And the happy path just inside every limit:
        String nineWeaponMods = String.join(",", java.util.Collections.nCopies(9, oneMod));
        mockMvc.perform(post("/api/builds/").cookie(cookie)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"Maxed\",\"warframe_uniqueName\":\"" + WARFRAME_UNIQUE_NAME
                                + "\",\"warframe_mods\":[],\"warframe_arcanes\":[\"" + ARCANE_UNIQUE_NAME
                                + "\",\"" + ARCANE_UNIQUE_NAME + "\"],\"primary_weapon\":{"
                                + "\"weapon_uniqueName\":\"" + WEAPON_UNIQUE_NAME + "\",\"mods\":["
                                + nineWeaponMods + "]}}"))
                .andExpect(status().isCreated());
    }

    @Test
    void createRejectsABlankWeaponUniqueName() throws Exception {
        Cookie cookie = registerAndLogin("build-blank@example.com", "buildblank");

        mockMvc.perform(post("/api/builds/").cookie(cookie)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"No weapon\",\"warframe_uniqueName\":\"" + WARFRAME_UNIQUE_NAME
                                + "\",\"warframe_mods\":[],\"warframe_arcanes\":[],\"primary_weapon\":{"
                                + "\"weapon_uniqueName\":\"\",\"mods\":[]}}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.detail").value("weapon_uniqueName must not be blank"));
    }

    @Test
    void updateCanClearAWeaponSlotWithABlankUniqueName() throws Exception {
        Cookie cookie = registerAndLogin("build-clear@example.com", "buildclear");

        String buildId = createBuild(cookie, "Slot clearer");
        mockMvc.perform(put("/api/builds/" + buildId).cookie(cookie)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"primary_weapon\":{\"weapon_uniqueName\":\"" + WEAPON_UNIQUE_NAME
                                + "\",\"mods\":[]}}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.primary_weapon.weapon_uniqueName").value(WEAPON_UNIQUE_NAME));

        // Blank uniqueName in update context = explicit slot clearing (unreachable in the old
        // backend because of its DTO-level NotBlank; that dead path is live again here).
        mockMvc.perform(put("/api/builds/" + buildId).cookie(cookie)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"primary_weapon\":{\"weapon_uniqueName\":\"\",\"mods\":[]}}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.primary_weapon").doesNotExist());
    }

    @Test
    void updateRejectsABlankName() throws Exception {
        Cookie cookie = registerAndLogin("build-empty-name@example.com", "buildemptyname");

        String buildId = createBuild(cookie, "Keep me");
        mockMvc.perform(put("/api/builds/" + buildId).cookie(cookie)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"   \"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.detail").value("Build name cannot be empty"));

        mockMvc.perform(get("/api/builds/" + buildId).cookie(cookie))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Keep me"));
    }

    @Test
    void otherUsersBuildsAreInvisibleAndUntouchable() throws Exception {
        Cookie owner = registerAndLogin("build-owner@example.com", "buildowner");
        Cookie intruder = registerAndLogin("build-intruder@example.com", "buildintruder");

        String buildId = createBuild(owner, "Not yours");

        // Cross-user access is 404 (not 403) on purpose: same as the old backend, this avoids
        // leaking the existence of other users' build ids.
        mockMvc.perform(get("/api/builds/" + buildId).cookie(intruder))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.detail").value("Build not found"));

        mockMvc.perform(put("/api/builds/" + buildId).cookie(intruder)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"Hijacked\"}"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.detail").value("Build not found"));

        mockMvc.perform(delete("/api/builds/" + buildId).cookie(intruder))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.detail").value("Build not found"));

        // The intruder's list never contained it, and the owner still has it.
        mockMvc.perform(get("/api/builds").cookie(intruder))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isEmpty());
        mockMvc.perform(get("/api/builds/" + buildId).cookie(owner))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Not yours"));
    }

    @Test
    void enforcesTheThirtyBuildCap() throws Exception {
        Cookie cookie = registerAndLogin("build-cap@example.com", "buildcap");

        for (int i = 1; i <= 30; i++) {
            createBuild(cookie, "Build " + i);
        }

        mockMvc.perform(post("/api/builds/").cookie(cookie)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(createBody("One too many")))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.detail").value("Maximum number of builds (30) reached"));

        // Deletion frees a slot again.
        MvcResult list = mockMvc.perform(get("/api/builds").cookie(cookie))
                .andExpect(status().isOk())
                .andReturn();
        String buildId = new com.fasterxml.jackson.databind.ObjectMapper()
                .readTree(list.getResponse().getContentAsString())
                .get(0)
                .get("id")
                .asText();
        mockMvc.perform(delete("/api/builds/" + buildId).cookie(cookie))
                .andExpect(status().isNoContent());

        mockMvc.perform(post("/api/builds/").cookie(cookie)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(createBody("Back under the cap")))
                .andExpect(status().isCreated());
    }
}
