"""Testes de aleatorio.py, baselines.py e desenho.py (PLANO.md, seção 5.4)."""
import random

from gerador.aleatorio import gerar_aleatorio
from gerador.avaliacao import avaliar
from gerador.baselines import busca_aleatoria, construtivo_rerolado, gerar_construtivo
from gerador.config import instancia_teste
from gerador.desenho import desenhar_mapa
from gerador.representacao import decodificar, dominios_ok
from gerador.validacao import caminho_critico


def test_construtivo_nunca_viola_obrigatoria_em_1000_sementes():
    for s in range(1000):
        c = gerar_construtivo(random.Random(s))
        assert dominios_ok(c)
        h, _, det = avaliar(c)
        assert h == 0, (s, det)


def test_construtivo_em_grade_pequena():
    inst = instancia_teste(colunas_por_zona=2, altura=3)
    for s in range(200):
        assert avaliar(gerar_construtivo(random.Random(s), inst), inst)[0] == 0


def test_construtivo_e_reprodutivel():
    assert gerar_construtivo(random.Random(42)) == gerar_construtivo(random.Random(42))
    assert gerar_construtivo(random.Random(1)) != gerar_construtivo(random.Random(2))


def test_aleatorio_respeita_dominios_e_e_reprodutivel():
    rng = random.Random(0)
    for _ in range(300):
        assert dominios_ok(gerar_aleatorio(rng))
    assert gerar_aleatorio(random.Random(9)) == gerar_aleatorio(random.Random(9))


def test_buscas_avaliam_exatamente_o_orcamento():
    r = busca_aleatoria(400, random.Random(0))
    assert r.n_avaliacoes == 400 and len(r.historico) == 2
    assert r.historico == sorted(r.historico, reverse=True)      # o melhor nunca piora
    r = construtivo_rerolado(250, random.Random(0))
    assert r.n_avaliacoes == 250 and len(r.historico) == 2
    assert r.primeiro_valido == 1                                  # o construtivo já nasce válido


def test_buscas_sao_reprodutiveis():
    a = busca_aleatoria(300, random.Random(3))
    b = busca_aleatoria(300, random.Random(3))
    assert a.melhor == b.melhor and a.historico == b.historico


def test_desenho_nao_quebra():
    m = decodificar(gerar_construtivo(random.Random(0)))
    ax = desenhar_mapa(m, caminho=caminho_critico(m), titulo="teste")
    assert ax is not None
