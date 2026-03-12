import os
import subprocess
from dotenv import load_dotenv


def collect_commits(workspace, output_dir, authors):
    current_folder = os.path.basename(output_dir)

    for folder in os.listdir(workspace):
        repo_path = os.path.join(workspace, folder)
        cmd = ["git", "-C", repo_path, "log"]

        for author in authors:
            cmd.append(f"--author={author}")

        cmd += [
            "--pretty=format:%h | %ad | %an | %s",
            "--date=short",
        ]

        if folder == current_folder:
            continue

        if not os.path.isdir(repo_path):
            continue

        if not os.path.isdir(os.path.join(repo_path, ".git")):
            continue

        print(f"Processing {folder}...")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.stdout.strip() == "":
            continue

        output_file = os.path.join(output_dir, f"{folder}.txt")

        with open(output_file, "w") as f:
            f.write(result.stdout)


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace = os.path.dirname(current_dir)
    
    load_dotenv(os.path.join(current_dir, ".env"))
    authors = os.getenv("AUTHORS").split(",")

    collect_commits(workspace, current_dir, authors)


if __name__ == "__main__":
    main()