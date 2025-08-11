#!/bin/bash
set -ex

# ── sshd 기동 (root)
mkdir -p /var/run/sshd
/usr/sbin/sshd -D & 

# HDFS 이름 디렉터리 생성 및 권한 설정
mkdir -p /hadoop/dfs/name
chown -R hadoop:hadoop /hadoop

# ──────────────────────────────────────────────────────────────
#  공통 환경변수
# ──────────────────────────────────────────────────────────────
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-arm64
export HADOOP_HOME=/usr/local/hadoop
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
export HADOOP_ROOT_LOGGER=INFO,console

# 데몬을 hadoop 사용자로 실행하도록 명시
export HDFS_NAMENODE_USER=hadoop
export HDFS_DATANODE_USER=hadoop
export HDFS_SECONDARYNAMENODE_USER=hadoop
export YARN_RESOURCEMANAGER_USER=hadoop
export YARN_NODEMANAGER_USER=hadoop

# hadoop-env.sh에 로거 한 줄만(중복 방지)
grep -q "HADOOP_ROOT_LOGGER=INFO,console" $HADOOP_HOME/etc/hadoop/hadoop-env.sh || \
echo -e "\nexport HADOOP_ROOT_LOGGER=INFO,console" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh

# ──────────────────────────────────────────────────────────────
#  노드 종류별 작업
# ──────────────────────────────────────────────────────────────
if [ "$HOSTNAME" = "namenode" ]; then
    # 최초 1회 namenode 포맷
    if [ ! -d "/hadoop/dfs/name/current" ]; then
        echo "▶ Formatting HDFS (namenode)"
        su hadoop -c "$HADOOP_HOME/bin/hdfs namenode -format -force" || true
    fi

    echo "▶ Starting HDFS + YARN (namenode)"
    rm -f /tmp/hadoop-hadoop-datanode.pid
    rm -f /tmp/hadoop-hadoop-namenode.pid
    rm -f /tmp/hadoop-hadoop-secondarynamenode.pid
    rm -f /tmp/hadoop-hadoop-resourcemanager.pid
    su hadoop -c "$HADOOP_HOME/bin/hdfs namenode" &
    su hadoop -c "$HADOOP_HOME/bin/hdfs secondarynamenode" &
    su hadoop -c "$HADOOP_HOME/bin/yarn resourcemanager" &
else
    echo "▶ Starting HDFS + YARN (worker)"
    rm -f /tmp/hadoop-hadoop-datanode.pid
    rm -f /tmp/hadoop-hadoop-nodemanager.pid
    su hadoop -c "$HADOOP_HOME/bin/hdfs datanode" &
    su hadoop -c "$HADOOP_HOME/bin/yarn nodemanager" &
fi

# 짧은 지연 후 데몬 확인
sleep 3
su - hadoop -c "jps"

# hadoop 사용자 .bashrc에 환경변수 등록
echo 'export HADOOP_HOME=/usr/local/hadoop' >> /home/hadoop/.bashrc
echo 'export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin' >> /home/hadoop/.bashrc
chown hadoop:hadoop /home/hadoop/.bashrc

# 컨테이너 유지
exec /bin/bash || tail -f /dev/null