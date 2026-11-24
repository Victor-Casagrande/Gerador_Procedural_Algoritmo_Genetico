# Gerador procedural de instalações com Algoritmo Genético

Trabalho Final de **Inteligência Artificial (CCC0736)**, IFC Campus Videira, 2026/2. Equipe: Lucas, Victor e Willighan.

Um gerador de mapas de instalações subterrâneas, no estilo de uma dungeon. O mapa é dividido em três zonas de segurança (Leve, Pesada e de Entrada), separadas por checkpoints, e tem portas que só abrem com cartões de acesso de nível 1 a 3. O projeto se inspira na estrutura de *SCP – Containment Breach*.

Um **algoritmo genético**, escrito pela equipe, procura mapas que sejam:
- **jogáveis:** tudo conectado e nenhum cartão preso atrás da porta que ele mesmo abre;
- **bem construídos:** poucos becos inúteis, armadilhas fora do caminho obrigatório, cartão longe da porta que destrava.

Os mapas do AG são comparados, com a mesma métrica, a três soluções sem IA: um gerador construtivo por regras, a busca aleatória e o construtivo "rerolado".

O plano completo (modelagem, arquitetura, testes, experimentos e cronograma) está em **[docs/PLANO.md](docs/PLANO.md)**. O estado atual (o que está pronto, quem faz o quê, próximos passos) está em **[docs/ESTADO.md](docs/ESTADO.md)**.

**Vai usar IA?** As regras para qualquer ferramenta de IA estão no **[AGENTS.md](AGENTS.md)**. Para IA de conversa que não lê o repositório, use o prompt pronto de [docs/PROMPT_INICIAL.md](docs/PROMPT_INICIAL.md) e registre o uso em [docs/REGISTRO_IA.md](docs/REGISTRO_IA.md).

## Estrutura

```
Projeto_Final_Gerador_AG.ipynb   o arquivo que roda do início ao fim (só chama funções)
gerador/                         todo o código, um módulo por responsabilidade
testes/                          um test_<modulo>.py por módulo, rodados com pytest
resultados/                      CSV da bateria completa (versionados)
figuras/                         PNG com fundo branco usados nos slides (versionados)
docs/PLANO.md                    o plano do projeto
```

O que cada módulo faz e quem é o dono: PLANO.md, seção 3.2.

## Como rodar

Requer o Python 3.10 ou mais novo.

```bash
python -m venv .venv
```

No Windows (Git Bash):

```bash
source .venv/Scripts/activate
```

No Linux e no macOS:

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

Rodar os testes:

```bash
python -m pytest
```

Rodar os baselines (sem IA) em 10 sementes, gravando em `resultados/` (alguns minutos):

```bash
python -m gerador.experimentos baselines --processos 4
```

Versão rápida, só para conferir que roda (não grava):

```bash
python -m gerador.experimentos baselines --rapido
```

Abrir o notebook:

```bash
jupyter notebook Projeto_Final_Gerador_AG.ipynb
```

O notebook tem a constante `MODO_RAPIDO`:
- **`True`:** 2 sementes e um orçamento pequeno. Roda em poucos minutos e serve de teste do dia a dia.
- **`False`:** a bateria completa. Leva horas, e só ela grava em `resultados/` e `figuras/`.

## Regras de trabalho (resumo do PLANO.md, seção 8)

- **A `main` sempre roda:** testes passando e notebook em modo rápido sem erro. Ninguém faz commit direto nela.
- **Uma branch curta por tarefa**, por exemplo `feat/validacao-simulacao`, `fix/mutacao-genes-fixos` ou `exp/bateria-e1`.
- **Pull request pequeno**, revisado por outro integrante. Quem aprova escreve uma frase explicando o que a função faz.
- **Commits em português**, no formato `tipo(módulo): o que mudou`. Os tipos são `feat`, `fix`, `test`, `docs`, `exp` e `refactor`.
- **Sorteios com semente local:** toda função que sorteia recebe um `rng = random.Random(semente)`. Nunca use `random.seed`, `random.random()` solto nem `np.random` global.
- **O AG é implementado pela equipe:** seleção, cruzamento, mutação e elitismo escritos à mão. Nada de DEAP, PyGAD ou similares.
- **O notebook tem um dono só** (papel C). Antes de commitar, limpe as saídas. Para experimentar, use `rascunho_*.ipynb`, que fica fora do Git.
- **O que nunca entra no repositório:** o material do professor, o Diário de Bordo em edição, a `.venv`, chaves e tokens.

## Uso de IA generativa

O planejamento teve apoio de IA generativa (Claude), como o plano de ensino permite. Todo uso relevante é registrado no Diário de Bordo da equipe: o que foi pedido, o que foi aceito ou rejeitado e como verificamos. Cada integrante precisa saber explicar qualquer parte do código.

## Referência principal

PEREIRA, L. T.; PRADO, P. V. S.; LOPES, R. M.; TOLEDO, C. F. M. Procedural generation of dungeons' maps and locked-door missions through an evolutionary algorithm validated with players. *Expert Systems with Applications*, v. 180, art. 115009, 2021. DOI: [10.1016/j.eswa.2021.115009](https://doi.org/10.1016/j.eswa.2021.115009).

As demais referências estão no PLANO.md e no Diário de Bordo.
