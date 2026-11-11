# Projet MECEN — Économie du crédit

Commencer par **Premier_point_avancement.html** (ouvrir dans un navigateur).
Le rapport est aussi disponible en Markdown.

## Contenu
- `01_premier_avancement.ipynb` : notebook avec toutes les cellules exécutées et leurs sorties.
- `analyse_credit.py` : même analyse sous forme de script reproductible.
- `data/credit_clients.csv` : version CSV complète de la base.
- `data/default of credit card clients.xls` : fichier original UCI.
- `figures/` : quatre graphiques calculés.
- `resultats_validation.csv`, `resultats.json` : mesures réelles sur la validation.
- `partitions.csv` : correspondance ID / partition, pour reproduire le protocole.
- `statistiques_descriptives.csv`, `environnement.json`, `requirements.txt`.
- `PROMPTS_ET_IA.md` : trace de l’assistance IA et limites du travail.

## Reproduire
Python 3.11 ou version compatible (version exacte dans environnement.json).
Depuis ce dossier :

```bash
python -m pip install -r requirements.txt
python analyse_credit.py
```

Le notebook s’ouvre dans Jupyter ou Google Colab (déposer le dossier `data` dans le répertoire de travail ; conserver la structure). Jupyter n’est nécessaire que pour l’interface notebook, pas pour le script.
Le script recalcule graphiques et métriques ; le rapport est un compte rendu daté du premier calcul.

## Source et protocole
https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
Yeh, I. (2009), DOI 10.24432/C55S3H, CC BY 4.0.
Téléchargement le 11 novembre 2026. Vérification SHA-256 dans provenance.json.

Le test n’a pas été évalué. Les chiffres présentés sont provisoires, issus de la validation. Le projet ne comporte pas encore d’optimisation d’hyperparamètres ni de revue bibliographique récente achevée. Il n’effectue aucun web scraping ; vérifier avec l’enseignante si cette composante est imposée.
