# Estado do projeto

**Atualize este arquivo em todo PR:** marque o que ficou pronto e escreva o próximo passo. É por ele que qualquer integrante, e qualquer IA, sabe onde o projeto está sem precisar perguntar.

Última atualização: 25/11/2026 (Lucas e Victor, com apoio de IA; ver o diario/06_registro_ia.md).

## Papéis

| Papel | Quem | Módulos |
|---|---|---|
| A: núcleo e experimentos | Victor | `config`, `representacao`, `validacao`, `experimentos` |
| B: sem IA, operadores e desenho | Lucas | `aleatorio`, `baselines`, `operadores`, `desenho` |
| C: avaliação, AG, gráficos e notebook | Willighan | `avaliacao`, `ag`, `graficos`, notebook |

Em 24/11, para não perder o CP2, o papel A também implementou `aleatorio`, `baselines`, `avaliacao` e `desenho`. Divisão combinada pela equipe para equilibrar:
- **B fica com `operadores.py`** (torneio, cruzamentos, mutação) e assume o `desenho.py` e o `baselines.py` (lendo, revisando e sabendo explicar);
- **C fica com `ag.py`, `graficos.py` e o notebook**, e assume o `avaliacao.py` da mesma forma.

Assim o coração do AG, que o professor mais vai perguntar, é escrito por B e C.

## Checkpoints

| Checkpoint | Situação |
|---|---|
| CP1 (17/11): Ficha | feito |
| CP2 (24/11): baseline rodando e medido | **pronto**; números abaixo e no Diário (`docs/diario/04_baseline.md`) |
| CP3 (24/11): Quadro, esqueleto, Ponto de Retomada | esqueleto pronto (`operadores`, `ag`, `graficos` com assinaturas); Quadro e Ponto de Retomada de 24/11 em `docs/diario/` |
| CP4 (03/12): experimentos e entrega | — |

Observação: em 23/11 não houve aula de IA, ao contrário do que dizia a grade.

## O que está pronto (24/11)

**Módulos implementados:**
- `config.py`: instância 12 × 8, layout do cromossomo (387 posições, 281 livres), `Regras` com os parâmetros provisórios da seção 2.4 do PLANO.md;
- `representacao.py`: posições dos genes, `definir_*`, `decodificar` → `Mapa`, `dominios_ok`, `descrever_posicao`;
- `validacao.py`: simulação de inventário e caminho crítico;
- `avaliacao.py`: H1–H7, S1–S5 (teto 19), `avaliar`, `penalidade`, `aptidao`;
- `aleatorio.py`: `gerar_aleatorio`, uniforme ou com pesos;
- `baselines.py`: construtivo (testado em 1000 sementes, nenhuma violação obrigatória), `busca_aleatoria`, `construtivo_rerolado`, `Resultado`;
- `desenho.py`: `desenhar_mapa` e `desenhar_lado_a_lado`;
- `experimentos.py`: `rodar_execucao`, `bateria` (com processos), `resumir`, `salvar_csv`, linha de comando.

**Testes:** 40 testes (29 do núcleo, da avaliação e dos baselines; 11 dos operadores, de 25/11). Entre eles:
- os mapas M1 a M4 com as respostas feitas à mão;
- o pior caso do `cromossomo_base` (penalidade 6078);
- as duas buscas concordando;
- o construtivo válido em 1000 sementes.

**Decisões tomadas no código (confirmar com a equipe):**
- H3 (cartão só em sala) e H7 (câmara com entrada única) **foram implementadas** como o PLANO.md propõe;
- o construtivo usa o tamanho de zona entre `ocup_min` e 24 células, e uma única porta de nível 1 na Zona Leve.

## Resultados dos baselines (CP2)

Rodado em 24/11 com `python -m gerador.experimentos baselines --processos 10`.
- **Orçamento:** 60 200 avaliações (200 × 301) por execução, sementes 0 a 9.
- **Arquivos:** `resultados/baselines_execucoes.csv` (uma linha por execução) e `resultados/baselines_resumo.csv`.

| Método | Válidos em 10 | Obrigatórias (média) | Desejáveis: média (melhor – pior) | Penalidade (média) | Tempo por execução |
|---|---|---|---|---|---|
| Construtivo (1 mapa) | 10 | 0 | 18,9 (8 – 24) | 18,9 | ~0,001 s |
| Busca aleatória | **0** | 23,5 | 29,3 (18 – 80) | 2379,3 | ~26 s |
| Construtivo rerolado | 10 | 0 | **2,4 (2 – 3)** | 2,4 | ~99 s |

Desejáveis por tipo (média): construtivo S1 = 8,2, S2 = 3,7, S3 = 3,9, S4 = 2,8, S5 = 0,3; rerolado S1 = 0,4, S2 = 2,0 e o resto 0.

**O que isso diz:**
- **Sortear mapas não funciona:** nenhuma das 60 200 tentativas, em nenhuma semente, saiu sem violação obrigatória.
- **O construtivo sempre gera mapa jogável, mas fraco:** 18,9 desejáveis em média, quase metade em becos (S1).
- **Sortear 60 200 mapas do construtivo e ficar com o melhor é um baseline muito forte:** penalidade de 2 a 3. É o risco previsto no PLANO.md (D8): **o AG precisa chegar perto de 2 para empatar.** O rerolado também é o método mais lento por avaliação (gerar um mapa construtivo custa cerca de 0,7 ms). Vale comparar também por tempo, não só por número de avaliações, e mostrar onde cada método erra (S1 a S5).
- **Os parâmetros de `Regras` congelam hoje.** Não podem ser mexidos para o AG "ganhar" (PLANO.md, D9).

## Próximos passos

| Quem | Tarefa | Prazo |
|---|---|---|
| B | **Concluído em 25/11:** `selecao_torneio`, `cruzamento_um_ponto`, `mutacao`, com os testes da seção 5.3 | 25/11 (aula extra) |
| C | `ag.py`: `populacao_inicial` e `algoritmo_genetico`, seguindo o laço do projeto exemplo | 25/11 |
| B | Próximo passo: `cruzamento_por_zona` e o teste de fechamento (1000 pares do construtivo) | até 30/11 |
| A | Fichamento de Pereira et al. (2021) em `docs/diario/03_fichamentos.md`; perguntas ao professor e Ponto de Retomada de 25/11 | 25/11 (aula extra) |
| A | Ensaio de convergência (3 sementes) e decisão do orçamento; integrar o AG em `experimentos.py` | 26 a 30/11 |
| C | Notebook em modo rápido do início ao fim; `grafico_convergencia` | até 01/12 |
| Todos | Ler os módulos que não escreveram; refazer à mão o mapa M1 (`testes/mapas_pequenos.py`) | até 01/12 |
| Todos | Conferir o Diário em `docs/diario/` (números do CP2, Ponto de Retomada de 24/11 e registro de IA já estão lá) e gerar o .docx com `python ferramentas/gerar_diario.py` para mostrar no checkpoint | 24/11 |

## Pendências e perguntas

- Perguntas ao professor (ver o Ponto de Retomada de 17/11 no Diário): um `.zip` com módulos e notebook vale como "baseline no mesmo arquivo"? A bateria pode rodar em casa? O AG semeado é aceito?
- Repositório público ou privado; proteção da `main`.

## Ideias (fora do escopo até o mínimo ficar pronto)

- Formato da peça no desenho (ponta, reto, curva, T, cruz).
- Grade 20 × 12 para falar de escala.
