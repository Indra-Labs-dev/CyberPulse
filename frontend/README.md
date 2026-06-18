# CyberPulse — Frontend Desktop (Flutter)

Application desktop (Windows/macOS/Linux) du centre de veille et d'analyse cybersécurité CyberPulse. Consomme le backend FastAPI défini dans [`../backend`](../backend).

## Stack

Flutter (Riverpod, GoRouter, Dio, Syncfusion Charts, socket_io_client, flutter_local_notifications, system_tray, window_manager, flutter_markdown, flutter_secure_storage, shared_preferences).

## Architecture

```
lib/
  core/            config, thème SOC dark/light, client Dio + intercepteurs JWT, stockage sécurisé,
                    notifications, intégration desktop (system tray)
  models/           User, Cve, WatchlistEntry, CyberAlert, CyberReport, ScrapedArticle
  features/
    auth/           login/register, AuthController (JWT access+refresh, auto-refresh sur 401)
    dashboard/      KPIs, graphique Syncfusion, flux temps réel
    cve/            liste paginée + filtres (CVSS, sévérité, produit), détail CVE
    alerts/         centre d'alertes, acquittement, notifications temps réel
    watchlist/      ajout/suppression de produits surveillés
    articles/       flux d'articles scrapés, mode lecture Markdown
    reports/        génération de rapports, téléchargement PDF, ouverture native
    websocket/      service socket.io + connexion liée à l'état d'authentification
    settings/       thème, préférences de notifications
  routes/           configuration GoRouter (redirections selon l'état d'auth)
  shared/           AppShell (NavigationRail)
  widgets/          composants réutilisables (KPI card, badge de sévérité, indicateur de connexion)
```

## Prérequis

- Flutter 3.41+ (stable)
- Le backend CyberPulse démarré (voir [`../backend/README.md`](../backend/README.md))
- Windows : Visual Studio avec le workload "Desktop development with C++"

## Installation

```bash
cd frontend
flutter pub get
```

## Configuration du backend

L'URL de l'API et du WebSocket sont configurables via `--dart-define` (valeurs par défaut : `http://127.0.0.1:8000`) :

```bash
flutter run -d windows \
  --dart-define=API_BASE_URL=http://127.0.0.1:8000 \
  --dart-define=SOCKET_URL=http://127.0.0.1:8000
```

Pour un build (`flutter build windows`), passez les mêmes `--dart-define` afin qu'ils soient figés dans le binaire.

## Lancer l'application

```bash
flutter run -d windows     # ou -d macos / -d linux
```

## Build

```bash
flutter build windows --release
```

L'exécutable est généré dans `build/windows/x64/runner/Release/frontend.exe`.

## Fonctionnalités implémentées

- **Auth** : login / register, JWT stocké via `flutter_secure_storage`, rafraîchissement automatique du token sur 401 (intercepteur Dio), déconnexion.
- **Dashboard SOC** : KPIs (CVE suivies, critiques, sévérité haute, alertes actives), graphique en anneau Syncfusion par sévérité, flux d'alertes et d'articles récents.
- **Veille CVE** : liste paginée avec filtres (recherche, produit, sévérité, CVSS min), synchronisation NVD/CISA, page de détail complète.
- **Alertes** : centre d'alertes, acquittement, réception temps réel via WebSocket avec notification (toast in-app + notification native sur Linux/macOS).
- **Watchlist** : ajout/suppression de produits surveillés avec seuil d'alerte.
- **Articles & Blogs** : flux scrapé, favoris, marquage lu/non lu, mode lecture Markdown sans distraction, déclenchement manuel du scraping.
- **Rapports** : génération de rapport PDF filtré, téléchargement et ouverture avec le lecteur PDF par défaut du système.
- **WebSocket temps réel** : connexion/déconnexion automatique selon l'état de session, événements `alert` et `new_article` propagés dans toute l'app (indicateur "Live" dans la barre de navigation).
- **Paramètres** : bascule thème clair/sombre (palette SOC néon), activation des notifications, informations de session.
- **Système** : icône persistante dans la barre des tâches (Windows/Linux) avec menu Afficher/Masquer/Quitter.

## Limitation connue

`flutter_local_notifications` ne fournit pas de backend natif pour Windows : les notifications natives fonctionnent sur Linux/macOS, et sur Windows l'alerte est affichée via un toast in-app (bandeau en bas de l'écran) — ce qui reste un retour temps réel visible immédiatement, combiné à l'icône de la barre des tâches et au centre d'alertes.

## Tests

```bash
flutter test
flutter analyze
```
