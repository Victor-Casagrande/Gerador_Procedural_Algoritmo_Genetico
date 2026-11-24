"""Restrições H1 a H7 e S1 a S5, penalidade e aptidão.

Seção 2.4 do PLANO.md. Papel responsável: C.

penalidade = peso_h x (soma das H) + peso_s x (soma das S)
aptidão    = 1 / (1 + penalidade)

Cada S tem teto `teto_s` (19). Com 5 desejáveis, a soma máxima é 95 < 100 = peso_h: um mapa
com uma violação obrigatória sempre perde de qualquer mapa sem nenhuma.
"""
from gerador.config import PADRAO, SALA_ESPECIAL, VAZIA
from gerador.representacao import decodificar, e_sala
from gerador.validacao import caminho_critico, nivel_exigido, simular_inventario

N_DESEJAVEIS = 5
assert N_DESEJAVEIS * PADRAO.regras.teto_s < PADRAO.regras.peso_h, "o peso das obrigatórias não fecha"


def _distancia_da_faixa(valor, faixa):
    lo, hi = faixa
    return lo - valor if valor < lo else (valor - hi if valor > hi else 0)


# ---------------------------------------------------------------- obrigatórias (H)

def h1_saida_inalcancavel(mapa, alcancadas):
    return 0 if mapa.inst.saida in alcancadas else 1


def h2_celulas_inalcancaveis(mapa, alcancadas):
    return sum(1 for i, t in enumerate(mapa.tipo) if t != VAZIA and i not in alcancadas)


def h3_cartao_mal_colocado(mapa):
    """Cartão fora de sala, mais 1 para cada cartão que divide a célula com outro."""
    fora_de_sala = sum(1 for c in mapa.cartao if not e_sala(mapa.tipo[c]))
    repetidos = len(mapa.cartao) - len(set(mapa.cartao))
    return fora_de_sala + repetidos


def h4_salas_especiais_fora_da_faixa(mapa):
    inst = mapa.inst
    total = 0
    for z, cels in enumerate(inst.celulas_zona):
        n = sum(1 for i in cels if mapa.tipo[i] == SALA_ESPECIAL)
        total += _distancia_da_faixa(n, inst.regras.faixa_especiais[z])
    return total


def h5_zona_pouco_ocupada(mapa):
    inst = mapa.inst
    return sum(max(0, inst.regras.ocup_min - sum(1 for i in cels if mapa.tipo[i] != VAZIA))
               for cels in inst.celulas_zona)


def h6_armadilhas_fora_da_faixa(mapa):
    return _distancia_da_faixa(len(mapa.armadilha), mapa.inst.regras.faixa_armadilhas)


def h7_sala_especial_sem_entrada_unica(mapa):
    return sum(1 for i, t in enumerate(mapa.tipo) if t == SALA_ESPECIAL and len(mapa.viz[i]) != 1)


# ---------------------------------------------------------------- desejáveis (S), sem o teto

def becos(mapa):
    """Células com 1 ligação que não são sala especial, nem têm cartão, nem são início ou saída."""
    inst = mapa.inst
    excluidas = set(mapa.cartao) | {inst.inicio, inst.saida}
    return [i for i, t in enumerate(mapa.tipo)
            if t not in (VAZIA, SALA_ESPECIAL) and len(mapa.viz[i]) == 1 and i not in excluidas]


def s1_becos(mapa):
    return max(0, len(becos(mapa)) - mapa.inst.regras.alvo_becos)


def s2_armadilhas_no_caminho(mapa, caminho):
    return len(set(caminho) & mapa.armadilha)


def distancia_cartao_porta(mapa, caminho, n):
    """Passos entre pisar na célula do cartão n e atravessar a primeira porta de nível n depois.

    0 se o cartão não é pego no caminho ou se nenhuma porta de nível n é atravessada depois.
    """
    c = mapa.cartao[n - 1]
    if c not in caminho:
        return 0
    p = caminho.index(c)
    for k in range(p, len(caminho) - 1):
        if nivel_exigido(mapa, caminho[k], caminho[k + 1]) == n:
            return k + 1 - p
    return 0


def s3_cartao_perto_da_porta(mapa, caminho):
    k = mapa.inst.regras.k_cartao
    return sum(max(0, k - distancia_cartao_porta(mapa, caminho, n))
               for n in range(1, len(mapa.cartao) + 1))


def s4_passos_repetidos(mapa, caminho):
    repetidos = len(caminho) - len(set(caminho))
    return max(0, repetidos - mapa.inst.regras.alvo_repetidos)


def s5_comprimento_fora_da_faixa(mapa, caminho):
    return _distancia_da_faixa(len(caminho) - 1, mapa.inst.regras.faixa_caminho)


# ---------------------------------------------------------------- avaliação completa

def avaliar_mapa(mapa):
    """Devolve (obrigatórias, desejáveis, detalhes) de um mapa já lido."""
    regras = mapa.inst.regras
    alcancadas, _, _ = simular_inventario(mapa)
    caminho = caminho_critico(mapa)
    det = {
        "H1": h1_saida_inalcancavel(mapa, alcancadas),
        "H2": h2_celulas_inalcancaveis(mapa, alcancadas),
        "H3": h3_cartao_mal_colocado(mapa),
        "H4": h4_salas_especiais_fora_da_faixa(mapa),
        "H5": h5_zona_pouco_ocupada(mapa),
        "H6": h6_armadilhas_fora_da_faixa(mapa),
        "H7": h7_sala_especial_sem_entrada_unica(mapa),
        "S1": min(regras.teto_s, s1_becos(mapa)),
    }
    if caminho is None:
        for s in ("S2", "S3", "S4", "S5"):
            det[s] = regras.teto_s
    else:
        det["S2"] = min(regras.teto_s, s2_armadilhas_no_caminho(mapa, caminho))
        det["S3"] = min(regras.teto_s, s3_cartao_perto_da_porta(mapa, caminho))
        det["S4"] = min(regras.teto_s, s4_passos_repetidos(mapa, caminho))
        det["S5"] = min(regras.teto_s, s5_comprimento_fora_da_faixa(mapa, caminho))
    hard = sum(v for k, v in det.items() if k[0] == "H")
    soft = sum(v for k, v in det.items() if k[0] == "S")
    return hard, soft, det


def avaliar(crom, inst=PADRAO):
    """Devolve (obrigatórias, desejáveis, detalhes), como no projeto exemplo."""
    return avaliar_mapa(decodificar(crom, inst))


def penalidade_de(hard, soft, inst=PADRAO):
    return inst.regras.peso_h * hard + inst.regras.peso_s * soft


def penalidade(crom, inst=PADRAO):
    h, s, _ = avaliar(crom, inst)
    return penalidade_de(h, s, inst)


def aptidao(crom, inst=PADRAO):
    return 1 / (1 + penalidade(crom, inst))
