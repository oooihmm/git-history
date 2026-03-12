import os
from dotenv import load_dotenv

from git_collector import collect_commits


def main():

    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace = os.path.dirname(current_dir)

    load_dotenv(os.path.join(current_dir, ".env"))
    authors = os.getenv("AUTHORS").split(",")

    collect_commits(
        workspace=workspace,
        output_dir=current_dir,
        authors=authors,
    )


if __name__ == "__main__":
    main()