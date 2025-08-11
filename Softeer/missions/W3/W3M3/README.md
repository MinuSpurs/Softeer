# W3M3

실습에서 사용한 책 정보

https://www.gutenberg.org/ebooks/1342

## Docker 네트워크 생성

```bash
docker network create hadoop-net
```

- 도커 네트워크를 생성해줌

## 컨테이너 실행

```bash
# namenode
docker run -d \
  --name namenode \
  --hostname namenode \
  --network hadoop-net \
  -p 9870:9870 -p 8088:8088 -p 8042:8042 -p 2222:22 \
  gapbu123/w3m3

# worker1
docker run -d \
  --name worker1 \
  --hostname worker1 \
  --network hadoop-net \
  gapbu123/w3m3

# worker2
docker run -d \
  --name worker2 \
  --hostname worker2 \
  --network hadoop-net \
  gapbu123/w3m3
```

## 데몬/클러스터 상태 확인

```bash
docker exec -it namenode bash -lc "su - hadoop -c 'jps'"

529 Jps
76 SecondaryNameNode
77 ResourceManager
78 NameNode
```

```bash
docker exec -it worker1 bash -lc "jps"
19 NodeManager
308 Jps
20 DataNode

docker exec -it worker2 bash -lc "jps"
306 Jps
19 NodeManager
20 DataNode
```

```bash
docker exec -it namenode bash -lc "su - hadoop -c '/usr/local/hadoop/bin/hdfs dfsadmin -report'"

here applicable
Configured Capacity: 970947969024 (904.27 GB)
Present Capacity: 802085183488 (747.00 GB)
DFS Remaining: 802085134336 (747.00 GB)
DFS Used: 49152 (48 KB)
DFS Used%: 0.00%
Replicated Blocks:
	Under replicated blocks: 0
	Blocks with corrupt replicas: 0
	Missing blocks: 0
	Missing blocks (with replication factor 1): 0
	Low redundancy blocks with highest priority to recover: 0
	Pending deletion blocks: 0
Erasure Coded Block Groups:
	Low redundancy block groups: 0
	Block groups with corrupt internal blocks: 0
	Missing block groups: 0
	Low redundancy blocks with highest priority to recover: 0
	Pending deletion blocks: 0

-------------------------------------------------
Live datanodes (2):

Name: 172.18.0.2:9866 (worker1.hadoop-net)
Hostname: worker1
Decommission Status : Normal
Configured Capacity: 485473984512 (452.13 GB)
DFS Used: 24576 (24 KB)
Non DFS Used: 59695435776 (55.60 GB)
DFS Remaining: 401042567168 (373.50 GB)
DFS Used%: 0.00%
DFS Remaining%: 82.61%
Configured Cache Capacity: 0 (0 B)
Cache Used: 0 (0 B)
Cache Remaining: 0 (0 B)
Cache Used%: 100.00%
Cache Remaining%: 0.00%
Xceivers: 0
Last contact: Thu Jul 24 08:37:54 UTC 2025
Last Block Report: Thu Jul 24 08:36:54 UTC 2025
Num of Blocks: 0

Name: 172.18.0.3:9866 (worker2.hadoop-net)
Hostname: worker2
Decommission Status : Normal
Configured Capacity: 485473984512 (452.13 GB)
DFS Used: 24576 (24 KB)
Non DFS Used: 59695435776 (55.60 GB)
DFS Remaining: 401042567168 (373.50 GB)
DFS Used%: 0.00%
DFS Remaining%: 82.61%
Configured Cache Capacity: 0 (0 B)
Cache Used: 0 (0 B)
Cache Remaining: 0 (0 B)
Cache Used%: 100.00%
Cache Remaining%: 0.00%
Xceivers: 0
Last contact: Thu Jul 24 08:37:55 UTC 2025
Last Block Report: Thu Jul 24 08:37:01 UTC 2025
Num of Blocks: 0
```

worker들이 제대로 작동하고 datanode가 잘 잡히는지 확인

## Mapper.py

```python
#!/usr/bin/env python3
import sys, re

word_re = re.compile(r"[A-Za-z']+")  # 단어만 추출(간단 정규식)
for line in sys.stdin:
    for w in word_re.findall(line.lower()):
        print(f"{w}\t1")
```

- 한 줄씩 stdin으로 텍스트를 받음
    - 정규식을 통해 영어 단어만 추출
    - 단어를 소문자로 통일
    - 각 단어마다 “단어\t1” 형태로 출력

## Reduce.py

```python
#!/usr/bin/env python3
import sys

current = None
count = 0

for line in sys.stdin:
    word, c = line.rstrip("\n").split("\t", 1)
    c = int(c)
    if current == word:
        count += c
    else:
        if current is not None:
            print(f"{current}\t{count}")
        current = word
        count = c

if current is not None:
    print(f"{current}\t{count}")
```

- 정렬된 “단어\t1” 또는 “단어\tN” 형식의 데이터 (Mapper 출력 → 정렬됨)
    - 동일한 단어가 연속으로 나올 때마다 개수를 누적
    - 단어가 바뀌면 지금까지 누적한 개수를 출력하고 초기화

```bash
docker cp mapper.py  namenode:/home/hadoop/ 

docker cp reducer.py namenode:/home/hadoop/
```

- 작성한 mapper.py와 reducer.py를 업로드 해줌

## e-book 업로드

```bash
docker cp /W3M3/pride_and_prejudice.txt namenode:/home/hadoop/
```

- pride_and_prejudice 라는 고전 책을 업로드

```bash
  hdfs dfs -mkdir -p /input
  hdfs dfs -put /home/hadoop/pride_and_prejudice.txt /input/'"
```

- input 폴더로 가져와 Mapreduce 실행을 준비해줌

## Mapreduce job

```bash
docker exec -it namenode bash -lc "su - hadoop -c '\
  chmod +x ~/wc_mapper.py ~/wc_reducer.py && \
  OUT=/output/wc_py_$(date +%s) && \
  JAR=$(ls /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-*.jar) && \
  hadoop jar $JAR \
    -D mapreduce.job.reduces=2 \
    -input /input/pride_and_prejudice.txt \
    -output $OUT \
    -mapper \"python3 wc_mapper.py\" \
    -reducer \"python3 wc_reducer.py\" \
    -file ~/wc_mapper.py \
    -file ~/wc_reducer.py && \
  hdfs dfs -ls $OUT'"
```

- MapReduce job을 실행

```bash
docker exec -it namenode bash -lc "su - hadoop -c '\
  hdfs dfs -cat $OUT/part-* | sort -k2nr | head -n 50'"
```

- 작업이 끝난 후 가장 많이 등장한 단어 50개를 확인

```bash
the	4853
to	4407
of	3966
and	3838
her	2284
i	2122
a	2096
in	2054
was	1878
she	1751
that	1661
it	1605
not	1528
you	1451
he	1361
his	1303
be	1281
as	1240
had	1186
with	1150
for	1122
but	1042
is	949
have	886
at	831
mr	808
him	777
on	745
my	728
by	724
s	686
all	668
elizabeth	645
they	612
so	608
which	575
were	570
been	536
could	532
from	526
no	519
this	512
very	505
what	494
would	485
your	464
me	462
their	456
them	445
will	436
```

- 순서대로 잘 정리된 모습을 볼 수 있음