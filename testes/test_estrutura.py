"""Teste de fumaça: todos os módulos do pacote existem e podem ser importados.

Os testes de cada módulo ficam em testes/test_<modulo>.py (PLANO.md, seção 5).
"""
import importlib

MODULOS = ["config", "representacao", "validacao", "aleatorio", "avaliacao", "baselines",
           "operadores", "ag", "experimentos", "desenho", "graficos"]


def test_modulos_importam():
    for nome in MODULOS:
        importlib.import_module(f"gerador.{nome}")
