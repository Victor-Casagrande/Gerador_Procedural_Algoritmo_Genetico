# 6. Registro de uso de IA generativa (Apêndice C)

Uma linha por uso relevante, **no mesmo PR do código**. Esta tabela já é a seção 6 do Diário: o .docx é gerado a partir dela.

O roteiro exige três coisas:
- **registrar:** o que foi pedido, o que a IA respondeu, o que aceitamos ou rejeitamos e por quê;
- **verificar:** código testado e referências encontradas de verdade;
- **explicar:** todos explicam tudo na apresentação.

As colunas "Aceitamos / rejeitamos" e "Como verificamos" são escritas pela pessoa, não pela IA.

| Data | Quem (papel) | Ferramenta | Objetivo | Prompt (resumo) | Resposta (resumo) | Aceitamos / rejeitamos e por quê | Como verificamos |
|---|---|---|---|---|---|---|---|
| 17/11 | Victor (A) | Claude | Conferir o roteiro e escolher o tema | "Analise o material; sei que nem tudo está certo." | Erros do roteiro, agenda real; temas avaliados (jogo, F1, dungeon) | Aceitamos a agenda corrigida; escolhemos o gerador com AG | Notebook do exemplo executado; grade de horários da turma |
| 17/11 | Victor (A) | Claude | Criticar a especificação inicial do gerador | "Avalie esta especificação de gerador com AG." | 6 problemas (monotonicidade errada, portas duplicadas, etc.) | Aceitamos: portas nas ligações, simulação de inventário, penalidade graduada, zonas fixas | Mapa M4 em `testes/mapas_pequenos.py` (contraexemplo da fórmula) passa no teste |
| 17/11 | Victor (A) | Claude | Buscar trabalhos científicos | "Trabalhos sobre dungeons com portas e chaves por AG e sem IA." | 7 trabalhos | Candidatos; só entram depois de lidos | DOIs conferidos no Crossref |
| 17/11 | Victor (A) | Claude Fable 5.2 | Planejar sem implementar | "Planeje modelagem, arquitetura, testes, experimentos e cronograma." | `docs/PLANO.md` | Aceitamos a modelagem; H3 e H7 a decidir pela equipe | Revisão por outra sessão de IA: contas de 387/281 genes, índices, caminho mínimo 20 |
| 24/11 | Victor (A) | Claude | Passar o Diário para Markdown no repositório | "Dá para pôr o Diário no repositório para as IAs preencherem?" | Diário em `docs/diario/` (Markdown) e script que gera o .docx | Aceitamos: o .docx no Git não mostra diferenças nem junta edições | .docx gerado e conferido visualmente |
| 24/11 | Victor (A) | Claude | Implementar o núcleo e os baselines para o CP2 | "Verifique o estado e faça o que precisava estar pronto até 24/11." | `config`, `representacao`, `validacao`, `avaliacao`, `aleatorio`, `baselines`, `desenho`, `experimentos`, 28 testes; esqueletos de `operadores`, `ag`, `graficos` | *(equipe preenche)* | Testes: M1–M4 com respostas feitas à mão; construtivo válido em 1000 sementes; buscas concordando em 2300 mapas; pior caso 6078. A FAZER: cada integrante refazer à mão o M1 |
| 25/11 | Lucas (B) | GitHub Copilot | Implementar os operadores do CP3 e seus testes | "Implementar seleção por torneio, cruzamento de um ponto e mutação na ordem, seguindo as seções 2.2, 3.4 e 5.3 do PLANO; deixar cruzamento por zona para depois." | Os três operadores e testes foram implementados; `cruzamento_por_zona` continua no esqueleto. | *(preencher)* | *(preencher)* |
| 25/11 | Victor (A) | Claude | Confirmar os papéis no ESTADO.md e na capa do Diário | "Tire o (proposto; confirmar) do meu papel e ponha Lucas (B) e Willighan (C) na capa." | Papel A confirmado; nomes de B e C e nomes completos da equipe na capa; divisão de módulos marcada como combinada e contagem de testes (40, com os operadores) corrigida no ESTADO.md | *(Victor preenche)* | *(Victor preenche)* |
| 25/11 | Victor (A) | Claude | Experimentos do AG e tabelas automáticas (tarefas 5 e 6 do papel A) | "Faça tudo da minha parte que for possível." | E0 a E3, ensaio e comparação por tempo em `experimentos.py`, testados com AG falso; `ferramentas/tabela_resultados.py`; marcadores no `08_resultados.md` e no ESTADO.md; revisão do `operadores.py` | *(Victor preenche)* | *(Victor preenche)* |
| 25/11 | Victor (A) | Claude | Replanejar para a apresentação em 01 ou 03/12 | "Não daria para adiantar mais alguma coisa da minha parte? A apresentação pode ser feita 01/12 ou 03/12." | Agenda no ESTADO.md e no 01_agenda.md com a apresentação em 03/12 (01/12 opcional) e prazos por pessoa; a primeira versão planejava para 01/12 com cortes de escopo e foi corrigida depois que Victor explicou que 01/12 é opcional; fora do repositório, um guia de sabatina dos módulos do papel A e o roteiro das partes 3 e 4 da apresentação | *(Victor preenche)* | *(Victor preenche)* |
