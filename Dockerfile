# syntax=docker/dockerfile:1
FROM maven:3.9.9-eclipse-temurin-21 AS build
WORKDIR /workspace
COPY api/pom.xml api/pom.xml
COPY api/src api/src
COPY web/index.html web/app.js web/style.css web/
RUN --mount=type=cache,target=/root/.m2 mvn --batch-mode --no-transfer-progress -f api/pom.xml package

FROM eclipse-temurin:21-jre-jammy AS runtime
WORKDIR /app
RUN groupadd --gid 10001 arcade && useradd --uid 10001 --gid arcade --no-create-home arcade
COPY --from=build --chown=arcade:arcade /workspace/api/target/arcade-api-0.1.0.jar /app/arcade-api.jar
USER arcade
ENV SERVER_ADDRESS=0.0.0.0 PORT=8080 DEBUG=false
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/arcade-api.jar"]
