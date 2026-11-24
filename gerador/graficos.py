"""Gráficos de convergência e dos experimentos, com fundo branco.

Seção 6.3 do PLANO.md. Papel responsável: C.

ESQUELETO (CP3, 24/11): as assinaturas estão definidas; o corpo é escrito pelo dono do módulo.
Os gráficos leem os CSV de resultados/ (gravados por experimentos.py) e salvam PNG em figuras/.
Fundo branco sempre (facecolor="white"): fundo escuro some no projetor.
"""


def grafico_convergencia(historicos, referencias, arquivo=None):
    """Média da melhor penalidade por geração nas sementes, com a faixa do mínimo ao máximo,
    eixo vertical em escala logarítmica (como no exemplo) e linhas horizontais de referência
    (construtivo, construtivo rerolado, busca aleatória). Devolve a Figure."""
    raise NotImplementedError


def grafico_parametro(resumos, rotulo_eixo, arquivo=None):
    """Um parâmetro (ex.: genes mutados por filho) x média das desejáveis, com a variação
    entre sementes. Devolve a Figure."""
    raise NotImplementedError


def grafico_desejaveis(resumos, arquivo=None):
    """Barras empilhadas de S1 a S5 por método: mostra O QUE cada método melhorou. Devolve a Figure."""
    raise NotImplementedError
