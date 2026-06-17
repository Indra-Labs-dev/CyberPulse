# CyberPulse — Cahier des Charges V1.0 Complet
# Centre de Veille et d'Analyse en Cybersécurité

**Version :** 1.0 — Édition Complète  
**Date :** Juin 2026  
**Type :** Application Desktop Cross-Platform  
**Auteur :** IndraLabs  
**Statut :** MVP + Fonctionnalités Avancées

---

# TABLE DES MATIÈRES

1. [Présentation du Projet](#1-présentation-du-projet)
2. [Objectifs Fonctionnels](#2-objectifs-fonctionnels)
3. [Architecture Générale](#3-architecture-générale)
4. [Technologies](#4-technologies)
5. [Modules Fonctionnels — MVP](#5-modules-fonctionnels--mvp)
6. [Modules Fonctionnels — Avancés (V1.0 Complète)](#6-modules-fonctionnels--avancés-v10-complète)
7. [Module Scraping de Blogs](#7-module-scraping-de-blogs)
8. [Base de Données](#8-base-de-données)
9. [Sécurité](#9-sécurité)
10. [Interface Utilisateur](#10-interface-utilisateur)
11. [Performances](#11-performances)
12. [Fonctionnalités Futures (v2.0)](#12-fonctionnalités-futures-v20)

---

# 1. PRÉSENTATION DU PROJET

## 1.1 Contexte

Les professionnels de la cybersécurité doivent surveiller quotidiennement un volume important d'informations : vulnérabilités CVE, bulletins de sécurité, alertes CERT, exploits publics, menaces émergentes, actualités cyber. Ces informations sont souvent dispersées entre plusieurs plateformes, rendant leur exploitation difficile.

**CyberPulse** vise à centraliser, analyser et présenter ces données au sein d'une interface moderne, intuitive et ultra-performante.

## 1.2 Objectif Principal

Développer une application Desktop permettant :
- La surveillance des vulnérabilités en temps réel
- L'analyse automatisée des risques par IA
- La génération de rapports professionnels
- La création de contenu cyber automatisée
- La gestion d'alertes personnalisées
- Le scraping intelligent de sources cyber

## 1.3 Vision du Produit

Devenir **LA** plateforme centralisée de veille, d'analyse et de génération de contenu cybersécurité destinée aux étudiants, professionnels IT, administrateurs systèmes, analystes SOC et chasseurs de menaces.

---

# 2. OBJECTIFS FONCTIONNELS

CyberPulse devra permettre :

| Domaine | Capacités |
|---------|-----------|
| **Veille** | Consulter les dernières CVE, alertes critiques, suivre les produits surveillés, scraper des blogs |
| **Analyse** | Évaluer les risques, obtenir une synthèse IA, identifier les produits impactés, corréler les menaces |
| **Reporting** | Générer des rapports PDF/HTML, exporter les données, créer des tableaux de bord personnalisés |
| **Notifications** | Alertes en temps réel, notifications système, surveillance personnalisée, webhooks |
| **Intelligence** | Scraping de blogs, agrégation RSS, veille OSINT, cartographie des menaces |
| **Productivité** | Générateur d'articles, templates de rapports, raccourcis clavier, mode focus |

---

# 3. ARCHITECTURE GÉNÉRALE

```text
┌─────────────────────────────────────────────────────────────┐
│                    FLUTTER UI (Desktop)                     │
│                                                             │
│  Riverpod      Go Router      Dio      Syncfusion Charts    │
│  Local Notifications    System Tray    WebView              │
└─────────────────────────────┬───────────────────────────────┘
                              │
                    REST API HTTPS / WebSocket
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                      FASTAPI BACKEND                        │
│                                                             │
│  JWT Auth    Business Logic    Scheduler    Rate Limiting   │
│  CVE Aggregator    IA Services    Scraping Engine           │
│  WebSocket Manager    Webhook Service    Export Engine      │
└─────────────────────────────┬───────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐        ┌──────▼──────┐      ┌──────▼──────┐
   │  MySQL  │        │   Ollama    │      │  Redis      │
   │    8    │        │  (Local AI) │      │  (Cache)    │
   └─────────┘        └─────────────┘      └─────────────┘
```

---

# 4. TECHNOLOGIES

## Frontend

| Technologie | Usage |
|-------------|-------|
| **Flutter** | Interface utilisateur cross-platform (Windows, macOS, Linux) |
| **Riverpod** | Gestion d'état réactive |
| **Go Router** | Navigation déclarative |
| **Dio** | Client HTTP pour API REST |
| **Syncfusion Charts** | Graphiques et visualisations avancées |
| **flutter_local_notifications** | Notifications desktop natives |
| **system_tray** | Icône persistante dans la barre des tâches |
| **webview_flutter** | Affichage de contenu web intégré |
| **flutter_markdown** | Rendu Markdown natif |
| **shared_preferences** | Stockage local des préférences |

## Backend

| Technologie | Usage |
|-------------|-------|
| **Python 3.11+** | Langage principal |
| **FastAPI** | API Backend haute performance |
| **SQLAlchemy 2.0** | ORM asynchrone |
| **Alembic** | Migrations de base de données |
| **Celery** | Tâches asynchrones et planifiées |
| **Redis** | Cache, file d'attente Celery, sessions |
| **BeautifulSoup4** | Scraping HTML |
| **Scrapy** | Scraping avancé et structuré |
| **Feedparser** | Parsing RSS/Atom |
| **Playwright** | Scraping JavaScript-rendered |
| **ReportLab** | Génération PDF |
| **WeasyPrint** | HTML → PDF |
| **Jinja2** | Templates de rapports |
| **python-socketio** | WebSocket temps réel |
| **APScheduler** | Planification des tâches |

## Base de Données

| Technologie | Usage |
|-------------|-------|
| **MySQL 8** | Stockage principal relationnel |
| **Redis** | Cache, sessions, file d'attente |

## IA

| Technologie | Usage |
|-------------|-------|
| **Ollama** | Analyse IA locale (LLM) |
| **LangChain** | Orchestration des prompts IA |

---

# 5. MODULES FONCTIONNELS — MVP (Déjà Définis)

## Module 1 : Authentification
- Connexion / Déconnexion sécurisée
- JWT + Refresh Token
- Hachage BCrypt
- 3 rôles : Administrateur, Analyste, Lecteur

## Module 2 : Dashboard
- Vue d'ensemble cybersécurité
- Indicateurs clés (CVE, exploits, alertes CISA)
- Widgets graphiques et cartes statistiques
- Flux temps réel
- Thèmes Clair & Sombre

## Module 3 : Veille CVE
- Sources : NVD, MITRE, CISA KEV
- Synchronisation automatique
- Recherche avancée + filtrage multi-critères
- Historique complet

## Module 4 : Analyse de Vulnérabilité
- Fiche détaillée (CVSS, CWE, produits, correctifs)
- Évaluation du risque
- Recommandations et priorités

## Module 5 : Analyse IA (Ollama)
- Résumé simplifié, analyse technique, impact métier
- 3 formats : court, détaillé, expert

## Module 6 : Watchlist
- Produits prédéfinis (Ubuntu, Debian, Docker, VMware, Apache, Nginx, Linux Kernel)
- Ajout/suppression personnalisé
- Alertes par produit

## Module 7 : Alertes et Notifications
- Notifications Desktop (CVE, alertes critiques)
- Icône System Tray persistante
- Paramétrage : criticité, produits, fréquence

## Module 8 : Actualités Cybersécurité
- Flux RSS par catégories (Vulnérabilités, Malware, Ransomware, Cloud, Linux, IA)
- Articles favoris
- Recherche

## Module 9 : Génération de Rapports
- Rapport CVE, Hebdomadaire, Mensuel
- Export PDF (ReportLab/WeasyPrint) et HTML

## Module 10 : Générateur d'Articles
- Entrée : CVE ou alerte
- Sortie : HTML/Markdown avec Titre SEO, Introduction, Analyse, Impact, Mitigation, Conclusion

---

# 6. MODULES FONCTIONNELS — AVANCÉS (V1.0 COMPLÈTE)

## Module 11 : Scraping Intelligent de Blogs Cybersécurité 🆕

### Objectif
Agréger automatiquement le contenu des meilleurs blogs de cybersécurité pour enrichir la veille au-delà des flux RSS standards.

### Sources Scrapées (30+ blogs)

#### 🇫🇷 Blogs Français
| Blog | URL | Type |
|------|-----|------|
| **Le Blog du Hacker** | leblogduhacker.fr | Actualités, tutos |
| **Zataz** | zataz.com | Actualités cyber |
| **Root Me** | root-me.org | Challenges, veille |
| **SecuObs** | secuobs.com | Veille sécurité |
| **UnderNews** | undernews.fr | Actualités IT |
| **Le Monde Informatique** | lemondeinformatique.fr | Actualités tech |
| **Silicon.fr** | silicon.fr | Cybersécurité entreprise |
| **IT-Connect** | it-connect.fr | Tutoriels sécurité |
| **Le Journal du Hacker** | journalduhacker.net | Agrégateur |
| **France Cybersecurity** | france-cybersecurity.com | Écosystème français |

#### 🇬🇧🇺🇸 Blogs Anglophones
| Blog | URL | Type |
|------|-----|------|
| **Krebs on Security** | krebsonsecurity.com | Investigations |
| **The Hacker News** | thehackernews.com | Actualités globales |
| **BleepingComputer** | bleepingcomputer.com | Actualités + guides |
| **SecurityWeek** | securityweek.com | Actualités entreprise |
| **Threatpost** | threatpost.com | Menaces émergentes |
| **Dark Reading** | darkreading.com | Actualités pro |
| **SC Media** | scmagazine.com | Magazine sécurité |
| **InfoSecurity Magazine** | infosecurity-magazine.com | Magazine |
| **Sophos News** | news.sophos.com | Recherche threat |
| **Graham Cluley** | grahamcluley.com | Blog indépendant |
| **Schneier on Security** | schneier.com | Analyses expert |
| **Troy Hunt** | troyhunt.com | Have I Been Pwned |
| **Malwarebytes Blog** | blog.malwarebytes.com | Malware research |
| **CrowdStrike Blog** | crowdstrike.com/blog | Threat intel |
| **Mandiant Blog** | mandiant.com/blog | APT / Incident response |
| **Palo Alto Networks** | paloaltonetworks.com/blog | Recherche |
| **CISA Blog** | cisa.gov/news-events | Alertes officielles |
| **NCSC UK** | ncsc.gov.uk | Conseils nationaux |
| **ANSSI** | anssi.fr | Alertes France |
| **SANS Internet Storm Center** | isc.sans.edu | Veille communautaire |

### Fonctionnalités de Scraping

| Fonctionnalité | Description |
|----------------|-------------|
| **Scraping Multi-Engine** | BeautifulSoup (statique) + Scrapy (structuré) + Playwright (JS-rendered) |
| **Détection Auto des Articles** | Sélecteurs CSS adaptatifs par site + fallback sur sitemaps |
| **Extraction Intelligente** | Titre, auteur, date, contenu, tags, images, liens internes |
| **Déduplication** | Hash du contenu + similarité textuelle pour éviter les doublons |
| **Catégorisation Auto** | Classification ML (Vulnérabilités, Malware, Ransomware, Cloud, Linux, IA, Politique, Formation) |
| **Résumé IA** | Génération automatique d'un résumé par Ollama pour chaque article scrapé |
| **Score de Pertinence** | Calcul basé sur mots-clés cyber, fraîcheur, source authority |
| **Veille Programmée** | Scraping toutes les 15 min / 1h / 4h selon la source |
| **Alerte sur Nouveaux Articles** | Notification desktop quand un article pertinent est publié |
| **Mode Hors-Ligne** | Cache local des articles pour lecture sans connexion |
| **Recherche Full-Text** | Indexation Elasticsearch-like dans MySQL (FULLTEXT) |
| **Export d'Articles** | PDF, HTML, Markdown d'un article ou d'une sélection |
| **Partage** | Lien partageable, copie dans le presse-papiers |
| **Favoris & Collections** | Sauvegarde d'articles, création de collections thématiques |
| **Historique de Lecture** | Suivi des articles lus/non lus |
| **Filtrage Avancé** | Par source, catégorie, date, pertinence, longueur, présence d'exploits |
| **Vue Lecteur** | Mode lecture sans distraction (comme Pocket) |
| **Comparaison d'Articles** | Côte à côte de 2 articles sur le même sujet |
| **Timeline d'Événement** | Regroupement des articles par événement cyber majeur |

### Architecture Scraping

```text
┌─────────────────────────────────────────┐
│         Scraping Scheduler              │
│    (APScheduler + Celery Beat)          │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐   ┌────▼────┐  ┌────▼────┐
│Static │   │  Scrapy │  │Dynamic  │
│BS4    │   │  Spider │  │Playwright│
└───┬───┘   └────┬────┘  └────┬────┘
    │            │            │
    └────────────┼────────────┘
                 │
        ┌────────▼────────┐
        │  Content Parser │
        │  + Deduplicator │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │  AI Summarizer  │
        │    (Ollama)     │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │  MySQL Storage  │
        │  + Redis Cache  │
        └─────────────────┘
```

---

## Module 12 : Corrélation de Menaces (Threat Correlation) 🆕

### Objectif
Identifier les liens entre vulnérabilités, exploits, IOCs et actualités pour détecter des campagnes d'attaque.

### Fonctionnalités
- **Graphe de Corrélation** : Visualisation des liens CVE ↔ Exploit ↔ Malware ↔ Acteur
- **Détection de Campagnes** : Regroupement automatique d'événements liés
- **Scoring de Menace** : Score global par campagne basé sur CVSS + exploitability + actualité
- **Timeline d'Attaque** : Chronologie d'une campagne identifiée
- **Acteurs de Menace** : Base de données des APT/groupes avec leurs TTPs

---

## Module 13 : Veille OSINT 🆕

### Objectif
Surveiller la surface d'attaque et les fuites de données.

### Fonctionnalités
- **Have I Been Pwned Integration** : Vérification d'emails/breaches
- **Shodan/Censys Lookup** : Scan passif d'IPs/domaines
- **GitHub Dorking** : Recherche de leaks (clés API, credentials)
- **Pastebin Monitoring** : Surveillance des pastes publics
- **Dark Web Mentions** : Alertes si l'entreprise est mentionnée (via APIs tierces)
- **Certificate Transparency** : Surveillance des nouveaux certificats SSL

---

## Module 14 : Tableau MITRE ATT&CK 🆕

### Objectif
Mapper les menaces identifiées sur le framework MITRE ATT&CK.

### Fonctionnalités
- **Matrice Interactive** : Navigation par tactics/techniques
- **Mapping Auto** : Association CVE → Technique ATT&CK via IA
- **Heatmap** : Visualisation des techniques les plus exploitées
- **Profil d'Acteur** : TTPs connus par APT/groupe
- **Gaps Analysis** : Identification des défenses manquantes

---

## Module 15 : Gestion des Incidents 🆕

### Objectif
Suivre et documenter les incidents de sécurité.

### Fonctionnalités
- **Création d'Incident** : À partir d'une CVE, alerte ou manuellement
- **Workflow de Réponse** : Étapes : Détection → Analyse → Containment → Eradication → Recovery → Lessons Learned
- **Assignation** : Attribution à un analyste
- **Journal d'Activité** : Timeline de toutes les actions
- **Pièces Jointes** : Screenshots, logs, rapports
- **Escalade** : Notification automatique si non résolu dans les délais
- **Metrics** : MTTD, MTTR, nombre d'incidents par sévérité

---

## Module 16 : Playbooks Automatisés 🆕

### Objectif
Automatiser les réponses récurrentes aux menaces.

### Fonctionnalités
- **Éditeur Visuel** : Création de playbooks par glisser-déposer
- **Déclencheurs** : Nouvelle CVE critique, nouvel exploit, alerte CISA
- **Actions** : Envoi d'email, création de ticket, scan de vulnérabilité, génération de rapport
- **Conditions** : IF/ELSE basés sur CVSS, produit impacté, criticité
- **Templates** : Playbooks pré-configurés (ex: "Réponse Ransomware", "Patch Tuesday")
- **Exécution Manuelle/Auto** : Lancement manuel ou automatique
- **Logs d'Exécution** : Historique complet des runs

---

## Module 17 : Scanner de Vulnérabilités Léger 🆕

### Objectif
Scan rapide des actifs locaux pour identifier les vulnérabilités connues.

### Fonctionnalités
- **Scan IP/Port** : Découverte des services ouverts (nmap-like)
- **Détection de Versions** : Identification des versions de services
- **Matching CVE** : Correspondance automatique version → CVE
- **Scan de Fichiers** : Analyse de fichiers de config (recherche de mots de passe en clair, mauvaises pratiques)
- **Rapport de Scan** : Export PDF/HTML des résultats
- **Planification** : Scans récurrents programmés

---

## Module 18 : Générateur de Signatures (YARA/Sigma) 🆕

### Objectif
Générer automatiquement des règles de détection.

### Fonctionnalités
- **YARA Generator** : Création de règles YARA à partir d'un hash, string, ou comportement
- **Sigma Generator** : Création de règles Sigma pour SIEM
- **Validation** : Test des règles générées
- **Bibliothèque** : Stockage et organisation des règles
- **Export** : Téléchargement des règles au format standard

---

## Module 19 : Collaboration Multi-Utilisateurs 🆕

### Objectif
Travail d'équipe sur les analyses et rapports.

### Fonctionnalités
- **Commentaires** : Discussion sur une CVE ou un article
- **Mentions** : @username pour notifier un collègue
- **Partage de Recherches** : Partage de filtres et requêtes
- **Rapports Collaboratifs** : Édition simultanée d'un rapport
- **Activité Récente** : Feed d'actions des collaborateurs
- **Notifications Internes** : Alertes sur les actions des collègues

---

## Module 20 : API Publique & Webhooks 🆕

### Objectif
Intégrer CyberPulse avec d'autres outils.

### Fonctionnalités
- **API REST Publique** : Accès programmatique aux CVE, articles, rapports
- **Clés API** : Gestion des clés avec rate limiting
- **Webhooks** : Envoi d'événements vers Slack, Discord, Teams, webhook personnalisé
- **Intégration Slack** : Commandes slash (/cyberpulse cve CVE-2026-XXXX)
- **Intégration Discord** : Bot de notifications
- **Intégration Microsoft Teams** : Connecteur de notifications
- **Zapier/Make** : Connexion aux plateformes no-code

---

## Module 21 : Mode Focus & Productivité 🆕

### Objectif
Optimiser la productivité de l'analyste.

### Fonctionnalités
- **Tableau de Bord Personnalisable** : Drag & drop des widgets
- **Raccourcis Clavier** : Navigation 100% au clavier
- **Mode Focus** : Masquage des notifications pendant l'analyse
- **Timer Pomodoro** : Sessions de travail structurées
- **Notes Rapides** : Bloc-notes intégré lié aux CVE/articles
- **To-Do List** : Tâches liées aux vulnérabilités à traiter
- **Rappels** : Alertes pour les actions en attente

---

## Module 22 : Statistiques & Analytics 🆕

### Objectif
Mesurer l'activité de veille et l'efficacité de l'équipe.

### Fonctionnalités
- **Stats Personnelles** : CVE consultées, articles lus, rapports générés
- **Stats Équipe** : Activité globale, temps de réponse moyen
- **Trends** : Évolution des menaces dans le temps
- **Rapport d'Activité** : Export mensuel de l'activité
- **Leaderboard** : Gamification de la veille (optionnel)

---

## Module 23 : Import/Export Avancé 🆕

### Objectif
Interoperabilité avec d'autres outils.

### Fonctionnalités
- **Import CVE** : Fichier JSON NVD, CSV personnalisé
- **Export JSON/CSV/XML** : Données brutes pour intégration
- **Export STIX/TAXII** : Format standard de threat intelligence
- **Export MISP** : Format compatible MISP
- **Export OpenIOC** : Format IOC standard
- **Backup/Restore** : Sauvegarde complète de la base

---

## Module 24 : Mode Offline 🆕

### Objectif
Fonctionner sans connexion internet.

### Fonctionnalités
- **Cache Local** : Dernières CVE, articles, rapports en local
- **Synchronisation Différée** : Mise à jour automatique dès la reconnexion
- **Lecture Hors-Ligne** : Articles et rapports consultables sans réseau
- **Analyse IA Locale** : Ollama fonctionne en local sans internet
- **Indicateur de Connectivité** : Statut réseau visible en permanence

---

# 7. MODULE SCRAPING DE BLOGS (DÉTAIL COMPLET)

## 7.1 Configuration des Sources

```json
{
  "sources": [
    {
      "name": "The Hacker News",
      "url": "https://thehackernews.com",
      "rss": "https://feeds.feedburner.com/TheHackersNews",
      "scraping": {
        "enabled": true,
        "frequency": "15min",
        "engine": "static",
        "selectors": {
          "article": "article.blog-post",
          "title": "h2.title",
          "content": "div.article-body",
          "date": "time",
          "author": "span.author"
        }
      },
      "categories": ["vulnérabilités", "malware", "actualités"]
    },
    {
      "name": "Krebs on Security",
      "url": "https://krebsonsecurity.com",
      "rss": "https://krebsonsecurity.com/feed/",
      "scraping": {
        "enabled": true,
        "frequency": "1h",
        "engine": "static",
        "selectors": {
          "article": "article.post",
          "title": "h2.entry-title",
          "content": "div.entry-content",
          "date": "time.entry-date",
          "author": "span.author"
        }
      },
      "categories": ["investigations", "fraude", "actualités"]
    }
  ]
}
```

## 7.2 Pipeline de Scraping

```python
# Pseudo-code du pipeline
async def scrape_pipeline(source):
    # 1. Fetch
    html = await fetch(source.url, engine=source.scraping.engine)

    # 2. Parse
    articles = parse(html, selectors=source.scraping.selectors)

    # 3. Deduplicate
    new_articles = filter_duplicates(articles, method="hash+similarity")

    # 4. Enrich
    for article in new_articles:
        article.summary = await ai_summarize(article.content)
        article.category = await ai_classify(article.content)
        article.relevance_score = calculate_relevance(article)
        article.mentioned_cves = extract_cve_ids(article.content)

    # 5. Store
    await store_articles(new_articles)

    # 6. Notify
    for article in new_articles:
        if article.relevance_score > user_threshold:
            await send_desktop_notification(article)
```

## 7.3 Table de Données des Articles Scrapés

```sql
CREATE TABLE scraped_articles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    source VARCHAR(255) NOT NULL,
    source_url VARCHAR(500),
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500),
    author VARCHAR(255),
    content LONGTEXT,
    summary TEXT,
    category VARCHAR(100),
    tags JSON,
    relevance_score DECIMAL(3,2),
    mentioned_cves JSON,
    published_at DATETIME,
    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    hash VARCHAR(64) UNIQUE,
    image_url VARCHAR(500),
    read_time INT,
    is_favorite BOOLEAN DEFAULT FALSE,
    is_read BOOLEAN DEFAULT FALSE,
    user_id INT,
    INDEX idx_source (source),
    INDEX idx_category (category),
    INDEX idx_published (published_at),
    FULLTEXT INDEX ft_content (title, content, summary)
);
```

---

# 8. BASE DE DONNÉES

## Tables Principales

### users
```sql
id, username, email, password_hash, role, 
preferences JSON, created_at, last_login
```

### cves
```sql
id, cve_id, title, description, cvss_score, cvss_vector,
severity, cwe_id, published_at, modified_at, 
references JSON, affected_products JSON, exploits JSON
```

### watchlists
```sql
id, user_id, product_name, vendor, version_pattern,
alert_threshold, created_at
```

### alerts
```sql
id, cve_id, user_id, type, status, severity,
message, created_at, acknowledged_at
```

### reports
```sql
id, title, type, format, file_path, content_json,
created_by, created_at
```

### scraped_articles *(Nouveau)*
```sql
id, source, source_url, title, slug, author, 
content, summary, category, tags, relevance_score,
mentioned_cves, published_at, scraped_at, hash,
image_url, read_time, is_favorite, is_read, user_id
```

### incidents *(Nouveau)*
```sql
id, title, description, severity, status, 
assigned_to, cve_id, created_by, created_at,
resolved_at, resolution_notes
```

### playbooks *(Nouveau)*
```sql
id, name, description, trigger_type, trigger_config,
actions JSON, is_active, created_by, created_at
```

### osint_results *(Nouveau)*
```sql
id, type, target, result, source, 
scanned_at, user_id
```

---

# 9. SÉCURITÉ

| Couche | Mesure |
|--------|--------|
| **Authentification** | JWT + Refresh Token + BCrypt |
| **API** | HTTPS + Validation Pydantic + Rate Limiting |
| **Scraping** | Respect robots.txt + User-Agent rotation + Delays |
| **Base de données** | Sauvegardes automatiques + Journalisation |
| **Cache** | Redis avec TTL + chiffrement des sessions |
| **Fichiers** | Scan antivirus des uploads + sandboxing |

---

# 10. INTERFACE UTILISATEUR

## Menu Principal

```text
📊 Dashboard
🔍 Veille CVE
📰 Actualités & Blogs
🕷️ Scraping de Blogs
🧠 Analyse IA
👁️ Watchlist
🎯 MITRE ATT&CK
🔔 Alertes
📰 Actualités RSS
📄 Rapports
✍️ Générateur d'Articles
🚨 Incidents
⚙️ Playbooks
🌐 OSINT
🔧 Scanner Léger
📝 Signatures YARA/Sigma
👥 Collaboration
🔌 API & Webhooks
⚙️ Paramètres
```

---

# 11. PERFORMANCES

| Métrique | Objectif |
|----------|----------|
| Chargement initial | < 2 secondes |
| Recherche CVE | < 500ms |
| Recherche articles scrapés | < 1 seconde |
| Synchronisation CVE | En arrière-plan |
| Scraping | 30+ sources toutes les 15 min |
| Notifications | Temps réel (WebSocket) |
| Export PDF | < 5 secondes |
| Analyse IA | < 10 secondes |

---

# 12. FONCTIONNALITÉS FUTURES (v2.0)

- Intégration SOC complète
- Version SaaS / Web
- Application mobile Flutter
- Intégration Wazuh, TheHive, MISP
- Corrélation d'événements avancée
- Machine Learning pour détection d'anomalies
- Blockchain pour l'intégrité des rapports
- Marketplace de playbooks communautaires

---

**Vision du produit :** Devenir la plateforme de référence en cybersécurité — la seule application dont un analyste a besoin pour sa veille quotidienne.

---

*Document généré pour CyberPulse — IndraLabs — Juin 2026*
