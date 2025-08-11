#!/bin/bash

# Hadoop 초기 포맷 (최초 1회만 실행 필요, 자동 실행시 주의)
$HADOOP_HOME/bin/hdfs namenode -format

# SSH 서비스 시작
service ssh start

# Hadoop 데몬 시작
$HADOOP_HOME/sbin/start-dfs.sh
$HADOOP_HOME/sbin/start-yarn.sh

# 컨테이너가 죽지 않도록 bash 유지
/bin/bash