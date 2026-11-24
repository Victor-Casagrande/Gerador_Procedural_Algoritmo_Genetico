"""Operadores genéticos escritos pela equipe: torneio, cruzamentos e mutação.

Seção 2.2 do PLANO.md. Proibido usar DEAP, PyGAD ou similares.
Papel responsável: B.

ESQUELETO (CP3, 24/11): as assinaturas estão definidas; o corpo é escrito pelo dono do módulo,
um operador por vez, cada um com os testes da seção 5.3 do PLANO.md (como os assert do laboratório).
Todo sorteio usa o `rng` recebido (random.Random), nunca o `random` global.
"""


def selecao_torneio(pop, apts, k, rng):
    """Sorteia k índices distintos da população e devolve uma CÓPIA do de maior aptidão.

    Teste: com k = len(pop), devolve sempre o melhor; alterar a cópia não altera a população.
    """
    raise NotImplementedError


def cruzamento_um_ponto(p1, p2, rng):
    """Corta os dois pais na mesma posição sorteada (1 a n-1) e troca as caudas.

    Com o cromossomo em ordem de colunas, o corte é uma linha vertical do mapa (PLANO.md, P3).
    Devolve (filho1, filho2). Teste: em cada posição, os filhos têm os dois valores dos pais.
    """
    raise NotImplementedError


def cruzamento_por_zona(p1, p2, rng, inst):
    """Cada zona inteira do filho (com os cartões dela) vem de um dos pais.

    Usa inst.fatia_zona. Teste de fechamento: dois pais válidos geram filhos válidos (1000 pares
    do construtivo). Devolve (filho1, filho2).
    """
    raise NotImplementedError


def mutacao(crom, taxa, rng, inst):
    """Devolve um NOVO cromossomo: cada gene livre, com probabilidade `taxa`, recebe outro valor
    do domínio dele (diferente do atual). Genes fixos nunca mudam.

    Testes: taxa 0 não muda nada; taxa 1 muda os 281 livres e nenhum dos 106 fixos; o original
    continua igual; dominios_ok continua verdadeiro.
    """
    raise NotImplementedError
