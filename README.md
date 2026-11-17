# EDF Hydro Watch

Application de veille informationnelle sur EDF Hydro : collecte de flux RSS, filtrage par mots-clés, archivage SQLite et tableau de bord Streamlit.

## Lancer en local

```bash
python -m venv .venv
# Windows : .venv\Scripts\activate
# macOS/Linux : source .venv/bin/activate
pip install -r requirements.txt
python collector.py
streamlit run app.py
```

## Déploiement GitHub

1. Créer un dépôt GitHub et y téléverser le contenu de ce dossier.
2. Dans **Settings > Actions > General**, autoriser les workflows à lire et écrire dans le dépôt (si nécessaire).
3. Dans **Actions**, lancer `Collecte quotidienne EDF Hydro` avec `Run workflow` pour tester.
4. Le workflow s'exécute ensuite chaque jour à 06:00 UTC.
5. Pour publier l'interface, connecter le dépôt à Streamlit Community Cloud et sélectionner `app.py`.

## Sources actuellement configurées

- Flux des communiqués EDF : https://www.edf.fr/tous-les-communiques/feed
- France Hydro Électricité : https://www.france-hydro-electricite.fr/feed/
- Connaissance des Énergies : https://www.connaissancedesenergies.org/rss.xml
- Google News : recherches ciblées EDF Hydro / hydroélectricité

Les flux RSS ne couvrent pas nécessairement toutes les actualités publiées sur les pages régionales EDF Hydro. Les résultats Google News dépendent de l'indexation du moteur. Pour une veille exhaustive, ajouter les pages régionales EDF Hydro comme sources dédiées avec un connecteur de collecte adapté, et vérifier les conditions d'utilisation des sites.

## Personnalisation

Modifier `RSS_SOURCES` et `KEYWORDS` dans `collector.py`. La pertinence est actuellement déterminée par mots-clés : elle peut donc produire des faux positifs ou manquer des articles formulés autrement.
