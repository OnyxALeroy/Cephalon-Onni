package com.cephalononni.repository;

import com.cephalononni.model.Build;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface BuildRepository extends JpaRepository<Build, Long> {
    long countByUserId(Long userId);
    Optional<Build> findByIdAndUserId(Long id, Long userId);
    long deleteByIdAndUserId(Long id, Long userId);

    /**
     * DB-level paging for the build list. Hibernate 6 HQL supports limit/offset, which lets us
     * page on an arbitrary offset (Spring Data's PageRequest only pages on page*size offsets).
     */
    @Query("select b from Build b where b.userId = :userId order by b.createdAt desc, b.id desc limit :limit offset :skip")
    List<Build> findPageByUserId(@Param("userId") Long userId, @Param("skip") int skip, @Param("limit") int limit);
}
