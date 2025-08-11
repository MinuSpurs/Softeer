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