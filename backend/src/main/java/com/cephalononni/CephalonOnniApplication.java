package com.cephalononni;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class CephalonOnniApplication {

    public static void main(String[] args) {
        SpringApplication.run(CephalonOnniApplication.class, args);
    }
}
