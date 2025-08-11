# W3M2b

- W3M2a에서 Dockerfile과 entrypoint.sh를 통해 Hadoop 멀티 노드 클러스터가 잘 작동될 때 수행된다.

## modify_config.py

```bash
import os
import shutil
import argparse
import subprocess
import xml.etree.ElementTree as ET

def run(cmd: list[str], check=True, capture_output=False, text=True):
    return subprocess.run(cmd, check=check, capture_output=capture_output, text=text)

def backup(src: str, dst: str):
    shutil.copy(src, dst)

def pretty_write_xml(tree: ET.ElementTree, path: str):
    def indent(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for child in elem:
                indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    root = tree.getroot()
    indent(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)

def update_config(file_path: str, updates: dict[str, str]):
    tree = ET.parse(file_path)
    root = tree.getroot()

    for name, value in updates.items():
        found = False
        for prop in root.findall("property"):
            n = prop.find("name")
            if n is not None and n.text == name:
                v = prop.find("value")
                if v is None:
                    v = ET.SubElement(prop, "value")
                v.text = value
                found = True
                break
        if not found:
            prop = ET.SubElement(root, "property")
            ET.SubElement(prop, "name").text = name
            ET.SubElement(prop, "value").text = value

    pretty_write_xml(tree, file_path)

def docker_exec(container: str, cmd: str, user: str = "hadoop"):
    return run(["docker", "exec", "--user", user, container, "bash", "-lc", cmd], check=False)

def docker_cp(src: str, dst: str):
    return run(["docker", "cp", src, dst], check=False)

def main():
    parser = argparse.ArgumentParser(description="Modify Hadoop config XML files and restart services.")
    parser.add_argument("config_dir", help="Path to the Hadoop configuration directory.")
    parser.add_argument("--containers", nargs="+", default=["hadoop-master", "worker1", "worker2"],
                        help="Container names to distribute configs to. Default: hadoop-master worker1 worker2")
    parser.add_argument("--nn-container", default="hadoop-master",
                        help="Container where stop/start-* will be executed (master). Default: hadoop-master")
    args = parser.parse_args()

    config_dir = args.config_dir
    backup_dir = os.path.join(config_dir, "backup")
    os.makedirs(backup_dir, exist_ok=True)
    
    config_updates = {
        "core-site.xml": {
            "fs.defaultFS": "hdfs://namenode:9000",
            "hadoop.tmp.dir": "/hadoop/tmp",
            "io.file.buffer.size": "131072",
        },
        "hdfs-site.xml": {
            "dfs.replication": "2",
            "dfs.blocksize": "134217728",
            "dfs.namenode.name.dir": "/hadoop/dfs/name",
        },
        "mapred-site.xml": {
            "mapreduce.framework.name": "yarn",
            "mapreduce.jobhistory.address": "namenode:10020",
            "mapreduce.task.io.sort.mb": "256",
            "mapreduce.job.tracker": "namenode:9001",
        },
        "yarn-site.xml": {
            "yarn.resourcemanager.address": "namenode:8032",
            "yarn.nodemanager.resource.memory-mb": "8192",
            "yarn.scheduler.minimum-allocation-mb": "1024",
        },
    }

    # 원본 백업, 수정
    for file_name, updates in config_updates.items():
        file_path = os.path.join(config_dir, file_name)
        backup_path = os.path.join(backup_dir, file_name)
        if os.path.exists(file_path):
            try:
                print(f"Backing up {file_name}...")
                backup(file_path, backup_path)
                print(f"Modifying {file_name}...")
                update_config(file_path, updates)
            except Exception as e:
                print(f"Error processing {file_name}: {e}")
        else:
            print(f"{file_name} not found.")

    # === 서비스 중지 ===
    print("Stopping Hadoop DFS...")
    docker_exec(args.nn_container, "stop-dfs.sh")
    print("Stopping YARN...")
    docker_exec(args.nn_container, "stop-yarn.sh")

    # 디렉터리 생성, 권한 맞추기
    print("Ensuring required dirs exist in all containers...")
    for c in args.containers:
        docker_exec(c, "mkdir -p /hadoop/dfs/name /hadoop/tmp", user="root")
        docker_exec(c, "chown -R hadoop:hadoop /hadoop", user="root")

    # 수정된 설정 파일 배포
    for container in args.containers:
        for file_name in config_updates.keys():
            src_path = os.path.join(config_dir, file_name)
            dst_path = f"{container}:/usr/local/hadoop/etc/hadoop/{file_name}"
            docker_cp(src_path, dst_path)
            print(f"Copied {file_name} to {container}")

    # 재시작
    print("Starting Hadoop DFS...")
    docker_exec(args.nn_container, "start-dfs.sh")
    print("Starting YARN...")
    docker_exec(args.nn_container, "start-yarn.sh")

    print("Configuration changes applied and services restarted.")

if __name__ == "__main__":
    main()
```

Hadoop 설정 파일(XML)을 수정하고, 도커 기반 클러스터에 반영한 뒤 Hadoop 서비스를 재시작하는 자동화 스크립트

```bash
python modify_config.py <CONFIG_DIR>
```

옵션:

—containers: 설정 파일을 배포할 도커 컨테이너 목록 (default: hadoop-master, worker1, worker2)

—nn-container: DFS 및 YARN을 중지/시작할 컨테이너(default: hadoop-master)

주요기능

1. XML 설정 자동 수정
    1. 각 XML 파일들의 주요 설정값을 자동 반영
2. 백업 기능
    1. 설정 변경 전, 원본 파일을 backup/ 폴더에 저장
3. 도커 컨테이너에 설정 배포
    1. docker cp를 사용하여 설정 파일을 각 컨테이너에 전송
4. Hadoop 서비스 자동 재시작
    1. stop-dfs.sh, stop-yarn.sh, start-dfs.sh, [start-yarn.sh](http://start-yarn.sh) 자동 실행

결과

```bash
Backing up core-site.xml...
Modifying core-site.xml...
Backing up hdfs-site.xml...
Modifying hdfs-site.xml...
Backing up mapred-site.xml...
Modifying mapred-site.xml...
Backing up yarn-site.xml...
Modifying yarn-site.xml...
Stopping Hadoop DFS...
Stopping namenodes on [namenode]
Stopping datanodes
Stopping secondary namenodes [master]
2025-07-24 05:31:56,088 WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
Stopping YARN...
Stopping nodemanagers
Stopping resourcemanager
Ensuring required dirs exist in all containers...
Successfully copied 2.05kB to hadoop-master:/usr/local/hadoop/etc/hadoop/core-site.xml
Copied core-site.xml to hadoop-master
Successfully copied 2.56kB to hadoop-master:/usr/local/hadoop/etc/hadoop/hdfs-site.xml
Copied hdfs-site.xml to hadoop-master
Successfully copied 2.56kB to hadoop-master:/usr/local/hadoop/etc/hadoop/mapred-site.xml
Copied mapred-site.xml to hadoop-master
Successfully copied 3.07kB to hadoop-master:/usr/local/hadoop/etc/hadoop/yarn-site.xml
Copied yarn-site.xml to hadoop-master
Successfully copied 2.05kB to worker1:/usr/local/hadoop/etc/hadoop/core-site.xml
Copied core-site.xml to worker1
Successfully copied 2.56kB to worker1:/usr/local/hadoop/etc/hadoop/hdfs-site.xml
Copied hdfs-site.xml to worker1
Successfully copied 2.56kB to worker1:/usr/local/hadoop/etc/hadoop/mapred-site.xml
Copied mapred-site.xml to worker1
Successfully copied 3.07kB to worker1:/usr/local/hadoop/etc/hadoop/yarn-site.xml
Copied yarn-site.xml to worker1
Successfully copied 2.05kB to worker2:/usr/local/hadoop/etc/hadoop/core-site.xml
Copied core-site.xml to worker2
Successfully copied 2.56kB to worker2:/usr/local/hadoop/etc/hadoop/hdfs-site.xml
Copied hdfs-site.xml to worker2
Successfully copied 2.56kB to worker2:/usr/local/hadoop/etc/hadoop/mapred-site.xml
Copied mapred-site.xml to worker2
Successfully copied 3.07kB to worker2:/usr/local/hadoop/etc/hadoop/yarn-site.xml
Copied yarn-site.xml to worker2
Starting Hadoop DFS...
Starting namenodes on [namenode]
Starting datanodes
Starting secondary namenodes [master]
2025-07-24 05:32:07,937 WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
Starting YARN...
Starting resourcemanager
Starting nodemanagers
Configuration changes applied and services restarted.
```

- 파일들이 정상적으로 수정되고 백업 파일들이 저장되는 것을 확인할 수 있음
- 서비스 재시작까지 잘 되는 것을 확인할 수 있음

## verify_config.py (컨테이너 내에서 실행)

```python
#!/usr/bin/env python3
import argparse
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

CHECKS = [
    (["hdfs", "getconf", "-confKey", "fs.defaultFS"], "core-site.xml", "fs.defaultFS", "hdfs://namenode:9000"),
    (["hdfs", "getconf", "-confKey", "hadoop.tmp.dir"], "core-site.xml", "hadoop.tmp.dir", "/hadoop/tmp"),
    (["hdfs", "getconf", "-confKey", "io.file.buffer.size"], "core-site.xml", "io.file.buffer.size", "131072"),
    (["hdfs", "getconf", "-confKey", "dfs.replication"], "hdfs-site.xml", "dfs.replication", "2"),
    (["hdfs", "getconf", "-confKey", "dfs.blocksize"], "hdfs-site.xml", "dfs.blocksize", "134217728"),
    (["hdfs", "getconf", "-confKey", "dfs.namenode.name.dir"], "hdfs-site.xml", "dfs.namenode.name.dir", "/hadoop/dfs/name"),
    (["hadoop", "getconf", "-confKey", "mapreduce.framework.name"], "mapred-site.xml""mapreduce.framework.name", "yarn"),
    (["hadoop", "getconf", "-confKey", "mapreduce.job.tracker"], "mapred-site.xml", "mapreduce.job.tracker", "namenode:9001"),
    (["hadoop", "getconf", "-confKey", "mapreduce.task.io.sort.mb"], "mapred-site.xml", "mapreduce.task.io.sort.mb", "256"),
    (["yarn", "getconf", "-confKey", "yarn.resourcemanager.address"], "yarn-site.xml", "yarn.resourcemanager.address", "namenode:8032"),
    (["yarn", "getconf", "-confKey", "yarn.nodemanager.resource.memory-mb"], "yarn-site.xml", "yarn.nodemanager.resource.memory-mb", "8192"),
    (["yarn", "getconf", "-confKey", "yarn.scheduler.minimum-allocation-mb"], "yarn-site.xml", "yarn.scheduler.minimum-allocation-mb", "1024"),
]

def run_cmd(cmd):
    """cmd 실행, 성공 시 (True, stdout), 실패 시 (False, stderr)"""
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if r.returncode == 0:
            return True, r.stdout.strip()
        else:
            return False, r.stderr.strip()
    except Exception as e:
        return False, str(e)

def get_from_xml(conf_dir: Path, file_name: str, key: str) -> str:
    """XML에서 key 값을 읽어서 반환 (없으면 '<NOT_SET>')"""
    path = conf_dir / file_name
    if not path.exists():
        return "<NOT_SET>"
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        for prop in root.findall("property"):
            n = prop.findtext("name")
            v = prop.findtext("value")
            if n and n.strip() == key:
                return (v or "").strip()
        return "<NOT_SET>"
    except Exception:
        return "<NOT_SET>"

def main():
    parser = argparse.ArgumentParser(description="Verify Hadoop configs by running *getconf* (with XML fallback).")
    parser.add_argument("config_dir", nargs="?", default="/usr/local/hadoop/etc/hadoop",
                        help="Hadoop configuration directory (default: /usr/local/hadoop/etc/hadoop)")
    args = parser.parse_args()
    conf_dir = Path(args.config_dir)

    # 결과 카운트
    total, passed = 0, 0

    for cmd, file_name, key, expected in CHECKS:
        total += 1
        ok, out = run_cmd(cmd)
        if not ok or out == "":
            # getconf가 실패하면 XML 파싱으로 폴백
            out = get_from_xml(conf_dir, file_name, key)

        if out == expected:
            print(f"PASS: {cmd} -> {out}")
            passed += 1
        else:
            print(f"FAIL: {cmd} -> {out} (expected {expected})")

    # replication factor
    ok, out = run_cmd(["hdfs", "getconf", "-confKey", "dfs.replication"])
    rep_val = out if ok else get_from_xml(conf_dir, "hdfs-site.xml", "dfs.replication")
    if rep_val == "2":
        print("PASS: Replication factor is 2")
    else:
        print(f"FAIL: Replication factor is {rep_val} (expected 2)")

    print()
    print(f"PASS {passed}/{total}")

if __name__ == "__main__":
    main()
```

- Hadoop 클러스터의 설정값들을 getconf 명령어를 통해 확인하고, 실패할 경우 XML 설정 파일에서 직접 값을 읽어와 검증
    - 기대값과 실제값이 일치하는 경우 PASS, 불일치 시 FAIL로 출력

```python
python3 verify_config.py /path/to/hadoop/conf
```

- 컨테이너 내에서 코드를 실행시킴

```bash
PASS: ['hdfs', 'getconf', '-confKey', 'fs.defaultFS'] -> hdfs://namenode:9000
PASS: ['hdfs', 'getconf', '-confKey', 'hadoop.tmp.dir'] -> /hadoop/tmp
PASS: ['hdfs', 'getconf', '-confKey', 'io.file.buffer.size'] -> 131072
PASS: ['hdfs', 'getconf', '-confKey', 'dfs.replication'] -> 2
PASS: ['hdfs', 'getconf', '-confKey', 'dfs.blocksize'] -> 134217728
PASS: ['hdfs', 'getconf', '-confKey', 'dfs.namenode.name.dir'] -> /hadoop/dfs/name
PASS: ['hadoop', 'getconf', '-confKey', 'mapreduce.framework.name'] -> yarn
PASS: ['hadoop', 'getconf', '-confKey', 'mapreduce.job.tracker'] -> namenode:9001
PASS: ['hadoop', 'getconf', '-confKey', 'mapreduce.task.io.sort.mb'] -> 256
PASS: ['yarn', 'getconf', '-confKey', 'yarn.resourcemanager.address'] -> namenode:8032
PASS: ['yarn', 'getconf', '-confKey', 'yarn.nodemanager.resource.memory-mb'] -> 8192
PASS: ['yarn', 'getconf', '-confKey', 'yarn.scheduler.minimum-allocation-mb'] -> 1024
PASS: Replication factor is 2

PASS 12/12
```

- 요구사항에서 원하는 방향으로 수정이 잘 된 것을 확인할 수 있음