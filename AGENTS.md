# AGENTS.md: regras para qualquer IA (e qualquer pessoa) que mexer neste repositório

Este arquivo é lido automaticamente por várias ferramentas de IA para código (Codex, Copilot, Cursor, Gemini CLI, Claude Code e outras). Quem usa uma IA de conversa que não lê o repositório (ChatGPT, Gemini no navegador etc.) cola o prompt de [docs/PROMPT_INICIAL.md](docs/PROMPT_INICIAL.md) no começo da conversa.

**Antes de qualquer tarefa, leia nesta ordem:**
1. este arquivo;
2. [docs/ESTADO.md](docs/ESTADO.md): o que está pronto, quem faz o quê e o próximo passo;
3. só a seção do [docs/PLANO.md](docs/PLANO.md) que a tarefa cita.

## O projeto em 5 linhas

Trabalho Final de Inteligência Artificial (CCC0736, IFC Videira, 2026/2), em equipe de 3 pessoas (Lucas, Victor e Willighan).

Um **algoritmo genético** gera mapas de uma instalação: uma grade de 12 × 8 com três zonas (Leve, Pesada e de Entrada) ligadas por checkpoints e com portas que exigem cartões de nível 1 a 3.

O mapa precisa ser:
- **jogável:** tudo alcançável, e nenhum cartão preso atrás da porta que ele mesmo abre;
- **bem construído:** poucos becos, armadilhas fora do caminho, cartão longe da porta.

O AG é comparado, com a mesma penalidade, a três soluções sem IA: o gerador construtivo, a busca aleatória e o construtivo rerolado. A modelagem completa está nas seções 2.1 a 2.4 do PLANO.md.

## Regras da disciplina (não negociáveis)

1. **Python.** O AG (seleção, cruzamento, mutação, elitismo, laço) é **escrito pela equipe**. É proibido DEAP, PyGAD ou qualquer biblioteca de AG. NumPy, pandas e Matplotlib só para dados e gráficos.
2. **Experimentos:** 10 sementes por configuração, com média, melhor e pior; pelo menos 2 parâmetros variados; a mesma métrica e o mesmo número de avaliações para todos os métodos que buscam.
3. **Reprodutível:** o notebook roda do início ao fim num kernel reiniciado, e os números dos slides são os que o código produz.
4. **Todo uso de IA vai para o registro.** Ele mostra o que foi pedido, o que foi aceito ou rejeitado e como foi verificado: uma linha em [docs/diario/06_registro_ia.md](docs/diario/06_registro_ia.md) no mesmo PR. Essa tabela já é a seção 6 do Diário de Bordo.
5. **Na apresentação, o professor pergunta a cada integrante sobre qualquer parte do código.** Código que a pessoa não sabe explicar não entra.

## O que a IA pode e não pode fazer aqui

- **Pode:** explicar, revisar, sugerir testes, achar erros, propor alternativas e escrever código **que a pessoa vai ler linha por linha, testar e saber explicar**.
- **Não pode:**
  - inventar referência bibliográfica (as que valem estão no PLANO.md, seção 5, e no Diário);
  - mudar regra de modelagem por conta própria (cromossomo, H1–H7, S1–S5, pesos, tetos, parâmetros de `config.Regras`);
  - mudar teste para ele passar;
  - mexer em módulo de outro papel sem combinar.
- **Parâmetros congelados:** os valores de `gerador/config.py` congelaram em 24/11. Mudança depois disso só com a equipe de acordo, registrada no ESTADO.md e no Diário com o motivo.
- **Em caso de dúvida ou conflito com o PLANO.md:** a IA pergunta à pessoa, em vez de adivinhar.

## Como o código é organizado

| Módulo | O que faz | Papel |
|---|---|---|
| `gerador/config.py` | Instância, layout do cromossomo, `Regras` | A |
| `gerador/representacao.py` | Posições dos genes, `decodificar` → `Mapa` | A |
| `gerador/validacao.py` | Simulação de inventário e caminho crítico | A |
| `gerador/avaliacao.py` | H1–H7, S1–S5, `avaliar`, `penalidade`, `aptidao` | C |
| `gerador/aleatorio.py` | `gerar_aleatorio` (população inicial e busca aleatória) | B |
| `gerador/baselines.py` | Construtivo, busca aleatória, rerolado, `Resultado` | B |
| `gerador/operadores.py` | Torneio, cruzamentos, mutação | B |
| `gerador/ag.py` | População inicial e laço do AG | C |
| `gerador/experimentos.py` | Execuções, baterias, CSV | A |
| `gerador/desenho.py`, `gerador/graficos.py` | Imagem do mapa e gráficos (fundo branco) | B / C |
| `Projeto_Final_Gerador_AG.ipynb` | Só chama funções e mostra resultados | C |

Quem é A, B e C está no ESTADO.md.

**Convenções:**
- **Nomes e comentários:** nomes de funções e variáveis em português, sem acento; comentários e docstrings em português.
- **Sorteios:** toda função que sorteia recebe um `rng` (`random.Random(semente)`). Nunca use `random.seed`, `random.random()` solto, `np.random` global, nem a ordem de um `set` para sortear.
- **Funções pequenas**, uma responsabilidade cada, como nos notebooks do laboratório.
- **O cromossomo é uma lista de 387 inteiros.** A posição de cada gene sai sempre das funções de `representacao.py` (`pos_tipo`, `pos_leste`, `pos_cartao`...), nunca de um número escrito à mão.
- **Lógica não entra no notebook:** ela fica nos `.py`.

## Diário de Bordo (docs/diario/)

O Diário de Bordo que o professor confere nos checkpoints é mantido **em Markdown, dentro do repositório**, um arquivo por seção. O `.docx` (e depois o PDF) é gerado com:

```bash
python ferramentas/gerar_diario.py
```

O arquivo sai em `entrega/Diario_de_Bordo.docx`. Ele não vai para o Git: é sempre gerado de novo a partir do Markdown.

**Toda tarefa atualiza a seção do Diário que ela afeta, no mesmo PR:**

| Se a tarefa... | Atualize |
|---|---|
| usou IA | `06_registro_ia.md`: uma linha nova (as duas últimas colunas são da pessoa, não da IA) |
| é um fichamento | `03_fichamentos.md`: só quem leu o trabalho preenche, com as próprias palavras; IA não ficha |
| mudou o baseline ou mediu algo dele | `04_baseline.md` e `08_resultados.md` |
| mudou uma decisão de modelagem (com a equipe de acordo) | `05_quadro_de_modelagem.md`, com a data e o motivo |
| terminou um encontro (aula) | `07_pontos_de_retomada.md`: um bloco novo no topo |
| produziu números de experimento | `08_resultados.md`, citando o arquivo de `resultados/` de onde saíram |
| é a análise final (03/12) | `09_analise.md` |

**O que a IA nunca faz no Diário:**
- inventar resultado;
- preencher as colunas "aceitamos/rejeitamos" e "como verificamos" no lugar da pessoa;
- escrever um fichamento de trabalho que ninguém leu.

## Testes

```bash
python -m pytest
```

- **Toda função nova vem com teste em `testes/`**, de preferência um caso pequeno com a resposta feita à mão. Os mapas de exemplo estão em `testes/mapas_pequenos.py`.
- **Os testes que não podem quebrar nunca:**
  - o construtivo sem violação obrigatória em 1000 sementes;
  - as duas buscas concordando;
  - o pior caso do `cromossomo_base` (penalidade 6078);
  - os mapas M1 a M4.
- **Nunca apague nem afrouxe um teste para o seu código passar.** Se um teste parece errado, pergunte à equipe.

## Fluxo de trabalho

1. **Atualize a main:** `git switch main` e depois `git pull`.
2. **Crie uma branch curta para a tarefa:** `git switch -c feat/operadores-torneio` (prefixos: `feat/`, `fix/`, `test/`, `docs/`, `exp/`).
3. **Faça só o que a tarefa pede.** Ideias extras vão para a seção "Ideias" do ESTADO.md.
4. **Antes de commitar,** confira:
   - `python -m pytest` passando;
   - o notebook sem saídas;
   - o [docs/ESTADO.md](docs/ESTADO.md) atualizado (o que ficou pronto e o próximo passo);
   - a linha no [docs/diario/06_registro_ia.md](docs/diario/06_registro_ia.md), se usou IA.
5. **Commit em português**, no formato `tipo(módulo): o que mudou`, por exemplo `feat(operadores): seleção por torneio com testes`.
6. **Abra um Pull Request** para a `main` e peça revisão a outro integrante. Quem aprova escreve uma frase explicando o que o código faz. Se não souber explicar, não aprova.
7. **O que nunca entra no repositório:** o material do professor, o Diário em edição, a `.venv`, chaves e senhas.

## Números de referência (para conferir se algo quebrou)

- `PADRAO.n_genes == 387` e `len(PADRAO.genes_livres) == 281`.
- `avaliar(cromossomo_base())` dá 60 violações obrigatórias e 78 desejáveis: penalidade 6078.
- Uma avaliação leva cerca de 0,2 ms; gerar um mapa construtivo, cerca de 0,7 ms.
