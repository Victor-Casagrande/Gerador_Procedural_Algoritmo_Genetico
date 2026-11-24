"""Imagem do mapa: zonas, portas por nível, cartões, armadilhas e caminho crítico.

Seção 3.4 do PLANO.md. Fundo branco, para projetar. Papel responsável: B.

Legenda:
  células: corredor cinza claro, sala comum azul claro, sala especial (câmara) roxo claro,
           início verde, saída vermelho;
  passagens: aberta cinza; porta de nível 1 amarela, nível 2 laranja, nível 3 vermelha;
  C1, C2, C3: cartões; X: armadilha; linha preta tracejada: caminho crítico.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from gerador.config import CORREDOR, SALA, SALA_ESPECIAL

COR_TIPO = {CORREDOR: "#D9D9D9", SALA: "#BDD7EE", SALA_ESPECIAL: "#D9C2E9"}
COR_NIVEL = {0: "#7F7F7F", 1: "#E3B505", 2: "#ED7D31", 3: "#C00000"}
COR_ZONA = ["#F4FBF4", "#FFF7EE", "#F2F6FC"]
NOME_ZONA = ["Zona Leve", "Zona Pesada", "Zona de Entrada"]


def _xy(i, inst):
    """Centro da célula i: x = coluna, y = linha (linha 0 em cima)."""
    return i // inst.altura, i % inst.altura


def desenhar_mapa(mapa, ax=None, caminho=None, titulo=""):
    """Desenha um mapa já lido (representacao.decodificar). Devolve o Axes."""
    inst = mapa.inst
    if ax is None:
        _, ax = plt.subplots(figsize=(inst.largura * 0.62 + 0.6, inst.altura * 0.62 + 0.8), facecolor="white")
    ax.set_facecolor("white")

    for z, (c0, c1) in enumerate(inst.zonas):
        ax.add_patch(Rectangle((c0 - 0.5, -0.5), c1 - c0 + 1, inst.altura, facecolor=COR_ZONA[z % 3],
                               edgecolor="#BFBFBF", lw=1, zorder=0))
        ax.text((c0 + c1) / 2, -0.75, NOME_ZONA[z] if z < 3 else f"Zona {z}", ha="center", va="bottom",
                fontsize=8, color="#595959")

    for i, t in enumerate(mapa.tipo):
        if t == 0:
            continue
        x, y = _xy(i, inst)
        cor = COR_TIPO[t]
        if i == inst.inicio:
            cor = "#A9D18E"
        elif i == inst.saida:
            cor = "#F4B183"
        ax.add_patch(Rectangle((x - 0.32, y - 0.32), 0.64, 0.64, facecolor=cor, edgecolor="#404040",
                               lw=0.8, zorder=2))

    for i, vizinhas in enumerate(mapa.viz):
        for j, nivel in vizinhas:
            if j < i:
                continue
            (x1, y1), (x2, y2) = _xy(i, inst), _xy(j, inst)
            ax.plot([x1, x2], [y1, y2], color=COR_NIVEL[nivel], lw=2.2 if nivel == 0 else 4.5,
                    solid_capstyle="butt", zorder=1)

    for k, c in enumerate(mapa.cartao):
        x, y = _xy(c, inst)
        ax.text(x, y, f"C{k + 1}", ha="center", va="center", fontsize=8, fontweight="bold", zorder=4)
    for i in mapa.armadilha:
        x, y = _xy(i, inst)
        ax.text(x, y, "X", ha="center", va="center", fontsize=11, color="#C00000", fontweight="bold", zorder=4)

    if caminho:
        xs = [_xy(i, inst)[0] for i in caminho]
        ys = [_xy(i, inst)[1] for i in caminho]
        ax.plot(xs, ys, color="black", lw=1.2, ls="--", alpha=0.7, zorder=3)

    ax.set_xlim(-0.6, inst.largura - 0.4)
    ax.set_ylim(inst.altura - 0.4, -1.0)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for lado in ax.spines.values():
        lado.set_visible(False)
    if titulo:
        ax.set_title(titulo, fontsize=10)
    return ax


def desenhar_lado_a_lado(mapas, titulos, caminhos=None, arquivo=None):
    """Vários mapas lado a lado (por exemplo, construtivo x melhor do AG). Devolve a Figure."""
    n = len(mapas)
    inst = mapas[0].inst
    fig, eixos = plt.subplots(1, n, figsize=(n * (inst.largura * 0.62 + 0.6), inst.altura * 0.62 + 1.0),
                              facecolor="white")
    if n == 1:
        eixos = [eixos]
    for k, (mapa, ax) in enumerate(zip(mapas, eixos)):
        desenhar_mapa(mapa, ax=ax, caminho=caminhos[k] if caminhos else None, titulo=titulos[k])
    fig.tight_layout()
    if arquivo:
        fig.savefig(arquivo, dpi=150, facecolor="white")
    return fig
