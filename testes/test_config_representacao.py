"""Testes de config.py e representacao.py (PLANO.md, seções 2.1, 2.2 e 5)."""
import random

import pytest

from gerador.config import (ARMADILHA, CARTAO, CORREDOR, LESTE, PADRAO, SALA, SUL, TIPO,
                            instancia_teste)
from gerador.aleatorio import gerar_aleatorio
from gerador.representacao import (celula, cromossomo_base, decodificar, definir_armadilha,
                                   definir_ligacao, definir_tipo, descrever_posicao, dominios_ok,
                                   linha_coluna, pos_cartao, pos_leste, pos_tipo)


def test_tamanho_do_cromossomo():
    assert PADRAO.n_genes == 387
    assert len(PADRAO.genes_livres) == 281
    assert PADRAO.fatia_zona == ((0, 130), (130, 259), (259, 387))


def test_genes_fixos_por_campo():
    fixos = [PADRAO.campo[p] for p in range(PADRAO.n_genes) if PADRAO.dominio[p] == 1]
    assert fixos.count(TIPO) == 6
    assert fixos.count(LESTE) == 24
    assert fixos.count(SUL) == 12
    assert fixos.count(ARMADILHA) == 64
    assert fixos.count(CARTAO) == 0
    assert len(fixos) == 106


def test_posicoes_fixas_da_instancia():
    assert PADRAO.inicio == 3 and PADRAO.saida == 92
    assert PADRAO.checkpoints == ((25, 33, 2), (62, 70, 3))
    assert PADRAO.celulas_fixas == {3, 25, 33, 62, 70, 92}
    assert PADRAO.valor_fixo[pos_leste(25)] == 3      # porta de nível 2
    assert PADRAO.valor_fixo[pos_leste(62)] == 4      # porta de nível 3
    assert PADRAO.valor_fixo[pos_leste(26)] == 0      # outra fronteira: fechada


def test_coordenadas():
    assert celula(1, 4) == 33
    assert linha_coluna(33) == (1, 4)


def test_posicao_137_da_pergunta_individual():
    assert descrever_posicao(137) == "posição 137: armadilha da célula 33 (linha 1, coluna 4)"
    assert pos_cartao(1) == 128 and pos_cartao(2) == 129 and pos_cartao(3) == 258


def test_nao_deixa_mudar_gene_fixo():
    c = cromossomo_base()
    with pytest.raises(ValueError):
        definir_tipo(c, 3, SALA)             # o início é sempre corredor
    with pytest.raises(ValueError):
        definir_armadilha(c, 0, 1)           # armadilha fora da Zona Pesada
    with pytest.raises(ValueError):
        definir_ligacao(c, 0, 9, 1)          # 0 e 9 não são vizinhas


def test_ligacao_para_celula_vazia_nao_existe():
    c = cromossomo_base()
    definir_tipo(c, 2, CORREDOR)
    definir_ligacao(c, 2, 3, 1)              # 2 e 3 ocupadas: existe
    definir_ligacao(c, 3, 4, 1)              # 4 vazia: não existe
    m = decodificar(c)
    assert m.viz[3] == [(2, 0)]
    assert m.viz[2] == [(3, 0)]


def test_vizinhanca_simetrica_em_mapas_sorteados():
    rng = random.Random(7)
    for _ in range(200):
        m = decodificar(gerar_aleatorio(rng))
        for i, vizinhas in enumerate(m.viz):
            for j, nivel in vizinhas:
                assert (i, nivel) in m.viz[j]


def test_armadilha_so_conta_em_corredor_da_zona_pesada():
    c = cromossomo_base()
    definir_tipo(c, 40, CORREDOR)
    definir_tipo(c, 41, SALA)
    definir_armadilha(c, 40, 1)
    definir_armadilha(c, 41, 1)
    assert decodificar(c).armadilha == {40}


def test_dominios_ok():
    assert dominios_ok(cromossomo_base())
    c = gerar_aleatorio(random.Random(1))
    assert dominios_ok(c)
    c[pos_tipo(3)] = SALA                    # mexe num gene fixo
    assert not dominios_ok(c)


def test_instancia_teste():
    inst = instancia_teste(2, 3)
    assert inst.inicio == 0 and inst.saida == 17
    assert inst.checkpoints == ((4, 7, 2), (10, 13, 3))
