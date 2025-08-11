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

    # === 원본 백업 & 수정 ===
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

    # === 디렉터리 생성 & 권한 맞추기 ===
    print("Ensuring required dirs exist in all containers...")
    for c in args.containers:
        docker_exec(c, "mkdir -p /hadoop/dfs/name /hadoop/tmp", user="root")
        docker_exec(c, "chown -R hadoop:hadoop /hadoop", user="root")

    # === 수정된 설정 파일 배포 ===
    for container in args.containers:
        for file_name in config_updates.keys():
            src_path = os.path.join(config_dir, file_name)
            dst_path = f"{container}:/usr/local/hadoop/etc/hadoop/{file_name}"
            docker_cp(src_path, dst_path)
            print(f"Copied {file_name} to {container}")

    # === 재시작 ===
    print("Starting Hadoop DFS...")
    docker_exec(args.nn_container, "start-dfs.sh")
    print("Starting YARN...")
    docker_exec(args.nn_container, "start-yarn.sh")

    print("Configuration changes applied and services restarted.")

if __name__ == "__main__":
    main()