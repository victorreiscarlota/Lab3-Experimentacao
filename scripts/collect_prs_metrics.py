import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

REPOS_FILE = "assets/popular_repos.txt"
OUTPUT_RAW = "assets/prs_dataset.csv"

def load_token():
    load_dotenv()
    return os.getenv("GITHUB_TOKEN")

def read_repos(path):
    with open(path, "r", encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]

def rate_limit_guard(resp):
    if resp.status_code == 403:
        remaining = resp.headers.get("X-RateLimit-Remaining")
        reset = resp.headers.get("X-RateLimit-Reset")
        if remaining == "0" and reset:
            wait_s = max(int(reset) - int(time.time()) + 5, 5)
            print(f"Limite atingido. Aguardando {wait_s} segundos...")
            time.sleep(wait_s)
            return True
    return False

def fetch_pr_list(repo, token, min_count=100):
    prs = []
    page = 1
    per_page = 100
    headers = {"Authorization": f"token {token}"} if token else {}
    base_url = f"https://api.github.com/repos/{repo}/pulls"
    while True:
        params = {"state": "all", "per_page": per_page, "page": page}
        resp = requests.get(base_url, headers=headers, params=params)
        if rate_limit_guard(resp):
            continue
        if resp.status_code != 200:
            print(f"[{repo}] Erro {resp.status_code}: {resp.text}")
            break
        data = resp.json()
        if not isinstance(data, list):
            print(f"[{repo}] Resposta inesperada: {data}")
            break
        for pr in data:
            prs.append({
                "repo": repo,
                "pr_number": pr.get("number"),
                "state": pr.get("state"),
                "created_at": pr.get("created_at"),
                "merged_at": pr.get("merged_at"),
                "closed_at": pr.get("closed_at"),
                "user_login": pr.get("user", {}).get("login"),
                "title": pr.get("title"),
                "body": pr.get("body"),
            })
        if len(data) < per_page or len(prs) >= min_count:
            break
        page += 1
    return prs

def main():
    token = load_token()
    repos = read_repos(REPOS_FILE)
    all_rows = []
    for repo in tqdm(repos, desc="Coletando PRs iniciais"):
        rows = fetch_pr_list(repo, token, min_count=100)
        all_rows.extend(rows)
    df = pd.DataFrame(all_rows)
    df.to_csv(OUTPUT_RAW, index=False, encoding="utf-8")
    print(f"Dataset bruto salvo em {OUTPUT_RAW} (linhas: {len(df)})")

if __name__ == "__main__":
    main()