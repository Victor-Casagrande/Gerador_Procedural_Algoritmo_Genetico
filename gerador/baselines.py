"""Soluções sem IA: gerador construtivo, busca aleatória e construtivo rerolado.

Seção 3.4 do PLANO.md. Papel responsável: B.

Gerador construtivo, zona por zona (é o que jogos assim fazem, sem IA):
  1. um caminho aleatório (busca em profundidade com vizinhos em ordem sorteada) da célula de
     chegada da zona até a célula de saída da zona;
  2. a árvore cresce, ligando vizinhas sorteadas, até o tamanho sorteado
     (entre a ocupação mínima e 24 células);
  3. pontas da árvore viram salas especiais, na quantidade sorteada dentro da faixa da zona;
     as outras células viram corredor ou sala comum por sorteio;
  4. zona com dois cartões (a Zona Leve): uma aresta sorteada recebe porta de nível 1, o cartão 1
     fica numa sala do lado do início e o cartão 2 numa sala do outro lado; zona com um cartão
     (a Zona Pesada): o cartão numa sala sorteada;
  5. zona das armadilhas: de 3 a 6 armadilhas em corredores sorteados.
Por construção ele não viola nenhuma restrição obrigatória (testado em 1000 sementes).
"""
import time
from typing import NamedTuple

from gerador.aleatorio import gerar_aleatorio
from gerador.avaliacao import avaliar, penalidade_de
from gerador.config import CORREDOR, PADRAO, SALA, SALA_ESPECIAL
from gerador.representacao import (cromossomo_base, definir_armadilha, definir_cartao,
                                   definir_ligacao, definir_tipo)

INTERVALO_HISTORICO = 200   # a busca aleatória e o rerolado registram o melhor a cada 200 avaliações


class Resultado(NamedTuple):
    """O que uma execução de qualquer método de busca devolve."""
    melhor: list              # o melhor cromossomo visto
    historico: list           # melhor penalidade até cada geração (AG) ou a cada 200 avaliações
    n_avaliacoes: int
    primeiro_valido: object   # índice da avaliação (1 a n_avaliacoes), no AG e nas buscas, do primeiro mapa sem violação obrigatória; None se nunca
    tempo: float              # segundos


# ---------------------------------------------------------------- gerador construtivo

def _vizinhas_na_zona(i, inst, zona):
    h = inst.altura
    linha = i % h
    candidatas = []
    if linha > 0:
        candidatas.append(i - 1)          # norte
    if i + h < inst.n_celulas:
        candidatas.append(i + h)          # leste
    if linha < h - 1:
        candidatas.append(i + 1)          # sul
    if i - h >= 0:
        candidatas.append(i - h)          # oeste
    return [j for j in candidatas if inst.zona_de[j] == zona]


def _caminho_aleatorio(origem, destino, inst, zona, rng):
    """Busca em profundidade com vizinhos em ordem sorteada; para ao achar o destino."""
    pai = {origem: None}
    pilha = [origem]
    while pilha:
        i = pilha.pop()
        if i == destino:
            break
        viz = _vizinhas_na_zona(i, inst, zona)
        rng.shuffle(viz)
        for j in viz:
            if j not in pai:
                pai[j] = i
                pilha.append(j)
    caminho = [destino]
    while pai[caminho[-1]] is not None:
        caminho.append(pai[caminho[-1]])
    return caminho[::-1]


def _fronteira(arvore, inst, zona, evitar=frozenset()):
    """Pares (célula da árvore, vizinha fora da árvore), em ordem fixa."""
    pares = []
    for a in sorted(arvore):
        if a in evitar:
            continue
        for b in _vizinhas_na_zona(a, inst, zona):
            if b not in arvore:
                pares.append((a, b))
    return pares


def _grau(arestas):
    g = {}
    for a, b in arestas:
        g[a] = g.get(a, 0) + 1
        g[b] = g.get(b, 0) + 1
    return g


def _lado_do_inicio(arvore, arestas, aresta_cortada, origem):
    """Células alcançadas a partir de `origem` sem usar a aresta cortada."""
    adj = {i: [] for i in arvore}
    for a, b in arestas:
        if {a, b} != set(aresta_cortada):
            adj[a].append(b)
            adj[b].append(a)
    visto = {origem}
    pilha = [origem]
    while pilha:
        i = pilha.pop()
        for j in adj[i]:
            if j not in visto:
                visto.add(j)
                pilha.append(j)
    return visto


def gerar_construtivo(rng, inst=PADRAO):
    """Gera um mapa jogável por regras, sem otimizar a qualidade."""
    regras = inst.regras
    crom = cromossomo_base(inst)
    for z, cels in enumerate(inst.celulas_zona):
        entrada, saida_z = inst.entrada_zona[z], inst.saida_zona[z]
        fixas = inst.celulas_fixas

        # 1. caminho da chegada até a saída da zona
        caminho = _caminho_aleatorio(entrada, saida_z, inst, z, rng)
        arvore = set(caminho)
        arestas = list(zip(caminho, caminho[1:]))

        # 2. crescer até o tamanho sorteado
        tamanho = rng.randint(min(regras.ocup_min, len(cels)), min(24, len(cels)))
        # cada cartão precisa de uma sala própria, fora das células fixas
        precisa_livres = len(inst.cartoes_zona[z])
        while len(arvore) < tamanho or len(arvore - inst.celulas_fixas) < precisa_livres:
            pares = _fronteira(arvore, inst, z)
            if not pares:
                break
            a, b = rng.choice(pares)
            arvore.add(b)
            arestas.append((a, b))

        # 3. salas especiais nas pontas (cria pontas novas se faltar)
        lo, hi = regras.faixa_especiais[z]
        k = rng.randint(lo, min(hi, lo + 2))

        def pontas():
            g = _grau(arestas)
            return sorted(i for i in arvore if g.get(i, 0) == 1 and i not in fixas)

        while len(pontas()) < k:
            pares = _fronteira(arvore, inst, z, evitar=frozenset(pontas()))
            if not pares:
                break
            a, b = rng.choice(pares)
            arvore.add(b)
            arestas.append((a, b))
        especiais = set(rng.sample(pontas(), min(k, len(pontas()))))

        tipo = {}
        for i in sorted(arvore):
            if i in fixas:
                tipo[i] = CORREDOR
            elif i in especiais:
                tipo[i] = SALA_ESPECIAL
            else:
                tipo[i] = rng.choice((CORREDOR, SALA))

        # 4. cartões
        cartoes = inst.cartoes_zona[z]
        candidatas = sorted(i for i in arvore if i not in fixas)
        porta = None
        celula_cartao = {}
        if len(cartoes) == 1:
            celula_cartao[cartoes[0]] = rng.choice(candidatas)
        elif len(cartoes) == 2:
            ordem = list(arestas)
            rng.shuffle(ordem)
            for aresta in ordem:
                lado_a = _lado_do_inicio(arvore, arestas, aresta, entrada)
                cand_a = [i for i in candidatas if i in lado_a]
                cand_b = [i for i in candidatas if i not in lado_a]
                if cand_a and cand_b:
                    porta = aresta
                    celula_cartao[cartoes[0]] = rng.choice(cand_a)
                    celula_cartao[cartoes[1]] = rng.choice(cand_b)
                    break
            else:
                raise RuntimeError(f"zona {z}: não há aresta que separe duas salas para os cartões")
        elif len(cartoes) > 2:
            raise NotImplementedError("o construtivo trata no máximo 2 cartões por zona")
        for c in celula_cartao.values():
            if tipo[c] == CORREDOR:
                tipo[c] = SALA

        # 5. armadilhas em corredores
        armadilhas = []
        if z == inst.zona_armadilhas:
            lo, hi = regras.faixa_armadilhas
            corredores = sorted(i for i in arvore if tipo[i] == CORREDOR)
            salas_livres = sorted(i for i in arvore if tipo[i] == SALA and i not in celula_cartao.values())
            while len(corredores) < lo and salas_livres:
                s = salas_livres.pop(rng.randrange(len(salas_livres)))
                tipo[s] = CORREDOR
                corredores.append(s)
            if len(corredores) < lo:
                raise RuntimeError(f"zona {z}: corredores insuficientes para {lo} armadilhas")
            n = rng.randint(lo, min(hi, len(corredores)))
            armadilhas = rng.sample(sorted(corredores), n)

        # grava no cromossomo
        for i, t in tipo.items():
            if i not in fixas:
                definir_tipo(crom, i, t, inst)
        for a, b in arestas:
            definir_ligacao(crom, a, b, 2 if porta and {a, b} == set(porta) else 1, inst)
        for n, c in celula_cartao.items():
            definir_cartao(crom, n, c, inst)
        for i in armadilhas:
            definir_armadilha(crom, i, 1, inst)
    return crom


# ---------------------------------------------------------------- buscas com orçamento

def _melhor_de(gerar, n_avaliacoes, inst):
    """Gera n_avaliacoes mapas com `gerar()` e guarda o melhor."""
    inicio = time.perf_counter()
    melhor, melhor_pen = None, None
    historico, primeiro_valido = [], None
    for k in range(1, n_avaliacoes + 1):
        crom = gerar()
        h, s, _ = avaliar(crom, inst)
        pen = penalidade_de(h, s, inst)
        if melhor_pen is None or pen < melhor_pen:
            melhor, melhor_pen = crom, pen
        if h == 0 and primeiro_valido is None:
            primeiro_valido = k
        if k % INTERVALO_HISTORICO == 0 or k == n_avaliacoes:
            historico.append(melhor_pen)
    return Resultado(melhor, historico, n_avaliacoes, primeiro_valido, time.perf_counter() - inicio)


def busca_aleatoria(n_avaliacoes, rng, inst=PADRAO, pesos=None):
    """Melhor de n_avaliacoes mapas sorteados com a mesma função da população inicial do AG."""
    return _melhor_de(lambda: gerar_aleatorio(rng, inst, pesos), n_avaliacoes, inst)


def construtivo_rerolado(n_avaliacoes, rng, inst=PADRAO):
    """Melhor de n_avaliacoes mapas do construtivo (o "sortear outra semente" da prática)."""
    return _melhor_de(lambda: gerar_construtivo(rng, inst), n_avaliacoes, inst)
