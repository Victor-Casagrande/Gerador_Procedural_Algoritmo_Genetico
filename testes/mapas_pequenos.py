"""Mapas pequenos de resposta conhecida (PLANO.md, seção 5.1), na instancia_teste(2, 3).

A grade tem 6 colunas e 3 linhas, numeradas coluna por coluna:

    linha 0:  0   3 |  6   9 | 12  15
    linha 1:  1   4 |  7  10 | 13  16
    linha 2:  2   5 |  8  11 | 14  17
              Leve   Pesada   Entrada

Início = 0, saída = 17. Checkpoint A (nível 2) entre 4 e 7; checkpoint B (nível 3) entre 10 e 13.
Células sempre corredor: 0, 4, 7, 10, 13, 17. Regras "zeradas": sem faixas de H4 a H6.
"""
from gerador.config import CORREDOR, SALA, instancia_teste
from gerador.representacao import (cromossomo_base, definir_cartao, definir_ligacao, definir_tipo)

INST = instancia_teste(colunas_por_zona=2, altura=3)
ABERTA, PORTA1, PORTA2, PORTA3 = 1, 2, 3, 4


def m1_perfeito():
    """Tudo ligado, cada cartão antes da porta que ele abre.

    0-1-2 (cartão 1 em 2); 1-4; 4-3 porta de nível 1 (cartão 2 em 3); checkpoint 4-7;
    7-8 (cartão 3 em 8); 7-10; checkpoint 10-13; 13-16-17.
    Caminho crítico (13 passos): 0 1 2 1 4 3 4 7 8 7 10 13 16 17.
    """
    c = cromossomo_base(INST)
    for i in (1,):
        definir_tipo(c, i, CORREDOR, INST)
    for i in (2, 3, 8):
        definir_tipo(c, i, SALA, INST)
    definir_tipo(c, 16, CORREDOR, INST)
    definir_ligacao(c, 0, 1, ABERTA, INST)
    definir_ligacao(c, 1, 2, ABERTA, INST)
    definir_ligacao(c, 1, 4, ABERTA, INST)
    definir_ligacao(c, 4, 3, PORTA1, INST)
    definir_ligacao(c, 7, 8, ABERTA, INST)
    definir_ligacao(c, 7, 10, ABERTA, INST)
    definir_ligacao(c, 13, 16, ABERTA, INST)
    definir_ligacao(c, 16, 17, ABERTA, INST)
    definir_cartao(c, 1, 2, INST)
    definir_cartao(c, 2, 3, INST)
    definir_cartao(c, 3, 8, INST)
    return c


def m2_deadlock():
    """Igual ao M1, mas o cartão 2 está atrás de uma porta de nível 2: ninguém chega nele."""
    c = m1_perfeito()
    definir_ligacao(c, 4, 3, PORTA2, INST)
    return c


def m3_ilha():
    """Igual ao M1, mais um corredor solto na célula 5 (sem nenhuma ligação)."""
    c = m1_perfeito()
    definir_tipo(c, 5, CORREDOR, INST)
    return c


def m4_contraexemplo_monotonicidade():
    """Igual ao M1, mais uma sala na Zona Leve (célula 5) atrás de uma porta de nível 3.

    O jogador pega o cartão 3 na Zona Pesada, volta pelo checkpoint A e abre a sala. O mapa é
    válido, mas a fórmula de "monotonicidade" da especificação inicial o proibia.
    """
    c = m1_perfeito()
    definir_tipo(c, 5, SALA, INST)
    definir_ligacao(c, 4, 5, PORTA3, INST)
    return c
