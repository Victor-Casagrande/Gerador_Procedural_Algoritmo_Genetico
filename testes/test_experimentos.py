"""Testes de experimentos.py (PLANO.md, seções 5.4 e 6).

O ag.py ainda não está implementado (papel C): os testes das configurações do AG trocam
ag.algoritmo_genetico por um AG falso, que só devolve um Resultado com o formato certo e anota
os argumentos que recebeu. Assim dá para conferir a tradução das configurações e os arquivos
gravados sem depender do laço de verdade.
"""
import csv
import json
import random

import pytest

import gerador.ag
from gerador import experimentos as ex
from gerador.avaliacao import penalidade
from gerador.baselines import Resultado, gerar_construtivo
from gerador.config import PADRAO


@pytest.fixture
def ag_falso(monkeypatch):
    chamadas = []

    def falso(tam_pop, geracoes, semente, inst, **kw):
        chamadas.append({"tam_pop": tam_pop, "geracoes": geracoes, **kw})
        melhor = gerar_construtivo(random.Random(semente), inst)
        pen = penalidade(melhor, inst)
        historico = [pen + geracoes - g for g in range(geracoes + 1)]   # cai 1 por geração até pen
        return Resultado(melhor, historico, tam_pop * (geracoes + 1), 0, 0.0)

    monkeypatch.setattr(gerador.ag, "algoritmo_genetico", falso)
    return chamadas


def test_parametros_ag_padrao_e_taxa_de_mutacao():
    assert ex.parametros_ag({}, 60200) == {"tam_pop": 200, "geracoes": 300}
    p = ex.parametros_ag({"genes_mut": 2}, 60200)
    assert p["taxa_mut"] == 2 / 281 and "genes_mut" not in p
    assert ex.parametros_ag({"genes_mut": 0}, 60200)["taxa_mut"] == 0


def test_parametros_ag_populacao_com_o_mesmo_orcamento():
    assert ex.parametros_ag({"tam_pop": 100}, 60200)["geracoes"] == 601      # 100 x 602 = 60 200
    p = ex.parametros_ag({"tam_pop": 400}, 60200)
    assert p["geracoes"] == 149 and 400 * (149 + 1) == 60000                # não divide exato


def test_toda_configuracao_esta_em_um_experimento():
    em_algum = {n for nomes in ex.EXPERIMENTOS.values() for n in nomes}
    assert em_algum == set(ex.CONFIGURACOES)


def test_configuracoes_chegam_ao_ag(ag_falso):
    for nome in ("ag_puro", "ag_mut_5", "ag_semeado_por_zona", "ag_pop_400", "ag_sem_elite"):
        linha = ex.rodar_execucao(nome, 0, n_avaliacoes=2000)
        assert linha["n_avaliacoes"] == ag_falso[-1]["tam_pop"] * (ag_falso[-1]["geracoes"] + 1)
    puro, mut5, zona, pop400, sem_elite = ag_falso
    assert puro == {"tam_pop": 200, "geracoes": 9, "inicial": "aleatoria"}
    assert mut5["taxa_mut"] == 5 / 281
    assert zona["cruzamento"] == "por_zona" and zona["inicial"] == "construtivo"
    assert pop400["tam_pop"] == 400 and pop400["geracoes"] == 4
    assert sem_elite["elite"] == 0


def test_historico_do_ag_tem_uma_linha_por_geracao(ag_falso):
    linha, hs, melhor = ex.executar("ag_puro", 3, n_avaliacoes=2000)
    assert [h["passo"] for h in hs] == list(range(10))
    assert [h["avaliacoes"] for h in hs] == [200 * (g + 1) for g in range(10)]
    assert hs[-1]["melhor_penalidade"] == linha["penalidade"] == penalidade(melhor)
    assert len(melhor) == PADRAO.n_genes


def test_historico_dos_baselines():
    _, hs, _ = ex.executar("busca_aleatoria", 0, n_avaliacoes=500)
    assert [h["avaliacoes"] for h in hs] == [200, 400, 500]
    linha, hs, _ = ex.executar("construtivo", 0)
    assert hs == [{"configuracao": "construtivo", "semente": 0, "passo": 0, "avaliacoes": 1,
                   "melhor_penalidade": linha["penalidade"]}]


def test_rodar_experimento_grava_os_quatro_arquivos(ag_falso, tmp_path):
    resumos = ex.rodar_experimento("e0", ex.EXPERIMENTOS["e0"], sementes=range(2),
                                   n_avaliacoes=1000, pasta=str(tmp_path))
    assert [r["configuracao"] for r in resumos] == ["ag_puro", "ag_semeado"]
    with open(tmp_path / "e0_execucoes.csv", encoding="utf-8") as f:
        execucoes = list(csv.DictReader(f))
    with open(tmp_path / "e0_historicos.csv", encoding="utf-8") as f:
        historicos = list(csv.DictReader(f))
    with open(tmp_path / "e0_melhores.json", encoding="utf-8") as f:
        melhores = json.load(f)
    assert len(execucoes) == 4
    assert len(historicos) == 4 * 5                      # 2 configurações x 2 sementes x 5 gerações
    assert (tmp_path / "e0_resumo.csv").exists()
    for m, e in zip(melhores, execucoes):                # o cromossomo gravado reproduz a penalidade
        assert m["configuracao"] == e["configuracao"] and m["semente"] == int(e["semente"])
        assert penalidade(m["cromossomo"]) == m["penalidade"] == int(e["penalidade"])


def test_bateria_da_os_mesmos_numeros_com_1_e_4_processos():
    def sem_tempo(linhas):
        return [{k: v for k, v in l.items() if k != "tempo"} for l in linhas]
    um = ex.bateria("busca_aleatoria", range(4), n_avaliacoes=300, processos=1)
    quatro = ex.bateria("busca_aleatoria", range(4), n_avaliacoes=300, processos=4)
    assert sem_tempo(um) == sem_tempo(quatro)


def test_ultima_melhora():
    assert ex.ultima_melhora([10, 8, 8, 5, 5, 5]) == 3
    assert ex.ultima_melhora([5, 5, 5]) == 0
    assert ex.ultima_melhora([7]) == 0


def test_orcamento_equivalente():
    assert ex.orcamento_equivalente(30, 99, 60200) == 18242
    assert ex.orcamento_equivalente(26, 26, 60200) == 60200
    assert ex.orcamento_equivalente(0.0001, 100, 10) == 1           # pelo menos uma avaliação


def test_linha_de_comando_rapida(ag_falso, tmp_path, monkeypatch):
    monkeypatch.setattr(ex, "PASTA_RAPIDO", str(tmp_path))
    ex._principal(["e2", "--rapido"])
    assert (tmp_path / "e2_resumo.csv").exists()
    assert {c["cruzamento"] for c in ag_falso} == {"por_zona"}
