FROM flink:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

RUN pip3 install --upgrade pip

RUN python3 -m pip install apache-flink

RUN python3 -m pip install kafka-python

RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/1.17.1/flink-sql-connector-kafka-1.17.1.jar

RUN python3 -m pip install jproperties

RUN python3 -m pip install psquare

RUN python3 -m pip install tdigest

RUN ln -s /usr/bin/python3 /usr/bin/python
