"""Índices do cromossomo (blocos de 4 genes por célula, ordem por colunas) e leitura do mapa.

Seções 2.2 e 3.4 do PLANO.md. Todo o resto do código depende deste módulo.
Papel responsável: A.

Leitura do mapa (genótipo -> fenótipo), seção 2.2 do PLANO.md:
- uma ligação só existe se as duas células não forem vazias e o gene for > 0;
- o nível exigido por uma passagem é (valor do gene - 1): aberta = 0;
- armadilha só conta em corredor da zona das armadilhas;
- o gene do cartão n é a posição da célula dentro da zona do cartão.
"""
from typing import NamedTuple

from gerador.config import (ARMADILHA, CARTAO, CORREDOR, GENES_POR_CELULA, LESTE, SALA,
                            SALA_ESPECIAL, SUL, TIPO, VAZIA, Instancia, PADRAO)

Cromossomo = list  # lista de inteiros, inst.n_genes posições

DESLOCAMENTO = {TIPO: 0, LESTE: 1, SUL: 2, ARMADILHA: 3}


class Mapa(NamedTuple):
    """O cromossomo já lido."""
    inst: Instancia
    tipo: list         # por célula: VAZIA, CORREDOR, SALA ou SALA_ESPECIAL
    viz: list          # por célula: [(vizinha, nível exigido de 0 a 3), ...] na ordem N, L, S, O
    cartao: tuple      # célula do cartão 1, 2, 3...
    armadilha: frozenset  # células com armadilha que conta


# ---------------------------------------------------------------- coordenadas

def celula(linha, coluna, inst=PADRAO):
    return coluna * inst.altura + linha


def linha_coluna(i, inst=PADRAO):
    return i % inst.altura, i // inst.altura


def zona_da_celula(i, inst=PADRAO):
    return inst.zona_de[i]


# ---------------------------------------------------------------- posições dos genes

def pos_tipo(i, inst=PADRAO):
    return inst.pos_bloco[i] + DESLOCAMENTO[TIPO]


def pos_leste(i, inst=PADRAO):
    return inst.pos_bloco[i] + DESLOCAMENTO[LESTE]


def pos_sul(i, inst=PADRAO):
    return inst.pos_bloco[i] + DESLOCAMENTO[SUL]


def pos_armadilha(i, inst=PADRAO):
    return inst.pos_bloco[i] + DESLOCAMENTO[ARMADILHA]


def pos_cartao(n, inst=PADRAO):
    """Posição do gene do cartão n (n = 1, 2, 3...)."""
    return inst.pos_cartao[n - 1]


def zona_do_cartao(n, inst=PADRAO):
    for z, cartoes in enumerate(inst.cartoes_zona):
        if n in cartoes:
            return z
    raise ValueError(f"cartão {n} não existe nesta instância")


def descrever_posicao(p, inst=PADRAO):
    """Explica o que guarda a posição p do cromossomo (útil nas perguntas individuais)."""
    if inst.campo[p] == CARTAO:
        n = inst.pos_cartao.index(p) + 1
        return f"posição {p}: cartão {n} (zona {zona_do_cartao(n, inst)})"
    for i, inicio in enumerate(inst.pos_bloco):
        if inicio <= p < inicio + GENES_POR_CELULA:
            linha, coluna = linha_coluna(i, inst)
            return f"posição {p}: {inst.campo[p]} da célula {i} (linha {linha}, coluna {coluna})"
    raise IndexError(p)


# ---------------------------------------------------------------- montar cromossomos

def cromossomo_base(inst=PADRAO):
    """Tudo vazio e fechado; só os genes fixos preenchidos; cartões na primeira célula da zona."""
    return [v if v is not None else 0 for v in inst.valor_fixo]


def _definir(crom, p, valor, inst):
    if not 0 <= valor < max(inst.dominio[p], 1) and inst.valor_fixo[p] is None:
        raise ValueError(f"valor {valor} fora do domínio da posição {p}")
    if inst.valor_fixo[p] is not None and valor != inst.valor_fixo[p]:
        raise ValueError(f"a posição {p} é fixa (valor {inst.valor_fixo[p]})")
    crom[p] = valor


def definir_tipo(crom, i, tipo, inst=PADRAO):
    _definir(crom, pos_tipo(i, inst), tipo, inst)


def definir_ligacao(crom, i, j, valor, inst=PADRAO):
    """Define a ligação entre as células vizinhas i e j (valor 0 a 4)."""
    a, b = min(i, j), max(i, j)
    if b == a + inst.altura:                       # mesma linha, coluna seguinte: leste de a
        _definir(crom, pos_leste(a, inst), valor, inst)
    elif b == a + 1 and a % inst.altura != inst.altura - 1:   # mesma coluna, linha seguinte: sul de a
        _definir(crom, pos_sul(a, inst), valor, inst)
    else:
        raise ValueError(f"as células {i} e {j} não são vizinhas")


def definir_cartao(crom, n, i, inst=PADRAO):
    """Põe o cartão n na célula i (que precisa estar na zona do cartão)."""
    cels = inst.celulas_zona[zona_do_cartao(n, inst)]
    if i not in cels:
        raise ValueError(f"a célula {i} não está na zona do cartão {n}")
    _definir(crom, pos_cartao(n, inst), cels.index(i), inst)


def definir_armadilha(crom, i, valor, inst=PADRAO):
    _definir(crom, pos_armadilha(i, inst), valor, inst)


def dominios_ok(crom, inst=PADRAO):
    """Todo gene dentro do domínio e todos os genes fixos intactos."""
    if len(crom) != inst.n_genes:
        return False
    for p, v in enumerate(crom):
        fixo = inst.valor_fixo[p]
        if fixo is not None:
            if v != fixo:
                return False
        elif not 0 <= v < inst.dominio[p]:
            return False
    return True


# ---------------------------------------------------------------- leitura

def decodificar(crom, inst=PADRAO):
    """Lê o cromossomo e devolve o Mapa (vizinhança com o nível exigido, cartões, armadilhas)."""
    h = inst.altura
    n = inst.n_celulas
    tipo = [crom[inst.pos_bloco[i]] for i in range(n)]
    viz = [[] for _ in range(n)]
    # Ligações em ordem N, L, S, O: monta primeiro um dicionário por direção.
    norte, leste, sul, oeste = {}, {}, {}, {}
    for i in range(n):
        if tipo[i] == VAZIA:
            continue
        p = inst.pos_bloco[i]
        g_leste, g_sul = crom[p + 1], crom[p + 2]
        j = i + h                                   # vizinha a leste
        if g_leste > 0 and j < n and tipo[j] != VAZIA:
            leste[i] = (j, g_leste - 1)
            oeste[j] = (i, g_leste - 1)
        j = i + 1                                   # vizinha ao sul
        if g_sul > 0 and i % h != h - 1 and tipo[j] != VAZIA:
            sul[i] = (j, g_sul - 1)
            norte[j] = (i, g_sul - 1)
    for i in range(n):
        for direcao in (norte, leste, sul, oeste):
            if i in direcao:
                viz[i].append(direcao[i])

    cartao = []
    for k, p in enumerate(inst.pos_cartao):
        z = zona_do_cartao(k + 1, inst)
        cartao.append(inst.celulas_zona[z][crom[p]])

    cels_armadilha = inst.celulas_zona[inst.zona_armadilhas]
    armadilha = frozenset(i for i in cels_armadilha
                          if tipo[i] == CORREDOR and crom[inst.pos_bloco[i] + 3] == 1)
    return Mapa(inst=inst, tipo=tipo, viz=viz, cartao=tuple(cartao), armadilha=armadilha)


def e_sala(tipo_celula):
    return tipo_celula in (SALA, SALA_ESPECIAL)
