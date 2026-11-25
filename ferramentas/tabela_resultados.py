"""Escreve as tabelas de resultados do Diário e do ESTADO.md a partir dos CSV de resultados/.

Uso, na raiz do repositório (depois de rodar os experimentos):
    python ferramentas/tabela_resultados.py
    python ferramentas/tabela_resultados.py --conferir   # só diz se as tabelas estão desatualizadas

Nenhum número das tabelas é digitado à mão: eles saem de resultados/<exp>_resumo.csv e
resultados/<exp>_execucoes.csv, gravados por gerador/experimentos.py. Cada tabela fica entre dois
marcadores no Markdown, que o gerar_diario.py não copia para o .docx:
    <!-- tabela:e0 -->            ... <!-- /tabela:e0 -->            (docs/diario/08_resultados.md)
    <!-- tabela:parametros -->    ... <!-- /tabela:parametros -->    (docs/diario/08_resultados.md)
    <!-- tabela:estado -->        ... <!-- /tabela:estado -->        (docs/ESTADO.md)
Só o que está entre os marcadores é trocado; o resto do arquivo fica como está. Configuração que
ainda não rodou aparece com as células vazias.
"""
import argparse
import csv
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA = os.path.join(RAIZ, "resultados")
EXPERIMENTOS = ("baselines", "e0", "e1", "e2", "e3")

# (configuração, rótulo na tabela)
LINHAS_E0 = (("construtivo", "Construtivo"), ("busca_aleatoria", "Busca aleatória"),
             ("construtivo_rerolado", "Construtivo rerolado"), ("ag_puro", "AG puro (principal)"),
             ("ag_semeado", "AG semeado"))
LINHAS_PARAMETROS = (("ag_mut_0", "E1: 0 genes por filho"), ("ag_mut_0.5", "E1: 0,5 genes por filho"),
                     ("ag_puro", "E1: 1 gene por filho (padrão)"), ("ag_mut_2", "E1: 2 genes por filho"),
                     ("ag_mut_5", "E1: 5 genes por filho"),
                     ("ag_puro_por_zona", "E2: AG puro, cruzamento por zona"),
                     ("ag_semeado_por_zona", "E2: AG semeado, cruzamento por zona"),
                     ("ag_pop_100", "E3: população 100"), ("ag_pop_400", "E3: população 400"),
                     ("ag_sem_elite", "E3: sem elitismo"))


# ---------------------------------------------------------------- leitura

def _ler_csv(arquivo):
    with open(arquivo, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ler_resultados(pasta=PASTA):
    """{configuracao: {"resumo": linha do resumo, "execucoes": linhas, "arquivo": nome do resumo}}.

    Lê os experimentos em ordem; se uma configuração aparece em dois, vale o último.
    """
    dados = {}
    for exp in EXPERIMENTOS:
        arq_resumo = os.path.join(pasta, f"{exp}_resumo.csv")
        arq_exec = os.path.join(pasta, f"{exp}_execucoes.csv")
        if not os.path.exists(arq_resumo):
            continue
        execucoes = _ler_csv(arq_exec) if os.path.exists(arq_exec) else []
        for r in _ler_csv(arq_resumo):
            c = r["configuracao"]
            dados[c] = {"resumo": r, "arquivo": f"{exp}_resumo.csv",
                        "execucoes": [e for e in execucoes if e["configuracao"] == c]}
    return dados


# ---------------------------------------------------------------- formatação

def numero(texto):
    """'18.90' -> '18,9'; '0' -> '0'; '2379.3' -> '2379,3' (vírgula decimal, sem zeros sobrando)."""
    v = float(texto)
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s.replace(".", ",")


def milhar(n):
    """60200 -> '60 200'."""
    return f"{int(n):,}".replace(",", " ")


def tempo(texto):
    """Tempo médio por execução: '0.001' -> '~0,001 s'; '26.114' -> '~26 s'."""
    v = float(texto)
    if v >= 1:
        return f"~{round(v)} s"
    return "~" + f"{v:.3f}".rstrip("0").rstrip(".").replace(".", ",") + " s"


def sementes(execucoes):
    ss = sorted(int(e["semente"]) for e in execucoes)
    if not ss:
        return ""
    return f"{ss[0]} a {ss[-1]}" if ss == list(range(ss[0], ss[-1] + 1)) else ", ".join(map(str, ss))


def desejaveis(r):
    return f"{numero(r['desejaveis_media'])} ({r['desejaveis_melhor']} – {r['desejaveis_pior']})"


def _linha(celulas):
    return "| " + " | ".join(celulas) + " |"


# ---------------------------------------------------------------- tabelas

def tabela_e0(dados):
    """A tabela do E0 no formato do 08_resultados.md."""
    cab = ["Método", "Sementes", "Válidos em 10", "Obrigatórias (média)",
           "Desejáveis: média (melhor – pior)", "Tempo", "Observações"]
    linhas = [_linha(cab), "|" + "---|" * len(cab)]
    for conf, rotulo in LINHAS_E0:
        if conf not in dados:
            linhas.append(_linha([rotulo] + [""] * (len(cab) - 1)))
            continue
        d = dados[conf]
        r, ex = d["resumo"], d["execucoes"]
        obs = f"`resultados/{d['arquivo']}`"
        if ex and conf != "construtivo":
            obs += f", {milhar(ex[0]['n_avaliacoes'])} avaliações"
        linhas.append(_linha([rotulo, sementes(ex), r["validos"], numero(r["obrigatorias_media"]),
                              desejaveis(r), tempo(r["tempo_medio"]), obs]))
    return "\n".join(linhas)


def tabela_parametros(dados):
    """A tabela do E1, E2 e E3 (formato da Tabela 15 do projeto exemplo). E3 só se já rodou."""
    cab = ["Configuração (demais parâmetros no padrão)", "Válidos em 10", "Obrigatórias (média)",
           "Desejáveis (média)"]
    linhas = [_linha(cab), "|" + "---|" * len(cab)]
    for conf, rotulo in LINHAS_PARAMETROS:
        if conf not in dados:
            if not rotulo.startswith("E3"):
                linhas.append(_linha([rotulo, "", "", ""]))
            continue
        r = dados[conf]["resumo"]
        linhas.append(_linha([rotulo, r["validos"], numero(r["obrigatorias_media"]),
                              numero(r["desejaveis_media"])]))
    return "\n".join(linhas)


def tabela_estado(dados):
    """A tabela resumida do ESTADO.md: só as configurações do E0 que já rodaram."""
    cab = ["Método", "Válidos em 10", "Obrigatórias (média)", "Desejáveis: média (melhor – pior)",
           "Penalidade (média)", "Tempo por execução"]
    linhas = [_linha(cab), "|" + "---|" * len(cab)]
    for conf, rotulo in LINHAS_E0:
        if conf in dados:
            r = dados[conf]["resumo"]
            linhas.append(_linha([rotulo, r["validos"], numero(r["obrigatorias_media"]), desejaveis(r),
                                  numero(r["penalidade_media"]), tempo(r["tempo_medio"])]))
    return "\n".join(linhas)


# ---------------------------------------------------------------- escrita

def trocar_entre_marcadores(texto, nome, conteudo):
    """Troca o que está entre <!-- tabela:nome --> e <!-- /tabela:nome --> por `conteudo`."""
    padrao = re.compile(rf"(<!-- tabela:{re.escape(nome)} -->\n).*?(\n<!-- /tabela:{re.escape(nome)} -->)", re.S)
    if not padrao.search(texto):
        raise ValueError(f"marcadores da tabela '{nome}' não encontrados")
    return padrao.sub(lambda m: m.group(1) + conteudo + m.group(2), texto, count=1)


def atualizar(arquivo, tabelas):
    """Aplica {nome: conteúdo} no arquivo. Devolve True se algo mudou."""
    with open(arquivo, encoding="utf-8") as f:
        antes = f.read()
    depois = antes
    for nome, conteudo in tabelas.items():
        depois = trocar_entre_marcadores(depois, nome, conteudo)
    if depois != antes:
        with open(arquivo, "w", encoding="utf-8", newline="\n") as f:
            f.write(depois)
    return depois != antes


def _principal():
    ap = argparse.ArgumentParser(description="Tabelas do Diário e do ESTADO.md a partir de resultados/")
    ap.add_argument("--pasta", default=PASTA)
    ap.add_argument("--conferir", action="store_true", help="não grava; sai com erro se algo mudaria")
    a = ap.parse_args()
    dados = ler_resultados(a.pasta)
    alvos = {os.path.join(RAIZ, "docs", "diario", "08_resultados.md"):
             {"e0": tabela_e0(dados), "parametros": tabela_parametros(dados)},
             os.path.join(RAIZ, "docs", "ESTADO.md"): {"estado": tabela_estado(dados)}}
    desatualizados = []
    for arquivo, tabelas in alvos.items():
        if a.conferir:
            with open(arquivo, encoding="utf-8") as f:
                texto = f.read()
            novo = texto
            for nome, conteudo in tabelas.items():
                novo = trocar_entre_marcadores(novo, nome, conteudo)
            if novo != texto:
                desatualizados.append(arquivo)
        elif atualizar(arquivo, tabelas):
            print(f"atualizado: {os.path.relpath(arquivo, RAIZ)}")
    if a.conferir:
        for arq in desatualizados:
            print(f"desatualizado: {os.path.relpath(arq, RAIZ)}")
        raise SystemExit(1 if desatualizados else 0)
    print(f"{len(dados)} configurações lidas de {os.path.relpath(a.pasta, RAIZ)}")


if __name__ == "__main__":
    _principal()
