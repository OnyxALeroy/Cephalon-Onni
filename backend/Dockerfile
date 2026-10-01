# ==========================================
# Stage 1: Build (Maven + JDK 21)
# ==========================================
FROM maven:3.9-eclipse-temurin-21 AS builder

WORKDIR /build

# Maven ignores HTTP(S)_PROXY, which Docker passes to builds when a proxy is configured; turn
# them into a settings.xml (empty when there is no proxy). They're not persisted in the image.
COPY docker/proxy-from-env.sh /usr/local/bin/proxy-from-env.sh
RUN mkdir -p /root/.m2 && proxy-from-env.sh maven-settings > /root/.m2/settings.xml

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
# The entrypoint applies the container's HTTP(S)_PROXY / NO_PROXY (if any) to the JVM, which
# ignores them otherwise: the catalog importer and worldstate poller need outbound HTTPS.
COPY docker/proxy-from-env.sh docker/entrypoint.sh /app/
RUN chown appuser:appgroup app.jar && chmod 755 /app/proxy-from-env.sh /app/entrypoint.sh

USER appuser

EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]
