# 4. Métrica e baseline (Etapa 2)

**Métrica:** penalidade = 100 × ΣH + 1 × ΣS, com H1 a H7 e S1 a S5 do Quadro de Modelagem (seção 5). Também: válidos em 10 execuções, cada S separada e o tempo.

**Baseline 1, gerador construtivo** (como jogos assim fazem, sem IA; código em `gerador/baselines.py`), para cada zona:

1. Um caminho aleatório (busca em profundidade com vizinhos em ordem sorteada) da célula de chegada da zona até a célula de saída da zona.
2. A árvore cresce, ligando vizinhas sorteadas, até o tamanho sorteado (entre a ocupação mínima e 24 células).
3. As pontas da árvore viram salas especiais na quantidade sorteada dentro da faixa da zona; as outras células viram corredor ou sala comum por sorteio.
4. Zona Leve: uma aresta sorteada recebe porta de nível 1; o cartão 1 fica numa sala do lado do início e o cartão 2 numa sala do outro lado. Zona Pesada: o cartão 3 numa sala sorteada.
5. Zona Pesada: de 3 a 6 armadilhas em corredores sorteados.
6. Avaliar com a mesma função de penalidade do AG.

Por construção ele não viola nenhuma restrição obrigatória: verificado por teste em 1000 sementes (`testes/test_baselines.py`).

**Baseline 2, busca aleatória:** sorteia mapas com a mesma função que gera a população inicial do AG e guarda o melhor, avaliando exatamente o mesmo número de mapas que o AG (contado por contador). Responde: "o AG é melhor que sortear muito?".

**Baseline 3, construtivo rerolado:** sorteia mapas do construtivo até o mesmo número de avaliações e guarda o melhor. É o "sortear outra semente" que se faz na prática, e a comparação mais honesta.

**Configuração extra do AG, o AG semeado:** a população inicial vem do construtivo. Comparado com o rerolado, responde: "partindo dos mesmos mapas, seleção, cruzamento e mutação fazem melhor do que sortear de novo?".

## Resultado dos baselines (24/11, CP2)

10 sementes (0 a 9), 60 200 avaliações por execução. Comando: `python -m gerador.experimentos baselines --processos 10`. Arquivos: `resultados/baselines_execucoes.csv` e `resultados/baselines_resumo.csv`.

| Método | Válidos em 10 | Obrigatórias (média) | Desejáveis: média (melhor – pior) | Penalidade (média) | Tempo por execução |
|---|---|---|---|---|---|
| Construtivo (1 mapa) | 10 | 0 | 18,9 (8 – 24) | 18,9 | ~0,001 s |
| Busca aleatória | 0 | 23,5 | 29,3 (18 – 80) | 2379,3 | ~26 s |
| Construtivo rerolado | 10 | 0 | 2,4 (2 – 3) | 2,4 | ~99 s |

Desejáveis por tipo (média): construtivo S1 = 8,2, S2 = 3,7, S3 = 3,9, S4 = 2,8, S5 = 0,3; rerolado S1 = 0,4, S2 = 2,0 e as outras 0.

**Leitura:**
- Sortear mapas não funciona: em nenhuma semente a busca aleatória achou um mapa sem violação obrigatória.
- O construtivo sempre gera mapa jogável, mas fraco: 18,9 desejáveis em média, quase metade em becos (S1).
- O construtivo rerolado é o número que o AG precisa superar. Ele também é o método mais lento por avaliação.
