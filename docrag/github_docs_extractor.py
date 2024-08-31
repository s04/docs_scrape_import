import os
import subprocess
from pathlib import Path

def clone_or_pull_repo(repo_url, target_dir):
    if os.path.exists(target_dir):
        print(f"Directory {target_dir} already exists. Updating instead of cloning...")
        current_dir = os.getcwd()
        try:
            os.chdir(target_dir)
            subprocess.run(["git", "pull"], check=True)
        finally:
            os.chdir(current_dir)
    else:
        print(f"Cloning repository to {target_dir}...")
        subprocess.run(["git", "clone", repo_url, target_dir], check=True)

def find_markdown_files(repo_dir):
    markdown_files = []
    for root, dirs, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(os.path.join(root, file))
    return markdown_files

if __name__ == "__main__":
    repo_url = "https://github.com/activeloopai/docs-gitbook"
    target_dir = "docs-gitbook"
    
    # Clone or update the repository
    clone_or_pull_repo(repo_url, target_dir)
    
    # Find all markdown files
    markdown_files = find_markdown_files(target_dir)
    
    print(f"Found {len(markdown_files)} markdown files:")
    for file in markdown_files:
        print(file)