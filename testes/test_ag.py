"""Testes de ag.py (PLANO.md, seção 5.3): população inicial, contador, elitismo e reprodutibilidade.

Populações pequenas e poucas gerações: o 200 x 300 não entra no pytest.
"""
import random

import pytest

from gerador.ag import _elite, algoritmo_genetico, populacao_inicial
from gerador.avaliacao import avaliar, penalidade
from gerador.config import PADRAO
from gerador.representacao import dominios_ok


def test_populacao_inicial_aleatoria_tem_tam_pop_cromossomos_dentro_do_dominio():
    pop = populacao_inicial(12, random.Random(0), PADRAO, "aleatoria")

    assert len(pop) == 12
    assert all(len(c) == PADRAO.n_genes and dominios_ok(c, PADRAO) for c in pop)


def test_populacao_inicial_construtivo_nao_tem_violacao_obrigatoria():
    pop = populacao_inicial(10, random.Random(1), PADRAO, "construtivo")

    assert len(pop) == 10
    assert all(avaliar(c, PADRAO)[0] == 0 for c in pop)


def test_populacao_inicial_e_reprodutivel():
    a = populacao_inicial(5, random.Random(7), PADRAO, "aleatoria")
    b = populacao_inicial(5, random.Random(7), PADRAO, "aleatoria")

    assert a == b


def test_populacao_inicial_modo_desconhecido_da_erro():
    with pytest.raises(ValueError):
        populacao_inicial(3, random.Random(0), PADRAO, "outro")


def test_contador_e_tamanho_do_historico():
    r = algoritmo_genetico(tam_pop=8, geracoes=4, semente=0)

    assert r.n_avaliacoes == 8 * (4 + 1)
    assert len(r.historico) == 4 + 1


def test_geracoes_zero_so_avalia_a_populacao_inicial():
    r = algoritmo_genetico(tam_pop=6, geracoes=0, semente=3)

    assert r.n_avaliacoes == 6
    assert len(r.historico) == 1
    assert r.historico[0] == penalidade(r.melhor, PADRAO)


@pytest.mark.parametrize("elite", [0, 2])
def test_historico_acumulado_nunca_sobe(elite):
    r = algoritmo_genetico(tam_pop=10, geracoes=6, elite=elite, taxa_mut=0.2, semente=5)

    assert all(b <= a for a, b in zip(r.historico, r.historico[1:]))


def test_ultimo_historico_e_a_penalidade_do_melhor():
    r = algoritmo_genetico(tam_pop=10, geracoes=5, semente=11)

    assert r.historico[-1] == penalidade(r.melhor, PADRAO)
    assert dominios_ok(r.melhor, PADRAO)


def test_sem_cruzamento_e_sem_mutacao_o_melhor_e_o_da_populacao_inicial():
    # Com taxa_cruz = 0 e taxa_mut = 0 todo filho é cópia de um indivíduo da população inicial,
    # então nada de novo aparece: o melhor final é o melhor da geração 0.
    pop = populacao_inicial(10, random.Random(21), PADRAO, "aleatoria")
    esperado = min(penalidade(c, PADRAO) for c in pop)

    r = algoritmo_genetico(tam_pop=10, geracoes=5, taxa_cruz=0, taxa_mut=0, semente=21)

    assert r.historico == [esperado] * 6
    assert penalidade(r.melhor, PADRAO) == esperado


def test_elite_devolve_copias_dos_melhores_com_desempate_pelo_indice():
    pop = [[0], [1], [2], [3]]
    penalidades = [30, 10, 10, 20]

    elite = _elite(pop, penalidades, 2)

    assert elite == [[1], [2]]
    elite[0][0] = 99
    assert pop[1] == [1]
    assert _elite(pop, penalidades, 0) == []


def test_primeiro_valido_do_ag_semeado_e_a_primeira_avaliacao():
    r = algoritmo_genetico(tam_pop=5, geracoes=2, inicial="construtivo", semente=0)

    assert r.primeiro_valido == 1


def test_primeiro_valido_e_indice_de_avaliacao_entre_1_e_o_orcamento():
    r = algoritmo_genetico(tam_pop=10, geracoes=3, inicial="construtivo", taxa_mut=0.05, semente=4)

    assert 1 <= r.primeiro_valido <= r.n_avaliacoes
    assert avaliar(r.melhor, PADRAO)[0] == 0


def test_mesma_semente_da_o_mesmo_resultado_e_sementes_diferentes_nao():
    a = algoritmo_genetico(tam_pop=8, geracoes=4, semente=17)
    b = algoritmo_genetico(tam_pop=8, geracoes=4, semente=17)
    c = algoritmo_genetico(tam_pop=8, geracoes=4, semente=18)

    assert a.melhor == b.melhor
    assert a.historico == b.historico
    assert a.melhor != c.melhor


@pytest.mark.parametrize("parametros", [
    {"tam_pop": 0},
    {"geracoes": -1},
    {"elite": 11},
    {"elite": -1},
    {"k": 0},
    {"k": 11},
    {"taxa_cruz": 1.5},
    {"taxa_mut": -0.1},
    {"cruzamento": "uniforme"},
    {"inicial": "outro"},
])
def test_parametros_invalidos_dao_erro(parametros):
    base = {"tam_pop": 10, "geracoes": 1, "semente": 0}
    base.update(parametros)

    with pytest.raises(ValueError):
        algoritmo_genetico(**base)
