package com.cephalononni;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.mongo.MongoAutoConfiguration;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * MongoAutoConfiguration is excluded deliberately: the mongodb-driver-sync dependency exists
 * only for DataMigrationRunner's one-time use (it builds its own MongoClient explicitly, from
 * MONGO_URL, only when app.migration.enabled=true). Without this exclusion, Spring Boot
 * auto-configures and eagerly connects a MongoClient bean on every startup just because the
 * driver is on the classpath - logging constant "connection refused" noise against
 * localhost:27017 in every environment that doesn't run Mongo (i.e. every environment after this
 * rework).
 */
@SpringBootApplication(exclude = MongoAutoConfiguration.class)
@EnableScheduling
public class CephalonOnniApplication {

    public static void main(String[] args) {
        SpringApplication.run(CephalonOnniApplication.class, args);
    }
}
