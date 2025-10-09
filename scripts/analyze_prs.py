import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

ENRICHED_FILE = "assets/prs_dataset_enriched.csv"
FIG_DIR = "assets/figures"

def ensure_fig_dir():
    if not os.path.exists(FIG_DIR):
        os.makedirs(FIG_DIR)

def load_data():
    if not os.path.exists(ENRICHED_FILE):
        raise FileNotFoundError(f"{ENRICHED_FILE} não encontrado.")
    return pd.read_csv(ENRICHED_FILE)

def save_fig(name):
    path = os.path.join(FIG_DIR, name)
    plt.tight_layout()
    plt.savefig(path, dpi=130)
    print(f"Figura: {path}")
    plt.close()

def plot_changed_files_dist(df):
    sns.set(style="whitegrid")
    plt.figure(figsize=(7,4))
    sns.kdeplot(data=df, x="changed_files", hue="final_status", fill=True, common_norm=False, alpha=0.4)
    plt.title("Distribuição de changed_files por Status Final")
    save_fig("dist_changed_files_status.png")

def plot_participants_box(df):
    plt.figure(figsize=(6,4))
    subset = df[df["final_status"].isin(["MERGED", "CLOSED_SEM_MERGE"])]
    sns.boxplot(data=subset, x="final_status", y="participants_count")
    plt.title("Participantes por Status Final")
    save_fig("box_interactions_status.png")

def plot_time_strip(df):
    plt.figure(figsize=(6,4))
    sns.stripplot(data=df, x="final_status", y="review_cycle_hours", alpha=0.45)
    plt.title("Tempo de Revisão (h) por Status Final")
    save_fig("scatter_time_status.png")

def spearman_analysis(df):
    subset = df[df["final_status"].isin(["MERGED", "CLOSED_SEM_MERGE"])].copy()
    subset["merged_bin"] = (subset["final_status"] == "MERGED").astype(int)

    targets = {
        "merged_bin": [
            "changed_files","additions","deletions","review_cycle_hours",
            "body_char_count","participants_count","issue_comment_count",
            "review_comment_count","review_count"
        ],
        "review_count": [
            "changed_files","additions","deletions","review_cycle_hours",
            "body_char_count","participants_count","issue_comment_count",
            "review_comment_count"
        ]
    }

    rows = []
    for target, vars_ in targets.items():
        for v in vars_:
            tmp = subset[[target, v]].dropna()
            if len(tmp) >= 10:
                rho, p = spearmanr(tmp[target], tmp[v])
                rows.append({"target": target, "var": v, "rho": rho, "p_value": p, "n": len(tmp)})
    res = pd.DataFrame(rows)
    res.to_csv("assets/spearman_results.csv", index=False, encoding="utf-8")
    print("Correlação (Spearman) salva em assets/spearman_results.csv")

    mb = res[res["target"] == "merged_bin"].pivot(index="var", columns="target", values="rho")
    plt.figure(figsize=(4, max(2.0, 0.45*len(mb))))
    sns.heatmap(mb, annot=True, fmt=".2f", cmap="coolwarm", center=0)
    plt.title("Spearman rho vs merged_bin")
    save_fig("heatmap_spearman.png")

def print_medians(df):
    vars_ = [
        "changed_files","additions","deletions","review_cycle_hours",
        "body_char_count","participants_count","review_count",
        "issue_comment_count","review_comment_count"
    ]
    print("\nMEDIANAS POR STATUS:")
    for st in df["final_status"].unique():
        sub = df[df["final_status"] == st]
        if len(sub) == 0:
            continue
        print(f"\nStatus: {st} (n={len(sub)})")
        med = sub[vars_].median(numeric_only=True)
        for k,v in med.items():
            print(f"  {k}: {v}")

def main():
    ensure_fig_dir()
    df = load_data()
    if df.empty:
        print("Dataset vazio após filtragem.")
        return
    print(f"Linhas pós-filtro: {len(df)}")
    print_medians(df)
    plot_changed_files_dist(df)
    plot_participants_box(df)
    plot_time_strip(df)
    spearman_analysis(df)
    print("Análises concluídas. Verifique assets/figures e assets/spearman_results.csv")

if __name__ == "__main__":
    main()