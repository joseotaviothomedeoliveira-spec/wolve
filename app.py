from __future__ import annotations

from io import BytesIO
from textwrap import wrap

from flask import Flask, Response, render_template, request
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

app = Flask(__name__)

MAX_ANO = 8


@app.get("/")
def index() -> str:
    return render_template("index.html", max_ano=MAX_ANO)


@app.post("/gerar-pdf")
def gerar_pdf() -> Response:
    disciplina = (request.form.get("disciplina") or "").strip()
    ano = (request.form.get("ano") or "").strip()
    tema = (request.form.get("tema") or "").strip()
    objetivo = (request.form.get("objetivo") or "").strip()
    quantidade = (request.form.get("quantidade") or "").strip()

    erro = validar_campos(disciplina, ano, tema, objetivo, quantidade)
    if erro:
        return Response(erro, status=400, mimetype="text/plain; charset=utf-8")

    pdf_buffer = criar_pdf_atividade(
        disciplina=disciplina,
        ano=int(ano),
        tema=tema,
        objetivo=objetivo,
        quantidade=int(quantidade),
    )

    return Response(
        pdf_buffer.getvalue(),
        mimetype="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=atividade-a4.pdf",
        },
    )


def validar_campos(disciplina: str, ano: str, tema: str, objetivo: str, quantidade: str) -> str | None:
    if not disciplina:
        return "A disciplina é obrigatória."
    if not ano.isdigit():
        return "O ano deve ser um número inteiro."

    ano_int = int(ano)
    if ano_int < 1 or ano_int > MAX_ANO:
        return f"O ano deve estar entre 1 e {MAX_ANO}."

    if not tema:
        return "O tema é obrigatório."
    if not objetivo:
        return "O objetivo é obrigatório."
    if not quantidade.isdigit():
        return "A quantidade de questões deve ser um número inteiro."

    qtd_int = int(quantidade)
    if qtd_int < 1 or qtd_int > 20:
        return "A quantidade de questões deve estar entre 1 e 20."

    return None


def criar_pdf_atividade(
    disciplina: str,
    ano: int,
    tema: str,
    objetivo: str,
    quantidade: int,
) -> BytesIO:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    largura, altura = A4
    margem_x = 20 * mm
    y = altura - 20 * mm

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(margem_x, y, "Folha de Atividade")

    y -= 10 * mm
    pdf.setFont("Helvetica", 11)
    cabecalho = [
        f"Disciplina: {disciplina}",
        f"Ano escolar: {ano}º ano",
        f"Tema: {tema}",
        f"Objetivo: {objetivo}",
    ]

    for linha in cabecalho:
        for parte in wrap(linha, width=88):
            pdf.drawString(margem_x, y, parte)
            y -= 6 * mm

    y -= 2 * mm
    pdf.setLineWidth(0.6)
    pdf.line(margem_x, y, largura - margem_x, y)
    y -= 10 * mm

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margem_x, y, "Exercícios")
    y -= 8 * mm
    pdf.setFont("Helvetica", 11)

    for i in range(1, quantidade + 1):
        texto = f"{i}. _________________________________________________"
        pdf.drawString(margem_x, y, texto)
        y -= 10 * mm

        if y < 25 * mm and i != quantidade:
            pdf.showPage()
            y = altura - 20 * mm
            pdf.setFont("Helvetica", 11)

    pdf.save()
    buffer.seek(0)
    return buffer


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
