"""Testes de ferramentas/tabela_resultados.py: as tabelas do Diário saem dos CSV, sem digitar número."""
import os

import pytest

from ferramentas import tabela_resultados as tr
from gerador import experimentos as ex

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_formatos():
    assert tr.numero("18.9") == "18,9"
    assert tr.numero("0") == "0"
    assert tr.numero("2379.30") == "2379,3"
    assert tr.numero("2.45") == "2,45"
    assert tr.tempo("0.001") == "~0,001 s"
    assert tr.tempo("26.114") == "~26 s"
    assert tr.milhar("60200") == "60 200"
    assert tr.sementes([{"semente": str(s)} for s in range(10)]) == "0 a 9"
    assert tr.sementes([{"semente": "0"}, {"semente": "3"}]) == "0, 3"


def test_baselines_de_24_11_reproduzem_a_tabela():
    """Os números do CP2 (resultados/baselines_*.csv) saem iguais aos que estavam no Diário."""
    tabela = tr.tabela_e0(tr.ler_resultados(os.path.join(RAIZ, "resultados")))
    assert "| Construtivo | 0 a 9 | 10 | 0 | 18,9 (8 – 24) | ~0,001 s |" in tabela
    assert "| Busca aleatória | 0 a 9 | 0 | 23,5 | 29,3 (18 – 80) | ~26 s |" in tabela
    assert "| Construtivo rerolado | 0 a 9 | 10 | 0 | 2,4 (2 – 3) | ~99 s |" in tabela
    assert "| AG puro (principal) |" in tabela


def test_tabela_com_resultados_gravados_pelo_experimentos(tmp_path):
    linhas = ex.bateria("busca_aleatoria", range(2), n_avaliacoes=300)
    ex.salvar_csv(linhas, str(tmp_path / "baselines_execucoes.csv"))
    ex.salvar_csv([ex.resumir(linhas)], str(tmp_path / "baselines_resumo.csv"))
    dados = tr.ler_resultados(str(tmp_path))
    assert set(dados) == {"busca_aleatoria"}
    e0 = tr.tabela_e0(dados)
    assert "| Busca aleatória | 0 a 1 |" in e0 and "300 avaliações" in e0
    assert "| Construtivo |  |" in e0                      # o que não rodou fica vazio
    assert "E3" not in tr.tabela_parametros(dados)         # o opcional só aparece se rodou


def test_trocar_entre_marcadores():
    texto = "antes\n<!-- tabela:x -->\nvelho\n<!-- /tabela:x -->\ndepois"
    novo = tr.trocar_entre_marcadores(texto, "x", "| novo |")
    assert novo == "antes\n<!-- tabela:x -->\n| novo |\n<!-- /tabela:x -->\ndepois"
    with pytest.raises(ValueError):
        tr.trocar_entre_marcadores(texto, "y", "z")


def test_diario_e_estado_estao_em_dia():
    """Se falhar: rode `python ferramentas/tabela_resultados.py` depois de gravar resultados novos."""
    dados = tr.ler_resultados(os.path.join(RAIZ, "resultados"))
    alvos = {os.path.join(RAIZ, "docs", "diario", "08_resultados.md"):
             {"e0": tr.tabela_e0(dados), "parametros": tr.tabela_parametros(dados)},
             os.path.join(RAIZ, "docs", "ESTADO.md"): {"estado": tr.tabela_estado(dados)}}
    for arquivo, tabelas in alvos.items():
        with open(arquivo, encoding="utf-8") as f:
            texto = f.read()
        novo = texto
        for nome, conteudo in tabelas.items():
            novo = tr.trocar_entre_marcadores(novo, nome, conteudo)
        assert novo == texto, arquivo
