"""Testes dos operadores genéticos (PLANO.md, seção 5.3)."""
import random

from gerador.aleatorio import gerar_aleatorio
from gerador.config import PADRAO
from gerador.operadores import cruzamento_um_ponto, mutacao, selecao_torneio
from gerador.representacao import dominios_ok


def test_torneio_com_populacao_inteira_devolve_melhor():
    pop = [[0], [1], [2]]
    apts = [0.1, 0.9, 0.5]
    for semente in range(10):
        assert selecao_torneio(pop, apts, len(pop), random.Random(semente)) == [1]


def test_torneio_devolve_copia():
    pop = [[0, 1], [2, 3], [4, 5]]
    resultado = selecao_torneio(pop, [0.1, 0.9, 0.5], 3, random.Random(0))

    assert resultado == [2, 3]
    assert resultado is not pop[1]
    resultado[0] = 99
    assert pop[1] == [2, 3]


def test_torneio_e_reprodutivel():
    rng_pop = random.Random(4)
    pop = [gerar_aleatorio(rng_pop) for _ in range(5)]
    apts = [0.1, 0.5, 0.2, 0.9, 0.3]
    a = [selecao_torneio(pop, apts, 3, random.Random(17)) for _ in range(10)]
    b = [selecao_torneio(pop, apts, 3, random.Random(17)) for _ in range(10)]

    assert a == b


def test_torneio_preserva_dominios_em_1000_aplicacoes():
    rng_pop = random.Random(19)
    pop = [gerar_aleatorio(rng_pop) for _ in range(5)]
    apts = [0.1, 0.5, 0.2, 0.9, 0.3]
    rng = random.Random(20)

    for _ in range(1000):
        selecionado = selecao_torneio(pop, apts, 3, rng)
        assert dominios_ok(selecionado, PADRAO)


def test_cruzamento_um_ponto_troca_os_dois_valores_em_cada_posicao():
    p1 = gerar_aleatorio(random.Random(1))
    p2 = gerar_aleatorio(random.Random(2))
    p1_original = list(p1)
    p2_original = list(p2)
    rng = random.Random(3)

    for _ in range(1000):
        filho1, filho2 = cruzamento_um_ponto(p1, p2, rng)
        assert len(filho1) == len(p1)
        assert len(filho2) == len(p2)
        for i in range(len(p1)):
            assert sorted((filho1[i], filho2[i])) == sorted((p1[i], p2[i]))

    assert p1 == p1_original
    assert p2 == p2_original


def test_cruzamento_de_pais_iguais_devolve_filhos_iguais():
    p = gerar_aleatorio(random.Random(5))

    filho1, filho2 = cruzamento_um_ponto(p, p, random.Random(6))

    assert filho1 == p
    assert filho2 == p


def test_cruzamento_preserva_dominios_em_1000_aplicacoes():
    p1 = gerar_aleatorio(random.Random(7))
    p2 = gerar_aleatorio(random.Random(8))
    rng = random.Random(9)

    for _ in range(1000):
        filhos = cruzamento_um_ponto(p1, p2, rng)
        assert all(dominios_ok(filho, PADRAO) for filho in filhos)


def test_mutacao_taxa_zero_nao_muda_nada():
    crom = gerar_aleatorio(random.Random(10))

    resultado = mutacao(crom, 0, random.Random(11), PADRAO)

    assert resultado == crom


def test_mutacao_taxa_um_muda_livres_e_preserva_fixos():
    crom = gerar_aleatorio(random.Random(12))
    original = list(crom)

    resultado = mutacao(crom, 1, random.Random(13), PADRAO)

    assert resultado is not crom
    assert crom == original
    assert all(resultado[p] != crom[p] for p in PADRAO.genes_livres)
    assert all(resultado[p] == crom[p] for p, fixo in enumerate(PADRAO.valor_fixo)
               if fixo is not None)
    assert len(PADRAO.genes_livres) == 281
    assert sum(fixo is not None for fixo in PADRAO.valor_fixo) == 106


def test_mutacao_e_reprodutivel():
    crom = gerar_aleatorio(random.Random(14))

    a = mutacao(crom, 1 / 281, random.Random(15), PADRAO)
    b = mutacao(crom, 1 / 281, random.Random(15), PADRAO)

    assert a == b


def test_mutacao_preserva_dominios_em_1000_aplicacoes():
    crom = gerar_aleatorio(random.Random(16))
    rng_leve = random.Random(17)
    for _ in range(1000):
        crom = mutacao(crom, 1 / 281, rng_leve, PADRAO)
        assert dominios_ok(crom, PADRAO)

    rng_total = random.Random(18)
    for _ in range(1000):
        crom = mutacao(crom, 1, rng_total, PADRAO)
        assert dominios_ok(crom, PADRAO)
