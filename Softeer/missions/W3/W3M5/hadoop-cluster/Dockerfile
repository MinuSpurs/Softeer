# 베이스 이미지
FROM ubuntu:20.04

# 비대화 모드 설정
ARG DEBIAN_FRONTEND=noninteractive

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    openjdk-8-jdk-headless \
    ssh \
    rsync \
    curl \
    wget \
    nano \
    openssh-server \
    net-tools \
    iputils-ping \
    vim \
    python3 \
    python3-pip

RUN ln -s /usr/bin/python3 /usr/bin/python

# JAVA 환경변수 설정
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-arm64
ENV HADOOP_VERSION=3.3.6
ENV HADOOP_HOME=/usr/local/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$JAVA_HOME/bin

# Hadoop 설치
RUN wget https://downloads.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && \
    tar -xzf hadoop-${HADOOP_VERSION}.tar.gz -C /usr/local/ && \
    mv /usr/local/hadoop-${HADOOP_VERSION} $HADOOP_HOME && \
    rm hadoop-${HADOOP_VERSION}.tar.gz


# SSH 데몬 실행을 위해 디렉토리 생성
RUN mkdir /var/run/sshd

# Hadoop 설정 복사
COPY config/* $HADOOP_HOME/etc/hadoop/

# 일반 사용자 추가
RUN useradd -m hadoop && \
    echo "hadoop:hadoop" | chpasswd

# 권한 설정
RUN mkdir -p $HADOOP_HOME/hdfs/namenode && \
    mkdir -p $HADOOP_HOME/hdfs/datanode && \
    chown -R hadoop:hadoop $HADOOP_HOME

# 포트 오픈 (HDFS/YARN UI용)
EXPOSE 9870 9864 8088 8042 22

# SSH 설정 (hadoop 사용자 기준)
RUN mkdir -p /home/hadoop/.ssh && chown hadoop:hadoop /home/hadoop/.ssh
RUN ssh-keygen -t rsa -P '' -f /home/hadoop/.ssh/id_rsa && \
    cat /home/hadoop/.ssh/id_rsa.pub >> /home/hadoop/.ssh/authorized_keys && \
    chmod 700 /home/hadoop/.ssh && chmod 600 /home/hadoop/.ssh/authorized_keys && \
    chown -R hadoop:hadoop /home/hadoop/.ssh

# entrypoint 스크립트 추가 (실행 권한은 COPY --chmod 로 부여됨)
COPY --chmod=755 entrypoint.sh /entrypoint.sh

# root 권한으로 ENTRYPOINT 실행 (sshd 기동 후 내부에서 su - hadoop)
ENTRYPOINT ["/entrypoint.sh"]