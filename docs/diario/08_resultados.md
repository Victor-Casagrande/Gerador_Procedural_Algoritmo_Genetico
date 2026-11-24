# 8. Tabela de resultados

Anotar na hora: configuração, sementes, resultado. Resultado que não foi anotado não existe na apresentação. Todo número aqui vem de um arquivo de `resultados/`, gerado pelo código; nunca digitado à mão a partir de uma execução não registrada.

## E0: comparação principal (mesmo número de avaliações para todos os métodos que buscam)

| Método | Sementes | Válidos em 10 | Obrigatórias (média) | Desejáveis: média (melhor – pior) | Tempo | Observações |
|---|---|---|---|---|---|---|
| Construtivo | 0 a 9 | 10 | 0 | 18,9 (8 – 24) | ~0,001 s | 24/11, `resultados/baselines_resumo.csv` |
| Busca aleatória | 0 a 9 | 0 | 23,5 | 29,3 (18 – 80) | ~26 s | 24/11, 60 200 avaliações |
| Construtivo rerolado | 0 a 9 | 10 | 0 | 2,4 (2 – 3) | ~99 s | 24/11, 60 200 avaliações |
| AG puro (principal) | 0 a 9 | | | | | |
| AG semeado | 0 a 9 | | | | | |

## E1 (taxa de mutação, genes mutados por filho) e E2 (tipo de cruzamento)

| Configuração (demais parâmetros no padrão) | Válidos em 10 | Obrigatórias (média) | Desejáveis (média) |
|---|---|---|---|
| E1: 0 genes por filho | | | |
| E1: 0,5 genes por filho | | | |
| E1: 1 gene por filho (padrão) | | | |
| E1: 2 genes por filho | | | |
| E1: 5 genes por filho | | | |
| E2: AG puro, cruzamento por zona | | | |
| E2: AG semeado, cruzamento por zona | | | |
