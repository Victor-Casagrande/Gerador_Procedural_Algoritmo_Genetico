"""População inicial e laço do algoritmo genético, com contador de avaliações.

Seções 2.2 e 3.4 do PLANO.md. Papel responsável: C.

O laço é o do projeto exemplo (seção 4), com três diferenças:
  1. conta as avaliações (n_avaliacoes == tam_pop x (geracoes + 1));
  2. guarda o índice da avaliação do primeiro mapa sem violação obrigatória
     (Resultado.primeiro_valido, de 1 a n_avaliacoes, a mesma unidade das buscas);
  3. avalia cada indivíduo uma vez só por geração (guarda a penalidade junto).
Devolve um baselines.Resultado, o mesmo tipo da busca aleatória e do rerolado.

Fórmulas (phi = penalidade, f = aptidão, N = tam_pop, G = geracoes):
    (H, S) = avaliar(x)        phi = peso_h x H + peso_s x S        f = 1 / (1 + phi)
    elite: os `elite` menores phi, ordenados por (phi, índice), passam por cópia
    filhos: dois torneios; com probabilidade taxa_cruz cruza, senão copia; muta os dois
    historico[g] = menor phi visto até a geração g (nunca sobe)
"""
import random
import time

from gerador.aleatorio import gerar_aleatorio
from gerador.avaliacao import avaliar, penalidade_de
from gerador.baselines import Resultado, gerar_construtivo
from gerador.config import PADRAO
from gerador.operadores import cruzamento_por_zona, cruzamento_um_ponto, mutacao, selecao_torneio


def populacao_inicial(tam_pop, rng, inst=PADRAO, inicial="aleatoria"):
    """inicial="aleatoria": aleatorio.gerar_aleatorio (a mesma função da busca aleatória).
    inicial="construtivo": baselines.gerar_construtivo (o AG semeado, experimento e plano B).
    Não avalia: só gera tam_pop cromossomos com o `rng` recebido.
    """
    if inicial == "aleatoria":
        return [gerar_aleatorio(rng, inst) for _ in range(tam_pop)]
    if inicial == "construtivo":
        return [gerar_construtivo(rng, inst) for _ in range(tam_pop)]
    raise ValueError(f"inicial deve ser 'aleatoria' ou 'construtivo', veio {inicial!r}")


def _avaliar_populacao(pop, inst):
    """Avalia cada indivíduo uma vez. Devolve (penalidades, validos), com validos[i] = (H == 0)."""
    penalidades, validos = [], []
    for crom in pop:
        h, s, _ = avaliar(crom, inst)
        penalidades.append(penalidade_de(h, s, inst))
        validos.append(h == 0)
    return penalidades, validos


def _elite(pop, penalidades, n_elite):
    """Cópias dos n_elite menores phi; o empate fica com o menor índice."""
    ordem = sorted(range(len(pop)), key=lambda i: (penalidades[i], i))
    return [list(pop[i]) for i in ordem[:n_elite]]


def _cruzar(p1, p2, cruzamento, rng, inst):
    if cruzamento == "um_ponto":
        return cruzamento_um_ponto(p1, p2, rng)
    return cruzamento_por_zona(p1, p2, rng, inst)


def _filhos(pop, aptidoes, n_filhos, taxa_cruz, taxa_mut, k, cruzamento, rng, inst):
    """Pares de filhos até ter n_filhos: dois torneios, uma moeda para o par, mutação nos dois."""
    filhos = []
    while len(filhos) < n_filhos:
        p1 = selecao_torneio(pop, aptidoes, k, rng)
        p2 = selecao_torneio(pop, aptidoes, k, rng)
        if rng.random() < taxa_cruz:
            c1, c2 = _cruzar(p1, p2, cruzamento, rng, inst)
        else:
            c1, c2 = p1, p2          # o torneio já devolve cópias
        filhos.append(mutacao(c1, taxa_mut, rng, inst))
        filhos.append(mutacao(c2, taxa_mut, rng, inst))
    return filhos[:n_filhos]


def _conferir_parametros(tam_pop, geracoes, taxa_cruz, taxa_mut, k, elite, cruzamento):
    if tam_pop < 1 or geracoes < 0:
        raise ValueError("tam_pop deve ser >= 1 e geracoes >= 0")
    if not 0 <= elite <= tam_pop:
        raise ValueError("elite deve estar entre 0 e tam_pop")
    if not 1 <= k <= tam_pop:
        raise ValueError("k deve estar entre 1 e tam_pop")
    if not 0 <= taxa_cruz <= 1 or not 0 <= taxa_mut <= 1:
        raise ValueError("taxa_cruz e taxa_mut devem estar entre 0 e 1")
    if cruzamento not in ("um_ponto", "por_zona"):
        raise ValueError(f"cruzamento deve ser 'um_ponto' ou 'por_zona', veio {cruzamento!r}")


def algoritmo_genetico(tam_pop=200, geracoes=300, taxa_cruz=0.9, taxa_mut=None, k=3, elite=2,
                       cruzamento="um_ponto", inicial="aleatoria", semente=42, inst=PADRAO):
    """Torneio (k), cruzamento ("um_ponto" ou "por_zona") com probabilidade taxa_cruz, mutação
    (taxa_mut=None: 1 / número de genes livres, em média 1 gene por filho) e elitismo (elite).

    Cria o próprio random.Random(semente) e passa adiante. Devolve baselines.Resultado com
    historico = melhor penalidade vista até cada geração (geracoes + 1 valores) e
    primeiro_valido = índice da avaliação (1 a n_avaliacoes) do primeiro mapa com H = 0.
    """
    if taxa_mut is None:
        taxa_mut = 1 / len(inst.genes_livres)
    _conferir_parametros(tam_pop, geracoes, taxa_cruz, taxa_mut, k, elite, cruzamento)

    inicio = time.perf_counter()
    rng = random.Random(semente)
    pop = populacao_inicial(tam_pop, rng, inst, inicial)
    melhor, melhor_pen = None, None
    historico, primeiro_valido = [], None

    for g in range(geracoes + 1):
        penalidades, validos = _avaliar_populacao(pop, inst)
        i_g = min(range(tam_pop), key=lambda i: (penalidades[i], i))
        if melhor_pen is None or penalidades[i_g] < melhor_pen:
            melhor, melhor_pen = list(pop[i_g]), penalidades[i_g]
        historico.append(melhor_pen)
        if primeiro_valido is None and True in validos:
            primeiro_valido = g * tam_pop + validos.index(True) + 1
        if g == geracoes:
            break
        aptidoes = [1 / (1 + p) for p in penalidades]
        proxima = _elite(pop, penalidades, elite)
        proxima += _filhos(pop, aptidoes, tam_pop - elite, taxa_cruz, taxa_mut, k, cruzamento,
                           rng, inst)
        pop = proxima

    return Resultado(melhor, historico, tam_pop * (geracoes + 1), primeiro_valido,
                     time.perf_counter() - inicio)
