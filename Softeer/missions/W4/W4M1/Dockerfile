FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

ARG SPARK_VERSION=4.0.0
ARG HADOOP_VERSION=3

ENV SPARK_VERSION=${SPARK_VERSION}
ENV HADOOP_VERSION=${HADOOP_VERSION}
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64

RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    curl \
    python3 \
    python3-pip \
    net-tools \
    iputils-ping \
    ssh \
    vim

RUN ln -sf /usr/bin/python3 /usr/bin/python

RUN curl -fSL https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -o spark.tgz && \
    tar -xzf spark.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} $SPARK_HOME && \
    rm spark.tgz

COPY scripts/ /scripts