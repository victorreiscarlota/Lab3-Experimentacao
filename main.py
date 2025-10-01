import os
import subprocess
import sys

def run_script(script_path):
    result = subprocess.run([sys.executable, script_path])  
    if result.returncode != 0:
        print(f"Erro ao executar {script_path}")
    else:
        print(f"{script_path} executado com sucesso!")

def ensure_assets_dir():
    if not os.path.exists("assets"):
        os.makedirs("assets")

if __name__ == "__main__":
    ensure_assets_dir()
    print("Coletando repositórios populares...")
    run_script(os.path.join("scripts", "collect_popular_repos.py"))
    print("Coletando PRs e métricas dos repositórios...")
    run_script(os.path.join("scripts", "collect_prs_metrics.py"))
    print("Processo concluído. Os arquivos estão em /assets.")