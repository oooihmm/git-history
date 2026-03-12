import os
import re
from collections import defaultdict

from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN


MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def is_merge_commit(msg):
    return msg.lower().startswith("merge")


def clean_message(msg):
    # prefix 제거 (: 기준)
    if ":" in msg:
        msg = msg.split(":", 1)[1]
    return msg.strip()


def extract_path_group(msg):
    if ">" not in msg:
        return None

    idx = msg.find(">")
    group = msg[:idx].strip()

    return group


def extract_leaf_message(msg):
    if ">" not in msg:
        return msg

    idx = msg.find(">")
    return msg[idx + 1 :].strip()


def parse_commit_line(line):

    parts = line.split("|")

    if len(parts) < 4:
        return None

    message = parts[-1].strip()

    if is_merge_commit(message):
        return None

    cleaned = clean_message(message)

    if cleaned == "":
        return None

    return cleaned


def load_repo_messages(file_path):

    messages = []

    with open(file_path) as f:
        for line in f:
            msg = parse_commit_line(line)

            if msg:
                messages.append(msg)

    return messages


def split_groups(messages):

    path_groups = defaultdict(list)
    normal_msgs = []

    for msg in messages:

        group = extract_path_group(msg)

        if group:
            path_groups[group].append(msg)

        else:
            normal_msgs.append(msg)

    return path_groups, normal_msgs


def cluster_messages(messages):

    if len(messages) == 0:
        return {}

    sentences = [extract_leaf_message(m) for m in messages]

    embeddings = MODEL.encode(sentences)

    clustering = DBSCAN(
        eps=0.5,
        min_samples=3,
        metric="cosine",
    ).fit(embeddings)

    clusters = defaultdict(list)

    for label, msg in zip(clustering.labels_, messages):
        clusters[label].append(msg)

    return clusters


def generate_repo_report(repo, messages, reports_dir):

    path_groups, normal_msgs = split_groups(messages)

    clusters = cluster_messages(normal_msgs)

    report = []

    report.append(f"# {repo}\n")

    # path 그룹 먼저
    for group, msgs in path_groups.items():

        report.append(f"## {group}")

        for m in msgs:
            report.append(f"- {m}")

        report.append("")

    # clustering 결과
    for cid, msgs in clusters.items():

        report.append(f"## cluster-{cid}")

        for m in msgs:
            report.append(f"- {m}")

        report.append("")

    output_path = os.path.join(reports_dir, f"{repo}.md")

    with open(output_path, "w") as f:
        f.write("\n".join(report))


def run_clustering(commits_dir):

    base_dir = os.path.dirname(commits_dir)

    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    txt_files = [
        f for f in os.listdir(commits_dir)
        if f.endswith(".txt")
    ]

    if not txt_files:
        print("분석할 commit 파일이 없습니다.")
        return

    for file in txt_files:

        repo = file.replace(".txt", "")

        file_path = os.path.join(commits_dir, file)

        messages = load_repo_messages(file_path)

        if not messages:
            continue

        print(f"Analyzing {repo}...")

        generate_repo_report(
            repo,
            messages,
            reports_dir
        )

    print("reports 생성 완료")