import os
import requests
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv

def read_repos(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f.readlines()]

def get_prs(repo_fullname, github_token, min_prs=100):
    prs = []
    page = 1
    per_page = 100
    headers = {"Authorization": f"token {github_token}"} if github_token else {}
    url = f"https://api.github.com/repos/{repo_fullname}/pulls"
    params = {
        "state": "all",
        "per_page": per_page,
        "page": page
    }
    while True:
        resp = requests.get(url, headers=headers, params=params)
        data = resp.json()
        if isinstance(data, dict) and data.get("message"):
            print(f"Erro: {data['message']} no repo {repo_fullname}")
            break
        prs.extend(data)
        if len(data) < per_page:
            break
        page += 1
        params["page"] = page
        if len(prs) >= min_prs:
            break
    return prs

def main():
    load_dotenv()
    github_token = os.getenv("GITHUB_TOKEN")
    repos = read_repos(os.path.join("assets", "popular_repos.txt"))
    dataset = []
    for repo in tqdm(repos):
        prs = get_prs(repo, github_token, min_prs=100)
        print(f"{repo}: {len(prs)} PRs coletados")
        for pr in prs:
            pr_data = {
                "repo": repo,
                "pr_number": pr.get("number"),
                "state": pr.get("state"),
                "created_at": pr.get("created_at"),
                "closed_at": pr.get("closed_at"),
                "merged_at": pr.get("merged_at"),
                "user": pr.get("user", {}).get("login"),
                "title": pr.get("title"),
                "body": pr.get("body"),
                "comments": pr.get("comments"),
            }
            dataset.append(pr_data)
    df = pd.DataFrame(dataset)
    df.to_csv(os.path.join("assets", "prs_dataset.csv"), index=False)
    print(f"Dataset de PRs salvo em assets/prs_dataset.csv")

if __name__ == "__main__":
    main()