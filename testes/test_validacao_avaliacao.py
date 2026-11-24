"""Testes de validacao.py e avaliacao.py (PLANO.md, seções 2.3, 2.4, 5.1 e 5.2)."""
import random

from gerador.aleatorio import gerar_aleatorio
from gerador.avaliacao import avaliar, penalidade
from gerador.baselines import gerar_construtivo
from gerador.config import PADRAO
from gerador.representacao import cromossomo_base, decodificar
from gerador.validacao import caminho_critico, simular_inventario
from testes.mapas_pequenos import (INST, m1_perfeito, m2_deadlock, m3_ilha,
                                   m4_contraexemplo_monotonicidade)


def test_m1_perfeito():
    m = decodificar(m1_perfeito(), INST)
    alcancadas, nivel, _ = simular_inventario(m)
    assert nivel == 3
    assert alcancadas == {0, 1, 2, 3, 4, 7, 8, 10, 13, 16, 17}
    assert caminho_critico(m) == [0, 1, 2, 1, 4, 3, 4, 7, 8, 7, 10, 13, 16, 17]
    h, s, det = avaliar(m1_perfeito(), INST)
    assert h == 0
    # S3: cartão 1 a 3 passos da porta de nível 1, cartão 2 a 2 passos do checkpoint A,
    # cartão 3 a 3 passos do checkpoint B: (6-3) + (6-2) + (6-3) = 10.
    # S4: 14 células no caminho, 11 distintas: 3 repetidos (alvo 4) = 0.
    # S5: 13 passos, faixa [30, 45]: 17.
    assert det == {"H1": 0, "H2": 0, "H3": 0, "H4": 0, "H5": 0, "H6": 0, "H7": 0,
                   "S1": 0, "S2": 0, "S3": 10, "S4": 0, "S5": 17}


def test_m2_deadlock_de_cartao():
    m = decodificar(m2_deadlock(), INST)
    alcancadas, nivel, _ = simular_inventario(m)
    assert nivel == 1
    assert alcancadas == {0, 1, 2, 4}
    assert caminho_critico(m) is None
    h, s, det = avaliar(m2_deadlock(), INST)
    assert det["H1"] == 1
    assert det["H2"] == 7                      # 3, 7, 8, 10, 13, 16, 17
    assert det["S2"] == det["S3"] == det["S4"] == det["S5"] == 19


def test_m3_ilha():
    h, s, det = avaliar(m3_ilha(), INST)
    assert det["H1"] == 0 and det["H2"] == 1 and h == 1


def test_m4_contraexemplo_da_monotonicidade_e_valido():
    m = decodificar(m4_contraexemplo_monotonicidade(), INST)
    alcancadas, _, _ = simular_inventario(m)
    assert 5 in alcancadas
    assert avaliar(m4_contraexemplo_monotonicidade(), INST)[0] == 0


def test_pior_caso_de_cabeca_cromossomo_base():
    """Tudo vazio e fechado: as contas feitas à mão (como o avaliar([0]*32) == 196 do exemplo)."""
    h, s, det = avaliar(cromossomo_base())
    assert det == {"H1": 1,
                   "H2": 5,    # 25, 33, 62, 70, 92 fora do alcance do início (3)
                   "H3": 4,    # 3 cartões em célula vazia + cartões 1 e 2 na mesma célula
                   "H4": 5,    # faltam 2 + 2 + 1 salas especiais
                   "H5": 42,   # cada zona tem 2 células ocupadas: 3 x (16 - 2)
                   "H6": 3,    # nenhuma armadilha, mínimo 3
                   "H7": 0,
                   "S1": 2,    # 25, 33, 62 e 70 têm uma ligação só: 4 becos, alvo 2
                   "S2": 19, "S3": 19, "S4": 19, "S5": 19}
    assert penalidade(cromossomo_base()) == 100 * 60 + 78


def test_as_duas_buscas_concordam():
    rng = random.Random(123)
    mapas = [gerar_aleatorio(rng) for _ in range(2000)]
    mapas += [gerar_construtivo(random.Random(s)) for s in range(300)]
    for c in mapas:
        m = decodificar(c)
        alcancadas, _, _ = simular_inventario(m)
        assert (PADRAO.saida in alcancadas) == (caminho_critico(m) is not None)


def test_caminho_critico_e_um_passeio_legal():
    for s in range(200):
        m = decodificar(gerar_construtivo(random.Random(s)))
        caminho = caminho_critico(m)
        assert caminho[0] == PADRAO.inicio and caminho[-1] == PADRAO.saida
        nivel = 0
        for a, b in zip(caminho, caminho[1:]):
            exigidos = [n for j, n in m.viz[a] if j == b]
            assert exigidos and exigidos[0] <= nivel
            nivel = max([nivel] + [k + 1 for k, c in enumerate(m.cartao) if c == b])


def test_teto_das_desejaveis():
    rng = random.Random(5)
    for _ in range(500):
        _, _, det = avaliar(gerar_aleatorio(rng))
        assert all(det[k] <= 19 for k in ("S1", "S2", "S3", "S4", "S5"))


def test_conta_do_peso():
    assert 5 * PADRAO.regras.teto_s < PADRAO.regras.peso_h
