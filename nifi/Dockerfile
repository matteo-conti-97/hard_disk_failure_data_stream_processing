FROM apache/nifi:latest
USER root
RUN sed -i 's/nifi.content.repository.archive.enabled=true/nifi.content.repository.archive.enabled=false/' /opt/nifi/nifi-current/conf/nifi.properties
