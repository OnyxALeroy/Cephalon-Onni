package com.cephalononni.repository;

import com.cephalononni.model.Mod;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;
import java.util.Optional;

public interface ModRepository extends JpaRepository<Mod, Integer> {
    Optional<Mod> findByUniqueName(String uniqueName);
    boolean existsByUniqueName(String uniqueName);

    /**
     * Scalar-only projection for the public /api/builds/available/mods listing. Matters most
     * here: the mods table's description/levelStats/upgradeEntries JSONB columns are the
     * heaviest in the catalog and are not needed for the listing.
     */
    @Query("select m.uniqueName as uniqueName, m.name as name, m.type as type, m.rarity as rarity, m.polarity as polarity from Mod m order by m.id")
    List<ModBrief> findAllBrief();

    interface ModBrief {
        String getUniqueName();
        String getName();
        String getType();
        String getRarity();
        String getPolarity();
    }
}
