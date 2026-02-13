from app import app, validar_campos


def test_validar_campos_rejeita_ano_invalido():
    erro = validar_campos("Matemática", "9", "Frações", "Praticar", "5")
    assert erro == "O ano deve estar entre 1 e 8."


def test_gerar_pdf_retorna_pdf():
    cliente = app.test_client()
    response = cliente.post(
        "/gerar-pdf",
        data={
            "disciplina": "Português",
            "ano": "6",
            "tema": "Interpretação de texto",
            "objetivo": "Desenvolver compreensão leitora",
            "quantidade": "6",
        },
    )

    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF")
