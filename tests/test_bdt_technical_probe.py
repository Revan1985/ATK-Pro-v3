from __future__ import annotations

from pathlib import Path

import verify_bdt_technical_probe as probe


def test_extract_candidates_finds_public_bdt_asset_links():
    html = """
    <html>
      <a href="/iiif/123/manifest.json">manifest</a>
      <img src="/storage/image/page-0001.jpg">
      <a data-download="/download/documento.pdf">PDF</a>
      <script>
        const info = "https://bdt.bibcom.trento.it/iiif/123/page-1/info.json";
      </script>
    </html>
    """

    candidates = probe.extract_candidates(html, "https://bdt.bibcom.trento.it/Iconografia/4052")
    by_kind = {candidate.kind: candidate for candidate in candidates}

    assert by_kind["manifest"].url == "https://bdt.bibcom.trento.it/iiif/123/manifest.json"
    assert by_kind["image"].url == "https://bdt.bibcom.trento.it/storage/image/page-0001.jpg"
    assert by_kind["pdf"].url == "https://bdt.bibcom.trento.it/download/documento.pdf"
    assert by_kind["pdf"].role == "document_pdf"
    assert by_kind["iiif_info"].url == "https://bdt.bibcom.trento.it/iiif/123/page-1/info.json"


def test_extract_candidates_ignores_duplicates_and_non_download_links():
    html = """
    <a href="#page/n0">anchor</a>
    <a href="mailto:info@example.test">mail</a>
    <a href="/Progetti/Tridentina-manifesta">project page, not an IIIF manifest</a>
    <img src="/storage/image/page-0001.jpg">
    <a href="/storage/image/page-0001.jpg">same image</a>
    """

    candidates = probe.extract_candidates(html, "https://bdt.bibcom.trento.it/Iconografia/4052")

    assert candidates == [
        probe.ProbeCandidate(
            kind="image",
            url="https://bdt.bibcom.trento.it/storage/image/page-0001.jpg",
            source="html_attribute",
            role="image_candidate",
        )
    ]


def test_extract_candidates_marks_bdt_content_images_and_site_assets():
    html = """
    <img src="https://s3-eu-west-1.amazonaws.com/static.comunitatrentina.it/var/trentoarchiviobiblioteca/storage/images/10032-157-ita-IT/Biblioteca-Digitale-Trentina-Biblioteca-comunale-di-Trento_header_logo.png">
    <img src="https://s3-eu-west-1.amazonaws.com/static.comunitatrentina.it/var/trentoarchiviobiblioteca/storage/images/media/immagini-iconografie/gg1atc30tav11.jpg/494856-1-ita-IT/GG1atc30TAV11.jpg_large.jpg">
    """

    candidates = probe.extract_candidates(html, "https://bdt.bibcom.trento.it/Iconografia/4052")
    roles = {candidate.url.rsplit("/", 1)[-1]: candidate.role for candidate in candidates}

    assert roles["Biblioteca-Digitale-Trentina-Biblioteca-comunale-di-Trento_header_logo.png"] == "site_asset"
    assert roles["GG1atc30TAV11.jpg_large.jpg"] == "content_image"


def test_extract_candidates_sorts_pdf_and_pages_naturally():
    html = """
    <a href="/content/download/78214/1625910/file/BDT-113-TIf37.pdf">PDF</a>
    <img src="/storage/images/media/immagini-testi-a-stampa/page-10.jpg110/340925-1-ita-IT/page-10.jpg.jpg">
    <img src="/storage/images/media/immagini-testi-a-stampa/page-2.jpg110/340925-1-ita-IT/page-2.jpg.jpg">
    <img src="/storage/images/media/immagini-testi-a-stampa/page-1.jpg165/340889-1-ita-IT/page-1.jpg_large.jpg">
    <img src="/storage/images/media/immagini-testi-a-stampa/page-1.jpg165/340889-1-ita-IT/page-1.jpg.jpg">
    """

    candidates = probe.extract_candidates(html, "https://bdt.bibcom.trento.it/Testi-a-stampa/113")

    assert [candidate.role for candidate in candidates] == [
        "document_pdf",
        "content_image",
        "content_image",
        "content_image",
        "content_image",
    ]
    assert candidates[0].url.endswith("BDT-113-TIf37.pdf")
    assert candidates[1].url.endswith("page-1.jpg.jpg")
    assert candidates[2].url.endswith("page-1.jpg_large.jpg")
    assert candidates[3].url.endswith("page-2.jpg.jpg")
    assert candidates[4].url.endswith("page-10.jpg.jpg")


def test_write_report_creates_csv(tmp_path: Path):
    report = tmp_path / "bdt_probe.csv"
    probe.write_report(
        report,
        [
            probe.ProbeCandidate(
                kind="pdf",
                url="https://bdt.bibcom.trento.it/download/documento.pdf",
                source="html_attribute",
            )
        ],
    )

    assert "kind,role,url,source" in report.read_text(encoding="utf-8")
    assert "documento.pdf" in report.read_text(encoding="utf-8")
