# Diário de Bordo · Trabalho Final de IA

**Gerador procedural de instalações com zonas e cartões de acesso via Algoritmo Genético** *(título provisório)*

| Campo | Resposta |
|---|---|
| Disciplina | Inteligência Artificial (CCC0736) · Prof. Tiago Heineck |
| Turma | Turma 01 · 2026/2 · IFC Campus Videira |
| Equipe | Lucas Duarte Lopes, Victor Casagrande e Willighan Tinelli de Souza |
| Técnica principal | Algoritmo genético |
| Criado em | 17/11/2026 (aula 1) |
| Onde estão os arquivos | Repositório github.com/Victor-Casagrande/Gerador_Procedural_Algoritmo_Genetico. Plano: `docs/PLANO.md`. Estado: `docs/ESTADO.md`. Este Diário: `docs/diario/` |
| Versão | 3 (24/11): o Diário passou a ser mantido em Markdown no repositório; o .docx e o PDF são gerados por `python ferramentas/gerar_diario.py` |

> Como usar: este é o único documento da equipe fora do código (seção 2.4 do roteiro). O professor consulta em cada checkpoint, e ele é entregue em PDF em 03/12. Cada seção é um arquivo em `docs/diario/`, atualizado no mesmo Pull Request do trabalho a que se refere (regras no `AGENTS.md`). Tudo o que foi feito com apoio de IA generativa está no Registro de IA (seção 6) e precisa ser revisado e assumido pela equipe.

## Papéis

| Papel | Quem | Escreve | Assume (lê até saber explicar) | Fichamento | Partes da apresentação |
|---|---|---|---|---|---|
| A: núcleo e experimentos | Victor | `config`, `representacao`, `validacao`, `experimentos` | — | Pereira et al. (2021) | 3 e 4 |
| B: sem IA e operadores | Lucas | `operadores` | `aleatorio`, `baselines`, `desenho` | Shaker et al. (2016) | 1, 2 e 7 |
| C: AG e resultados | Willighan | `ag`, `graficos`, notebook | `avaliacao` | Togelius et al. (2011) | 5 e 6 |
