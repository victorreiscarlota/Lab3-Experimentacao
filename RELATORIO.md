# Caracterização da Atividade de Code Review em Repositórios Populares do GitHub  
**Relatório Parcial – Sprint 2 (Lab03S02)**  

**Curso:** Engenharia de Software  
**Disciplina:** Laboratório de Experimentação de Software  
**Período:** 6º  
**Equipe:** Victor Reis Carlota; Luís Felipe Brescia  

---

## Sumário  
- [Caracterização da Atividade de Code Review em Repositórios Populares do GitHub](#caracterização-da-atividade-de-code-review-em-repositórios-populares-do-github)
  - [Sumário](#sumário)
  - [Resumo](#resumo)
  - [Introdução](#introdução)
  - [Trabalhos Relacionados](#trabalhos-relacionados)
  - [Questões de Pesquisa e Hipóteses](#questões-de-pesquisa-e-hipóteses)
  - [Metodologia](#metodologia)
    - [5.1 Escopo e Critérios de Seleção](#51-escopo-e-critérios-de-seleção)
    - [5.2 Coleta e Enriquecimento dos Dados](#52-coleta-e-enriquecimento-dos-dados)
    - [5.3 Definição das Métricas](#53-definição-das-métricas)
    - [5.4 Tratamento, Filtragem e Preparação](#54-tratamento-filtragem-e-preparação)
    - [5.5 Abordagem Estatística](#55-abordagem-estatística)
  - [Resultados Preliminares](#resultados-preliminares)
  - [Discussão](#discussão)
  - [Ameaças à Validade](#ameaças-à-validade)
  - [Conclusão Parcial e Próximos Passos](#conclusão-parcial-e-próximos-passos)
  - [Referências](#referências)

---

## Resumo  
Este relatório parcial apresenta uma análise exploratória sobre fatores associados ao desfecho (merge ou fechamento sem merge) e à intensidade do processo de revisão (número de revisões, comentários e participantes) de Pull Requests (PRs) em repositórios populares do GitHub. Foram coletados PRs dos 200 repositórios mais estrelados e extraídas métricas que capturam dimensões estruturais (tamanho das mudanças), temporais (duração do ciclo de revisão), textuais (extensão da descrição) e sociais (interações e revisões formais). Definimos oito questões de pesquisa (RQs) e hipóteses informais. A abordagem conceitual inspira-se na noção de “issue tales” de Fiechter et al. (2021), adaptando a perspectiva narrativa para um eixo PR-cêntrico. As análises quantitativas iniciais empregam estatística descritiva (medianas globais) e correlações de Spearman, adequadas a distribuições assimétricas com caudas longas. Os resultados numéricos finais serão consolidados na próxima sprint (Lab03S03); aqui enfatizamos metodologia, fundamentação e indícios preliminares.  

---

## Introdução  
Pull Requests constituem o principal ponto de convergência entre atividade de contribuição, avaliação técnica, diálogo social e decisão de integração em ecossistemas open source. A literatura mostra que fatores como tamanho do patch, clareza textual, responsividade dos revisores e dinâmica social impactam a velocidade e a taxa de aceitação de contribuições (Bacchelli & Bird, 2013; Gousios et al., 2014; Tsay et al., 2014). Entretanto, em repositórios altamente populares, há adicionalmente pressão de escala, presença de automação (CI/CD, bots) e fragmentação de atenção, o que potencialmente altera padrões de revisão.

Inspiramo-nos no conceito de **issue tale** (Fiechter et al., 2021), que estrutura a evolução de um issue como narrativa multirrelacional. Transpondo a ideia, tratamos cada PR como uma micro‑narrativa composta por: (i) artefatos de modificação (arquivos, linhas); (ii) temporalidade (janela de revisão); (iii) discurso e descrição (texto do corpo); (iv) interações sociais (comentários, revisões, participantes); (v) decisão final (merge ou fechamento). A partir dessa perspectiva, investigamos: que atributos correlacionam com maior probabilidade de merge? Que fatores se associam a mais revisões? Em que medida a densidade social favorece ou dificulta a convergência?

Este relatório parcial descreve desenho experimental, definição de métricas, hipóteses e primeiros sinais estatísticos, estabelecendo base reprodutível para análise aprofundada subsequente (visualizações ampliadas, testes não paramétricos e modelagem preditiva).

---

## Trabalhos Relacionados  
Estudos clássicos sobre code review moderno (Bacchelli & Bird, 2013) destacam o papel do contexto social e informacional na efetividade da revisão. Gousios et al. (2014) investigam determinantes de aceitação de PRs, ressaltando aspectos de confiança e experiência. Tsay et al. (2014) apontam que fatores sociais podem rivalizar em importância com aspectos puramente técnicos no desfecho de um PR. Jiang et al. (2022) e outros trabalhos recentes reforçam o impacto de automação na triagem e priorização. Fiechter et al. (2021) propõem um modelo visual narrativo (“issue tales”) que motiva a abstração relacional adotada aqui. Nosso trabalho diferencia-se por combinar essa visão narrativa adaptada a PRs com uma organização sistemática de métricas multidimensionais (tamanho–tempo–texto–interação) aplicada a um grande conjunto de repositórios populares.

---

## Questões de Pesquisa e Hipóteses  
Dimensão A – Status Final (MERGED vs CLOSED sem merge):  
- RQ01: Qual a relação entre o tamanho do PR e o status final?  
  Hipótese H01: PRs menores (menos arquivos e linhas) têm maior probabilidade de merge.  
- RQ02: Qual a relação entre o tempo de análise e o status final?  
  Hipótese H02: Ciclos muito longos sinalizam atrito e reduzem chance de merge.  
- RQ03: Qual a relação entre a extensão da descrição e o status final?  
  Hipótese H03: Descrições mais extensas (maior detalhamento) elevam chance de merge.  
- RQ04: Qual a relação entre interações (comentários/participantes) e o status final?  
  Hipótese H04: Interações moderadas favorecem merge; excesso pode refletir disputa ou ambiguidade.

Dimensão B – Número de Revisões (`review_count`):  
- RQ05: Tamanho do PR vs número de revisões.  
  H05: PRs maiores exigem mais revisões incrementais.  
- RQ06: Tempo de análise vs número de revisões.  
  H06: Maior duração correlaciona-se positivamente com revisões acumuladas.  
- RQ07: Extensão da descrição vs número de revisões.  
  H07: Descrições ricas reduzem revisões adicionais (inversamente correlacionado).  
- RQ08: Interações sociais vs número de revisões.  
  H08: Mais participantes e comentários correlacionam-se com mais revisões (efeito facilitador porém possivelmente inflando iterações).

---

## Metodologia  

### 5.1 Escopo e Critérios de Seleção  
Selecionamos os 200 repositórios mais populares (ordenados por estrelas) independente de linguagem, garantindo heterogeneidade de domínios. Não estratificamos por ecossistema nesta fase (análise agregada global).  

### 5.2 Coleta e Enriquecimento dos Dados  
Para cada repositório: coleta de PRs (estado `all`) até um limiar mínimo de 100. Para cada PR, invocamos endpoints adicionais para obter diffs agregados (additions, deletions, changed_files), revisões formais (`/pulls/{number}/reviews`), comentários de conversa (`/issues/{number}/comments`) e comentários de diff (`/pulls/{number}/comments`). A construção de participantes únicos exclui logins de bots via heurística simples (`[bot]`, sufixo `-bot`).  

### 5.3 Definição das Métricas  
- Tamanho: `changed_files`, `additions`, `deletions`.  
- Tempo: `review_cycle_hours` (delta entre criação e merge/close).  
- Texto: `body_char_count` (comprimento bruto em caracteres).  
- Interações: `review_count` (revisões formais), `review_comment_count` (comentários em diffs), `issue_comment_count` (comentários de discussão), `participants_count` (autor + revisores/comentadores únicos não-bot).  
- Estado derivado: `final_status` ∈ {MERGED, CLOSED_SEM_MERGE}; `merged` boolean.  

### 5.4 Tratamento, Filtragem e Preparação  
Critérios aplicados ao conjunto enriquecido:  
1. Manter somente PRs com estado final MERGED ou CLOSED.  
2. Exigir pelo menos uma revisão formal (`review_count ≥ 1`).  
3. Remover PRs com ciclo inferior a 1 hora (possíveis merges triviais ou ações automatizadas).  
4. Excluir entradas com campos críticos ausentes.  
Não realizamos (nesta fase) truncamento de outliers; métricas podem exibir caudas pesadas (será abordado na Sprint 3).  

### 5.5 Abordagem Estatística  
Optamos por correlação de Spearman (ρ) para avaliar monotonicidade entre variáveis contínuas e: (a) status binário codificado (MERGED=1), (b) `review_count`. Spearman é robusto a não linearidades suaves e a distribuições assimétricas. Estatísticas descritivas (medianas) são preferidas à média dada a presença de assimetria e outliers. Testes de significância complementares (ex.: Mann–Whitney U) e modelos multivariados (regressão logística) serão introduzidos na próxima fase.

---

## Resultados Preliminares  
(Os valores quantitativos definitivos serão inseridos após consolidação da execução completa. Abaixo apresentamos a estrutura interpretativa planejada.)  

1. Distribuições iniciais sugerem forte assimetria em métricas de tamanho (long tail), reforçando a escolha de Spearman.  
2. Indícios exploratórios (amostras parciais) apontam mediana de `changed_files` inferior em PRs merged quando comparados a fechados sem merge.  
3. `review_cycle_hours` tende a se alongar em PRs não aceitos, possivelmente refletindo reiteração de discussões ou abandono gradual.  
4. `body_char_count` apresenta tendência de ser maior em PRs aceitos, ainda que com sobreposição significativa (fato comum em estudos de documentação).  
5. Interações (participantes e comentários) mostram padrão potencialmente curvilíneo: baixo engajamento correlaciona-se a rejeição rápida; excesso, a alongamento do ciclo — exigindo futura modelagem não linear.  
6. Para número de revisões, variáveis de tamanho parecem exercer efeito positivo fraco a moderado (ρ esperado entre 0.2 e 0.4), enquanto texto pode ter correlação próxima de zero ou levemente negativa (a validar).  

---

## Discussão  
Os achados preliminares estão alinhados com a literatura que destaca: (i) penalização implícita de patches grandes devido ao aumento da carga cognitiva; (ii) relevância de contexto textual para acelerar entendimento; (iii) papel ambivalente das interações — simultaneamente suporte à qualidade e sinal de atrito. A hipótese H07 (descrições extensas reduzem número de revisões) pode ser frágil caso a extensão textual sirva mais para clarificar inicialmente do que para evitar iterações posteriores inevitáveis (ex.: exigências arquiteturais). A adoção de uma perspectiva narrativa inspirada em “issue tales” reforça a necessidade futura de visualizações temporais e relacionais (e.g., sequências de eventos, densidade de autores por fase).  

A ausência, por ora, de modelos multivariados implica que correlações simples podem confundir co-ocorrências (ex.: PRs grandes atraem mais participantes e também têm mais revisões; distinguir causa exige controle estatístico adicional).  

---

## Ameaças à Validade  

- Interna: Heurística simples para remoção de bots pode subestimar participação automatizada residual.  
- Externa: Foco em repositórios altamente populares (viés de maturidade, governança formal) limita extrapolação a projetos pequenos.  
- Construto: `body_char_count` não captura qualidade semântica (clareza, estrutura, presença de checklist).  
- Conclusão: Correlações não estabelecem causalidade; efeitos potenciais mediadores (linguagem, tipo de mudança) não foram isolados.  
- Evolutiva: Política de revisão pode mudar ao longo do tempo; análise agregada ignora regime temporal (será mitigado em versão final com cortes por período).  

---

## Conclusão Parcial e Próximos Passos  
Este relatório parcial consolidou: (i) definição de escopo e métricas; (ii) formulação de oito questões de pesquisa com hipóteses estruturadas; (iii) delineamento estatístico apropriado para dados assimétricos; (iv) primeiros indícios consistentes com literatura de code review. A próxima fase (Sprint 3) incluirá:  
1. Inserção dos resultados quantitativos definitivos (tabelas de medianas e coeficientes ρ reais).  
2. Testes não paramétricos (Mann–Whitney U) para diferenças entre grupos.  
3. Regressão logística/multivariada para explicar probabilidade de merge.  
4. Segmentação por quartis de tamanho e tempo.  
5. Visualizações temporais inspiradas em narrativas (adaptação de “issue tales” para “PR tales”).  
6. Análise de outliers e normalização (log-transformações).  

---

## Referências  

- Bacchelli, A.; Bird, C. (2013). Expectations, Outcomes, and Challenges of Modern Code Review. ICSE.  
- Fiechter, A.; Minelli, R.; Nagy, C.; Lanza, M. (2021). Visualizing GitHub Issues. VISSOFT 2021, pp. 155–159. DOI: 10.1109/VISSOFT52517.2021.00030.  
- Gousios, G.; Pinzger, M.; Deursen, A. (2014). An Exploratory Study of the Pull-Based Software Development Model. ICSE.  
- Jiang, Y. et al. (2022). Understanding the Impact of Bots on Pull Request Review. (Referência indicativa; ajustar conforme seleção final).  
- Tsay, J.; Dabbish, L.; Herbsleb, J. (2014). Influence of Social and Technical Factors for Evaluating Contribution in GitHub. ICSE.  
- Sommerville, I. (2020). Software Engineering (10th ed.).  
- McConnell, S. (2004). Code Complete. Microsoft Press.  
- Gamma, E. et al. (1994). Design Patterns. Addison-Wesley.  

*(Referências adicionais poderão ser refinadas e normalizadas em estilo único – ABNT ou IEEE – na versão final.)*  

---
_Fim do Relatório Parcial (Sprint 2)._