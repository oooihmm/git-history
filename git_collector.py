import os
import subprocess


def collect_commits(workspace, output_dir, authors):

    current_folder = os.path.basename(output_dir)

    commits_dir = os.path.join(output_dir, "commits")
    os.makedirs(commits_dir, exist_ok=True)

    for folder in os.listdir(workspace):

        repo_path = os.path.join(workspace, folder)

        if folder == current_folder:
            continue

        if not os.path.isdir(repo_path):
            continue

        if not os.path.isdir(os.path.join(repo_path, ".git")):
            continue

        cmd = ["git", "-C", repo_path, "log"]

        for author in authors:
            cmd.append(f"--author={author}")

        cmd += [
            "--pretty=format:%h | %ad | %an | %s",
            "--date=short",
        ]

        print(f"Processing {folder}...")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.stdout.strip() == "":
            continue

        output_file = os.path.join(commits_dir, f"{folder}.txt")

        with open(output_file, "w") as f:
            f.write(result.stdout)