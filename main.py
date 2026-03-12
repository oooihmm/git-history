import os
from dotenv import load_dotenv

from git_collector import collect_commits
from commit_clusterer import run_clustering

def commits_exist(commits_dir):

    if not os.path.exists(commits_dir):
        return False

    files = [
        f for f in os.listdir(commits_dir)
        if f.endswith(".txt")
    ]

    return len(files) > 0

def ask_overwrite():

    while True:

        answer = input("commits 폴더가 이미 존재합니다. 덮어쓸까요? (y/n): ")

        if answer.lower() in ["y", "yes"]:
            return True

        if answer.lower() in ["n", "no"]:
            return False

def main():

    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace = os.path.dirname(current_dir)
    commits_dir = os.path.join(current_dir, "commits")

    load_dotenv(os.path.join(current_dir, ".env"))
    authors = os.getenv("AUTHORS").split(",")

    exists = commits_exist(commits_dir)

    if not exists:
        print("commit 로그 수집 시작")
        collect_commits(
        workspace=workspace,
        output_dir=current_dir,
        authors=authors,
        )

    else: 
        overwrite = ask_overwrite()
        if overwrite:
            print("commit 로그 다시 수집")
            collect_commits(
            workspace=workspace,
            output_dir=current_dir,
            authors=authors,
            )
        else:
            print("기존 commit 데이터 사용")

    run_clustering(commits_dir)

    print("완료")


if __name__ == "__main__":
    main()