from src.main_gui_qt import (
    _get_effective_record_policy_context,
    _get_effective_record_portal,
    _is_bdt_direct_pdf_full_record_allowed,
)


def test_effective_record_portal_uses_url_before_selected_portal():
    record = {
        "modalita": "R",
        "url": "https://dl.ficlit.unibo.it/s/lib/item/28429",
    }

    assert _get_effective_record_portal("antenati", record) == "dl_ficlit"


def test_effective_record_policy_uses_detected_r_limited_portal():
    record = {
        "modalita": "R",
        "url": "https://bub.unibo.it/iiif/2/manifest/bub/bollettiniparrocchiali/_castenaso_-_s_giovanni_battista/jpg/1933.json",
    }

    context = _get_effective_record_policy_context("antenati", record)

    assert context["portal_key"] == "bub_digitale"
    assert context["policy_code"] == "r_limited"


def test_effective_record_policy_blocks_detected_d_only_portal():
    record = {
        "modalita": "R",
        "url": "https://teca.bncf.firenze.sbn.it/ImageViewer/servlet/ImageViewer?idr=BNCF000000",
    }

    context = _get_effective_record_policy_context("antenati", record)

    assert context["portal_key"] == "bncf_teca"
    assert context["policy_code"] == "d_only"


def test_bdt_pdf_only_exemption_uses_effective_portal_when_menu_differs():
    record = {
        "modalita": "R",
        "url": "https://bdt.bibcom.trento.it/Testi-a-stampa/113",
    }
    effective_portal = _get_effective_record_portal("antenati", record)

    assert effective_portal == "biblioteca_digitale_trentina"
    assert _is_bdt_direct_pdf_full_record_allowed(effective_portal, ["PDF"], record)


def test_mixed_portal_batch_keeps_per_record_policy():
    records = [
        {
            "modalita": "R",
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua331306/0Z89vd3",
        },
        {
            "modalita": "R",
            "url": "https://dl.ficlit.unibo.it/s/lib/item/28429",
        },
        {
            "modalita": "R",
            "url": "https://teca.bncf.firenze.sbn.it/ImageViewer/servlet/ImageViewer?idr=BNCF000000",
        },
    ]

    contexts = [
        _get_effective_record_policy_context("antenati", record)
        for record in records
    ]

    assert [ctx["portal_key"] for ctx in contexts] == [
        "antenati",
        "dl_ficlit",
        "bncf_teca",
    ]
    assert [ctx["policy_code"] for ctx in contexts] == [
        "r_ok",
        "r_limited",
        "d_only",
    ]
