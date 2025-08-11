# Base image
FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG SPARK_VERSION=4.0.0
ARG HADOOP_VERSION=3

ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64

# Install required packages
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    curl \
    python3 \
    python3-pip \
    net-tools \
    iputils-ping \
    ssh \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Symlink python
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Install Spark
RUN curl -fSL https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -o spark.tgz && \
    tar -xzf spark.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} $SPARK_HOME && \
    rm spark.tgz

# Install Jupyter Notebook
RUN pip install notebook pyspark matplotlib pandas

# Set working directory
WORKDIR /scripts

# Copy local scripts
COPY data/ /data