"""Execuções, baterias de 10 sementes, CSV e resumos.

Seção 6 do PLANO.md. Papel responsável: A.

Uso pela linha de comando (a partir da raiz do repositório):
    python -m gerador.experimentos baselines            # E0 sem IA, 10 sementes, orçamento cheio
    python -m gerador.experimentos baselines --rapido   # 2 sementes, orçamento pequeno
    python -m gerador.experimentos baselines --processos 4

Cada execução cria o próprio random.Random(semente): o resultado não muda com o número de
processos nem com a ordem das configurações.
"""
import argparse
import csv
import os
import random
import statistics
import time
from concurrent.futures import ProcessPoolExecutor

from gerador.avaliacao import avaliar, penalidade_de
from gerador.baselines import busca_aleatoria, construtivo_rerolado, gerar_construtivo
from gerador.config import PADRAO

TAM_POP, GERACOES = 200, 300
ORCAMENTO = TAM_POP * (GERACOES + 1)          # 60 200 avaliações, igual para todos os métodos de busca
ORCAMENTO_RAPIDO = 2000
CHAVES = ("H1", "H2", "H3", "H4", "H5", "H6", "H7", "S1", "S2", "S3", "S4", "S5")

# nome -> (método, parâmetros extras). Os do AG só funcionam depois de ag.py implementado.
CONFIGURACOES = {
    "construtivo": ("construtivo", {}),
    "busca_aleatoria": ("busca_aleatoria", {}),
    "construtivo_rerolado": ("construtivo_rerolado", {}),
    "ag_puro": ("ag", {"inicial": "aleatoria"}),
    "ag_semeado": ("ag", {"inicial": "construtivo"}),
}
BASELINES = ("construtivo", "busca_aleatoria", "construtivo_rerolado")


def rodar_execucao(nome, semente, inst=PADRAO, n_avaliacoes=ORCAMENTO):
    """Roda uma configuração com uma semente e devolve uma linha da tabela (dict)."""
    metodo, extras = CONFIGURACOES[nome]
    rng = random.Random(semente)
    inicio = time.perf_counter()
    primeiro_valido = None
    if metodo == "construtivo":
        melhor, avaliacoes = gerar_construtivo(rng, inst), 1
    elif metodo == "busca_aleatoria":
        r = busca_aleatoria(n_avaliacoes, rng, inst, **extras)
        melhor, avaliacoes, primeiro_valido = r.melhor, r.n_avaliacoes, r.primeiro_valido
    elif metodo == "construtivo_rerolado":
        r = construtivo_rerolado(n_avaliacoes, rng, inst)
        melhor, avaliacoes, primeiro_valido = r.melhor, r.n_avaliacoes, r.primeiro_valido
    elif metodo == "ag":
        from gerador.ag import algoritmo_genetico
        geracoes = max(1, n_avaliacoes // TAM_POP - 1)
        r = algoritmo_genetico(tam_pop=TAM_POP, geracoes=geracoes, semente=semente, inst=inst, **extras)
        melhor, avaliacoes, primeiro_valido = r.melhor, r.n_avaliacoes, r.primeiro_valido
    else:
        raise ValueError(metodo)
    tempo = time.perf_counter() - inicio
    h, s, det = avaliar(melhor, inst)
    linha = {"configuracao": nome, "semente": semente, "penalidade": penalidade_de(h, s, inst),
             "obrigatorias": h, "desejaveis": s, "valido": int(h == 0),
             "primeiro_valido": "" if primeiro_valido is None else primeiro_valido,
             "n_avaliacoes": avaliacoes, "tempo": round(tempo, 3)}
    linha.update({k: det[k] for k in CHAVES})
    return linha


def _rodar(args):
    return rodar_execucao(*args)


def bateria(nome, sementes=range(10), inst=PADRAO, n_avaliacoes=ORCAMENTO, processos=1):
    """Roda uma configuração em várias sementes (em paralelo se processos > 1)."""
    tarefas = [(nome, s, inst, n_avaliacoes) for s in sementes]
    if processos <= 1:
        return [_rodar(t) for t in tarefas]
    with ProcessPoolExecutor(max_workers=processos) as ex:
        return list(ex.map(_rodar, tarefas))


def resumir(linhas):
    """Média, melhor e pior de uma configuração, como na tabela final do PLANO.md (seção 6.3)."""
    des = [l["desejaveis"] for l in linhas]
    obr = [l["obrigatorias"] for l in linhas]
    pen = [l["penalidade"] for l in linhas]
    return {"configuracao": linhas[0]["configuracao"], "execucoes": len(linhas),
            "validos": sum(l["valido"] for l in linhas),
            "obrigatorias_media": round(statistics.mean(obr), 2),
            "desejaveis_media": round(statistics.mean(des), 2),
            "desejaveis_melhor": min(des), "desejaveis_pior": max(des),
            "penalidade_media": round(statistics.mean(pen), 2),
            "tempo_medio": round(statistics.mean(l["tempo"] for l in linhas), 3),
            **{f"{k}_media": round(statistics.mean(l[k] for l in linhas), 2) for k in CHAVES if k[0] == "S"}}


def salvar_csv(linhas, arquivo):
    os.makedirs(os.path.dirname(arquivo) or ".", exist_ok=True)
    with open(arquivo, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)


def _principal():
    ap = argparse.ArgumentParser(description="Baterias de experimentos do gerador")
    ap.add_argument("quais", choices=["baselines"], help="o que rodar")
    ap.add_argument("--rapido", action="store_true", help="2 sementes e orçamento pequeno")
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    sementes = range(2) if a.rapido else range(10)
    orcamento = ORCAMENTO_RAPIDO if a.rapido else ORCAMENTO
    todas, resumos = [], []
    for nome in BASELINES:
        linhas = bateria(nome, sementes, n_avaliacoes=orcamento, processos=a.processos)
        todas += linhas
        resumos.append(resumir(linhas))
        print(resumos[-1])
    if not a.rapido:   # só a bateria completa grava em resultados/
        salvar_csv(todas, os.path.join("resultados", "baselines_execucoes.csv"))
        salvar_csv(resumos, os.path.join("resultados", "baselines_resumo.csv"))


if __name__ == "__main__":
    _principal()
