import os
import requests
from tqdm import tqdm
from dotenv import load_dotenv

def get_popular_repos(top_n=200, github_token=None):
    repos = []
    per_page = 100
    pages = (top_n // per_page) + (1 if top_n % per_page else 0)
    url = "https://api.github.com/search/repositories"
    headers = {"Authorization": f"token {github_token}"} if github_token else {}
    for page in tqdm(range(1, pages + 1)):
        params = {
            "q": "stars:>1",
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page
        }
        resp = requests.get(url, headers=headers, params=params)
        data = resp.json()
        for repo in data.get("items", []):
            full_name = repo["full_name"]
            repos.append(full_name)
        if len(repos) >= top_n:
            break
    return repos[:top_n]

def save_repos(repos, filename):
    with open(filename, "w") as f:
        for repo in repos:
            f.write(repo + "\n")

def main():
    load_dotenv()
    github_token = os.getenv("GITHUB_TOKEN")
    repos = get_popular_repos(top_n=200, github_token=github_token)
    save_repos(repos, os.path.join("assets", "popular_repos.txt"))
    print(f"Salvo {len(repos)} repositórios populares em assets/popular_repos.txt")

if __name__ == "__main__":
    main()