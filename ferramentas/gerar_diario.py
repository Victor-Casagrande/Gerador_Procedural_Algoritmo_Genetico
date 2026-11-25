"""Gera o Diário de Bordo (.docx) a partir dos arquivos Markdown de docs/diario/.

Uso, na raiz do repositório:
    python ferramentas/gerar_diario.py
    python ferramentas/gerar_diario.py --saida entrega/Diario_de_Bordo.docx

Para o PDF da entrega: abrir o .docx no Word (ou LibreOffice) e salvar como PDF.

Entende o Markdown que o Diário usa: títulos (#, ##, ###), parágrafos com **negrito**, *itálico*,
`código` e [links](url), listas com "- " e "1. ", tabelas com "|" e citações com "> " (que viram
um quadro destacado). Cada arquivo começa numa página nova.
"""
import argparse
import glob
import os
import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

AZUL = RGBColor(0x1F, 0x4E, 0x79)
FONTE = "Arial"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PADRAO_INLINE = re.compile(r"(\*\*.+?\*\*|`.+?`|\*.+?\*|\[.+?\]\(.+?\))")


def _sombrear(celula, cor):
    tc_pr = celula._tc.get_or_add_tcPr()
    sombra = OxmlElement("w:shd")
    sombra.set(qn("w:val"), "clear")
    sombra.set(qn("w:color"), "auto")
    sombra.set(qn("w:fill"), cor)
    tc_pr.append(sombra)


def _texto_inline(paragrafo, texto, negrito=False, tamanho=None, cor=None):
    """Escreve o texto com **negrito**, *itálico*, `código` e [link](url) (o link vira só o texto)."""
    for parte in PADRAO_INLINE.split(texto):
        if not parte:
            continue
        run_negrito, run_italico, run_codigo = negrito, False, False
        if parte.startswith("**") and parte.endswith("**"):
            parte, run_negrito = parte[2:-2], True
        elif parte.startswith("`") and parte.endswith("`"):
            parte, run_codigo = parte[1:-1], True
        elif parte.startswith("[") and "](" in parte:
            parte = parte[1:parte.index("](")]
        elif parte.startswith("*") and parte.endswith("*") and len(parte) > 2:
            parte, run_italico = parte[1:-1], True
        run = paragrafo.add_run(parte)
        run.bold = run_negrito
        run.italic = run_italico
        run.font.name = "Consolas" if run_codigo else FONTE
        if tamanho:
            run.font.size = Pt(tamanho)
        if cor is not None:
            run.font.color.rgb = cor


def _celulas(linha):
    return [c.strip() for c in linha.strip().strip("|").split("|")]


def _tabela(doc, linhas):
    cabecalho = _celulas(linhas[0])
    corpo = [_celulas(l) for l in linhas[2:]]          # linhas[1] é o separador |---|
    tamanho = 7.5 if len(cabecalho) >= 7 else 9        # tabelas largas com letra menor
    tabela = doc.add_table(rows=1 + len(corpo), cols=len(cabecalho))
    tabela.style = "Table Grid"
    tabela.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, texto in enumerate(cabecalho):
        cel = tabela.rows[0].cells[j]
        _sombrear(cel, "1F4E79")
        _texto_inline(cel.paragraphs[0], texto, negrito=True, tamanho=tamanho, cor=RGBColor(0xFF, 0xFF, 0xFF))
    for i, linha in enumerate(corpo, start=1):
        for j in range(len(cabecalho)):
            texto = linha[j] if j < len(linha) else ""
            cel = tabela.rows[i].cells[j]
            if j == 0 and len(cabecalho) == 2:
                _sombrear(cel, "F2F2F2")
            _texto_inline(cel.paragraphs[0], texto, negrito=(j == 0 and len(cabecalho) == 2), tamanho=tamanho)
    doc.add_paragraph()


def _citacao(doc, texto):
    tabela = doc.add_table(rows=1, cols=1)
    cel = tabela.rows[0].cells[0]
    _sombrear(cel, "FFF4CE")
    _texto_inline(cel.paragraphs[0], texto, tamanho=9)
    doc.add_paragraph()


def adicionar_markdown(doc, texto):
    linhas = texto.splitlines()
    k = 0
    paragrafo_aberto = []

    def fecha_paragrafo():
        if paragrafo_aberto:
            p = doc.add_paragraph()
            _texto_inline(p, " ".join(paragrafo_aberto))
            paragrafo_aberto.clear()

    while k < len(linhas):
        linha = linhas[k]
        s = linha.strip()
        if not s:
            fecha_paragrafo()
            k += 1
        elif s.startswith("<!--") and s.endswith("-->"):   # comentário (ex.: marcador de tabela): não vai para o .docx
            k += 1
        elif s.startswith("```"):                    # bloco de código: copia como está
            fecha_paragrafo()
            k += 1
            while k < len(linhas) and not linhas[k].strip().startswith("```"):
                p = doc.add_paragraph()
                _texto_inline(p, "`" + linhas[k] + "`" if linhas[k].strip() else "")
                k += 1
            k += 1
        elif s.startswith("#"):
            fecha_paragrafo()
            nivel = len(s) - len(s.lstrip("#"))
            titulo = doc.add_heading(level=min(nivel, 3))
            _texto_inline(titulo, s[nivel:].strip(), cor=AZUL)
            k += 1
        elif s.startswith("|"):
            fecha_paragrafo()
            bloco = []
            while k < len(linhas) and linhas[k].strip().startswith("|"):
                bloco.append(linhas[k])
                k += 1
            _tabela(doc, bloco)
        elif s.startswith(">"):
            fecha_paragrafo()
            bloco = []
            while k < len(linhas) and linhas[k].strip().startswith(">"):
                bloco.append(linhas[k].strip()[1:].strip())
                k += 1
            _citacao(doc, " ".join(bloco))
        elif s.startswith("- "):
            fecha_paragrafo()
            p = doc.add_paragraph(style="List Bullet")
            _texto_inline(p, s[2:])
            k += 1
        elif re.match(r"^\d+\. ", s):
            fecha_paragrafo()
            # numeração escrita no texto: o estilo "List Number" do Word continua a contagem
            # de uma lista para a outra, e cada lista do Diário precisa começar do 1
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.9)
            p.paragraph_format.first_line_indent = Cm(-0.5)
            _texto_inline(p, s)
            k += 1
        elif s == "---":
            fecha_paragrafo()
            k += 1
        else:
            paragrafo_aberto.append(s)
            k += 1
    fecha_paragrafo()


def gerar(pasta, saida):
    doc = Document()
    secao = doc.sections[0]
    secao.page_width, secao.page_height = Cm(21), Cm(29.7)
    for margem in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(secao, margem, Cm(2))
    estilo = doc.styles["Normal"]
    estilo.font.name = FONTE
    estilo.font.size = Pt(10.5)
    for nome in ("Heading 1", "Heading 2", "Heading 3"):
        doc.styles[nome].font.name = FONTE
    arquivos = sorted(glob.glob(os.path.join(pasta, "*.md")))
    for n, arquivo in enumerate(arquivos):
        if n > 0:
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        with open(arquivo, encoding="utf-8") as f:
            adicionar_markdown(doc, f.read())
    os.makedirs(os.path.dirname(saida) or ".", exist_ok=True)
    doc.save(saida)
    return arquivos


def _principal():
    ap = argparse.ArgumentParser(description="Gera o Diário de Bordo (.docx) a partir de docs/diario/")
    ap.add_argument("--pasta", default=os.path.join(RAIZ, "docs", "diario"))
    ap.add_argument("--saida", default=os.path.join(RAIZ, "entrega", "Diario_de_Bordo.docx"))
    a = ap.parse_args()
    arquivos = gerar(a.pasta, a.saida)
    print(f"{len(arquivos)} seções -> {a.saida}")


if __name__ == "__main__":
    _principal()
