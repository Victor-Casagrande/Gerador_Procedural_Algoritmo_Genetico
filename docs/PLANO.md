# Plano do Trabalho Final: gerador procedural de instalações com Algoritmo Genético

CCC0736 – Inteligência Artificial · IFC Campus Videira · 2026/2 · Equipe: Lucas, Victor e Willighan

Escrito em 17/11/2026 com apoio de IA generativa (Claude). **Este documento é uma proposta: só vale depois que a equipe ler, discutir e assumir cada decisão.** Ele não contém código, só assinaturas, estruturas de dados e pseudocódigo. Registrar o uso no Diário de Bordo (texto sugerido na seção 7.4).

Material lido antes de escrever: `Roteiro_Projeto_Final_IA.docx`, `Projeto_Exemplo_Horarios_AG.docx` e `.ipynb`, `Diario_de_Bordo.docx`. O repositório no GitHub foi consultado e está vazio.

Quatro decisões já tomadas pela equipe nesta conversa (17/11):

| Decisão | Escolha |
|---|---|
| Como os cartões abrem portas | Hierárquico: o cartão N abre toda porta de nível ≤ N |
| Restrições que o cromossomo pode garantir | Garantir no cromossomo (deixam de ser penalidade) |
| Formato do código entregue | Módulos `.py` + um notebook que roda tudo (confirmar com o professor) |
| Ponto de partida do AG | AG puro é a configuração principal; AG semeado com o construtivo é experimento e plano B |

Sumário: 1. Dúvidas e riscos de modelagem · 2. Decisões de modelagem finais · 3. Arquitetura do código · 4. Orçamento de tempo de execução · 5. Plano de testes · 6. Plano de experimentos · 7. Cronograma por data e por pessoa · 8. Fluxo de trabalho no Git · 9. Roteiro da apresentação · 10. Riscos e plano B · 11. Decisões que a equipe precisa tomar · 12. Primeiras 3 tarefas de amanhã

---

## 1. Dúvidas e riscos de modelagem

O que estava mal definido na proposta inicial e a recomendação para cada ponto. Os três primeiros são os mais graves: do jeito que estava, a aptidão premiava mapas ruins e a conta do peso 100 não fechava.

### 1.1 Problemas que mudam o resultado

**P1. A aptidão tinha "soluções ruins com nota boa".** É a pergunta da oficina do roteiro ("existe solução ruim que receberia nota alta?"), e a resposta era sim, de quatro jeitos:

| Mapa ruim | Por que tirava nota boa | Correção |
|---|---|---|
| Quase vazio: um corredor reto do início à saída | Poucas células não vazias, logo nada inalcançável e nenhum beco | Ocupação mínima por zona (nova H5) |
| Sem nenhuma armadilha | S2 (armadilha no caminho crítico) fica zero de graça | Quantidade de armadilhas da Zona Pesada dentro de uma faixa (nova H6) |
| Sem nenhuma porta interna | O cartão 1 não serve para nada e ninguém é punido | S3 passa a exigir que cada cartão seja usado no caminho crítico |
| Todo beco rotulado como "sala" | S1 (becos) fica zero trocando só o rótulo | Beco é definido pelo número de ligações; só sala especial pode ser ponta, e a quantidade delas tem faixa (H4) |

**P2. O peso 100 não se sustentava.** A regra é: um mapa com uma violação obrigatória tem de perder de qualquer mapa sem nenhuma. Isso exige `100 > soma máxima das desejáveis`. Mas S1, S4 e S5 eram contagens sem limite: um caminho crítico pode ter até 383 passos (são 96 células × 4 níveis de cartão = 384 estados), então a soma das desejáveis podia passar de 500. **Correção:** cada desejável tem um teto de 19 pontos. A conta fica `5 × 19 = 95 < 100` (seção 2.4).

**P3. O cruzamento de um ponto no cromossomo achatado destrói a localidade 2D.** Com a ordem "96 células, depois 172 ligações, depois cartões, depois armadilhas", um corte no meio das células dá ao filho metade das células de um pai e **todas** as ligações do outro. As ligações de um pai não fazem sentido com as células do outro, e o filho sai quebrado quase sempre. **Correção** (seção 2.2): reordenar o cromossomo em blocos de 4 genes por célula (tipo, ligação leste, ligação sul, armadilha), percorrendo a grade **coluna por coluna**, com o gene de cada cartão logo depois da zona dele. Assim:

- o cruzamento de um ponto, igual ao do laboratório, passa a ser um **corte vertical do mapa**: a parte esquerda vem de um pai e a direita do outro; a emenda tem no máximo uma coluna (8 células);
- como as zonas são faixas de colunas, duas das três zonas chegam ao filho inteiras;
- o cruzamento por zona vira um caso particular (cortar exatamente na fronteira) com uma propriedade forte: **se os dois pais são válidos, o filho é válido**. As zonas só se tocam pelos checkpoints, que são fixos, então trocar uma zona inteira não quebra nada dentro das outras. Isso é testável (seção 5.3) e é o melhor argumento para o diferencial "zonas com checkpoints".

Cruzamento 2D (trocar um retângulo) fica no escopo desejável: o corte vertical já resolve o problema com o operador do laboratório.

### 1.2 Respostas às perguntas pedidas

**Vale um operador de reparo?** Não no escopo mínimo. Um reparo que conserta conectividade é, na prática, um pedaço do gerador construtivo dentro do AG: funciona, mas enfraquece a resposta a "foi o AG que resolveu?". O plano B para "o AG não chega a mapas válidos" é a **inicialização semeada** (população inicial vinda do construtivo), que não exige código novo. Se mesmo assim a equipe quiser o reparo como experimento, a comparação justa tem quatro regras:

1. o reparo roda antes da avaliação e cada indivíduo conta como **uma** avaliação, com ou sem reparo;
2. a busca aleatória ganha o mesmo reparo (senão a diferença AG × aleatória passa a medir o reparo, não a seleção e o cruzamento);
3. a tabela mostra as duas linhas, "AG sem reparo" e "AG com reparo", com o **tempo** de cada uma, porque o reparo custa processamento;
4. o indivíduo reparado substitui o original na população (o conserto é herdado), e isso é dito no Quadro.

**Como definir caminho crítico, becos e "voltar pelo mesmo caminho"?** Tudo sai de uma única busca em largura (seção 2.3):

- **Caminho crítico:** o menor passeio do início até a saída, calculado por busca em largura no espaço de estados `(célula, nível do cartão)`. O nível sobe ao pisar numa célula com cartão. São no máximo 96 × 4 = 384 estados. O passeio já inclui as idas e voltas obrigatórias para buscar cartão. É a mesma busca em largura da aula de busca não informada, só que o estado guarda também o cartão.
- **Beco inútil (S1):** célula com exatamente 1 ligação que não é sala especial, não tem cartão e não é o início nem a saída.
- **Voltar pelo mesmo caminho (S4):** número de passos do caminho crítico que pisam numa célula já visitada: `tamanho da lista do caminho − número de células distintas`.

Limitação a declarar: pode haver mais de um caminho mínimo. O desempate é pela ordem fixa dos vizinhos (norte, leste, sul, oeste), o que deixa o resultado reprodutível, mas S2 e S4 medem **um** caminho mínimo, não todos.

**Quais são as salas obrigatórias e especiais de cada zona?** No escopo mínimo, "sala especial" é um tipo só (valor 3), com duas regras calculáveis: tem exatamente **uma entrada** (é uma câmara, não uma passagem) e cada zona exige uma quantidade dentro de uma faixa. Os nomes são só para a legenda do desenho. Catálogo com tipos distintos e orientação da porta fica no desejável.

| Zona | Colunas | Células fixas (sempre corredor) | Salas especiais exigidas | Nome na legenda | Outras regras da zona |
|---|---|---|---|---|---|
| Leve | 0–3 | início; lado oeste do checkpoint A | 2 a 4 | câmara de contenção | cartões 1 e 2 ficam aqui |
| Pesada | 4–7 | lado leste do checkpoint A; lado oeste do checkpoint B | 2 a 4 | câmara reforçada | cartão 3 fica aqui; 3 a 6 armadilhas, só em corredor |
| Entrada | 8–11 | lado leste do checkpoint B; saída | 1 a 3 | sala de controle | sem cartão e sem armadilha |

**A grade 12 × 8 com os genes de armadilha deixa o espaço grande demais?** O tamanho em si não é o problema. O projeto exemplo tem 10³² grades e o AG resolve com 30 000 avaliações; o que importa é quanto do espaço é inválido e se a penalidade dá uma direção para melhorar. Três fatos:

- Proposta original, 367 genes: cerca de 10²¹³ mapas. Desses genes, 64 de armadilha (fora da Zona Pesada) e a maior parte das posições de cartão só serviam para gerar violação. Com as restrições garantidas pelo cromossomo ficam **281 genes livres**, cerca de 10¹⁷⁷ mapas, e nenhum gene inútil.
- Mapas sorteados nascem quase todos travados. Medi 300 grades 12 × 8 sorteadas: do início alcançam-se, em média, **2 a 8 estados** de 384. A penalidade inicial fica na casa dos milhares, e é a contagem graduada de células inalcançáveis (H2) que dá a direção ao AG.
- Portanto o risco real é o AG puro gastar o orçamento inteiro aprendendo a conectar o mapa, coisa que o construtivo faz de graça. Por isso o AG semeado está no plano desde o começo, e o orçamento só é fixado depois de um ensaio de convergência (seção 4.3).

### 1.3 Outros pontos mal definidos

| # | Ponto | Recomendação |
|---|---|---|
| D1 | "Entrada" significa duas coisas: o ponto onde o jogador nasce e a Zona de Entrada, onde fica a saída | Chamar o ponto de **início** em todo o código, nos slides e no Diário |
| D2 | "Checkpoints em posições fixas" não dizia quais, nem o que acontece com as outras 14 ligações que cruzam fronteiras de zona | Checkpoint A (nível 2) entre (linha 1, coluna 3) e (linha 1, coluna 4); checkpoint B (nível 3) entre (linha 6, coluna 7) e (linha 6, coluna 8). As outras 14 ligações de fronteira ficam sempre fechadas. Em linhas diferentes de propósito, para obrigar a atravessar a Zona Pesada na vertical |
| D3 | H1 (célula isolada) é um caso particular de H3 (célula inalcançável): a mesma falha contava duas vezes | Juntar numa só: células ocupadas inalcançáveis (H2 nova) |
| D4 | "Sala comum" não tinha função: era só um rótulo | Cartão só pode ficar em sala (comum ou especial), e armadilha só conta em corredor. O formato da peça (ponta, reto, curva, T, cruz) é **derivado** das ligações na hora de desenhar, sem gene novo |
| D5 | Sem caminho crítico (saída inalcançável), S2 a S5 não têm valor | Nesse caso S2 a S5 valem o teto. Chegar à saída nunca piora a nota |
| D6 | Dois cartões na mesma célula | Conta como violação em H3 |
| D7 | A busca aleatória só é justa se sortear da **mesma distribuição** da população inicial do AG | Uma função só, `gerar_aleatorio`, usada pelos dois; avaliações contadas por um contador, não estimadas |
| D8 | "Rerolar o construtivo" com o mesmo orçamento é um baseline forte e **pode ganhar do AG puro** | Deixa de ser opcional: é a comparação mais honesta. Se ele ganhar, isso vai para a tabela e para a análise crítica do jeito que saiu. O AG semeado responde à pergunta seguinte: "partindo dos mesmos mapas, seleção, cruzamento e mutação fazem melhor do que sortear de novo?" |
| D9 | Os alvos das desejáveis (número de becos, faixa de comprimento, k) podem ser ajustados até o AG parecer bom | Os alvos são definidos por raciocínio de design e **congelados em 24/11**, antes de existir qualquer resultado do AG. Mudou depois, registra no Diário com o motivo |
| D10 | O Diário é um `.docx` na pasta de um integrante, editado por três pessoas | Passar para Word online ou Google Docs compartilhado, com um responsável por encontro |
| D11 | O roteiro diz "não há tarefa para casa" e o checklist diz "baseline no mesmo arquivo" | Perguntar ao professor em 18/11 (seção 11) |

---

## 2. Decisões de modelagem finais

No formato do Quadro de Modelagem do roteiro. Esta seção substitui a seção 5 do Diário (hoje marcada como proposta inicial).

### 2.1 O que é fixo (fora do cromossomo)

- Grade de 12 colunas × 8 linhas. Célula `i = coluna × 8 + linha` (numeração coluna por coluna): 0–31 Zona Leve, 32–63 Zona Pesada, 64–95 Zona de Entrada.
- Início em (linha 3, coluna 0), célula 3. Saída em (linha 4, coluna 11), célula 92.
- Checkpoint A, nível 2, entre as células 25 e 33. Checkpoint B, nível 3, entre as células 62 e 70.
- Seis células são sempre corredor: 3, 92, 25, 33, 62 e 70.
- As outras 14 ligações que cruzam fronteira de zona são sempre fechadas.

### 2.2 Quadro de Modelagem

| Item | Decisão final | Alternativa descartada | Por quê |
|---|---|---|---|
| **Indivíduo** | Um mapa completo: tipo de cada célula, todas as passagens e portas, a posição dos 3 cartões e as armadilhas | Evoluir só o esqueleto e completar portas e cartões por regra | Com portas e cartões por regra o AG não teria o que otimizar em S3; a parte interessante do problema ficaria fora dele |
| **Cromossomo** | Lista de 387 inteiros, 281 livres. Para cada célula, na ordem coluna por coluna, um bloco de 4 genes: tipo (0 vazia, 1 corredor, 2 sala comum, 3 sala especial); ligação leste e ligação sul (0 sem passagem, 1 aberta, 2 porta nível 1, 3 porta nível 2, 4 porta nível 3); armadilha (0 ou 1). Depois do bloco da Zona Leve vêm os genes dos cartões 1 e 2 (0 a 31: posição dentro da zona); depois do bloco da Zona Pesada, o do cartão 3 | Ordem achatada "células, ligações, cartões, armadilhas" (proposta inicial); porta guardada na célula; zona como gene | Achatado: o cruzamento separa as células das ligações que dão sentido a elas (P3). Porta por célula: a mesma porta descrita duas vezes. Zona como gene: contradiz zonas fixas |
| **Genes fixos** | 106 das 387 posições têm valor fixo e nunca são sorteadas nem mutadas: 6 tipos de célula, 24 ligações leste (8 da última coluna e 16 de fronteira, das quais 2 são os checkpoints), 12 ligações sul (última linha) e 64 armadilhas fora da Zona Pesada | Cromossomo compacto, sem posições fixas (blocos de tamanho variável) | Blocos iguais dão uma regra só para achar um gene (`4 × célula + campo + deslocamento da zona`), fácil de explicar em pergunta individual. O custo é só memória |
| **Leitura do mapa** (genótipo → fenótipo) | Uma ligação só existe se as duas células não forem vazias. Armadilha só conta em corredor da Zona Pesada. O nível exigido por uma passagem é `valor − 1` (aberta = 0) | Penalizar ligação para célula vazia, cartão fora da zona e armadilha na Zona Leve (antigas H4, H5 e H7) | Mesmo argumento do projeto exemplo ao escolher o vetor de inteiros: uma representação que não consegue gerar o erro é melhor do que gastar gerações punindo o erro |
| **Restrições garantidas pelo cromossomo** | R1 cada porta existe uma vez só. R2 não há ligação para célula vazia. R3 cada cartão está na zona dele. R4 armadilha só na Zona Pesada e só em corredor. R5 zonas, checkpoints, início e saída fixos | — | Ficam no Quadro como "garantidas pela representação", para o professor ver que foram tratadas |
| **Restrições obrigatórias** | H1 a H7 (seção 2.4) | Nota zero para todo inválido | Trava o AG: no começo quase tudo é inválido, e sem diferença de nota não há o que selecionar |
| **Restrições desejáveis** | S1 a S5, cada uma com teto de 19 (seção 2.4) | Termos sem fórmula ("equilíbrio", "progressão") | Cada termo precisa ser calculável e ter um máximo conhecido |
| **Função de aptidão** | `penalidade = 100 × ΣH + 1 × ΣS`; `aptidão = 1 / (1 + penalidade)` | Pesos diferentes por restrição desejável | Mesma forma do projeto exemplo. Pesos iguais nas desejáveis é limitação assumida (vai para o slide de limitações) |
| **Seleção** | Torneio com k = 3, sorteio sem repetição, vence a maior aptidão | Roleta | Com penalidades na casa dos milhares, as aptidões dos inválidos ficam todas perto de zero e a roleta vira sorteio; quando surge o primeiro válido ele domina a roleta. O torneio só depende da ordem |
| **Cruzamento** | Um ponto, probabilidade 0,9, sobre o cromossomo em ordem de colunas (corte vertical do mapa). Experimento: cruzamento por zona (cada zona inteira vem de um dos pais, com os cartões dela) | Um ponto no cromossomo achatado; cruzamento uniforme gene a gene | O uniforme mistura genes vizinhos de pais diferentes e destrói corredores. O por zona preserva validade, mas mistura pouco: só 6 combinações diferentes dos pais |
| **Mutação** | Cada gene livre, com probabilidade `taxa`, recebe outro valor do domínio dele (diferente do atual). Padrão: `taxa = 1/281`, em média 1 gene por filho | Mutação própria de porta (sobe ou desce um nível) no escopo mínimo | Sortear entre 5 valores já alcança os vizinhos. A mutação de porta fica como variação opcional (E4) |
| **Elitismo** | Os 2 melhores passam direto | Sem elitismo | É um dos experimentos opcionais (E3) |
| **População inicial** | Principal: sorteio uniforme em cada gene livre (`gerar_aleatorio`). Experimento e plano B: mapas do gerador construtivo | Sorteio enviesado (mais passagens abertas, menos portas) | O uniforme é a escolha neutra, igual à do laboratório. O enviesado é a primeira alavanca se o AG puro não sair do lugar; se for usado, a busca aleatória usa o mesmo |
| **Parâmetros e parada** | População 200, 300 gerações, 200 × 301 = 60 200 avaliações (**provisório**: confirmar no ensaio de convergência, seção 4.3). Parada por número fixo de gerações. Sementes 0 a 9 | Parar quando a penalidade chegar a zero | A parada fixa garante o mesmo número de avaliações para todos os métodos |

### 2.3 Os dois algoritmos de busca que sustentam a avaliação

**Simulação de inventário** (decide se o mapa é jogável; é a que substitui a fórmula de monotonicidade):

```
nível = 0
repita:
    alcançadas = busca em largura a partir do início,
                 passando só por passagens que exigem nível ≤ nível atual
    novo = maior nível entre o atual e os cartões que estão em células alcançadas
    se novo == nível: pare
    nível = novo
devolve (alcançadas, nível, registro das rodadas)
```

No máximo 4 rodadas. O mapa é jogável se a saída e todas as células ocupadas estiverem em `alcançadas`.

**Caminho crítico** (base de S2 a S5):

```
estado inicial = (início, nível do cartão que estiver no início, ou 0)
fila = [estado inicial]; pai = {estado inicial: nenhum}
enquanto a fila não estiver vazia:
    (célula, nível) = retira o primeiro da fila
    se célula == saída: reconstrói a lista de células pelos pais e devolve
    para cada (vizinha, exigido) de célula, na ordem norte, leste, sul, oeste:
        se exigido > nível: pula
        novo = (vizinha, maior entre nível e o cartão que estiver na vizinha)
        se novo ainda não foi visto: pai[novo] = (célula, nível); põe na fila
devolve nenhum
```

As duas buscas precisam concordar: a saída está em `alcançadas` se, e somente se, existe caminho crítico. Isso vira um teste automático sobre milhares de mapas sorteados (seção 5.2), e é a melhor defesa contra erro na avaliação.

### 2.4 Restrições, fórmulas e a conta do peso

Parâmetros provisórios (revisar até 24/11 e congelar): ocupação mínima 16 células por zona; armadilhas entre 3 e 6; alvo de becos 2; K = 6 passos; alvo de passos repetidos 4; comprimento entre 30 e 45 passos (o caminho mais curto possível entre início, checkpoints e saída tem 20).

**Obrigatórias.** Cada linha é uma contagem de violações; todas valem 100.

| Código | O que conta | Fórmula |
|---|---|---|
| H1 | A saída é inalcançável | 1 se a saída não está em `alcançadas`, senão 0 |
| H2 | Células ocupadas inalcançáveis ao fim da simulação | número de células não vazias fora de `alcançadas` |
| H3 | Cartão mal colocado | número de cartões em célula que não é sala, mais 1 para cada cartão que divide a célula com outro |
| H4 | Quantidade de salas especiais da zona fora da faixa | soma, nas 3 zonas, da distância entre a quantidade e a faixa da zona |
| H5 | Zona com poucas células ocupadas | soma, nas 3 zonas, de `max(0, 16 − ocupadas)` |
| H6 | Quantidade de armadilhas da Zona Pesada fora da faixa | distância entre a quantidade e a faixa [3, 6] |
| H7 | Sala especial com número de entradas diferente de 1 | número de salas especiais nessa situação |

Quando a saída é inalcançável ela conta em H1 e em H2. É de propósito: não conseguir terminar o jogo é pior do que perder uma sala lateral.

**Desejáveis.** `caminho` é a lista de células do caminho crítico, com repetição. Cada termo é `min(19, valor)`.

| Código | O que conta | Valor antes do teto |
|---|---|---|
| S1 | Becos inúteis acima do alvo | `max(0, becos − 2)` |
| S2 | Armadilhas no caminho crítico | número de células distintas do caminho que têm armadilha |
| S3 | Cartão perto demais da porta que ele destrava | soma, para N = 1, 2, 3, de `max(0, 6 − d_N)`; `d_N` = passos do caminho entre pisar na célula do cartão N e atravessar a primeira porta de nível N depois disso. Se o cartão não é pego ou não é usado no caminho, `d_N = 0` |
| S4 | Passos repetidos acima do alvo | `max(0, (tamanho do caminho − células distintas) − 4)` |
| S5 | Comprimento do caminho crítico fora da faixa | distância entre o número de passos e a faixa [30, 45] |

Sem caminho crítico, S2 a S5 valem 19.

**A conta do peso.** São 5 desejáveis, cada uma com no máximo 19 pontos: a soma máxima é `5 × 19 = 95`. Um mapa com uma única violação obrigatória tem penalidade ≥ 100. Um mapa sem nenhuma tem penalidade ≤ 95. Como 100 > 95, **qualquer mapa com violação obrigatória perde de qualquer mapa sem nenhuma**, e o AG nunca troca jogabilidade por qualidade. O código deve ter um `assert` com essa conta. O S3 tem máximo natural de 18 (3 cartões × 6).

O que não foi conferido: se a penalidade 0 é alcançável nesta grade. Parece ser (um caminho em zigue-zague com os cartões no trajeto, câmaras como pontas laterais e armadilhas em ramos fora do caminho), mas só as execuções vão dizer. Se nenhuma execução chegar a 0, dizer isso na análise em vez de afirmar que 0 é o ótimo.

### 2.5 Como mostrar o diferencial em relação a Pereira et al.

Antes de afirmar qualquer coisa sobre o método deles, conferir na leitura do fichamento 1 (representação usada, o que a aptidão mede, como validam). Do nosso lado, três evidências, uma por diferencial:

| Diferencial | Evidência no trabalho |
|---|---|
| Zonas com checkpoints fixos | O teste de fechamento do cruzamento por zona (pais válidos → filho válido) e o experimento E2 |
| Peças com entrada em parede | A regra H7 (sala especial com uma entrada só) e o desenho do mapa com o formato de cada peça derivado das ligações. No desejável: orientação exigida da porta |
| Armadilhas | H6 e S2, e a figura lado a lado: no construtivo o caminho crítico passa por armadilhas, no AG não. Com o número de S2 de cada um |

---

## 3. Arquitetura do código

### 3.1 Estrutura de pastas

```
Gerador_Procedural_Algoritmo_Genetico/
├── README.md                  como instalar, rodar os testes e o notebook
├── requirements.txt
├── .gitignore
├── Projeto_Final_Gerador_AG.ipynb    o arquivo que "roda do início ao fim"
├── gerador/                   o pacote com todo o código
│   ├── __init__.py
│   ├── config.py              instância (grade, zonas, fixos) e parâmetros da penalidade
│   ├── representacao.py       índices do cromossomo e leitura do mapa
│   ├── aleatorio.py           gerador aleatório de cromossomos
│   ├── validacao.py           simulação de inventário e caminho crítico
│   ├── avaliacao.py           H1–H7, S1–S5, penalidade e aptidão
│   ├── baselines.py           construtivo, busca aleatória, construtivo rerolado
│   ├── operadores.py          torneio, cruzamentos, mutação
│   ├── ag.py                  população inicial e laço do AG
│   ├── experimentos.py        baterias de 10 sementes, CSV e resumo
│   ├── desenho.py             imagem do mapa
│   └── graficos.py            convergência e gráficos dos experimentos
├── testes/                    um arquivo test_*.py por módulo
├── resultados/                CSV produzidos pela bateria (versionados)
├── figuras/                   PNG com fundo branco usados nos slides (versionados)
└── docs/
    └── PLANO.md               este documento
```

### 3.2 Módulos, responsabilidades e donos

| Módulo | Responsabilidade | Dono | Depende de |
|---|---|---|---|
| `config.py` | Montar a instância (tamanho, zonas, início, saída, checkpoints, regras) e as tabelas derivadas | A | — |
| `representacao.py` | Posição de cada gene, domínios, genes fixos, montar e ler cromossomo | A | config |
| `validacao.py` | Simulação de inventário e caminho crítico | A | representacao |
| `aleatorio.py` | Sortear um cromossomo respeitando domínios e fixos | B | representacao |
| `baselines.py` | Construtivo, busca aleatória, construtivo rerolado | B | representacao, avaliacao |
| `desenho.py` | Desenhar um mapa (zonas, portas por nível, cartões, armadilhas, caminho crítico) | B | representacao |
| `operadores.py` | Torneio, cruzamento de um ponto, cruzamento por zona, mutação | B | representacao |
| `avaliacao.py` | Cada H e cada S como função separada, `avaliar`, `penalidade`, `aptidao` | C | representacao, validacao |
| `ag.py` | População inicial e laço do AG com contador de avaliações | C | operadores, avaliacao, aleatorio, baselines |
| `graficos.py` | Gráficos com fundo branco | C | — (lê os CSV) |
| `experimentos.py` | Rodar uma execução, uma bateria, salvar e resumir | A | ag, baselines |
| notebook | Só chama funções e mostra resultados; nenhuma lógica | C | tudo |

A, B e C são papéis; a equipe decide quem é quem (seção 11). Cada arquivo tem um dono só, o que elimina conflito de edição. Dono não é "o único que sabe": a revisão cruzada da seção 8 existe para isso.

### 3.3 Estruturas de dados

```python
Cromossomo = list[int]          # 387 inteiros na instância padrão

class Regras(NamedTuple):       # parâmetros da penalidade
    ocup_min: int               # 16
    faixa_especiais: tuple      # por zona: ((2, 4), (2, 4), (1, 3))
    faixa_armadilhas: tuple     # (3, 6)
    alvo_becos: int             # 2
    k_cartao: int               # 6
    alvo_repetidos: int         # 4
    faixa_caminho: tuple        # (30, 45)
    teto_s: int                 # 19
    peso_h: int                 # 100
    peso_s: int                 # 1

class Instancia(NamedTuple):    # tudo que é fixo; criada uma vez e só lida
    largura: int; altura: int
    zonas: tuple                # faixa de colunas de cada zona: ((0, 3), (4, 7), (8, 11))
    inicio: int; saida: int     # índices de célula
    checkpoints: tuple          # ((célula oeste, célula leste, nível), ...)
    regras: Regras
    # tabelas derivadas, calculadas em criar_instancia:
    n_genes: int                # 387
    dominio: tuple              # por posição: quantos valores o gene aceita (1 = fixo)
    valor_fixo: tuple           # por posição: o valor, quando fixo
    genes_livres: tuple         # as 281 posições com domínio > 1
    fatia_zona: tuple           # início e fim do trecho de cada zona: ((0, 130), (130, 259), (259, 387))

class Mapa(NamedTuple):         # o cromossomo já lido
    inst: Instancia
    tipo: list[int]             # por célula: 0 vazia, 1 corredor, 2 sala comum, 3 sala especial
    viz: list[list[tuple]]      # por célula: [(vizinha, nível exigido de 0 a 3), ...] em ordem N, L, S, O
    cartao: tuple               # célula do cartão 1, 2 e 3
    armadilha: frozenset        # células com armadilha que conta

class Resultado(NamedTuple):    # o que uma execução de qualquer método devolve
    melhor: Cromossomo
    historico: list[int]        # melhor penalidade até cada geração (ou a cada 200 avaliações)
    n_avaliacoes: int
    primeiro_valido: int | None # geração em que apareceu o primeiro mapa sem violação obrigatória
    tempo: float                # segundos
```

Listas e tuplas simples, como nos notebooks do laboratório, sem herança nem classes com método. NumPy só entra nas estatísticas e nos gráficos.

### 3.4 Assinaturas das funções principais

`config.py`
```python
def criar_instancia(largura, altura, zonas, inicio, saida, checkpoints, regras) -> Instancia
PADRAO: Instancia                        # a grade 12 x 8 da seção 2.1
def instancia_teste(colunas_por_zona=1, altura=3) -> Instancia   # grades pequenas, regras zeradas
```

`representacao.py`
```python
def celula(linha, coluna, inst) -> int
def linha_coluna(i, inst) -> tuple[int, int]
def zona_da_celula(i, inst) -> int
def pos_tipo(i, inst) -> int             # posição do gene no cromossomo
def pos_leste(i, inst) -> int
def pos_sul(i, inst) -> int
def pos_armadilha(i, inst) -> int
def pos_cartao(n, inst) -> int           # n = 1, 2, 3
def cromossomo_base(inst) -> Cromossomo  # tudo vazio e fechado, só os fixos preenchidos
def definir_tipo(crom, i, tipo, inst) -> None
def definir_ligacao(crom, i, j, valor, inst) -> None      # i e j vizinhas
def definir_cartao(crom, n, i, inst) -> None
def definir_armadilha(crom, i, valor, inst) -> None
def decodificar(crom, inst) -> Mapa
def dominios_ok(crom, inst) -> bool      # todo gene dentro do domínio e fixos intactos
```
As funções `definir_*` servem ao construtivo e aos mapas de teste desenhados à mão.

`aleatorio.py`
```python
def gerar_aleatorio(rng, inst, pesos=None) -> Cromossomo   # pesos=None: uniforme
```

`validacao.py`
```python
def simular_inventario(mapa) -> tuple[set[int], int, list]   # (alcançadas, nível final, rodadas)
def caminho_critico(mapa) -> list[int] | None                # células, com repetição
```

`avaliacao.py`
```python
def h1_saida_inalcancavel(mapa, alcancadas) -> int
def h2_celulas_inalcancaveis(mapa, alcancadas) -> int
def h3_cartao_mal_colocado(mapa) -> int
def h4_salas_especiais_fora_da_faixa(mapa) -> int
def h5_zona_pouco_ocupada(mapa) -> int
def h6_armadilhas_fora_da_faixa(mapa) -> int
def h7_sala_especial_sem_entrada_unica(mapa) -> int
def s1_becos(mapa) -> int
def s2_armadilhas_no_caminho(mapa, caminho) -> int
def s3_cartao_perto_da_porta(mapa, caminho) -> int
def s4_passos_repetidos(mapa, caminho) -> int
def s5_comprimento_fora_da_faixa(mapa, caminho) -> int
def avaliar(crom, inst=PADRAO) -> tuple[int, int, dict]      # (obrigatórias, desejáveis, detalhes)
def penalidade(crom, inst=PADRAO) -> int
def aptidao(crom, inst=PADRAO) -> float
```
`avaliar` devolve o mesmo trio do projeto exemplo; `detalhes` tem as chaves `"H1"` a `"H7"` e `"S1"` a `"S5"`.

`baselines.py`
```python
def gerar_construtivo(rng, inst=PADRAO) -> Cromossomo
def busca_aleatoria(n_avaliacoes, rng, inst=PADRAO) -> Resultado
def construtivo_rerolado(n_avaliacoes, rng, inst=PADRAO) -> Resultado
```
Passos do construtivo, a escrever no Diário em 18/11:
```
para cada zona:
    sorteia quantas células a zona terá (entre a ocupação mínima e 24)
    cresce uma árvore por busca em profundidade com vizinhos em ordem sorteada,
        a partir da célula fixa de chegada, até ter o tamanho sorteado
        e conter a célula fixa de saída da zona
    pontas da árvore viram salas especiais até a quantidade sorteada dentro da faixa
    as outras células viram corredor ou sala comum por sorteio
Zona Leve: sorteia uma aresta da árvore, põe ali uma porta de nível 1,
    cartão 1 numa sala do lado do início, cartão 2 numa sala do lado de lá
Zona Pesada: cartão 3 numa sala sorteada; 3 a 6 armadilhas em corredores sorteados
```
Por construção ele não viola nenhuma H, e isso é verificado por teste em 1000 sementes.

`operadores.py`
```python
def selecao_torneio(pop, apts, k, rng) -> Cromossomo           # devolve uma cópia
def cruzamento_um_ponto(p1, p2, rng) -> tuple[Cromossomo, Cromossomo]
def cruzamento_por_zona(p1, p2, rng, inst) -> tuple[Cromossomo, Cromossomo]
def mutacao(crom, taxa, rng, inst) -> Cromossomo               # devolve um novo cromossomo
```

`ag.py`
```python
def populacao_inicial(tam_pop, rng, inst, inicial="aleatoria") -> list[Cromossomo]   # ou "construtivo"
def algoritmo_genetico(tam_pop=200, geracoes=300, taxa_cruz=0.9, taxa_mut=None,
                       k=3, elite=2, cruzamento="um_ponto", inicial="aleatoria",
                       semente=42, inst=PADRAO) -> Resultado     # taxa_mut=None: 1 / genes livres
```
O laço é o do projeto exemplo, com três diferenças: conta as avaliações, guarda a geração do primeiro válido e avalia cada indivíduo uma vez só por geração (guarda a penalidade junto, em vez de recalcular).

`experimentos.py`
```python
CONFIGURACOES: dict[str, dict]      # nome da configuração -> método e parâmetros
def rodar_execucao(nome, semente, inst=PADRAO) -> dict          # uma linha da tabela
def bateria(nome, sementes=range(10), inst=PADRAO, processos=1) -> list[dict]
def resumir(linhas) -> dict         # média, melhor, pior, desvio, válidos em 10, tempo médio
def salvar_csv(linhas, arquivo) -> None
```

`desenho.py` e `graficos.py`
```python
def desenhar_mapa(mapa, ax=None, caminho=None, titulo="") -> Axes
def desenhar_lado_a_lado(mapas, titulos, arquivo=None) -> Figure
def grafico_convergencia(historicos, referencias, arquivo=None) -> Figure
def grafico_parametro(resumos, rotulo_eixo, arquivo=None) -> Figure
def grafico_desejaveis(resumos, arquivo=None) -> Figure         # S1 a S5 por método
```

### 3.5 Reprodutibilidade

- Toda função que sorteia recebe um `rng` (`random.Random(semente)`), como no projeto exemplo. **Proibido** `random.seed(...)`, `random.random()` solto e `np.random.*` global em qualquer módulo.
- Uma execução cria o próprio `random.Random(semente)` logo no começo e passa adiante. Execuções não compartilham gerador, então o resultado não muda se a bateria rodar em um processo ou em oito, nem com a ordem das configurações.
- Não sortear a partir de `set` nem depender da ordem de um `set`: converter para lista ordenada antes. A ordem dos vizinhos em `Mapa.viz` é fixa.
- Teste que cobra isso: a mesma semente rodada duas vezes devolve o mesmo cromossomo e o mesmo histórico.
- `random.Random` no lugar de `np.random.default_rng` porque é o que o laboratório e o exemplo usam, e as contas são sobre listas de inteiros.

### 3.6 O produto final e como ele "roda do início ao fim"

O produto é `Projeto_Final_Gerador_AG.ipynb` mais a pasta `gerador/`, entregues num `.zip`. O notebook importa os módulos e segue a ordem do projeto exemplo:

1. O problema e a instância (desenho da grade vazia com as zonas e os fixos).
2. Cromossomo e avaliação, com os testes rápidos à vista (os `assert`).
3. Soluções sem IA: construtivo, busca aleatória, construtivo rerolado, com os números.
4. Algoritmo genético: uma execução, a curva e o mapa.
5. Experimentos E0 a E2, tabelas e gráficos.
6. Mapas lado a lado.

Regras para rodar sem erro num kernel reiniciado:

- Uma constante no topo, `MODO_RAPIDO`. Com `True`, usa 2 sementes e orçamento pequeno, e o notebook inteiro roda em menos de 2 minutos: é o teste de fumaça de todo dia. Com `False`, roda a bateria completa. **O arquivo entregue está com `False` e já executado; os números dos slides vêm só dele.**
- Cada seção demorada tem uma célula de texto com o tempo esperado, como no exemplo.
- A bateria grava `resultados/*.csv` e `figuras/*.png`; os slides usam esses arquivos, nunca um número digitado à mão.
- O baseline é chamado no mesmo notebook, antes do AG.

**Plano B se o professor exigir arquivo único:** montar `entrega/projeto_unico.py` concatenando os módulos na ordem da tabela 3.2. Para isso continuar possível, os módulos não usam `import ... as`, não repetem nome de função entre arquivos e só importam uns dos outros na forma `from gerador.x import y`.

---

## 4. Orçamento de tempo de execução

### 4.1 Custo de uma avaliação

O que foi medido de verdade (17/11, no computador onde este plano foi escrito, processador de 20 núcleos lógicos, Python 3.10): uma busca em largura genérica sobre estados `(célula, nível)` numa grade 12 × 8 leva **0,25 ms** quando o mapa inteiro é alcançável (364 estados) e menos de 0,01 ms num mapa sorteado, porque quase nada é alcançável. A medição usou um teste descartável, que não é código do projeto e não está no repositório.

O resto é estimativa:

| Parte da avaliação | Mapa válido e cheio | Mapa sorteado |
|---|---|---|
| Ler o cromossomo (`decodificar`) | ~0,10 ms | ~0,10 ms |
| Simulação de inventário (até 4 rodadas) | ~0,10 ms | ~0,01 ms |
| Caminho crítico | 0,25 ms (medido) | ~0,01 ms |
| Contagens de H e S | ~0,05 ms | ~0,05 ms |
| **Total** | **~0,5 ms** | **~0,2 ms** |

Para planejar: **0,55 ms por indivíduo** numa máquina rápida (avaliação mais seleção, cruzamento e mutação) e **1,65 ms** numa máquina três vezes mais lenta. **Primeira tarefa de medição, em 23/11: cronometrar 1000 avaliações de mapas do construtivo em cada computador da equipe e refazer a tabela abaixo.**

### 4.2 Tempo de uma execução e da bateria

| | Máquina rápida (0,55 ms) | Máquina lenta (1,65 ms) |
|---|---|---|
| Uma execução de 60 200 avaliações | ~33 s | ~100 s |
| Bateria mínima: 100 execuções (E0 + E1 + E2) | ~55 min | ~2 h 45 min |
| Bateria com os opcionais: 130 execuções | ~1 h 10 min | ~3 h 35 min |
| Bateria mínima com 8 processos | ~8 min | — |
| Bateria mínima com orçamento de 30 100 avaliações | ~28 min | ~1 h 25 min |

Conclusão: **a bateria completa não cabe numa aula de 50 minutos em máquina comum.** Ela roda em casa, na máquina mais rápida da equipe, e em sala usa-se o modo rápido.

### 4.3 Como fixar o orçamento (ensaio de convergência, 26 a 30/11)

1. Rodar o AG puro com 200 × 300 em 3 sementes e olhar a curva.
2. Se a curva fica plana antes da geração 150, cortar para 150 gerações (metade do tempo).
3. Se ainda está caindo na geração 300, não aumentar o orçamento sem antes tentar as alavancas da seção 10 (inicialização enviesada, semeada).
4. O orçamento escolhido vale para todos os métodos e é registrado no Diário com a curva que o justificou.

### 4.4 Cortes e otimizações, em ordem

| Ordem | Medida | Ganho | Custo ou risco |
|---|---|---|---|
| 1 | Rodar as sementes em paralelo (`processos` em `bateria`) | 4 a 8 vezes | No Windows, as funções precisam estar em módulos (já estão). Padrão `processos=1`; os números não mudam com o valor |
| 2 | Cortar gerações pelo ensaio de convergência | até 2 vezes | Nenhum, se a curva estiver plana |
| 3 | Tirar os experimentos opcionais (E3, E4) | 30 execuções | Menos material; o mínimo da disciplina continua cumprido |
| 4 | População 100 em vez de 200 | 2 vezes | Menos diversidade; anotar |
| 5 | Guardar a nota de cromossomos repetidos | 10 a 30% no fim da execução | O contador conta indivíduos gerados, não avaliações únicas, igual para todos os métodos |

Descartados: avaliar só o que mudou (as buscas são globais: mudar uma ligação muda tudo) e vetorizar a busca em largura com NumPy (ganho pequeno numa grade de 96 células, e código mais difícil de explicar).

### 4.5 O que roda em casa antes de 03/12

- 26 a 30/11: primeira execução completa do AG puro e o ensaio de convergência.
- 01/12 à noite ou 02/12: bateria completa na máquina mais rápida, com o notebook em `MODO_RAPIDO = False`. Código congelado em 02/12 às 23h.
- 03/12 em sala: nada de execução longa. Só conferir que o notebook abre e que o modo rápido passa.

---

## 5. Plano de testes

Testes como os `assert` do laboratório: funções `test_...` com `assert`, um arquivo por módulo, executados com `python -m pytest`. Os mais ilustrativos também aparecem numa célula do notebook.

### 5.1 Mapas pequenos de resposta conhecida

Feitos com `instancia_teste` (3 zonas de 1 coluna, 3 linhas: 9 células; ou 2 colunas por zona quando o caminho precisa ser maior) e montados com as funções `definir_*`. Desenhar cada um no papel em 18/11, com a resposta esperada, e colar a foto no Diário.

| Mapa | Como é | Resposta esperada |
|---|---|---|
| M1 perfeito | Tudo ligado; cartões antes das portas | H = 0; `alcançadas` = todas as ocupadas; caminho crítico com o comprimento contado à mão |
| M2 deadlock de cartão | O cartão 2 atrás de uma porta de nível 2 | H1 = 1; H2 = número de células depois da porta, contado à mão; nível final 1 |
| M3 ilha | Uma célula ocupada sem nenhuma ligação | H1 = 0; H2 = 1 |
| M4 contraexemplo da monotonicidade | Na Zona Leve, uma sala atrás de uma porta de nível 3; o jogador busca o cartão 3 na Zona Pesada e volta | H = 0 pela simulação (a fórmula antiga proibia este mapa). Quita a pendência "A FAZER" do registro de IA de 17/11 |
| M5 cartão num ramo | O cartão 2 no fim de um ramo de 2 células fora do trajeto | Passos repetidos = 2, contados à mão |
| M6 porta sem uso | Porta de nível 1 que não fica no caminho | `d_1 = 0`, S3 recebe 6 pontos pelo cartão 1 |

### 5.2 Validação e avaliação

- Um teste por restrição: para cada H e cada S, um mapa pequeno que viola **só aquela** e o valor esperado em `detalhes`, com as outras em zero. São 12 testes.
- Teto: um mapa com 30 becos devolve S1 = 19.
- Sem caminho crítico: S2 a S5 = 19.
- A conta do peso: `assert 5 * regras.teto_s < regras.peso_h`.
- As duas buscas concordam: em 2000 cromossomos sorteados e 500 do construtivo, `saída em alcançadas` é igual a `caminho_critico(mapa) is not None`.
- O caminho crítico é um passeio legal: começa no início, termina na saída, cada passo usa uma ligação existente e o nível no momento é suficiente.
- Leitura do mapa: ligação com gene 1 entre uma célula ocupada e uma vazia não aparece em `viz`; `viz` é simétrica (se j está em `viz[i]`, i está em `viz[j]` com o mesmo nível).
- Pior caso de cabeça, como o `avaliar([0] * 32) == 196` do exemplo: o `cromossomo_base` tem H e S conhecidos, calculados à mão.

### 5.3 Operadores e laço

| Teste | O que afirma |
|---|---|
| Torneio com k = tamanho da população | Devolve sempre o melhor |
| Torneio devolve cópia | Alterar o resultado não altera a população |
| Cruzamento de um ponto só troca genes | Em cada posição, os dois filhos têm exatamente os dois valores dos pais; os tamanhos não mudam |
| Cruzamento de pais iguais | Filhos iguais aos pais |
| Cruzamento por zona | Cada zona do filho é idêntica à zona de um dos pais, incluindo os cartões dela |
| **Fechamento do cruzamento por zona** | Dois pais do construtivo (H = 0) geram filhos com H = 0, em 1000 pares |
| Mutação com taxa 0 | Não muda nada |
| Mutação com taxa 1 | Muda todos os 281 genes livres e nenhum dos 106 fixos |
| Mutação não altera o original | O cromossomo de entrada continua igual |
| Domínios | Depois de 1000 aplicações de cada operador, `dominios_ok` continua verdadeiro |
| Elitismo | Com `elite ≥ 1`, o histórico nunca piora de uma geração para a outra |
| Contador | `n_avaliacoes == tam_pop × (geracoes + 1)` |
| Reprodutibilidade | A mesma semente duas vezes dá resultado idêntico; sementes diferentes dão resultados diferentes |

### 5.4 Baselines e experimentos

- O construtivo devolve H = 0 em 1000 sementes: a frase "garante a jogabilidade" vira fato verificado.
- A busca aleatória e o rerolado avaliam exatamente `n_avaliacoes` mapas e devolvem o melhor que viram.
- `gerar_aleatorio` respeita os domínios e os fixos.
- `bateria` com `processos=1` e com `processos=4` grava os mesmos números.
- O notebook em modo rápido roda do início ao fim com `jupyter nbconvert --execute`.

---

## 6. Plano de experimentos

### 6.1 Configurações

Sementes 0 a 9 em tudo. O mesmo número de avaliações para todos os métodos que buscam.

**E0 – Comparação principal** (responde "precisava de IA?")

| Método | O que é | Execuções |
|---|---|---|
| Construtivo | Um mapa por semente | 10 (custo desprezível) |
| Busca aleatória | Melhor de N mapas sorteados | 10 |
| Construtivo rerolado | Melhor de N mapas do construtivo | 10 |
| AG puro (principal) | População inicial sorteada | 10 |
| AG semeado | População inicial do construtivo | 10 |

**E1 – Parâmetro: taxa de mutação**, sobre o AG puro, em genes mutados por filho: 0 · 0,5 · 1 (padrão) · 2 · 5. São 40 execuções novas.

**E2 – Decisão: tipo de cruzamento**, um ponto × por zona, no AG puro e no semeado. São 20 execuções novas.

E0 + E1 + E2 somam 100 execuções com orçamento e já variam três coisas (população inicial, taxa de mutação, tipo de cruzamento), acima do mínimo de duas.

**Opcionais, só com o mínimo pronto:** E3 população 100 e 400 com o mesmo total de avaliações, e sem elitismo (30 execuções). E4 mutação de porta (sobe ou desce um nível). E5 grade 20 × 12 com o AG padrão, para falar de escala nas limitações.

### 6.2 O que cada execução grava

Uma linha por execução em `resultados/execucoes.csv`: configuração, semente, penalidade, obrigatórias, desejáveis, H1 a H7, S1 a S5, válido (obrigatórias = 0), geração do primeiro válido, número de avaliações, tempo. O histórico de cada execução vai para `resultados/historicos.csv`, e o melhor cromossomo para `resultados/melhores.json`, para poder redesenhar o mapa sem rodar de novo.

### 6.3 Tabela final e gráficos

**Tabela final** (uma linha por método do E0, mesma métrica), a que vai para o Diário e para o slide:

| Método | Válidos em 10 | Obrigatórias (média) | Desejáveis: média (melhor – pior) | Penalidade (média) | Tempo por execução |
|---|---|---|---|---|---|

**Tabela de parâmetros** (E1 e E2), no formato da Tabela 15 do exemplo: configuração, válidos em 10, média de obrigatórias, média de desejáveis.

**Gráficos, todos com fundo branco:**

1. Convergência: média da melhor penalidade por geração nas 10 sementes, com a faixa do mínimo ao máximo, eixo vertical em escala logarítmica como no exemplo, e três linhas horizontais de referência (construtivo, construtivo rerolado, busca aleatória). AG puro e AG semeado no mesmo gráfico.
2. Desejáveis por método: barras empilhadas de S1 a S5. Mostra **o que** o AG melhorou, não só quanto.
3. Taxa de mutação × média das desejáveis, com a variação entre sementes.
4. Mapas lado a lado: um mapa do construtivo (a semente de resultado mediano, não a pior) e o melhor do AG, com o caminho crítico, as armadilhas e os cartões desenhados.

### 6.4 Por que a comparação com a busca aleatória é justa

- Mesmo número de avaliações, contado por contador: `tam_pop × (gerações + 1)`.
- Mesma função de avaliação e mesmas sementes.
- Mesma distribuição de sorteio da população inicial do AG (`gerar_aleatorio`).
- Fica com o melhor mapa visto, como o AG com elitismo.
- O tempo aparece ao lado: a busca aleatória avalia mapas inválidos, que são mais rápidos.

Assim a diferença vem da seleção, do cruzamento e da mutação, e não de "tentar mais". O mesmo raciocínio vale para o par construtivo rerolado × AG semeado, que partem dos mesmos mapas.

### 6.5 Cuidados na leitura

- Com 10 sementes, relatar média, melhor e pior, e a contagem "em quantas das 10". Não escrever "significativamente melhor" sem teste estatístico.
- Se o construtivo rerolado empatar com o AG ou ganhar dele, o resultado vai para a tabela como saiu. A análise crítica vale 1,0 ponto e um resultado negativo bem explicado conta a favor.
- Não trocar alvos, pesos nem tetos depois de ver os resultados (D9).

---

## 7. Cronograma por data e por pessoa

Papéis: **A** núcleo (instância, representação, validação, depois experimentos) · **B** sem IA (aleatório, construtivo, desenho, depois operadores) · **C** AG (avaliação, depois laço, gráficos e notebook).

### 7.1 Encontro a encontro

| Data | A | B | C | Pronto ao fim |
|---|---|---|---|---|
| **17/11** ter, 3 aulas · CP1 | Ficha e pitch | Ficha e pitch | Ficha e pitch | CP1. Em casa: cada um lê este plano e anota discordâncias |
| **18/11** qua, 2 aulas | Fichamento de Pereira et al. (2021). Depois: cria o esqueleto do repositório e o `config.py` | Fichamento de Shaker et al. (2016). Depois: passos do construtivo no Diário | Fichamento de Togelius et al. (2011). Depois: desenha no papel os mapas M1 a M6 com a resposta esperada | 3 fichamentos; métrica e baseline atualizados no Diário; perguntas ao professor respondidas; parâmetros provisórios escolhidos |
| *em casa até 22/11* | `representacao.py` com testes, **na `main` até 20/11**: todo o resto depende dele | `aleatorio.py`, `desenhar_mapa` e começo do construtivo | H3 a H7 e S1, que só dependem do `Mapa` | Marco M0: dá para montar, ler e desenhar um mapa |
| **23/11** seg, 3 aulas | `validacao.py`: simulação e caminho crítico, com M1 a M5 | Termina o construtivo e o teste das 1000 sementes; `busca_aleatoria` e `construtivo_rerolado` | H1, H2 e S1 a S5; junta tudo em `avaliar` | `avaliar` funciona num mapa do construtivo; tempo de 1000 avaliações medido |
| **24/11** ter, 3 aulas · CP2 e CP3 | Aula 1: roda os três baselines em 10 sementes. Aula 3: esqueleto de `experimentos.py` | Aula 1: imagem de um mapa do construtivo. Aula 3: esqueleto de `operadores.py` | Aula 1: números na tabela do Diário. Aula 3: esqueleto de `ag.py` e `graficos.py` | **CP2:** baseline medido e anotado. Aula 2, todos: oficina de IA e Quadro de Modelagem. **CP3:** Quadro, esqueleto, Ponto de Retomada. **Escopo e alvos congelados** |
| **25/11** qua, 2 aulas (extra) | `rodar_execucao` e `bateria` com o contador | Torneio, cruzamento de um ponto e mutação, com testes (na primeira aula) | Laço do AG: escreve contra as assinaturas na primeira aula, integra na segunda | O AG roda uma semente com poucas gerações, sem erro |
| *em casa, 26 a 30/11* | Ensaio de convergência (3 sementes); decide o orçamento | `cruzamento_por_zona` e o teste de fechamento; opção `inicial="construtivo"` junto com C | Primeira execução completa; curva; notebook em modo rápido | Decisão sobre as alavancas da seção 10, se o AG puro não chegar a válidos |
| **01/12** ter, 3 aulas | Lê o Ponto de Retomada em voz alta. Integra e roda E0 em modo rápido; deixa a bateria pronta para rodar | Mapas lado a lado; começa os slides das partes 1 a 3 | Notebook do início ao fim; gráfico de convergência | Primeira execução completa anotada no Diário ao lado do baseline; esqueleto dos slides |
| *em casa, 01 e 02/12* | Roda a bateria completa; grava os CSV | Slides das partes 1 a 3 e 7 | Figuras finais; slides das partes 4 e 5 | **Código congelado em 02/12 às 23h**; notebook executado e salvo |
| **03/12** qui, 3 aulas · CP4 | Tabela final e respostas das perguntas de análise no Diário | Slides fechados; exporta os PDFs | Confere o notebook entregue; slide de limitações | Aula 1: tabela, gráfico e análise. Aula 2: ensaio cronometrado e revisão do professor. Aula 3: correções e **envio no SIGAA com 15 minutos de folga** |
| *em casa, 04 a 06/12* | | | | Dois ensaios cronometrados. Sabatina cruzada: cada um explica um módulo que não escreveu |
| **07/12** seg | | | | Apresentação. Não há dia reserva |

A dependência crítica é o `representacao.py` na `main` até 20/11. Se atrasar, B e C trabalham contra as assinaturas da seção 3.4 com um `Mapa` montado à mão.

### 7.2 O que precisa estar pronto em cada checkpoint

| Checkpoint | O professor verifica | Evidência |
|---|---|---|
| CP1 (17/11) | Ficha aprovada | Ficha no Diário |
| CP2 (24/11, aula 1) | Fichamentos; métrica definida; baseline rodando com número anotado | 3 fichamentos; seção 4 do Diário; tabela de resultados com o construtivo (10 sementes), a busca aleatória e o rerolado; imagem de um mapa |
| CP3 (24/11, aula 3) | Quadro completo e coerente com a Ficha; registro de IA com entrada completa; esqueleto com as funções nomeadas; Ponto de Retomada | Seção 2 deste plano transcrita no Diário; `operadores.py`, `ag.py` e `experimentos.py` com assinaturas e `raise NotImplementedError`; tag `cp3` |
| CP4 (03/12) | Tabela baseline × IA com repetições; 2 parâmetros variados; slides nas 7 partes; ensaio em 12 min; entrega | CSV, tabela final, tabela de parâmetros, 4 figuras, slides em PDF, Diário em PDF, `.zip` do código |

A Ficha precisa de dois ajustes para ficar coerente com o Quadro: a conta do espaço de busca (281 genes livres, cerca de 10¹⁷⁷ mapas) e a lista de restrições do escopo mínimo.

### 7.3 O que pode ser adiantado em casa

Tudo que está em itálico na tabela 7.1. O que **não** pode ficar só para a sala: o `representacao.py` (até 20/11), a primeira execução completa (até 30/11) e a bateria final (até 02/12).

### 7.4 O Diário de Bordo em cada data

| Data | O que entra |
|---|---|
| 17/11 | Registro de IA: esta conversa (texto abaixo). Ficha revisada depois do pitch |
| 18/11 | 3 fichamentos; seção 4 (métrica e baseline) com as novas H e S e os passos do construtivo; fotos dos mapas M1 a M6; respostas do professor; Ponto de Retomada |
| 23/11 | Tempo medido de 1000 avaliações; primeiros números do construtivo; Ponto de Retomada |
| 24/11 | Tabela de resultados com os baselines (CP2); Quadro de Modelagem final (CP3); registro de IA da oficina, com o que a equipe rejeitou; parâmetros congelados; **Ponto de Retomada** nos últimos 10 minutos |
| 25/11 | Ponto de Retomada; resultado dos testes dos operadores |
| 26 a 30/11 | Curva do ensaio de convergência e o orçamento escolhido; qualquer alavanca usada e o motivo |
| 01/12 | Primeira execução completa na tabela, ao lado do baseline; Ponto de Retomada |
| 03/12 | Tabela final; tabela de parâmetros; gráficos; respostas das 5 perguntas de análise; registro de IA completo; exportar em PDF |

**Texto sugerido para o registro de IA de 17/11** (as duas últimas colunas são da equipe):

| Data | Objetivo | Prompt (resumo) | Resposta (resumo) | Aceitamos / rejeitamos | Como verificamos |
|---|---|---|---|---|---|
| 17/11 | Planejar o projeto sem implementar | "Planeje o trabalho: critique a modelagem, proponha arquitetura, testes, experimentos e cronograma. Não escreva código." | Apontou 4 mapas ruins que tirariam nota boa; mostrou que o peso 100 não fechava sem teto nas desejáveis; propôs reordenar o cromossomo por colunas, 3 restrições garantidas pela representação, caminho crítico por busca em largura em (célula, nível), AG semeado e construtivo rerolado como comparação. Mediu o tempo de uma busca em largura com um teste descartável | *(a equipe preenche: o que aceitou, o que rejeitou e por quê)* | *(sugestões: refazer à mão a conta 5 × 19 = 95; contar os 281 genes livres; medir 1000 avaliações no próprio código; rodar o teste de fechamento do cruzamento por zona)* |

---

## 8. Fluxo de trabalho no Git

**Branches.** A `main` sempre roda: testes passando e notebook em modo rápido sem erro. Ninguém faz commit direto nela (proteger a branch no GitHub, exigindo 1 aprovação). Cada tarefa tem uma branch curta: `feat/validacao-simulacao`, `fix/mutacao-genes-fixos`, `exp/bateria-e1`, `docs/quadro`.

**Pull requests.** Pequenos (até cerca de 150 linhas), um por função ou grupo de funções, abertos no mesmo dia. Revisão em rodízio: A revisa B, B revisa C, C revisa A; depois de 24/11 inverte, para que todos tenham lido tudo. Checklist do revisor:

- os testes passam;
- a assinatura é a da seção 3.4, ou o plano foi atualizado no mesmo PR;
- não há `random` global;
- o revisor escreve, no comentário de aprovação, uma frase explicando o que a função faz. Se não consegue, pede explicação antes de aprovar. É assim que "todos explicam tudo" deixa de ser promessa.

**Commits.** Em português, no formato `tipo(módulo): o que mudou`: `feat(validacao): simulação de inventário em rodadas`, `test(operadores): mutação com taxa 0`, `fix(avaliacao): teto de S4`. Tipos: `feat`, `fix`, `test`, `docs`, `exp`, `refactor`.

**Tags.** `cp2`, `cp3`, `v1-primeira-execucao`, `entrega`. Qualquer número citado no Diário aponta para a tag ou o commit que o produziu.

**Notebook sem conflito.**

- Um dono só (C). Os outros não editam o `.ipynb`; quem precisa de algo nele pede ou muda o módulo.
- O notebook não tem lógica, só chamadas. O código que muda mora nos `.py`, que o Git compara bem.
- Antes de cada commit, limpar as saídas (Kernel → Restart & Clear Output, ou `nbstripout` instalado como filtro do Git). A versão **com** saídas é gravada uma vez, na tag `entrega`.
- Para experimentar, cada um usa um notebook de rascunho fora do Git (`rascunho_*.ipynb` no `.gitignore`).

**`requirements.txt`.** `numpy`, `matplotlib`, `pandas`, `notebook`, `pytest` e, opcional, `nbstripout`. O núcleo (`gerador/` menos `graficos.py` e `desenho.py`) só usa a biblioteca padrão. Anotar no README a versão do Python usada (3.10 no computador onde o plano foi feito).

**`.gitignore`.** `.venv/`, `__pycache__/`, `.ipynb_checkpoints/`, `.pytest_cache/`, `rascunho_*.ipynb`, `*.tmp`, `.claude/`, arquivos do sistema e do editor.

**O que nunca subir.**

- O material do professor (roteiro, projeto exemplo, slides): não é da equipe e o repositório pode ser público.
- O Diário de Bordo em edição: tem nomes e fica no documento compartilhado. Decidir no fim se o PDF final entra no repositório.
- A pasta `.venv`, dados de outros temas (a amostra da OpenF1), chaves ou tokens de qualquer serviço.
- Resultados gerados em modo rápido dentro de `resultados/`: só a bateria completa grava ali.

Opcional, 10 minutos: uma ação do GitHub que roda `pytest` a cada PR.

---

## 9. Roteiro da apresentação (12 minutos)

Os colchetes são números que o código vai produzir. Sugestão de divisão das falas: B nas partes 1, 2 e 7; A nas partes 3 e 4; C nas partes 5 e 6. Todos respondem perguntas sobre tudo.

| Parte | Tempo | O que mostrar | Números e imagens |
|---|---|---|---|
| 1. Problema | 1,5 min | Mapas gerados por semente podem travar o jogador ou ser chatos. Mostrar um mapa com deadlock (cartão atrás da própria porta) | Imagem do mapa M2 ampliado; o tamanho do espaço: 281 genes, cerca de 10¹⁷⁷ mapas |
| 2. Solução sem IA | 1,5 min | O gerador construtivo em 4 passos e um mapa dele, com o caminho crítico passando por armadilhas e os becos destacados. "Garante jogar, não garante qualidade" | Válidos [10 de 10]; desejáveis média [x]; rerolado com N avaliações [y]; busca aleatória: válidos [0 de 10] |
| 3. Por que AG | 1 min | Pergunta 2 do guia de decisão. O que Pereira et al. fizeram e o que Shaker et al. descrevem; o que é nosso | Tabela de 3 linhas da seção 2.5 |
| 4. Modelagem | 3 min | (a) Desenho do cromossomo: uma célula ampliada com os 4 genes e a ordem por colunas. (b) Restrições garantidas, H1 a H7 e S1 a S5 numa tabela só. (c) A simulação de inventário animada em 3 quadros. (d) A penalidade e a conta 5 × 19 = 95 < 100. (e) Operadores: o corte vertical desenhado sobre o mapa | Figura do cromossomo; figura do corte; uma linha: torneio 3, cruzamento 0,9, mutação 1/281, elite 2, 200 × 300 |
| 5. Resultados | 3 min | Tabela final do E0; gráfico de convergência com as linhas de referência; mapas lado a lado; tabela de mutação e de cruzamento | Válidos em 10; desejáveis média (melhor – pior); geração do primeiro válido; tempo |
| 6. Limitações | 1 min | Respostas das perguntas de análise: variação entre sementes; quando o rerolado basta; um caminho mínimo entre vários; pesos iguais nas desejáveis; grade pequena; nenhum teste com jogadores (Pereira et al. fizeram) | Um mapa ruim do próprio AG (a pior semente) |
| 7. IA generativa | 1 min | Um exemplo concreto: a IA apontou que um corredor reto vazio tirava nota boa; a equipe conferiu com um teste e criou H5 e H6. E **um exemplo de algo rejeitado** | A linha do registro de IA e o teste que comprovou |

Demonstração ao vivo (opcional, até 1 minuto, dentro da parte 5): gerar um mapa com uma semente dita pela plateia, em modo rápido.

### Perguntas difíceis e a resposta esperada

| Pergunta | Resposta esperada |
|---|---|
| Por que não só o gerador construtivo? | Ele garante a jogabilidade ([1000 de 1000] no teste), mas não escolhe: média de [x] nas desejáveis. Sortear de novo N vezes chega a [y]; o AG com as mesmas N avaliações chega a [z]. Se [z] não for menor que [y], dizer isso e explicar em que caso o AG ainda vale |
| Por que o peso é 100? | Cada desejável tem teto de 19; são 5; a soma máxima é 95. Com 100, uma violação obrigatória custa mais do que todas as desejáveis juntas. Tem um `assert` no código |
| O que acontece se uma regra da zona for impossível, por exemplo exigir 40 armadilhas em 32 células? | O AG não trava e não mente: H6 nunca zera, a penalidade para em [800 + ...] e o relatório de `detalhes` aponta qual restrição ficou. O construtivo, nesse caso, precisa parar com erro claro em vez de ficar em laço |
| Por que a porta é gene da ligação? | Uma porta fica entre duas células. Guardada nas células ela existiria duas vezes, e os dois lados poderiam discordar |
| Por que simular o inventário em vez de uma regra do tipo "porta de nível maior fica mais longe"? | Porque a regra proíbe mapas válidos. Mapa M4: uma sala de nível 3 na Zona Leve, que o jogador abre voltando com o cartão 3 |
| Por que torneio e não roleta? | As penalidades iniciais são milhares; as aptidões ficam todas perto de zero e a roleta vira sorteio. O torneio só usa a ordem |
| O cruzamento de um ponto não quebra o mapa? | Quebraria com os genes na ordem "células, depois ligações". Por isso a ordem é por colunas, com os 4 genes de cada célula juntos: o corte é uma linha vertical. E o cruzamento por zona nunca quebra: há um teste com 1000 pares |
| Começar o AG com mapas do construtivo não é trapaça? | É outra pergunta. O AG puro responde "o AG resolve sozinho?". O semeado responde "partindo dos mesmos mapas, os operadores fazem melhor do que sortear de novo?". Os dois estão na tabela, com o mesmo número de avaliações |
| A comparação com a busca aleatória é justa? | Mesmas avaliações (contadas), mesma função, mesmas sementes, mesma distribuição de sorteio, e ela fica com o melhor mapa visto |
| O que significa o gene da posição 137? | Saber fazer a conta ao vivo: descontar o deslocamento da zona, dividir por 4 para achar a célula; o resto diz o campo. Posição 137: Zona Pesada (130 a 257), 137 − 130 = 7, célula 32 + 1 = 33, campo 3: armadilha da célula 33 (linha 1, coluna 4) |
| Como sabem que a avaliação está certa? | Mapas pequenos com resposta feita à mão; um teste por restrição; e duas buscas independentes que precisam concordar em milhares de mapas |
| O caminho crítico é único? | Não. Usamos um caminho mínimo com desempate fixo. S2 e S4 poderiam ser diferentes em outro caminho do mesmo tamanho: é uma limitação |
| Busca em largura é a IA do projeto? | Não. A técnica principal é o AG; a busca em largura é apoio dentro da avaliação, o que o roteiro permite |
| O que a IA generativa escreveu e o que vocês mudaram? | Apontar no registro de IA uma sugestão aceita, uma rejeitada e como cada uma foi verificada |

---

## 10. Riscos e plano B

**Escopo mínimo, congela em 24/11:** grade 12 × 8, 3 zonas, 2 checkpoints, cartões hierárquicos; H1 a H7 e S1 a S5; construtivo, busca aleatória e rerolado; AG com torneio, um ponto, mutação e elitismo; AG semeado; E0, E1 e E2; imagem do mapa; notebook rodando.

**Desejável, só entra com o gatilho cumprido:**

| Item | Gatilho para começar | Prazo-limite |
|---|---|---|
| Formato da peça no desenho (ponta, reto, curva, T, cruz) | Mínimo rodando | 01/12 |
| E3 (população e elitismo) | Bateria mínima pronta | 02/12 |
| Salas especiais com nome por zona e orientação da porta | E0 a E2 prontos em 30/11 | 30/11 |
| Armadilhas com regra (nunca vizinhas, nunca ao lado de checkpoint) | idem | 30/11 |
| Grade 20 × 12 (E5) | idem; é só criar outra instância | 02/12 |
| Operador de reparo; cruzamento 2D; mutação de porta | Só se sobrar uma aula inteira | 30/11 |

Nada do desejável começa depois de 30/11.

**Riscos por fase:**

| Fase | Risco | Sinal | Plano B | Critério de corte |
|---|---|---|---|---|
| 18 a 23/11 | `representacao.py` atrasa e trava todos | Não está na `main` em 20/11 | Os três fazem juntos em 23/11, na primeira aula; B e C seguem com `Mapa` montado à mão | — |
| 23 e 24/11 | Baseline sem número para o CP2 | `avaliar` incompleto no fim de 23/11 | Medir só com as H e com S1 e S2, e dizer isso; completar S3 a S5 em 25/11 | CP2 exige um número, não o número final |
| 23 e 24/11 | O construtivo viola alguma H | O teste das 1000 sementes falha | Corrigir o construtivo, nunca afrouxar a restrição | — |
| 24/11 | A modelagem cresce na oficina | Restrição nova surgindo | Vai para a lista do desejável, não para o código | Escopo congelado |
| 25 a 30/11 | **O AG puro não chega a mapas válidos** | Menos de 8 válidos em 10 no ensaio | Alavancas, uma por vez e registrando: (1) sorteio inicial enviesado, com mais passagens abertas e menos portas; (2) aumentar as gerações, se o tempo permitir; (3) grade 9 × 6; (4) reparo. O AG semeado já cobre a comparação principal | Em 30/11, se nada resolveu: o AG semeado vira a configuração principal e o AG puro vai para a análise como caso de falha, com a curva |
| 25 a 30/11 | O AG chega a válido, mas não melhora as desejáveis | Curva plana logo depois do primeiro válido | Conferir a mutação (taxa efetiva) e a diversidade (indivíduos repetidos na população); testar 2 genes por filho | — |
| 26 a 30/11 | Ninguém roda nada na semana sem aula | Nenhum commit até 28/11 | Chamada de 30 minutos em 28/11 para a primeira execução, juntos | — |
| 01 e 02/12 | A bateria não cabe no tempo | Mais de 3 horas na máquina mais rápida | Ordem de cortes da seção 4.4 | O mínimo da disciplina: 10 sementes, 2 parâmetros variados |
| 01 e 02/12 | O rerolado ganha do AG | Tabela do E0 | Não esconder. Mostrar o gráfico de S1 a S5 por método (onde cada um é melhor) e discutir custo × benefício na parte 6 | — |
| 03/12 | Erro descoberto no dia da entrega | Teste falhando em sala | Voltar para a tag `v1` e entregar aquela versão; só slides e Diário mudam em 03/12 | Código congelado em 02/12 |
| 03/12 | O SIGAA falha ou o arquivo é grande demais | — | `.zip` sem `.venv` nem caches; enviar com 15 minutos de folga; avisar o professor na hora | — |
| 07/12 | Um integrante não sabe explicar uma parte | Sabatina de 04 a 06/12 | Cada um explica em voz alta um módulo que não escreveu; quem trava refaz à mão um teste daquele módulo | — |

**Último degrau, se tudo atrasar:** grade 9 × 6; só S1 e S2 como desejáveis; cruzamento de um ponto; variar taxa de mutação e tamanho da população. Ainda cumpre todos os mínimos do roteiro.

---

## 11. Decisões que a equipe precisa tomar

1. **Quem é A, B e C** (seção 3.2) e quem cuida do Diário em cada encontro. Hoje.
2. **Perguntar ao professor em 18/11:** (a) um `.zip` com módulos `.py` e um notebook que os importa cumpre "baseline no mesmo arquivo"? (b) a bateria pode rodar em casa, com o notebook entregue já executado? (c) o AG semeado com o construtivo é aceito como uma das configurações?
3. **Posições fixas:** início, saída e a linha de cada checkpoint (proposta na seção 2.1). Até 18/11, porque o `config.py` depende disso.
4. **Parâmetros das restrições:** ocupação mínima, faixas de salas especiais e de armadilhas, alvo de becos, K, alvo de passos repetidos, faixa de comprimento. Provisórios em 18/11, congelados em 24/11.
5. **Cartão só em sala** (H3) e **sala especial com uma entrada só** (H7): aceitar ou tirar. São as duas regras que eu acrescentei além do que vocês pediram.
6. **Orçamento:** 200 × 300 ou outro, decidido pelo ensaio de convergência até 30/11.
7. **Onde o Diário fica** (documento compartilhado) e se o PDF final entra no repositório.
8. **Repositório público ou privado**, e proteção da `main`.
9. **Divisão das falas** da apresentação. Até 01/12.

## 12. Primeiras 3 tarefas de amanhã (18/11)

1. **Cada um ficha o seu trabalho** nos primeiros 30 minutos (A: Pereira et al., 2021; B: Shaker et al., 2016; C: Togelius et al., 2011), com as próprias palavras, e anota o que confirma ou contradiz a seção 2.5.
2. **Fechar as pendências que travam o código:** fazer as três perguntas ao professor (item 2 acima), decidir as posições fixas e os parâmetros provisórios (itens 3 e 4), e atualizar no Diário a seção 4 e o rascunho do Quadro com as restrições novas e a conta 5 × 19 = 95.
3. **Criar o esqueleto do repositório** (pastas, `requirements.txt`, `.gitignore`, README, este `PLANO.md`), proteger a `main`, e A começa o `config.py` e o `representacao.py`, enquanto C desenha no papel os mapas M1 a M6 com a resposta esperada.
