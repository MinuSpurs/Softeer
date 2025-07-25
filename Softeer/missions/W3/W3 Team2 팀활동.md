# TEAM2 팀 활동

# W3M2b 팀활동

## Core-site.xml

- core-site.xml은 Hadoop의 **기본 파일 시스템 설정**과 **전역 환경 변수**를 정의하는 핵심 설정 파일입니다. 이 파일은 HDFS뿐 아니라 YARN, MapReduce, Spark 등 Hadoop 위에서 동작하는 다양한 서비스들의 **기본 동작을 제어**합니다.

1. **fs.defaultFS**

```python
<property>
  <name>fs.defaultFS</name>
  <value>hdfs://namenode:9000</value>
</property>
```

- **용도**: 클러스터의 기본 파일 시스템을 지정 (HDFS, S3, etc.)
- **중요성**: 모든 작업의 기본 입출력 경로를 결정하는 핵심 설정
- **예시**: hadoop fs -ls / 하면 이 주소를 기준으로 경로가 처리됨

1. **hadoop.tmp.dir**

```python
<property>
  <name>hadoop.tmp.dir</name>
  <value>/hadoop/tmp</value>
</property>
```

- **용도**: HDFS의 임시 파일 및 로그, PID, socket 등의 경로를 지정
- **중요성**: 이 디렉토리에 쓰기 권한이 없으면 데몬들이 제대로 기동되지 않음
- **팁**: Docker 등 컨테이너 환경에서는 명시적으로 이 경로를 생성해주는 것이 좋음

1. **dfs.client.use.datanode.hostname**

```python
<property>
  <name>dfs.client.use.datanode.hostname</name>
  <value>true</value>
</property>
```

- **용도**: 클라이언트가 DataNode에 접속할 때 내부 IP 대신 호스트명을 사용할지 여부
- **중요성**: Docker, AWS 등 **NAT 환경**에서 **접속 불가 문제 방지**에 매우 중요
- **권장값**: true로 설정하는 것이 일반적

1. **io.file.buffer.size**

```python
<property>
  <name>dfs.client.use.datanode.hostname</name>
  <value>true</value>
</property>
```

****

****

****

- **용도**: HDFS 파일을 읽고 쓸 때 사용하는 버퍼 크기
- **중요성**: I/O 성능 최적화에 영향
- **팁**: 고속 네트워크 환경일수록 값 증가 → 쓰기/읽기 속도 향상

## hdfs-site.xml

- 핵심 설정: dfs.replication- 역할: 데이터 블록의 복제 개수를 지정- 중요성: - 데이터의 내결함성(Fault Tolerance) 확보 - 클러스터 일부 노드 장애 시에도 데이터 손실 없이 복구 가능 - 멀티 노드 클러스터에서 데이터 분산 및 가용성 향상 - 복제 수 조정을 통해 자원 활용 및 확장성 조절 가능

## yarn-site

- yarn에서 resource memory 관리를 직접 할 수 있다 보니까 map reduce 작업을 돌릴 때 가용 자원에 맞추어 세팅할 수 있는 장점이 있다. scheduler.minimum-allocation-mb 또는 maximum-allocation-mb를 사용하여 하나의 컨테이너당 최대/최소 할당 메모리를 지정하고, nodemanager.resource.memory-mb로 클러스터의 각 노드에서 운영할 수 있는 메모리의 총량도 지정할 수 있다.

# W3M4 팀활동

- Mapreduce에서는 최대한 간단한 걸 쓰는게 좋음
- 기존에는 "good", "bad", "happy"처럼 사람이 미리 정한 키워드로 감정을 나눴다면,
- 우리는 TextBlob 라이브러리를 사용해 문장 전체의 맥락과 어휘에 기반해 polarity(극성)를 계산하고, 이를 기준으로 positive / neutral / negative로 분류함.
- TextBlob은 문장의 감정 상태를 수치화하여 다음과 같이 판단합니다:
    - polarity (극성): -1.0 (매우 부정적) ~ 1.0 (매우 긍정적)
    - subjectivity (주관성): 0.0 (객관적) ~ 1.0 (주관적)

### 이 방법의 장점

- 사전 정의 키워드에 의존하지 않음 → 새로운 단어나 문맥도 자동으로 해석 가능
- 문장 전체의 톤과 분위기를 수치로 해석 → 더 유연하고 일반화된 판단 가능
- 키워드 기반 방식보다 정확도와 확장성 측면에서 유리함