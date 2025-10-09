import os
import requests
from tqdm import tqdm
from dotenv import load_dotenv

OUTPUT_FILE = "assets/popular_repos.txt"
TOP_N = 200

def load_token():
    load_dotenv()
    return os.getenv("GITHUB_TOKEN")

def fetch_popular_repos(top_n=200, token=None):
    repos = []
    per_page = 100
    pages = (top_n // per_page) + (1 if top_n % per_page else 0)
    headers = {"Authorization": f"token {token}"} if token else {}
    url = "https://api.github.com/search/repositories"
    for page in tqdm(range(1, pages + 1), desc="Buscando repositórios"):
        params = {
            "q": "stars:>1",
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page
        }
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            print(f"Erro {resp.status_code} na página {page}: {resp.text}")
            break
        data = resp.json()
        for item in data.get("items", []):
            repos.append(item["full_name"])
        if len(repos) >= top_n:
            break
    return repos[:top_n]

def main():
    token = load_token()
    if os.path.exists(OUTPUT_FILE):
        print(f"{OUTPUT_FILE} já existe. Remova-o se quiser refazer.")
    repos = fetch_popular_repos(TOP_N, token)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for r in repos:
            f.write(r + "\n")
    print(f"Salvo {len(repos)} repositórios em {OUTPUT_FILE}")

if __name__ == "__main__":
    main()