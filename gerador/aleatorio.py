"""Gerador aleatório de cromossomos, usado pela população inicial do AG e pela busca aleatória.

Seções 1.3 (D7) e 3.4 do PLANO.md. A busca aleatória e o AG usam ESTA mesma função, para a
comparação entre os dois ser justa (mesma distribuição de sorteio).
Papel responsável: B.
"""
from gerador.config import PADRAO


def gerar_aleatorio(rng, inst=PADRAO, pesos=None):
    """Sorteia um cromossomo: genes fixos com o valor fixo, genes livres no domínio deles.

    pesos=None: sorteio uniforme em cada gene livre (a configuração principal).
    pesos={campo: [peso de cada valor]}: sorteio enviesado só nos campos citados, por exemplo
    {"leste": [3, 4, 1, 1, 1], "sul": [3, 4, 1, 1, 1]} para mais passagens abertas e menos portas
    (alavanca do PLANO.md, seção 10). Se usado, a busca aleatória usa os mesmos pesos.
    """
    crom = []
    for p, dom in enumerate(inst.dominio):
        fixo = inst.valor_fixo[p]
        if fixo is not None:
            crom.append(fixo)
        elif pesos and inst.campo[p] in pesos:
            crom.append(rng.choices(range(dom), weights=pesos[inst.campo[p]])[0])
        else:
            crom.append(rng.randrange(dom))
    return crom
