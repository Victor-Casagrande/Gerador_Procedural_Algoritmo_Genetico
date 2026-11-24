"""Simulação de inventário e caminho crítico (busca em largura em (célula, nível)).

Seção 2.3 do PLANO.md. Papel responsável: A.

Cartões hierárquicos: o cartão N abre toda porta de nível <= N. O nível do jogador é o
maior cartão que ele já pegou.

As duas buscas precisam concordar: a saída está em `alcancadas` se, e somente se, existe
caminho crítico. Isso é testado em milhares de mapas (testes/test_validacao.py).
"""
from collections import deque


def _nivel_na_celula(mapa):
    """Por célula: o maior cartão que está nela (0 se nenhum)."""
    nivel = [0] * mapa.inst.n_celulas
    for k, c in enumerate(mapa.cartao):
        nivel[c] = max(nivel[c], k + 1)
    return nivel


def simular_inventario(mapa):
    """Simula o jogador juntando cartões.

    Começa no início com nível 0; anda por tudo que dá para abrir com o nível atual; sobe o
    nível para o maior cartão alcançado; repete até o nível não mudar.

    Devolve (alcancadas, nivel_final, rodadas), em que rodadas é a lista de
    (nível usado na rodada, quantas células alcançou).
    """
    nivel_cel = _nivel_na_celula(mapa)
    inicio = mapa.inst.inicio
    nivel = 0
    rodadas = []
    while True:
        alcancadas = {inicio}
        fila = deque([inicio])
        while fila:
            i = fila.popleft()
            for j, exigido in mapa.viz[i]:
                if exigido <= nivel and j not in alcancadas:
                    alcancadas.add(j)
                    fila.append(j)
        rodadas.append((nivel, len(alcancadas)))
        novo = max([nivel] + [nivel_cel[i] for i in alcancadas])
        if novo == nivel:
            return alcancadas, nivel, rodadas
        nivel = novo


def caminho_critico(mapa):
    """Menor passeio do início até a saída, por busca em largura em (célula, nível).

    O nível sobe ao pisar numa célula com cartão. Desempate pela ordem fixa dos vizinhos
    (N, L, S, O). Devolve a lista de células, com repetição, ou None se a saída é inalcançável.
    """
    nivel_cel = _nivel_na_celula(mapa)
    inicio, saida = mapa.inst.inicio, mapa.inst.saida
    estado0 = (inicio, nivel_cel[inicio])
    pai = {estado0: None}
    fila = deque([estado0])
    while fila:
        estado = fila.popleft()
        i, nivel = estado
        if i == saida:
            caminho = []
            while estado is not None:
                caminho.append(estado[0])
                estado = pai[estado]
            return caminho[::-1]
        for j, exigido in mapa.viz[i]:
            if exigido > nivel:
                continue
            novo = (j, max(nivel, nivel_cel[j]))
            if novo not in pai:
                pai[novo] = estado
                fila.append(novo)
    return None


def nivel_exigido(mapa, i, j):
    """Nível exigido para atravessar a ligação entre as vizinhas i e j (None se não há ligação)."""
    for k, exigido in mapa.viz[i]:
        if k == j:
            return exigido
    return None
