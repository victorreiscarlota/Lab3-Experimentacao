import os
import time
import math
import requests
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm
from datetime import datetime, timezone
 
INPUT_RAW = "assets/prs_dataset.csv"
OUTPUT_ENRICHED_FINAL = "assets/prs_dataset_enriched.csv"
OUTPUT_ENRICHED_PARTIAL = "assets/prs_dataset_enriched_partial.csv"

MAX_PR_PER_REPO = 10      
BATCH_SIZE = 200            
STOP_AFTER = 80        
SILENT_BOTS = True         
MIN_REVIEW_HOURS = 1.0      
REQUIRE_AT_LEAST_ONE_REVIEW = True

def load_token():
    load_dotenv()
    return os.getenv("GITHUB_TOKEN")

def rate_limit_guard(resp):
    if resp.status_code == 403:
        remaining = resp.headers.get("X-RateLimit-Remaining")
        reset = resp.headers.get("X-RateLimit-Reset")
        if remaining == "0" and reset:
            wait_s = max(int(reset) - int(time.time()) + 5, 5)
            print(f"[RATE-LIMIT] Aguardando {wait_s} segundos...")
            time.sleep(wait_s)
            return True
    return False

def parse_iso(ts):
    if not ts or (isinstance(ts, float) and math.isnan(ts)):
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None

def hours_between(start, end):
    if not start or not end:
        return None
    return (end - start).total_seconds() / 3600.0

def is_bot(login):
    if not login or not isinstance(login, str):
        return False
    low = login.lower()
    return low.endswith("[bot]") or low.endswith("-bot") or low.endswith("bot")

def safe_get(url, headers, params=None):
    while True:
        resp = requests.get(url, headers=headers, params=params)
        if rate_limit_guard(resp):
            continue
        return resp

def paginated(url, headers):
    page = 1
    per_page = 100
    items = []
    while True:
        resp = safe_get(url, headers, params={"per_page": per_page, "page": page})
        if resp.status_code != 200:
            return items
        data = resp.json()
        if not isinstance(data, list):
            return items
        items.extend(data)
        if len(data) < per_page:
            break
        page += 1
    return items

def normalize_body(val):
    if isinstance(val, str):
        return val
    if val is None:
        return ""
    if isinstance(val, float):
        if math.isnan(val):
            return ""
        return str(val)
    return str(val)

def enrich_single_pr(row_dict, token):
    headers = {"Authorization": f"token {token}"} if token else {}
    repo = row_dict.get("repo")
    pr_number = int(row_dict.get("pr_number"))
    pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    reviews_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    issue_comments_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    diff_comments_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"

    pr_resp = safe_get(pr_url, headers)
    if pr_resp.status_code != 200:
        return None
    pr_data = pr_resp.json()

    additions = pr_data.get("additions")
    deletions = pr_data.get("deletions")
    changed_files = pr_data.get("changed_files")

    created_at = parse_iso(pr_data.get("created_at"))
    merged_at = parse_iso(pr_data.get("merged_at"))
    closed_at = parse_iso(pr_data.get("closed_at"))
    end_ts = merged_at if merged_at else closed_at

    reviews = paginated(reviews_url, headers)
    issue_comments = paginated(issue_comments_url, headers)
    diff_comments = paginated(diff_comments_url, headers)

    review_users = {r.get("user", {}).get("login") for r in reviews if r.get("user")}
    issue_comment_users = {c.get("user", {}).get("login") for c in issue_comments if c.get("user")}
    diff_comment_users = {c.get("user", {}).get("login") for c in diff_comments if c.get("user")}

    all_users = set()
    for u in review_users | issue_comment_users | diff_comment_users:
        if not u:
            continue
        if SILENT_BOTS and is_bot(u):
            continue
        all_users.add(u)

    author = row_dict.get("user_login")
    if author and isinstance(author, str):
        if not (SILENT_BOTS and is_bot(author)):
            all_users.add(author)

    body_raw = normalize_body(row_dict.get("body"))
    body_char_count = len(body_raw)

    review_cycle_hours = hours_between(created_at, end_ts)
    merged_flag = merged_at is not None
    final_status = "MERGED" if merged_flag else ("CLOSED_SEM_MERGE" if row_dict.get("state") == "closed" else "OTHER")

    return {
        **row_dict,
        "additions": additions,
        "deletions": deletions,
        "changed_files": changed_files,
        "review_count": len(reviews),
        "review_comment_count": len(diff_comments),
        "issue_comment_count": len(issue_comments),
        "participants_count": len(all_users),
        "body_char_count": body_char_count,
        "review_cycle_hours": review_cycle_hours,
        "final_status": final_status,
        "merged": merged_flag
    }

def load_partial_checkpoint():
    if os.path.exists(OUTPUT_ENRICHED_PARTIAL):
        try:
            part = pd.read_csv(OUTPUT_ENRICHED_PARTIAL)
            done_keys = set(zip(part["repo"], part["pr_number"]))
            return part, done_keys
        except Exception:
            return pd.DataFrame(), set()
    return pd.DataFrame(), set()

def append_partial(rows):
    df_part = pd.DataFrame(rows)
    header = not os.path.exists(OUTPUT_ENRICHED_PARTIAL)
    df_part.to_csv(OUTPUT_ENRICHED_PARTIAL, mode="a", header=header, index=False, encoding="utf-8")

def finalize_output():
    if not os.path.exists(OUTPUT_ENRICHED_PARTIAL):
        print("Nenhum parcial encontrado; nada para finalizar.")
        return
    df = pd.read_csv(OUTPUT_ENRICHED_PARTIAL)

    before = len(df)
    df = df[df["final_status"].isin(["MERGED", "CLOSED_SEM_MERGE"])]
    if REQUIRE_AT_LEAST_ONE_REVIEW:
        df = df[df["review_count"] >= 1]
    df = df[df["review_cycle_hours"].notna() & (df["review_cycle_hours"] >= MIN_REVIEW_HOURS)]
    after = len(df)

    df.to_csv(OUTPUT_ENRICHED_FINAL, index=False, encoding="utf-8")
    print(f"[FINALIZAÇÃO] Linhas antes filtros: {before} | após: {after}")
    print(f"Salvo dataset final em {OUTPUT_ENRICHED_FINAL}")

def main():
    token = load_token()
    if not os.path.exists(INPUT_RAW):
        print(f"Arquivo {INPUT_RAW} não encontrado. Execute a etapa anterior.")
        return

    raw = pd.read_csv(INPUT_RAW)
    print(f"PRs brutos carregados: {len(raw)}")

    
    partial_df, done = load_partial_checkpoint()
    if len(done) > 0:
        print(f"[RESUME] PRs já processados: {len(done)}")

    processed_batch = []
    processed_count = 0
    total_to_do = 0

    grouped = raw.groupby("repo")
    rows_to_process = []
    for repo, grp in grouped:
        if MAX_PR_PER_REPO:
            grp = grp.head(MAX_PR_PER_REPO)
        for _, r in grp.iterrows():
            key = (r["repo"], r["pr_number"])
            if key in done:
                continue
            rows_to_process.append(r)

    total_to_do = len(rows_to_process)
    print(f"PRs restantes a enriquecer: {total_to_do}")

    pbar = tqdm(rows_to_process, desc="Enriquecendo", unit="pr")
    for idx, row in enumerate(pbar, start=1):
        if STOP_AFTER and idx > STOP_AFTER:
            print(f"STOP_AFTER={STOP_AFTER} atingido. Interrompendo enriquecimento.")
            break
        row_dict = row.to_dict()
        try:
            enriched = enrich_single_pr(row_dict, token)
            if enriched:
                processed_batch.append(enriched)
        except Exception as e:
            print(f"Erro {row_dict.get('repo')}#{row_dict.get('pr_number')}: {e}")

        if len(processed_batch) >= BATCH_SIZE:
            append_partial(processed_batch)
            processed_count += len(processed_batch)
            processed_batch = []
            pbar.set_postfix(saved=processed_count)

    if processed_batch:
        append_partial(processed_batch)
        processed_count += len(processed_batch)

    print(f"Total enriquecidos nesta execução: {processed_count}")
    finalize_output()
    print("Enriquecimento concluído (parcial + final).")

if __name__ == "__main__":
    main()