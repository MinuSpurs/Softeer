# W3M2a

## Dockerfile

```docker
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
    vim

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

# entrypoint 스크립트
COPY --chmod=755 entrypoint.sh /entrypoint.sh

# root 권한으로 ENTRYPOINT 실행
ENTRYPOINT ["/entrypoint.sh"]
```

- FROM ubuntu:20.04
    - Docker 이미지의 기반이 될 OS로 Ubuntu 20.04 버전 사용
- ARG DEBIAN_FRONTEND=noninteractive
    - apt 설치 시 입력을 받지 않도록 비대화 모드로 설정. Docker 이미지 빌드 과정에서 프롬프트가 멈추는 것을 방지
- Run apt-get update …
    - 패키지 목록을 업데이트하고 Hadoop 실행에 필요한 필수 패키지를 설치
- ENV JAVA_HOME, HADOOP_HOME, HADOOP_VERSION=3.3.6
    - Hadoop의 기본 경로 및 실행 경로, Java 경로를 명시적으로 설정하여 내부 스크립트 및 명령어가 정상적으로 동작하도록 함
    - 사용한 Hadoop 버전을 명시하여 유지보수성과 가독성 높임
- RUN wget …
    - Apache 공식 사이트에서 Hadoop 패키지를 다운로드하고 지정 경로에 압축 해재
- RUN mkdir var/run/sshd
    - SSH 데몬 실행에 필요한 디렉토리 생성
- COPY config/* HADOOP_HOME/etc/hadoop
    - 로컬의 config 디렉토리에 준비된 hadoop 설정 파일(core-site, hdfs-site, mapred-site, yarn-site)들을 이미지 내부의 hadoop 설정 경로로 복사
- RUN useradd -m hadoop …
    - Hadoop 데몬을 실행할 hadoop 사용자 계정을 생성하고 비밀번호 설정
- RUN mkdir -p ~
    - Hadoop의 NameNode, DataNode 데이터를 저장할 디렉토리를 만들고 hadoop 사용자에게 권한을 부여
- EXPOSE …
    - 클러스터 운영에 필요한 포트들을 외부에 오픈
- RUN ssh-keygen …
    - hadoop 사용자 계정으로 SSH 키를 생성하고, 자기 자신의 공개키를 authorized_keys에 추가하여 비밀번호 없는 SSH 접속을 허용
- COPY —chmod=755 [entrypoint.sh](http://entrypoint.sh) /entrypoint.sh
    - Hadoop 클러스터를 위한 entrypoint.sh를 복사하고 실행 권한 부여
- ENTRYPOINT [”/entrypoint.sh”]
    - 컨테이너 시작 시 자동으로 Hadoop 서비스를 실행하도록 entrypoint 스크립트를 지정

## Entrypoint.sh

```bash
#!/bin/bash
set -ex

# ── sshd 기동 (root)
mkdir -p /var/run/sshd
/usr/sbin/sshd -D & 

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
if [ "$HOSTNAME" = "master" ]; then
    # 최초 1회 namenode 포맷
    if [ ! -d "/usr/local/hadoop/hdfs/namenode/current" ]; then
        echo "▶ Formatting HDFS (namenode)"
        su hadoop -c "$HADOOP_HOME/bin/hdfs namenode -format -force" || true
    fi

    echo "▶ Starting HDFS + YARN (master)"
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

# 컨테이너 유지
exec /bin/bash || tail -f /dev/null
```

- #!/bin/bash
    - Bash 쉘로 스크립트를 실행하도록 지정
- set -ex
    - 실행 중 명령어를 출력하고 실패시 중단
- mkdir -p /var/run/sshd ~
    - SSH 데몬 실행에 필요한 디렉토리 생성 후 백그라운드로 SSH 실행
- export ~
    - Java와 Hadoop 경로, 로그 레벨 등을 환경 변수로 등록
- Hadoop 데몬 사용자 설정
    - 각 Hadoop 데몬을 hadoop 사용자로 실행하도록 지정
- grep -q “HADOOP_ROOT_LOGGER ~”
    - [hadoop-env.sh](http://hadoop-env.sh) 로그 설정 보완
- if [ “$HOSTNAME” = “master” ]; then
    - 마스터 노드 분기 처리
        - namenode가 포맷되지 않은 경우에만 최초 1회 포맷
        - 불필요한 PID 파일 제거 후 데몬 실행
- else ~
    - 워커 노드용 데몬 실행
- sleep 3
su - hadoop -c "jps"
exec /bin/bash || tail -f /dev/null
    - 데몬 실행 후 3초 지연 후 jps 프로세스 확인
    - 컨테이너가 종료되지 않도록 bash 셸 또는 로그 tail 유지

## Docker network 생성

```bash
docker network create hadoop-net
```

- Docker network를 생성해줌

```bash
docker network ls

NETWORK ID     NAME         DRIVER    SCOPE
1768f7fcb1bb   bridge       bridge    local
8b3722acf15f   hadoop-net   bridge    local
c48867b297e0   host         host      local
7435e5c77fd9   none         null      local
```

- 잘 생성된 것을 확인해줌

```bash
docker run -dit --name worker1 --hostname worker1 --network hadoop-net gapbu123/w3m2

docker run -dit --name worker2 --hostname worker2 --network hadoop-net gapbu123/w3m2

docker run -it --name hadoop-master \              ✔ │ base  │ 10:38:31
  --hostname master \
  --network hadoop-net \
  -p 9870:9870 -p 8088:8088 -p 8042:8042 -p 2222:22 \
  gapbu123/w3m2 \
  /bin/bash
```

- 생성된 dockerfile을 불러와 worker는 백그라운드로, master는 bash로 실행시켜줌
<img width="175" height="74" alt="image" src="https://github.com/user-attachments/assets/deb321a3-462f-4fc9-887d-e8f38b58b756" />

- master container에는 노드가 잘 생성된 것을 확인할 수 있음

```bash
docker exec -it worker1 bash
```
<img width="165" height="65" alt="image 1" src="https://github.com/user-attachments/assets/679a8542-ab1b-4b4e-9959-1dee5066622b" />

- 워커노드에 docker exec으로 들어가 확인하면 역시 node가 잘 생성된 것을 확인할 수 있음

## **HDFS Operations**

```bash
hdfs dfs -mkdir -p /user/hadoop/input

echo "Hello Hadoop" > hello.txt
hdfs dfs -put hello.txt /user/hadoop/input/

hdfs dfs -get /user/hadoop/input/hello.txt downloaded_hello.txt

cat downloaded_hello.txt
```

- cat을 통해 확인해보면
<img width="220" height="37" alt="image 2" src="https://github.com/user-attachments/assets/46d1e152-1453-43f4-a01c-a41e06a227f8" />

- 잘 나오는 것을 확인할 수 있음

## **Cluster Operations (MapReduce Job 실행)**

- Hadoop이 기본적으로 제공하는 예제를 확인

```bash
ls $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar

echo "this is a simple test for hadoop mapreduce" > word_input.txt
hdfs dfs -mkdir -p /user/hadoop/wordcount/input

hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar wordcount \
  /user/hadoop/wordcount/input \
  /user/hadoop/wordcount/output
```

- Wordcount용 입력파일을 준비한 뒤, wordcount를 실행해줌

```bash
2025-07-24 01:35:47,642 INFO mapreduce.Job:  map 0% reduce 0%
2025-07-24 01:35:52,779 INFO mapreduce.Job:  map 100% reduce 0%
2025-07-24 01:35:58,845 INFO mapreduce.Job:  map 100% reduce 100%
2025-07-24 01:35:59,878 INFO mapreduce.Job: Job job_1753320580653_0001 completed successfully
2025-07-24 01:36:00,029 INFO mapreduce.Job: Counters: 54
	File System Counters
		FILE: Number of bytes read=97
		FILE: Number of bytes written=552877
		FILE: Number of read operations=0
		FILE: Number of large read operations=0
		FILE: Number of write operations=0
		HDFS: Number of bytes read=169
		HDFS: Number of bytes written=59
		HDFS: Number of read operations=8
		HDFS: Number of large read operations=0
		HDFS: Number of write operations=2
		HDFS: Number of bytes read erasure-coded=0
	Job Counters
		Launched map tasks=1
		Launched reduce tasks=1
		Data-local map tasks=1
		Total time spent by all maps in occupied slots (ms)=2339
		Total time spent by all reduces in occupied slots (ms)=3228
		Total time spent by all map tasks (ms)=2339
		Total time spent by all reduce tasks (ms)=3228
		Total vcore-milliseconds taken by all map tasks=2339
		Total vcore-milliseconds taken by all reduce tasks=3228
		Total megabyte-milliseconds taken by all map tasks=2395136
		Total megabyte-milliseconds taken by all reduce tasks=3305472
	Map-Reduce Framework
		Map input records=1
		Map output records=8
		Map output bytes=75
		Map output materialized bytes=97
		Input split bytes=126
		Combine input records=8
		Combine output records=8
		Reduce input groups=8
		Reduce shuffle bytes=97
		Reduce input records=8
		Reduce output records=8
		Spilled Records=16
		Shuffled Maps =1
		Failed Shuffles=0
		Merged Map outputs=1
		GC time elapsed (ms)=245
		CPU time spent (ms)=920
		Physical memory (bytes) snapshot=495820800
		Virtual memory (bytes) snapshot=4949180416
		Total committed heap usage (bytes)=371720192
		Peak Map Physical memory (bytes)=253288448
		Peak Map Virtual memory (bytes)=2468593664
		Peak Reduce Physical memory (bytes)=242532352
		Peak Reduce Virtual memory (bytes)=2480586752
	Shuffle Errors
		BAD_ID=0
		CONNECTION=0
		IO_ERROR=0
		WRONG_LENGTH=0
		WRONG_MAP=0
		WRONG_REDUCE=0
	File Input Format Counters
		Bytes Read=43
	File Output Format Counters
		Bytes Written=59
```

- 위와 같은 성공 메세지를 확인한 뒤

```bash
hdfs dfs -ls /user/hadoop/wordcount/output
```
<img width="791" height="100" alt="image 3" src="https://github.com/user-attachments/assets/e2ba5c79-aa52-440b-8e0b-3198eb423ac9" />

```bash
hdfs dfs -cat /user/hadoop/wordcount/output/part-r-00000
```
<img width="809" height="197" alt="image 4" src="https://github.com/user-attachments/assets/7ef95487-0f05-4f12-8515-cd97e59f558e" />

- 결과가 잘 나온 것을 확인할 수 있음

## **Accessibility**

[http://localhost:9870/](http://localhost:9870/)
<img width="1185" height="457" alt="image 5" src="https://github.com/user-attachments/assets/d62eb079-40f6-4b89-9121-c0e728245a67" />

[http://localhost:8088/cluster](http://localhost:8088/cluster)
<img width="1709" height="552" alt="image 6" src="https://github.com/user-attachments/assets/82ecd778-3629-475a-a91a-c3db5a96385e" />

- URL을 통해 들어가도 잘 작동하고 파일이 저장되어 있는 것을 확인할 수 있음
