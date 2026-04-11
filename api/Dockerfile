# Fase 1: Construcción (Maven)
FROM maven:3.8.4-openjdk-11-slim AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
# Compilamos el proyecto de Spring Boot
RUN mvn clean package -DskipTests

# Fase 2: Ejecución (Java Liviano)
FROM openjdk:11-jre-slim
WORKDIR /app
COPY --from=build /app/target/TERMOMETRO-RED-0.0.1-SNAPSHOT.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]