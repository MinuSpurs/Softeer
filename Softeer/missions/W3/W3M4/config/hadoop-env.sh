# Hadoop 환경 변수
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-arm64
export HADOOP_ROOT_LOGGER=INFO,console

# 데몬을 hadoop 계정으로 실행
export HDFS_NAMENODE_USER=hadoop
export HDFS_DATANODE_USER=hadoop
export HDFS_SECONDARYNAMENODE_USER=hadoop
export YARN_RESOURCEMANAGER_USER=hadoop
export YARN_NODEMANAGER_USER=hadoop