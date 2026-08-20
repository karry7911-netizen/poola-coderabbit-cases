FROM mirror.gcr.io/eclipse-temurin:17-jre-jammy

WORKDIR /app

# Copy the built Quarkus application
COPY target/quarkus-app/lib/ /app/lib/
COPY target/quarkus-app/*.jar /app/
COPY target/quarkus-app/app/ /app/app/
COPY target/quarkus-app/quarkus/ /app/quarkus/

EXPOSE 8082

CMD ["java", "-jar", "/app/quarkus-run.jar"]
