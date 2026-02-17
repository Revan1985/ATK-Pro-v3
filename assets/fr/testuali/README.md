# ATK-Pro – Reconstructeur de tuiles Antenati
**Remarque :** Ce projet est développé, maintenu et supporté entièrement par une seule personne. Tout commentaire, signalement ou contribution est le bienvenu, mais il n'y a pas d'équipe ou de structure d'entreprise derrière le développement.
## Description
ATK-Pro est un outil avancé pour la reconstruction, l'archivage et la consultation d'images et de documents généalogiques numérisés à partir du portail Antenati. Le projet prend en charge la gestion multilingue et la distribution en tant qu'application autonome pour Windows.
## Fonctionnalités principales
- Reconstruction automatique d'images à partir de tuiles IIIF
- Support multilingue (20 langues)
- Interface graphique moderne (Qt)
- Créer un exécutable autonome et un installateur multilingue
## Installation
1. Téléchargez l'installateur ATK-Pro-Setup-v2.0.exe ou l'exécutable autonome ATK-Pro.exe depuis la section releases.
1. Suivez les instructions à l'écran pour terminer l'installation.
1. Lancez ATK-Pro depuis le menu Démarrer ou le dossier d'installation.
## Structure du projet
- `src/` – Code source principal (GUI, logique, modules)
- `assets/` – Actifs multilingues (guides, modèles, ressources)
- `locales/` – Fichiers de traduction .ini pour chaque langue
- `docs_generali/` – Glossaires, documentation générale, feuille de route
- `scripts/` – Scripts de maintenance, traduction, validation
- `tests/` – Tests automatiques et de couverture
- `dist/` – Génération de la sortie build/installateur
## Documentation
- La documentation historique et d'approfondissement est maintenant archivée dans `docs_generali/archivio/`.
- Le présent README et le fichier `CHANGELOG.md` résument l'état et les principales étapes du projet.
## Histoire et développement
Le projet naît comme une évolution d'outils pour la généalogie numérique, avec une attention particulière à la transparence, à l'archivage historique et au soutien international. Chaque étape est tracée et documentée dans le dépôt.
## Crédits
Développement et maintenance : Daniele Pigoli
Contributions : voir le journal des modifications et les notes de version
## Journal des modifications
Consultez le fichier `docs_generali/CHANGELOG.md` pour connaître les principales nouveautés et les étapes importantes du projet.
Pour des détails historiques et des notes complètes, voir le dossier `docs_generali/archivio/`.

-----
## État actuel
- Tous les modules actifs ont été testés avec une couverture directe et défensive
- Annotation avec bloc `# === Couverture de test ===` dans les modules validés
- Le module main.py, bien qu'avec une couverture partielle (64%), a été validé logiquement en tant qu'orchestrateur
### Prochaines étapes
- Préparer la v2.1 avec une évolution incrémentale et une documentation mise à jour

✍️ Sous la direction de Daniele Pigoli – avec l'intention d'unir rigueur technique et mémoire historique.
