import os
import sys
import subprocess

SCRIPTS = [
    ("scripts/collect_popular_repos.py", "Coleta dos 200 repositórios populares"),
    ("scripts/collect_prs_metrics.py", "Coleta inicial dos PRs (lista bruta)"),
    ("scripts/enrich_prs.py", "Enriquecimento e filtragem dos PRs"),
    ("scripts/analyze_prs.py", "Análises estatísticas e geração de gráficos"),
]

def ensure_dirs():
    for d in ["assets", "assets/figures", "scripts"]:
        if not os.path.exists(d):
            os.makedirs(d)

def run_script(path, description):
    print(f"\n=== Etapa: {description} ===")
    result = subprocess.run([sys.executable, path])
    if result.returncode != 0:
        print(f"[ERRO] Falha ao executar {path}")
        sys.exit(result.returncode)
    else:
        print(f"[OK] {path} concluído.")

if __name__ == "__main__":
    ensure_dirs()
    for script, desc in SCRIPTS:
        run_script(script, desc)
    print("\nPipeline completa. Verifique pasta assets/ e assets/figures/.")