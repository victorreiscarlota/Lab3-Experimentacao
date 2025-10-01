# Análise de Code Review em Repositórios Populares do GitHub

Este projeto tem como objetivo analisar a atividade de code review realizada em repositórios populares do GitHub, coletando dados de Pull Requests (PRs) e suas métricas para responder questões de pesquisa sobre o processo de revisão de código.

## Estrutura do Projeto

```
/
├── .env
├── main.py
├── requirements.txt
├── assets/
│   ├── popular_repos.txt
│   └── prs_dataset.csv
└── scripts/
    ├── collect_popular_repos.py
    └── collect_prs_metrics.py
```

- **scripts/**: scripts Python para coleta dos dados.
- **assets/**: arquivos gerados (lista de repositórios e dataset de PRs).
- **main.py**: executa o fluxo completo do projeto.
- **requirements.txt**: dependências do projeto.
- **.env**: arquivo para inserir seu token pessoal do GitHub.

## Configuração Inicial

### 1. Crie o ambiente virtual

No VSCode, abra um terminal Git Bash na raiz do projeto e execute:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure seu token GitHub

Crie um arquivo `.env` na raiz do projeto contendo:

```
GITHUB_TOKEN=seu_token_aqui
```

Para gerar seu token, acesse [github.com/settings/tokens](https://github.com/settings/tokens) e crie um novo token com permissão de leitura em repositórios públicos.

## Execução dos Scripts

Execute o fluxo completo do projeto rodando apenas o arquivo `main.py`:

```bash
python main.py
```

Esse comando irá:

1. Coletar os 200 repositórios mais populares e salvar em `assets/popular_repos.txt`.
2. Coletar os PRs desses repositórios e salvar o dataset em `assets/prs_dataset.csv`.

## Observações Importantes

- **Limite de requisições:** A API do GitHub possui limites de requisição. Se atingir o limite, aguarde ou utilize um token com maior permissão.
- **Os arquivos gerados ficam na pasta `assets/`.**
- **Os scripts podem ser ajustados para coletar mais métricas conforme avanço do laboratório.**

## Dependências

- requests
- pandas
- tqdm
- PyGithub
- python-dotenv

Todas estão listadas em `requirements.txt`.

## Autor

## Autores

- [Victor Reis Carlota](https://github.com/victorreiscarlota)
  
  <img src="./docs/vitola.png" alt="Victor Reis Carlota" width="150"/>

- [Luís Felipe Brescia](https://github.com/LuisBrescia)

  <img src="./docs/lulu.png" alt="Victor Reis Carlota" width="150"/>

---

---

**Dúvidas ou sugestões:** Abra uma issue ou entre em contato!
