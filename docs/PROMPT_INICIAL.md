# Prompt inicial para IA de conversa (ChatGPT, Gemini, Copilot Chat, DeepSeek...)

Use quando a IA **não lê o repositório sozinha**. Cole, no começo da conversa:
1. o texto do bloco abaixo, preenchendo os colchetes;
2. o conteúdo do `AGENTS.md`;
3. o conteúdo do `docs/ESTADO.md`;
4. os arquivos `.py` que a tarefa usa (o seu módulo e os que ele importa) e, se precisar, a seção do `docs/PLANO.md` citada na tarefa.

Ferramentas que leem a pasta do projeto (Codex, Cursor, Copilot no VS Code, Gemini CLI, Claude Code) já leem o `AGENTS.md` sozinhas: basta pedir "leia o AGENTS.md e o docs/ESTADO.md antes de começar".

---

```
Você vai me ajudar no Trabalho Final de Inteligência Artificial da minha equipe (gerador
procedural de mapas com algoritmo genético, em Python). Abaixo estão as regras do repositório
(AGENTS.md), o estado atual do projeto (ESTADO.md) e os arquivos que importam para esta tarefa.

Eu sou o papel [A / B / C] e a minha tarefa agora é: [descreva, por exemplo: "implementar
selecao_torneio em gerador/operadores.py, com os testes da seção 5.3 do PLANO.md"].

Regras para você:
- Siga o AGENTS.md. Não use bibliotecas de algoritmo genético (DEAP, PyGAD etc.): o AG é escrito
  à mão. Não mude regras de modelagem, pesos nem testes existentes.
- Todo sorteio usa o `rng` recebido (random.Random), nunca o random global.
- Explique o código que propuser, linha por linha quando eu pedir: eu preciso saber explicar
  tudo ao professor. Prefira a solução mais simples, no estilo dos notebooks de laboratório.
- Proponha também os testes (pytest, com casos pequenos de resposta conhecida).
- Se algo estiver ambíguo ou parecer contradizer o PLANO.md, pergunte antes de escrever.
- Não invente referências bibliográficas.
- No fim, escreva uma linha para o registro de IA no formato:
  | data | papel | objetivo | prompt (resumo) | resposta (resumo) | aceitamos/rejeitamos e por quê | como verificamos |

[cole aqui o AGENTS.md]
[cole aqui o docs/ESTADO.md]
[cole aqui os arquivos .py da tarefa]
```

---

Depois da conversa:
- **Rode `python -m pytest`.**
- **Leia o código que a IA escreveu até saber explicar cada linha.**
- **Preencha a linha do [diario/06_registro_ia.md](diario/06_registro_ia.md)**, principalmente as duas últimas colunas: elas são suas, não da IA.
