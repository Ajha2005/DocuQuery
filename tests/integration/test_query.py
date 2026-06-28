SAMPLE_PDF_PATH = "tests/fixtures/sample.pdf"


def _upload_sample(client):
    with open(SAMPLE_PDF_PATH, "rb") as f:
        response = client.post(
            "/documents",
            files={"file": ("sample.pdf", f, "application/pdf")},
        )
    return response.json()["id"]


def test_query_returns_answer_and_sources(client):
    document_id = _upload_sample(client)

    response = client.post(
        f"/documents/{document_id}/query",
        json={"question": "What does this document say?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0
    assert data["sources"][0]["page_number"] == 1


def test_query_nonexistent_document_returns_404(client):
    response = client.post(
        "/documents/99999/query",
        json={"question": "anything"},
    )
    assert response.status_code == 404
