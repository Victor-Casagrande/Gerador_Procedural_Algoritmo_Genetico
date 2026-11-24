"""População inicial e laço do algoritmo genético, com contador de avaliações.

Seções 2.2 e 3.4 do PLANO.md. Papel responsável: C.

ESQUELETO (CP3, 24/11): as assinaturas estão definidas; o corpo é escrito pelo dono do módulo.
O laço é o do projeto exemplo (Projeto_Exemplo_Horarios_AG.ipynb, seção 4), com três diferenças:
  1. conta as avaliações (n_avaliacoes == tam_pop x (geracoes + 1));
  2. guarda a geração do primeiro mapa sem violação obrigatória (Resultado.primeiro_valido);
  3. avalia cada indivíduo uma vez só por geração (guarda a penalidade junto).
Devolve um baselines.Resultado, o mesmo tipo da busca aleatória e do rerolado.
"""
from gerador.config import PADRAO


def populacao_inicial(tam_pop, rng, inst=PADRAO, inicial="aleatoria"):
    """inicial="aleatoria": aleatorio.gerar_aleatorio (a mesma função da busca aleatória).
    inicial="construtivo": baselines.gerar_construtivo (o AG semeado, experimento e plano B).
    """
    raise NotImplementedError


def algoritmo_genetico(tam_pop=200, geracoes=300, taxa_cruz=0.9, taxa_mut=None, k=3, elite=2,
                       cruzamento="um_ponto", inicial="aleatoria", semente=42, inst=PADRAO):
    """Torneio (k), cruzamento ("um_ponto" ou "por_zona") com probabilidade taxa_cruz, mutação
    (taxa_mut=None: 1 / número de genes livres, em média 1 gene por filho) e elitismo (elite).

    Cria o próprio random.Random(semente) e passa adiante. Devolve baselines.Resultado com
    historico = melhor penalidade de cada geração (geracoes + 1 valores).
    """
    raise NotImplementedError
