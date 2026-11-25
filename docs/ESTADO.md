# Estado do projeto

**Atualize este arquivo em todo PR:** marque o que ficou pronto e escreva o próximo passo. É por ele que qualquer integrante, e qualquer IA, sabe onde o projeto está sem precisar perguntar.

Última atualização: 25/11/2026 (Papel C, laço do AG, com apoio de IA; ver o diario/06_registro_ia.md).

## Papéis

| Papel | Quem | Módulos |
|---|---|---|
| A: núcleo e experimentos | Victor *(proposto; confirmar)* | `config`, `representacao`, `validacao`, `experimentos` |
| B: sem IA, operadores e desenho | Lucas | `aleatorio`, `baselines`, `operadores`, `desenho` |
| C: avaliação, AG, gráficos e notebook | Willighan | `avaliacao`, `ag`, `graficos`, notebook |

Em 24/11, para não perder o CP2, o papel A também implementou `aleatorio`, `baselines`, `avaliacao` e `desenho`. Sugestão para equilibrar:
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

**Testes:** 28 testes. Entre eles:
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
| C | **Concluído em 25/11 (branch `feat/ag-laco`, falta revisão):** `populacao_inicial` e `algoritmo_genetico` em `ag.py`, com `testes/test_ag.py` (63 testes passando no total). Fórmulas no cabeçalho do módulo. Falta rodar o 200 × 300 (ensaio do papel A) | 25/11 |
| C | Revisar o `ag.py` linha por linha e responder os "Pontos a discutir" abaixo antes do ensaio de convergência | até 26/11 |
| B | Próximo passo: `cruzamento_por_zona` e o teste de fechamento (1000 pares do construtivo) | até 30/11 |
| A | Ensaio de convergência (3 sementes) e decisão do orçamento; integrar o AG em `experimentos.py` | 26 a 30/11 |
| C | Notebook em modo rápido do início ao fim; `grafico_convergencia` | até 01/12 |
| Todos | Ler os módulos que não escreveram; refazer à mão o mapa M1 (`testes/mapas_pequenos.py`) | até 01/12 |
| Todos | Conferir o Diário em `docs/diario/` (números do CP2, Ponto de Retomada de 24/11 e registro de IA já estão lá) e gerar o .docx com `python ferramentas/gerar_diario.py` para mostrar no checkpoint | 24/11 |

## Pendências e perguntas

- Perguntas ao professor (ver o Ponto de Retomada de 17/11 no Diário): um `.zip` com módulos e notebook vale como "baseline no mesmo arquivo"? A bateria pode rodar em casa? O AG semeado é aceito?
- Repositório público ou privado; proteção da `main`.

## Pontos a discutir com a equipe (levantados na análise do laço do AG, 25/11)

Nada abaixo mudou parâmetro congelado. São decisões ou conferências que dependem do grupo. Os números marcados "estimativa" não foram medidos.

**Decisões tomadas no código que o PLANO.md não dizia (confirmar):**
1. **`primeiro_valido` é o índice da avaliação (1 a `n_avaliacoes`), não a geração.** O PLANO.md (seção 3.3 e 6.2) diz "geração". Mudei para a unidade ser a mesma das buscas no CSV do E0. Se a equipe preferir a geração, `experimentos.py` converte, mas aí o E0 mistura unidades. O comentário de `Resultado` em `baselines.py` (papel B) foi ajustado só nisso.
2. **`historico` é o melhor visto até cada geração (acumulado), não o mínimo da geração.** Igual ao das buscas. Com `elite ≥ 1` os dois coincidem; com `elite = 0` (E3 opcional) o acumulado nunca sobe.
3. **Uma moeda por par no cruzamento e elite que não cruza nem muta.** Atribuídas ao projeto exemplo, mas o notebook dele não está no repositório. Conferir na seção 4 do exemplo.
4. **O par inteiro é cruzado e mutado e a lista é cortada em `tam_pop − elite`.** No padrão (200, 2) são 99 pares exatos e o corte não faz nada.
5. **A aptidão `1/(1+φ)` não influencia o torneio** (só a ordem de φ conta). Mantida pela forma do exemplo.

**Riscos para ler antes dos experimentos (e registrar a previsão no Diário antes de rodar E0 a E2):**
6. **Pressão de seleção alta:** com k = 3 e N = 200, a linhagem do melhor domina em 6 a 7 gerações. O progresso depois disso vem quase só da mutação (cerca de 1 gene por filho).
7. **Mutação:** genes mutados por filho seguem aproximadamente Poisson(1): 37% dos filhos não mutam nada. Estimativa: perto de metade dos filhos repete o φ do pai (genes inertes: ligação com ponta vazia, armadilha fora de corredor). O PLANO.md (seção 4.4, item 5) conta indivíduos gerados, então o AG é um pouco desfavorecido na contagem de 60 200. Dizer isso na análise.
8. **Cruzamento de um ponto:** só cortes em 130 ou 259 respeitam a fronteira de zona (2 em 386). Entre pais distantes tende a quebrar a conectividade; entre irmãos da mesma população é benigno. O por zona só mistura 6 combinações. Previsão: E2 com diferença pequena no AG puro.
9. **Paisagem em estágios:** se a Zona Leve não conecta ao checkpoint A, todo o resto fica inalcançável (H2 alto) e melhorias nas outras zonas não aparecem em φ.
10. **Hipótese do esvaziamento:** esvaziar uma célula inalcançável baixa H2 mais barato que conectá-la, e o freio é H5 (16 ocupadas por zona). Conferir nos mapas finais se o AG fica perto de 16 por zona, ao contrário do construtivo (16 a 24).
11. **Previsões a registrar:** AG puro chega a H = 0 em muitas sementes mas fica acima do rerolado (2,4) nas desejáveis; E1 (mutação) mostra o efeito mais claro; o AG semeado depende do cruzamento por zona para não perder validade.

**Medições que ajudariam (fora do escopo desta tarefa):** φ da população inicial sorteada, fração de filhos com φ igual ao do pai e diversidade por geração.

## Ideias (fora do escopo até o mínimo ficar pronto)

- Medir a diversidade e a fração de filhos neutros por geração, para sustentar os pontos 6 a 8 acima.
- Formato da peça no desenho (ponta, reto, curva, T, cruz).
- Grade 20 × 12 para falar de escala.
