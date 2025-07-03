############ docker/Dockerfile ############
FROM apache/airflow:2.8.3-python3.11

# ───────── System deps ─────────
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openjdk-17-jdk curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# ───────── Spark 3.4.3 (Hadoop 3) ─────────
ARG SPARK_VERSION=3.4.3
ARG HADOOP_VERSION=3

ENV SPARK_TGZ_URL=https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/\
spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

RUN curl -fSL "$SPARK_TGZ_URL" -o /tmp/spark.tgz && \
    tar -xzf /tmp/spark.tgz -C /opt && \
    ln -s /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark && \
    rm /tmp/spark.tgz

ENV SPARK_HOME=/opt/spark
ENV PATH="${SPARK_HOME}/bin:${PATH}"

# ───────── Python deps ─────────
USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
############################################
