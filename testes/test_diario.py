"""O Diário de Bordo em Markdown gera um .docx sem erro (ferramentas/gerar_diario.py)."""
import os

import pytest

docx = pytest.importorskip("docx")

from ferramentas.gerar_diario import gerar  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_diario_gera_docx(tmp_path):
    saida = tmp_path / "Diario.docx"
    arquivos = gerar(os.path.join(RAIZ, "docs", "diario"), str(saida))
    assert len(arquivos) >= 10
    texto = "\n".join(p.text for p in docx.Document(str(saida)).paragraphs)
    assert "Ficha do Problema" in texto and "Registro de uso de IA" in texto
