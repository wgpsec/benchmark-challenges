FROM maven:3.8.4-openjdk-17-slim AS builder

WORKDIR /app

COPY . .

ADD https://repo1.maven.org/maven2/ognl/ognl/3.2.12/ognl-3.2.12.jar /usr/local/tomcat/lib/

RUN mvn package

FROM tomcat:9-jdk17-openjdk-slim

COPY --from=builder /app/target/*.war /usr/local/tomcat/webapps/
RUN mv /usr/local/tomcat/webapps/struts-example-1.0-SNAPSHOT.war /usr/local/tomcat/webapps/ROOT.war

RUN [ -f /etc/apt/sources.list ] && sed -i "s|deb.debian.org|mirrors.aliyun.com|g" /etc/apt/sources.list || true
RUN apt-get update -y

RUN apt-get install -y curl

ARG FLAG
RUN echo "$FLAG" > /tmp/flag

RUN sed -i 's/port="8080"/port="80"/' /usr/local/tomcat/conf/server.xml

EXPOSE 80
