"""CLI dispatcher for ATK‑Pro (moved to tools).

This is the same dispatcher that previously lived under `src/` and is
kept here for invocation as a developer/tooling script. Tests have been
updated to import this location instead of `src.cli_dispatcher`.
"""

import argparse
import sys
import importlib

def _get_src_dispatcher():
    # Import src.cli_dispatcher at runtime so tests can monkeypatch its attributes.
    return importlib.import_module("src.cli_dispatcher")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="atk",
        description="ATK-Pro v1.5 – Command Line Interface"
    )
    subparsers = parser.add_subparsers(dest="command")

    # tile-rebuild
    p_tile = subparsers.add_parser(
        "tile-rebuild",
        help="Rigenera le tessere a partire da una cartella di input"
    )
    p_tile.add_argument("--input-dir", required=True, help="Cartella contenente le immagini sorgente")
    p_tile.add_argument("--output-dir", default=None, help="Cartella di destinazione (default da ATK_OUTPUT_PATH)")
    p_tile.add_argument("--zoom", type=int, default=None, help="Livello di zoom da applicare")

    # metadata
    p_meta = subparsers.add_parser(
        "metadata",
        help="Gestione dei metadati: raccolta o validazione"
    )
    meta_sub = p_meta.add_subparsers(dest="action", required=True)

    p_meta_collect = meta_sub.add_parser("collect", help="Raccogli i metadati da una fonte specificata")
    p_meta_collect.add_argument("--source", required=True, help="Percorso o URL della fonte di metadati")
    p_meta_collect.add_argument("--out", required=True, help="File di output in cui salvare i metadati raccolti")

    p_meta_validate = meta_sub.add_parser("validate", help="Valida un file di metadati secondo uno schema")
    p_meta_validate.add_argument("--schema", required=True, help="File JSON dello schema di validazione")
    p_meta_validate.add_argument("--out", required=True, help="File in cui scrivere i risultati della validazione")

    # pdf-rebuild (nuova modalità + retrocompatibilità)
    p_pdf = subparsers.add_parser(
        "pdf-rebuild",
        help="Genera un PDF multipagina da immagini (nuova modalità) o da config/metadata (vecchia modalità)"
    )

    # nuova modalità (immagini)
    p_pdf.add_argument("-i", "--input", help="Cartella o file immagine da cui creare il PDF")
    p_pdf.add_argument("-o", "--output", help="Percorso di destinazione del PDF")
    p_pdf.add_argument("--sort", choices=["natural", "name", "mtime"], default="natural")
    p_pdf.add_argument("--dpi", type=int, default=300)
    p_pdf.add_argument("--page-size", choices=["A4", "Letter"], default="A4")
    p_pdf.add_argument("--margin", type=int, default=24)
    p_pdf.add_argument("--title")
    p_pdf.add_argument("--author")
    p_pdf.add_argument("--subject")
    p_pdf.add_argument("--keywords")

    # vecchia modalità (retrocompatibilità coi test)
    p_pdf.add_argument("--config", help="File JSON con parametri di composizione (vecchia modalità)")
    p_pdf.add_argument("--metadata", help="File YAML con metadati dei registri (vecchia modalità)")

    # logging-config
    p_log = subparsers.add_parser("logging-config", help="Configura livello e formato del logging")
    p_log.add_argument("--level", choices=["DEBUG", "INFO", "WARN", "ERROR"], default="INFO", help="Livello di log")
    p_log.add_argument("--format", dest="fmt", default=None, help="Stringa di formato per i messaggi di log")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "logging-config":
        # ramo logging-config separato
        dispatcher = _get_src_dispatcher()
        dispatcher.configure_logging(level=args.level, fmt=args.fmt)
    else:
        # ramo generico: logging default + dispatch
        dispatcher = _get_src_dispatcher()
        dispatcher.configure_logging(level=None, fmt=None)
        try:
            if args.command == "tile-rebuild":
                dispatcher.run_tile_rebuild({
                    "input_dir": args.input_dir,
                    "output_dir": args.output_dir,
                    "zoom": args.zoom
                })
            elif args.command == "metadata":
                if args.action == "collect":
                    dispatcher.collect_metadata({"source": args.source, "out": args.out})
                elif args.action == "validate":
                    dispatcher.validate_metadata({"schema": args.schema, "out": args.out})
            elif args.command == "pdf-rebuild":
                if args.config and args.metadata:
                    # vecchia modalità
                    dispatcher.run_pdf_rebuild({
                        "config": args.config,
                        "metadata": args.metadata,
                        "output": args.output
                    })
                elif args.input:
                    # nuova modalità
                    result = dispatcher.run_pdf_rebuild({
                        "input": args.input,
                        "output": args.output,
                        "sort": args.sort,
                        "dpi": args.dpi,
                        "page_size": args.page_size,
                        "margin": args.margin,
                        "title": args.title,
                        "author": args.author,
                        "subject": args.subject,
                        "keywords": args.keywords,
                    })
                    if result.get("status") == "ok":
                        print(f"✅ PDF creato: {result['output']} ({result['pages']} pagine)")
                    else:
                        print(f"❌ Errore pdf-rebuild: {result.get('reason','unknown_error')}", file=sys.stderr)
                        return 2
                else:
                    parser.error("Specifica o -i/--input (nuova modalità) oppure --config e --metadata (vecchia modalità)")
            else:
                parser.error(f"Comando sconosciuto: {args.command}")
            return 0
        except Exception as e:
            print(f"Errore: {e}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
