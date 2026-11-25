"""Execuções, baterias de 10 sementes, CSV, JSON e resumos.

Seção 6 do PLANO.md. Papel responsável: A.

Uso pela linha de comando (a partir da raiz do repositório):
    python -m gerador.experimentos baselines            # os 3 métodos sem IA (já rodado em 24/11)
    python -m gerador.experimentos ensaio               # AG puro 200 x 300 em 3 sementes (PLANO.md, 4.3)
    python -m gerador.experimentos e0                   # AG puro e AG semeado
    python -m gerador.experimentos e1                   # taxa de mutação: 0, 0,5, 2 e 5 genes por filho
    python -m gerador.experimentos e2                   # cruzamento por zona, no AG puro e no semeado
    python -m gerador.experimentos e3                   # opcional: população 100 e 400, sem elitismo
    python -m gerador.experimentos tudo                 # e0, e1 e e2, nessa ordem
    python -m gerador.experimentos tempo                # baselines com o mesmo TEMPO do AG puro (6.4)
Opções de todos: --rapido (2 sementes, 2000 avaliações, grava em resultados/rapido/) e
--processos N (sementes em paralelo; os números não mudam com N).

Cada experimento grava em resultados/ quatro arquivos com o nome dele na frente:
    <exp>_execucoes.csv   uma linha por execução (configuração, semente, H1 a H7, S1 a S5...)
    <exp>_resumo.csv      uma linha por configuração: média, melhor, pior, válidos em 10
    <exp>_historicos.csv  a melhor penalidade a cada geração (AG) ou a cada 200 avaliações
    <exp>_melhores.json   o melhor cromossomo de cada execução, para redesenhar sem rodar de novo

Cada execução cria o próprio random.Random(semente): o resultado não muda com o número de
processos nem com a ordem das configurações.
"""
import argparse
import csv
import json
import os
import random
import statistics
import time
from concurrent.futures import ProcessPoolExecutor

from gerador.avaliacao import avaliar, penalidade_de
from gerador.baselines import (INTERVALO_HISTORICO, busca_aleatoria, construtivo_rerolado,
                               gerar_construtivo)
from gerador.config import PADRAO

TAM_POP, GERACOES = 200, 300
ORCAMENTO = TAM_POP * (GERACOES + 1)          # 60 200 avaliações, igual para todos os métodos de busca
ORCAMENTO_RAPIDO = 2000
SEMENTES, SEMENTES_RAPIDO, SEMENTES_ENSAIO = range(10), range(2), range(3)
PASTA, PASTA_RAPIDO = "resultados", os.path.join("resultados", "rapido")
CHAVES = ("H1", "H2", "H3", "H4", "H5", "H6", "H7", "S1", "S2", "S3", "S4", "S5")

# nome -> (método, parâmetros extras). No AG, "genes_mut" é a média de genes mutados por filho
# (vira taxa_mut = genes_mut / número de genes livres) e "tam_pop" muda a população mantendo o
# orçamento (as gerações saem da conta orçamento // tam_pop - 1). O que não aparece fica no padrão
# de ag.algoritmo_genetico: 1 gene por filho, cruzamento de um ponto, k = 3, elite = 2.
CONFIGURACOES = {
    # sem IA
    "construtivo": ("construtivo", {}),
    "busca_aleatoria": ("busca_aleatoria", {}),
    "construtivo_rerolado": ("construtivo_rerolado", {}),
    # E0: comparação principal
    "ag_puro": ("ag", {"inicial": "aleatoria"}),
    "ag_semeado": ("ag", {"inicial": "construtivo"}),
    # E1: taxa de mutação (o de 1 gene por filho é o ag_puro)
    "ag_mut_0": ("ag", {"inicial": "aleatoria", "genes_mut": 0}),
    "ag_mut_0.5": ("ag", {"inicial": "aleatoria", "genes_mut": 0.5}),
    "ag_mut_2": ("ag", {"inicial": "aleatoria", "genes_mut": 2}),
    "ag_mut_5": ("ag", {"inicial": "aleatoria", "genes_mut": 5}),
    # E2: tipo de cruzamento (o de um ponto é o do E0)
    "ag_puro_por_zona": ("ag", {"inicial": "aleatoria", "cruzamento": "por_zona"}),
    "ag_semeado_por_zona": ("ag", {"inicial": "construtivo", "cruzamento": "por_zona"}),
    # E3 (opcional): população com o mesmo orçamento, e sem elitismo
    "ag_pop_100": ("ag", {"inicial": "aleatoria", "tam_pop": 100}),
    "ag_pop_400": ("ag", {"inicial": "aleatoria", "tam_pop": 400}),
    "ag_sem_elite": ("ag", {"inicial": "aleatoria", "elite": 0}),
}
BASELINES = ("construtivo", "busca_aleatoria", "construtivo_rerolado")
EXPERIMENTOS = {
    "baselines": BASELINES,
    "e0": ("ag_puro", "ag_semeado"),
    "e1": ("ag_mut_0", "ag_mut_0.5", "ag_mut_2", "ag_mut_5"),
    "e2": ("ag_puro_por_zona", "ag_semeado_por_zona"),
    "e3": ("ag_pop_100", "ag_pop_400", "ag_sem_elite"),
}


# ---------------------------------------------------------------- uma execução

def parametros_ag(extras, n_avaliacoes, inst=PADRAO):
    """Traduz os parâmetros de CONFIGURACOES nos argumentos de ag.algoritmo_genetico.

    Ex.: {"genes_mut": 2} com 60 200 avaliações -> tam_pop 200, geracoes 300, taxa_mut 2/281.
    Com tam_pop 400 o orçamento não divide exato: 60 200 // 400 - 1 = 149 gerações, ou seja,
    60 000 avaliações. O número real fica gravado na coluna n_avaliacoes.
    """
    args = dict(extras)
    tam_pop = args.pop("tam_pop", TAM_POP)
    args["tam_pop"] = tam_pop
    args["geracoes"] = max(1, n_avaliacoes // tam_pop - 1)
    if "genes_mut" in args:
        args["taxa_mut"] = args.pop("genes_mut") / len(inst.genes_livres)
    return args


def avaliacoes_do_passo(metodo, passo, n_avaliacoes, tam_pop=TAM_POP):
    """Quantas avaliações já tinham sido feitas no passo `passo` do histórico."""
    if metodo == "ag":
        return tam_pop * (passo + 1)                   # geração 0 = população inicial
    if metodo == "construtivo":
        return 1
    return min(INTERVALO_HISTORICO * (passo + 1), n_avaliacoes)


def executar(nome, semente, inst=PADRAO, n_avaliacoes=ORCAMENTO):
    """Roda uma configuração com uma semente.

    Devolve (linha, historicos, melhor): a linha da tabela (dict), as linhas do histórico
    (uma por geração ou a cada 200 avaliações) e o melhor cromossomo.
    """
    metodo, extras = CONFIGURACOES[nome]
    rng = random.Random(semente)
    inicio = time.perf_counter()
    primeiro_valido, tam_pop = None, TAM_POP
    if metodo == "construtivo":
        melhor, avaliacoes = gerar_construtivo(rng, inst), 1
        historico = None                               # preenchido depois da avaliação
    elif metodo == "busca_aleatoria":
        r = busca_aleatoria(n_avaliacoes, rng, inst, **extras)
    elif metodo == "construtivo_rerolado":
        r = construtivo_rerolado(n_avaliacoes, rng, inst)
    elif metodo == "ag":
        from gerador.ag import algoritmo_genetico
        args = parametros_ag(extras, n_avaliacoes, inst)
        tam_pop = args["tam_pop"]
        r = algoritmo_genetico(semente=semente, inst=inst, **args)
    else:
        raise ValueError(metodo)
    if metodo != "construtivo":
        melhor, avaliacoes, primeiro_valido, historico = r.melhor, r.n_avaliacoes, r.primeiro_valido, r.historico
    tempo = time.perf_counter() - inicio

    h, s, det = avaliar(melhor, inst)
    pen = penalidade_de(h, s, inst)
    if historico is None:
        historico = [pen]
    linha = {"configuracao": nome, "semente": semente, "penalidade": pen,
             "obrigatorias": h, "desejaveis": s, "valido": int(h == 0),
             "primeiro_valido": "" if primeiro_valido is None else primeiro_valido,
             "n_avaliacoes": avaliacoes, "tempo": round(tempo, 3)}
    linha.update({k: det[k] for k in CHAVES})
    historicos = [{"configuracao": nome, "semente": semente, "passo": p,
                   "avaliacoes": avaliacoes_do_passo(metodo, p, avaliacoes, tam_pop),
                   "melhor_penalidade": v}
                  for p, v in enumerate(historico)]
    return linha, historicos, list(melhor)


def rodar_execucao(nome, semente, inst=PADRAO, n_avaliacoes=ORCAMENTO):
    """Roda uma configuração com uma semente e devolve só a linha da tabela (dict)."""
    return executar(nome, semente, inst, n_avaliacoes)[0]


# ---------------------------------------------------------------- várias sementes

def _executar(args):
    return executar(*args)


def bateria_detalhada(nome, sementes=SEMENTES, inst=PADRAO, n_avaliacoes=ORCAMENTO, processos=1):
    """Roda uma configuração em várias sementes (em paralelo se processos > 1).

    Devolve a lista de (linha, historicos, melhor), na ordem das sementes.
    """
    tarefas = [(nome, s, inst, n_avaliacoes) for s in sementes]
    if processos <= 1:
        return [_executar(t) for t in tarefas]
    with ProcessPoolExecutor(max_workers=processos) as ex:
        return list(ex.map(_executar, tarefas))   # ex.map mantém a ordem das tarefas


def bateria(nome, sementes=SEMENTES, inst=PADRAO, n_avaliacoes=ORCAMENTO, processos=1):
    """Como bateria_detalhada, mas devolve só as linhas da tabela."""
    return [linha for linha, _, _ in bateria_detalhada(nome, sementes, inst, n_avaliacoes, processos)]


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


# ---------------------------------------------------------------- arquivos

def salvar_csv(linhas, arquivo):
    os.makedirs(os.path.dirname(arquivo) or ".", exist_ok=True)
    with open(arquivo, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)


def salvar_json(dados, arquivo):
    os.makedirs(os.path.dirname(arquivo) or ".", exist_ok=True)
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f)


def gravar(prefixo, resultados, pasta=PASTA):
    """Grava os quatro arquivos de um experimento. `resultados`: lista de (linha, historicos, melhor).

    Devolve os resumos (um por configuração, na ordem em que aparecem).
    """
    linhas = [linha for linha, _, _ in resultados]
    configs = list(dict.fromkeys(l["configuracao"] for l in linhas))
    resumos = [resumir([l for l in linhas if l["configuracao"] == c]) for c in configs]
    salvar_csv(linhas, os.path.join(pasta, f"{prefixo}_execucoes.csv"))
    salvar_csv(resumos, os.path.join(pasta, f"{prefixo}_resumo.csv"))
    salvar_csv([h for _, hs, _ in resultados for h in hs], os.path.join(pasta, f"{prefixo}_historicos.csv"))
    melhores = [{"configuracao": l["configuracao"], "semente": l["semente"],
                 "penalidade": l["penalidade"], "cromossomo": m} for l, _, m in resultados]
    salvar_json(melhores, os.path.join(pasta, f"{prefixo}_melhores.json"))
    return resumos


def rodar_experimento(prefixo, nomes, sementes=SEMENTES, inst=PADRAO, n_avaliacoes=ORCAMENTO,
                      processos=1, pasta=PASTA):
    """Roda cada configuração de `nomes` em todas as sementes e grava os arquivos de `prefixo`."""
    resultados = []
    for nome in nomes:
        resultados += bateria_detalhada(nome, sementes, inst, n_avaliacoes, processos)
        print(resumir([l for l, _, _ in resultados if l["configuracao"] == nome]))
    return gravar(prefixo, resultados, pasta)


# ---------------------------------------------------------------- ensaio de convergência (4.3)

def ultima_melhora(historico):
    """Último passo em que a melhor penalidade caiu (0 se nunca caiu).

    Ex.: [10, 8, 8, 5, 5, 5] -> 3. Se for menor que 150 em todas as sementes, a curva ficou plana
    antes da geração 150 e o orçamento pode ser cortado pela metade (PLANO.md, seção 4.3).
    """
    passo = 0
    for p in range(1, len(historico)):
        if historico[p] < historico[p - 1]:
            passo = p
    return passo


def ensaio(sementes=SEMENTES_ENSAIO, n_avaliacoes=ORCAMENTO, processos=1, pasta=PASTA, inst=PADRAO):
    """AG puro 200 x 300 em 3 sementes; grava ensaio_* e imprime o que decide o orçamento."""
    resultados = bateria_detalhada("ag_puro", sementes, inst, n_avaliacoes, processos)
    gravar("ensaio", resultados, pasta)
    metade = (n_avaliacoes // TAM_POP - 1) // 2
    ultimas = []
    for linha, hs, _ in resultados:
        hist = [h["melhor_penalidade"] for h in hs]
        ultimas.append(ultima_melhora(hist))
        print(f"semente {linha['semente']}: válido={linha['valido']}, penalidade final={linha['penalidade']}, "
              f"na geração {metade}={hist[min(metade, len(hist) - 1)]}, última melhora na geração {ultimas[-1]}, "
              f"primeiro válido na geração {linha['primeiro_valido'] or 'nunca'}")
    if max(ultimas) < metade:
        print(f"Curva plana antes da geração {metade} nas {len(ultimas)} sementes: dá para cortar o orçamento pela metade.")
    else:
        print(f"Ainda melhora depois da geração {metade}: manter o orçamento (PLANO.md, 4.3).")
    validos = sum(l["valido"] for l, _, _ in resultados)
    print(f"Válidos: {validos} de {len(resultados)}. A meta da seção 10 é 8 de 10 na bateria.")
    return resultados


# ---------------------------------------------------------------- comparação por tempo (6.4)

def orcamento_equivalente(tempo_referencia, tempo_metodo, n_avaliacoes=ORCAMENTO):
    """Quantas avaliações o método faz no mesmo tempo que a referência leva.

    Ex.: o AG leva 30 s e o rerolado leva 99 s para 60 200 avaliações -> 60 200 x 30 / 99 = 18 242.
    """
    return max(1, round(n_avaliacoes * tempo_referencia / tempo_metodo))


def ler_resumo(arquivo):
    """Lê um <exp>_resumo.csv e devolve {configuracao: linha (dict de textos)}."""
    with open(arquivo, encoding="utf-8") as f:
        return {l["configuracao"]: l for l in csv.DictReader(f)}


def por_tempo(referencia="ag_puro", sementes=SEMENTES, processos=1, pasta=PASTA, inst=PADRAO):
    """Roda a busca aleatória e o rerolado com o mesmo tempo médio da `referencia` (do e0_resumo.csv).

    Análise a mais, que não substitui a comparação por avaliações. Os tempos dependem da máquina e
    do número de processos: os do e0 e os dos baselines precisam ter sido medidos nas mesmas condições.
    """
    tempo_ref = float(ler_resumo(os.path.join(pasta, "e0_resumo.csv"))[referencia]["tempo_medio"])
    base = ler_resumo(os.path.join(pasta, "baselines_resumo.csv"))
    resultados = []
    for nome in ("busca_aleatoria", "construtivo_rerolado"):
        n = orcamento_equivalente(tempo_ref, float(base[nome]["tempo_medio"]))
        print(f"{nome}: {n} avaliações no tempo de {referencia} ({tempo_ref} s)")
        resultados += bateria_detalhada(nome, sementes, inst, n, processos)
    return gravar("tempo", resultados, pasta)


# ---------------------------------------------------------------- linha de comando

def _principal(argv=None):
    ap = argparse.ArgumentParser(description="Baterias de experimentos do gerador")
    ap.add_argument("quais", choices=[*EXPERIMENTOS, "ensaio", "tudo", "tempo"], help="o que rodar")
    ap.add_argument("--rapido", action="store_true",
                    help="2 sementes e 2000 avaliações; grava em resultados/rapido/")
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args(argv)
    sementes = SEMENTES_RAPIDO if a.rapido else SEMENTES
    orcamento = ORCAMENTO_RAPIDO if a.rapido else ORCAMENTO
    pasta = PASTA_RAPIDO if a.rapido else PASTA
    if a.quais == "ensaio":
        ensaio(SEMENTES_RAPIDO if a.rapido else SEMENTES_ENSAIO, orcamento, a.processos, pasta)
    elif a.quais == "tempo":
        por_tempo(sementes=sementes, processos=a.processos, pasta=pasta)
    else:
        for exp in (("e0", "e1", "e2") if a.quais == "tudo" else (a.quais,)):
            rodar_experimento(exp, EXPERIMENTOS[exp], sementes, n_avaliacoes=orcamento,
                              processos=a.processos, pasta=pasta)


if __name__ == "__main__":
    _principal()
