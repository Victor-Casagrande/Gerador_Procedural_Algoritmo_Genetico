"""Instância do problema: grade, zonas, início, saída, checkpoints e regras da penalidade.

Seções 2.1 e 2.4 do PLANO.md. Tudo aqui é fixo: nada deste módulo é evoluído pelo AG.
Papel responsável: A.

Layout do cromossomo (seção 2.2 do PLANO.md), zona por zona, da esquerda para a direita:
    para cada célula da zona, na ordem coluna por coluna, um bloco de 4 genes:
        [tipo, ligação leste, ligação sul, armadilha]
    depois do bloco da zona, os genes dos cartões que ficam nessa zona.
Na instância padrão: 96 células x 4 genes + 3 cartões = 387 posições, das quais 281 são livres.
"""
from typing import NamedTuple

# Valores dos genes de tipo de célula
VAZIA, CORREDOR, SALA, SALA_ESPECIAL = 0, 1, 2, 3
# Valores dos genes de ligação: 0 sem passagem, 1 aberta, 2/3/4 porta de nível 1/2/3.
# O nível exigido para atravessar é (valor - 1).
SEM_PASSAGEM, ABERTA = 0, 1
# Nomes dos campos de cada posição do cromossomo
TIPO, LESTE, SUL, ARMADILHA, CARTAO = "tipo", "leste", "sul", "armadilha", "cartao"
GENES_POR_CELULA = 4


class Regras(NamedTuple):
    """Parâmetros da penalidade (seção 2.4 do PLANO.md). Provisórios até 24/11."""
    ocup_min: int = 16                                   # H5: células ocupadas mínimas por zona
    faixa_especiais: tuple = ((2, 4), (2, 4), (1, 3))   # H4: salas especiais por zona
    faixa_armadilhas: tuple = (3, 6)                     # H6: armadilhas na zona das armadilhas
    alvo_becos: int = 2                                  # S1
    k_cartao: int = 6                                    # S3
    alvo_repetidos: int = 4                              # S4
    faixa_caminho: tuple = (30, 45)                      # S5: passos do caminho crítico
    teto_s: int = 19                                     # teto de cada desejável
    peso_h: int = 100
    peso_s: int = 1


class Instancia(NamedTuple):
    """Tudo o que é fixo. Criada uma vez por criar_instancia e só lida depois."""
    largura: int
    altura: int
    zonas: tuple            # faixa de colunas de cada zona, ex.: ((0, 3), (4, 7), (8, 11))
    inicio: int             # índice da célula de início
    saida: int              # índice da célula de saída
    checkpoints: tuple      # ((célula oeste, célula leste, nível exigido), ...), um entre cada par de zonas
    cartoes_zona: tuple     # cartões de cada zona, ex.: ((1, 2), (3,), ())
    zona_armadilhas: int    # zona em que armadilha vale (a Zona Pesada)
    regras: Regras
    # Tabelas derivadas, calculadas em criar_instancia:
    n_celulas: int
    n_genes: int
    celulas_zona: tuple     # por zona: tupla das células da zona, em ordem coluna por coluna
    zona_de: tuple          # por célula: índice da zona
    celulas_fixas: frozenset  # células que são sempre corredor
    entrada_zona: tuple     # por zona: célula fixa por onde o jogador entra na zona
    saida_zona: tuple       # por zona: célula fixa por onde o jogador sai da zona
    pos_bloco: tuple        # por célula: posição do primeiro gene (tipo) do bloco da célula
    pos_cartao: tuple       # por cartão (índice 0 = cartão 1): posição do gene
    campo: tuple            # por posição: TIPO, LESTE, SUL, ARMADILHA ou CARTAO
    dominio: tuple          # por posição: quantos valores o gene aceita (1 = fixo)
    valor_fixo: tuple       # por posição: o valor, quando fixo (senão None)
    genes_livres: tuple     # posições com domínio > 1
    fatia_zona: tuple       # por zona: (início, fim) do trecho do cromossomo


def celula_de(linha, coluna, altura):
    """Índice da célula na numeração coluna por coluna."""
    return coluna * altura + linha


def criar_instancia(largura, altura, zonas, inicio, saida, checkpoints,
                    cartoes_zona=((1, 2), (3,), ()), zona_armadilhas=1, regras=Regras()):
    """Monta a instância e todas as tabelas derivadas do cromossomo."""
    n_celulas = largura * altura
    celulas_zona = tuple(tuple(range(c0 * altura, (c1 + 1) * altura)) for c0, c1 in zonas)
    zona_de = [None] * n_celulas
    for z, cels in enumerate(celulas_zona):
        for i in cels:
            zona_de[i] = z
    if None in zona_de:
        raise ValueError("as zonas precisam cobrir todas as colunas da grade")
    if len(checkpoints) != len(zonas) - 1:
        raise ValueError("é preciso um checkpoint entre cada par de zonas vizinhas")

    entrada_zona = [inicio] + [leste for _, leste, _ in checkpoints]
    saida_zona = [oeste for oeste, _, _ in checkpoints] + [saida]
    celulas_fixas = frozenset([inicio, saida] + [c for o, l, _ in checkpoints for c in (o, l)])

    # Ligações leste com valor fixo: última coluna (não existe vizinha) e fronteiras entre zonas
    # (fechadas, menos os checkpoints, que têm a porta do nível exigido).
    leste_fixo = {}
    for i in range(n_celulas):
        linha, coluna = i % altura, i // altura
        if coluna == largura - 1:
            leste_fixo[i] = SEM_PASSAGEM
        elif zona_de[i] != zona_de[i + altura]:
            leste_fixo[i] = SEM_PASSAGEM
    for oeste, leste, nivel in checkpoints:
        if leste != oeste + altura or zona_de[oeste] == zona_de[leste]:
            raise ValueError("cada checkpoint liga duas células vizinhas na horizontal, de zonas diferentes")
        leste_fixo[oeste] = nivel + 1

    campo, dominio, valor_fixo = [], [], []
    pos_bloco = [None] * n_celulas
    pos_cartao = {}
    fatia_zona = []

    def adiciona(nome, dom, fixo=None):
        campo.append(nome)
        dominio.append(1 if fixo is not None else dom)
        valor_fixo.append(fixo)

    for z, cels in enumerate(celulas_zona):
        inicio_fatia = len(campo)
        for i in cels:
            linha = i % altura
            pos_bloco[i] = len(campo)
            adiciona(TIPO, 4, CORREDOR if i in celulas_fixas else None)
            adiciona(LESTE, 5, leste_fixo.get(i))
            adiciona(SUL, 5, SEM_PASSAGEM if linha == altura - 1 else None)
            adiciona(ARMADILHA, 2, None if z == zona_armadilhas else 0)
        for n in cartoes_zona[z]:
            pos_cartao[n] = len(campo)
            adiciona(CARTAO, len(cels))
        fatia_zona.append((inicio_fatia, len(campo)))

    cartoes = sorted(pos_cartao)
    if cartoes != list(range(1, len(cartoes) + 1)):
        raise ValueError("os cartões precisam ser numerados 1, 2, 3...")

    return Instancia(
        largura=largura, altura=altura, zonas=tuple(zonas), inicio=inicio, saida=saida,
        checkpoints=tuple(checkpoints), cartoes_zona=tuple(tuple(c) for c in cartoes_zona),
        zona_armadilhas=zona_armadilhas, regras=regras,
        n_celulas=n_celulas, n_genes=len(campo), celulas_zona=celulas_zona, zona_de=tuple(zona_de),
        celulas_fixas=celulas_fixas, entrada_zona=tuple(entrada_zona), saida_zona=tuple(saida_zona),
        pos_bloco=tuple(pos_bloco), pos_cartao=tuple(pos_cartao[n] for n in cartoes),
        campo=tuple(campo), dominio=tuple(dominio), valor_fixo=tuple(valor_fixo),
        genes_livres=tuple(p for p, d in enumerate(dominio) if d > 1), fatia_zona=tuple(fatia_zona),
    )


# Instância padrão (seção 2.1 do PLANO.md): grade 12 x 8, zonas em faixas de 4 colunas.
# Início (linha 3, coluna 0) = 3; saída (linha 4, coluna 11) = 92.
# Checkpoint A, nível 2, entre 25 (linha 1, coluna 3) e 33 (linha 1, coluna 4).
# Checkpoint B, nível 3, entre 62 (linha 6, coluna 7) e 70 (linha 6, coluna 8).
PADRAO = criar_instancia(
    largura=12, altura=8, zonas=((0, 3), (4, 7), (8, 11)),
    inicio=celula_de(3, 0, 8), saida=celula_de(4, 11, 8),
    checkpoints=((celula_de(1, 3, 8), celula_de(1, 4, 8), 2),
                 (celula_de(6, 7, 8), celula_de(6, 8, 8), 3)),
)


def instancia_teste(colunas_por_zona=1, altura=3, regras=None):
    """Grade pequena para testes: 3 zonas, sem as faixas de H4 a H6 (regras "zeradas").

    Início na linha 0 da primeira coluna; saída na última linha da última coluna; os
    checkpoints ficam na linha do meio. Os parâmetros das desejáveis são os padrões.
    """
    if regras is None:
        regras = Regras(ocup_min=0, faixa_especiais=((0, 99),) * 3, faixa_armadilhas=(0, 99))
    c = colunas_por_zona
    meio = altura // 2
    return criar_instancia(
        largura=3 * c, altura=altura, zonas=((0, c - 1), (c, 2 * c - 1), (2 * c, 3 * c - 1)),
        inicio=celula_de(0, 0, altura), saida=celula_de(altura - 1, 3 * c - 1, altura),
        checkpoints=((celula_de(meio, c - 1, altura), celula_de(meio, c, altura), 2),
                     (celula_de(meio, 2 * c - 1, altura), celula_de(meio, 2 * c, altura), 3)),
        regras=regras,
    )
