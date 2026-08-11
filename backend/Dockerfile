# ==========================================
# Stage 1: Build (Maven + JDK 21)
# ==========================================
FROM maven:3.9-eclipse-temurin-21 AS builder

WORKDIR /build

# Cache dependencies separately from source so a source-only change doesn't refetch the world.
COPY pom.xml .
RUN mvn -B -q dependency:go-offline

COPY src ./src
RUN mvn -B -q package -DskipTests

# ==========================================
# Stage 2: Runtime (JRE only)
# ==========================================
FROM eclipse-temurin:21-jre-alpine

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app
COPY --from=builder /build/target/cephalon-onni-backend-*.jar app.jar
RUN chown appuser:appgroup app.jar

USER appuser

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
