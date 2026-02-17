# ATK-Pro – Ancestor Tile Rebuilder
**Note:** This project is developed, maintained, and supported entirely by one person. Every feedback, report, or contribution is welcome, but there is no team or corporate structure behind the development.
## Description
ATK-Pro is an advanced tool for the reconstruction, storage, and consultation of digitized genealogical images and documents from the Antenati portal. The project supports multilingual management and distribution as a standalone application for Windows.
## Main functionalities
- Automatic reconstruction of images from IIIF tiles
- Multilingual support (20 languages)
- Modern graphical interface (Qt)
- Build standalone EXE and multilingual installer
## Installation
1. Download the ATK-Pro-Setup-v2.0.exe installer or the ATK-Pro.exe standalone executable from the releases section.
1. Follow the on-screen instructions to complete the installation.
1. Start ATK-Pro from the Start menu or the installation folder.
## Project Structure
- `src/` – Main source code (GUI, logic, modules)
- `assets/` – Multilingual assets (guides, templates, resources)
- `locales/` – .ini translation files for each language
- `docs_generali/` – Glossaries, general documentation, roadmap
- `scripts/` – Maintenance, translation, validation scripts
- `tests/` – Automatic and coverage tests
- `dist/` – Output build/installer
## Documentation
- Historical and in-depth documentation is now archived in `docs_generali/archivio/`.
- This README and the `CHANGELOG.md` file summarize the project's status and milestones.
## History and development
The project was born as an evolution of digital genealogy tools, with a focus on transparency, historical archiving, and international support. Every milestone is tracked and documented in the repository.
## Credits
Development and maintenance: Daniele Pigoli
Contributions: see changelog and release notes
## Changelog
Consult the `docs_generali/CHANGELOG.md` file for the main news and milestones of the project.
For historical details and complete notes, see the folder `docs_generali/archivio/`.

-----
## Current status
- All active modules have been tested with direct and defensive coverage
- Annotation with block `# === Test Coverage ===` in validated modules
- The main.py module, despite partial coverage (64%), has been logically validated as it is orchestrative
### Next steps
- Prepare v2.1 with incremental evolution and updated documentation

Curated by Daniele Pigoli – with the intent of uniting technical rigor and historical memory.
