SAMPLE_PDF_PATH = "tests/fixtures/sample.pdf"


def test_upload_pdf_returns_ready_status(client):
    with open(SAMPLE_PDF_PATH, "rb") as f:
        response = client.post(
            "/documents",
            files={"file": ("sample.pdf", f, "application/pdf")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["filename"] == "sample.pdf"
    assert data["page_count"] == 1


def test_upload_rejects_non_pdf_file(client):
    response = client.post(
        "/documents",
        files={"file": ("notes.txt", b"just some text", "text/plain")},
    )

    assert response.status_code == 415


def test_list_documents_includes_uploaded_file(client):
    with open(SAMPLE_PDF_PATH, "rb") as f:
        client.post(
            "/documents",
            files={"file": ("sample.pdf", f, "application/pdf")},
        )

    response = client.get("/documents")
    assert response.status_code == 200
    documents = response.json()["documents"]
    assert any(doc["filename"] == "sample.pdf" for doc in documents)


def test_get_nonexistent_document_returns_404(client):
    response = client.get("/documents/99999")
    assert response.status_code == 404
