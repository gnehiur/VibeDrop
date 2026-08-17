[简体中文](README.md) | [繁體中文](README.zh-TW.md) | [English](README.en.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Русский](README.ru.md) | [Kiswahili](README.sw.md) | [Runasimi](README.qu.md)

<div align="center">

<img src="docs/logo.png" width="120" alt="VibeDrop logo">

# VibeDrop

**Outil de synchronisation du presse-papiers et de transfert de texte et de fichiers entre un téléphone et un Mac — connexion directe sur le réseau local, sans dépendance au cloud**

[![release](https://img.shields.io/github/v/release/jncdke/VibeDrop?color=2f6fed)](https://github.com/jncdke/VibeDrop/releases)
[![license](https://img.shields.io/github/license/jncdke/VibeDrop?color=green)](LICENSE)
![platform](https://img.shields.io/badge/platform-macOS%20%7C%20Android%20%7C%20iOS-8a63d2)
![i18n](https://img.shields.io/badge/languages-11-2f6fed)
![tauri](https://img.shields.io/badge/Tauri-2.x-ffc131?logo=tauri&logoColor=white)
![rust](https://img.shields.io/badge/Rust-stable-e43717?logo=rust)

[Télécharger la Release](https://github.com/jncdke/VibeDrop/releases) · [Fonctionnalités](#fonctionnalités) · [message d'auto-apprentissage](#message-dauto-apprentissage-et-rapport-de-fréquence-des-mots)

</div>

---

VibeDrop se compose de trois éléments qui communiquent directement sur le réseau local via **WebSocket**, sans Internet ni service cloud :

- **Application de bureau Mac** (`desktop/`) — réception de texte et de fichiers, diffusion du presse-papiers, barre des menus système
- **Application mobile** (`mobile/`, Android + iOS) — envoi de texte, d'images, de vidéos et de fichiers, chronologie de l'historique
- **Home Vault** (`scripts/`) — serveur domestique pour fusionner l'historique entre appareils, conserver les médias originaux et collecter les journaux des sondes

---

## Captures d'écran

**Carte d'envoi intelligente « Envoyer le curseur suivant »**——parlez au téléphone et le texte arrive automatiquement sur l'ordinateur où se trouve le curseur (scénario avec Commande universelle) :

<div align="center">
<table>
  <tr>
    <td align="center" colspan="2"><img src="assets/screenshots/desktop-overview.jpg" width="680" alt="Vue d'ensemble de l'application de bureau macOS"><br><sub>Application de bureau macOS — appareils · jumelage · glisser pour envoyer</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/screenshots/ios-smart-card.png" width="320" alt="Carte d'envoi intelligente iOS"><br><sub>iOS (iPhone 17 Pro Max)</sub></td>
    <td align="center"><img src="assets/screenshots/android-smart-card.jpg" width="320" alt="Carte d'envoi intelligente Android"><br><sub>Android (OnePlus Ace 5)</sub></td>
  </tr>
</table>
</div>

---

## Fonctionnalités

| Fonction | Mac | Mobile (Android + iOS) |
|------|--------|------------------------|
| 🎯 Carte d'envoi intelligente « Envoyer le curseur suivant » | ✅ Signale l'activité du clavier et de la souris (`CGEventSource`, aucune autorisation) | ✅ Envoie automatiquement texte, images et fichiers au Mac où se trouve le curseur, le suit en 1 seconde et permet une sélection manuelle |
| 📝 Transfert de texte (téléphone → Mac) | ✅ Reçoit et simule la saisie au clavier | ✅ Conserve le clavier et la saisie vocale après l'envoi pour dicter sans action supplémentaire |
| 📋 Synchronisation du presse-papiers (Mac → téléphone) | ✅ Surveille les changements et les diffuse | ✅ Un service natif en arrière-plan écrit dans le presse-papiers |
| 🌍 Langues | ✅ Réglage système | ✅ 11 langues (chinois simplifié/traditionnel, anglais, japonais, coréen, espagnol, français, allemand, russe, swahili et quechua), avec retour au chinois façon gettext lorsqu'une traduction manque |
| 🤝 Découverte automatique et jumelage | ✅ Affiche les demandes de jumelage à confirmer et les appareils connectés | ✅ Recherche les Mac à proximité et les jumelle par code de vérification ; les appareils peuvent être renommés et synchronisés automatiquement entre téléphones |
| 📜 Chronologie de l'Historique | ✅ Vue fusionnée de tous les appareils + miniatures | ✅ Fusion de tous les appareils, filtres par source/cible/type/original/heure et mise en évidence de la recherche |
| 📈 Carte thermique des activités | ✅ Carte de réception + filtre par cellule | ✅ Carte d'envoi + filtre par cellule |
| 🔬 message d'auto-apprentissage | — (rapport généré par Home Vault) | ✅ Rapport complet intégré à l'Historique : nuage de mots/tics de langage/histogramme des tendances d'envoi, avec balayage pour les détails |
| 📁 Transfert bidirectionnel de fichiers | ✅ Glisser-déposer / services Finder / partage Finder | ✅ Envoyer à la boîte / images dans l'album photo, lots automatiquement regroupés |
| 🗄 Home Vault | Serveur domestique : fusion de l'historique entre appareils · stockage des originaux (déduplication par hachage + streaming Range) · collecte des journaux de sondes | ✅ Envoi incrémental + synchronisation SSE en temps réel |
| 🔒 Authentification par PIN | ✅ Génération aléatoire et conservation dans un fichier | ✅ Enregistrement automatique après jumelage par code de vérification |
| 🕰 Réglage du fuseau horaire d'affichage | ✅ Local/Pékin/côte ouest des États-Unis, même référence pour l'affichage et les statistiques | — |
| 📡 Maintien au premier plan / barre des menus | ✅ Barre des menus système + ouverture à la connexion | ✅ Notification Android permanente |

---

## Vue d'ensemble de l'architecture technique

```
        ┌────────────────────────────┐      ┌────────────────────────────┐
        │   Mac 桌面端 × N (Tauri 2) │      │  手机端 × N (Tauri 2 Mobile)│
        │  ├ Axum HTTP/WS :9001      │◄────►│  ├ app.js  单文件前端       │
        │  ├ enigo 键盘模拟          │  WS  │  ├ lib.rs  16 个原生命令    │
        │  ├ arboard 剪贴板监听      │      │  ├ Kotlin  保活/播放器/剪贴板│
        │  ├ CGEventSource 活动上报  │      │  └ iOS     滚动锁(KVO)      │
        │  └ UDP/HTTP 发现应答       │      └──────────────┬─────────────┘
        └──────────────┬─────────────┘                     │
                       │              HTTP :8788           │
                       ▼                                   ▼
        ┌──────────────────────────────────────────────────────────┐
        │        Home Vault (家庭服务器, home-vault-receiver.py)     │
        │  跨设备历史合并 · 媒体原件仓(哈希去重+Range) · SSE 广播     │
        │  设备名公告板 · 探针日志回收 · 自我研究报告(SWR)            │
        └──────────────────────────────────────────────────────────┘
```

Trois voies de communication, toutes directes sur le réseau local et indépendantes du cloud :

1. **Téléphone ↔ Mac** : WebSocket (`:9001/ws`), transfert de texte, fichiers, presse-papiers et requêtes d'activité après authentification PIN ;
2. **Tous les appareils → Home Vault** : HTTP (`:8788`), envoi incrémental de l'historique, téléversement des médias et récupération des rapports ;
3. **Vault → clients** : connexion SSE persistante (`/api/events`), diffusion dès l'écriture sur disque et pulsation toutes les 25 secondes.

---

## Détail des flux principaux

### Carte d'envoi intelligente « Envoyer le curseur suivant »

1. Quand l'application de bureau reçoit `activity_query`, elle appelle `CGEventSourceSecondsSinceLastEventType`
   pour répondre « combien de secondes depuis la dernière activité clavier ou souris » (zéro autorisation, zéro thread : elle lit le registre que le système tient déjà pour l'économiseur d'écran) ;
2. Le téléphone interroge chaque seconde tous les Mac connectés et compare leurs **secondes d'inactivité relatives** (insensibles aux écarts d'horloge entre machines).
   Le plus récent est le Mac qui porte le curseur : Commande universelle transmet réellement les événements de clavier et de souris à cette machine, ce qui lie étroitement le signal au fait observé ;
3. La cible est verrouillée au moment exact de l'envoi du texte, des images ou des fichiers ; l'indicateur permet d'alterner entre mode automatique et manuel.

### Découverte et jumelage

Le téléphone analyse deux voies en parallèle : diffusion UDP + sondage HTTP (`discover_desktops`). Après avoir découvert l'application de bureau, il lance le jumelage par code de vérification (le bureau affiche une carte en attente et les deux côtés vérifient le même code) ; après approbation, l'appareil est enregistré et connecté automatiquement.
Une fois le nom personnalisé enregistré, le tableau d'affichage de Vault (`/api/device-names`, serverId comme clé, LWW) le synchronise entre les téléphones.

### Texte et fichiers

- Texte : les actions `type` / `type_enter` font simuler la saisie par enigo sur le bureau ; le Mode Absent utilise plutôt
  `clipboard_text` (écriture dans le presse-papiers uniquement, avec des outils de contrôle à distance tels que UU Remote) ;
- Fichiers : protocole de transfert par blocs (begin/append/finish/cancel). Sur le téléphone, ils vont dans la boîte ou l'album photo ;
  sur le Mac, le glisser-déposer ou un service Finder les envoie immédiatement. Toute la chaîne porte un identifiant `transferId`, ce qui permet de fusionner précisément les enregistrements d'envoi et de réception ;
- Les boutons d'envoi ne prennent pas le focus (mousedown preventDefault) : les sessions de clavier et de saisie vocale restent actives après l'envoi,
  ce qui permet de dicter sans action supplémentaire.

### Synchronisation de l'historique (incrémentale + temps réel)

- Chaque appareil conserve un historique local + un curseur d'envoi (`lastPushedEntryId`) et ne pousse que les ajouts (mesure réelle : 3 ms/188 B par entrée) ;
- Vault fusionne la chronologie de tous les appareils (`/api/history/merged`). Les clients récupèrent normalement 2 000 entrées légères et effectuent une lecture approfondie de 10 000 entrées une fois par session ; un événement SSE déclenche une actualisation immédiate ;
- Les identités portant le même nom sont fusionnées automatiquement (la « vie antérieure » dotée d'un nouvel ID aléatoire après réinstallation est intégrée à l'identité locale) ; le nom relève de l'affichage, l'identité de l'empreinte.

### Stockage des médias originaux

Les originaux sont stockés par SHA-256 (`/api/media/upload`, streaming + déduplication, limite de 2 Go). Tout appareil peut récupérer l'original en ligne par son hachage (`/api/media/blob/<hash>`, streaming Range pris en charge) — « perdu localement ≠ perdu partout ».

### Sonde d'autodiagnostic au démarrage (boîte noire)

Le début de `app.js` installe la capture window.onerror et les points de mesure probe(). Six secondes après le démarrage ou 1,5 seconde après une erreur, un POST est envoyé à Vault `/api/client-log` et conservé par appareil. Pour un écran noir ou blanc sur un appareil réel, ne devinez pas : consultez les journaux.

---

## Carte du code

### Application de bureau Mac `desktop/`

| Fichier | Lignes | Responsabilité |
|------|------|------|
| `src-tauri/src/main.rs` | ~4900 | Serveur HTTP/WS, authentification PIN, clavier enigo, presse-papiers arboard, envoi/réception de fichiers, barre des menus, réponses de découverte et remontée d'activité |
| `src/main.js` | ~2600 | UI de bureau : appareils, confirmation de jumelage, historique fusionné + miniatures, carte de réception, fuseau horaire et envoi par glisser-déposer |
| `src/style.css` | ~2000 | Styles du bureau |
| `static/*` | — | Miroir octet pour octet de `mobile/src/` (à recopier après toute modification mobile ; voir la section de compilation) |

### Application mobile `mobile/` (même code pour Android + iOS)

| Fichier | Lignes | Responsabilité |
|------|------|------|
| `src/app.js` | ~11500 | Toute la logique front-end : Carte d'envoi intelligente, connexions multiples, chronologie (filtres/recherche en surbrillance/défilement virtuel), carte thermique, synchronisation Vault, visionneuse de médias et sondes |
| `src/i18n.js` | ~110 | Moteur multilingue façon gettext : t()/repli/interpolation/détection de langue/cache des dictionnaires |
| `src/locales/*.json` | ×10 | Paquets de langues (le texte chinois original est la clé ; ajouter une langue revient à ajouter un fichier) |
| `src-tauri/src/lib.rs` | ~1900 | 16 commandes natives : persistance de l'historique, réception de fichiers par blocs, découverte et jumelage, identification du modèle, téléversement des médias vers Vault et résolution des chemins ; verrouillage du défilement iOS (KVO observe contentOffset et le remet à zéro avant le rendu) |
| `gen/android/.../MainActivity.kt` | — | Transfert de console (VibeDropConsole) + délégation au WebChromeClient d'origine (sélecteur de fichiers, etc.) |
| `gen/android/.../KeepAliveService.kt` | — | Maintien au premier plan |
| `gen/android/.../VideoPlayerActivity.kt` | — | Lecteur natif ExoPlayer (Media3) en plein écran |
| `gen/android/.../BackgroundClipboardSyncManager.kt` | — | Écriture native du presse-papiers en arrière-plan |

### Home Vault et outils `scripts/`

| Script | Responsabilité |
|------|------|
| `home-vault-receiver.py` (~1000 lignes) | Tous les endpoints du serveur domestique (voir le tableau ci-dessous) ; persistant via launchd |
| `message-self-study.py` | Analyse complète du corpus par jieba → rapport HTML autonome (avec histogramme des tendances d'envoi) |
| `vault-media-uploader.py` / `sync-home-vault.py` | Rattrapage des médias existants / synchronisation de l'historique sur disque |
| `i18n-check.py` | Contrôle qualité multilingue : analyse toutes les clés t()/data-i18n et signale les entrées manquantes ou superflues des paquets |
| `deploy-android.sh` / `deploy-desktop.sh` / `deploy-ios.sh` | Compilation et déploiement des trois plateformes en une commande |
| `generate-app-icons.py` / `generate-tray-frames.py` | Génération des ressources de marque |

### Référence rapide des endpoints Home Vault

| Endpoint | Rôle |
|------|------|
| `POST /api/history/append` · `GET /api/history/merged` | Ingestion incrémentale / chronologie fusionnée |
| `GET /api/events` | SSE : diffusion dès l'écriture sur disque |
| `POST /api/media/upload` · `/lookup` · `GET /api/media/blob/<hash>` | Stockage média : ingestion dédupliquée/recherche/lecture en streaming Range |
| `GET/POST /api/device-names` | Tableau des noms d'appareils (LWW) |
| `POST /api/client-log` | Collecte de la boîte noire des sondes |
| `GET /report/self-study` | Rapport d'auto-apprentissage (SWR : cache instantané, recalcul en arrière-plan après expiration, `?refresh=1` force l'actualisation) |

---

## Retours d'expérience par plateforme

### Différences entre moteurs WebView (important)

| | Android | iOS | Bureau macOS |
|---|---------|-----|-----------|
| Moteur | Chromium | **WKWebView** | **WKWebView (comme iOS !)** |
| `content-visibility: auto` | ✅ Virtualisation native | ❌ Écran noir | ❌ Blanc lors du défilement |
| Stratégie pour les longues listes | content-visibility | Défilement virtuel JS | Montage par fragments |
| Segmentation chinoise avec `Intl.Segmenter` | ❌ Découpe caractère par caractère | ✅ Dictionnaire complet | ✅ |

**Conclusion : la segmentation chinoise entre moteurs doit utiliser jieba côté serveur ; content-visibility n'est autorisé que sur Android.**

### iOS

- **Mise en page fixe** : le défilement du WKWebView externe est désactivé par l'architecture de l'enveloppe (`isScrollEnabled=false` ne bloque que les gestes ;
  WebKit révèle le clavier par défilement programmatique, il faut donc aussi **observer contentOffset avec KVO et le remettre en place avant le rendu** ;
  l'« origine » épinglée est la position de repos système `-adjustedContentInset`, pas (0,0)) ; réinstaller le verrou à chaque retour au premier plan ;
- Règle de création du paquet : `cargo tauri ios build --export-method debugging`, sans lancer directement Xcode Run ;
- La signature gratuite reste valide 7 jours à partir de sa création et nécessite une chaîne de renouvellement automatique.

### Android

- Un WebChromeClient personnalisé **doit déléguer au client d'origine** (onShowFileChooser, etc.) ; le remplacer entièrement désactive le sélecteur de fichiers ;
- La vraie console se consulte avec `adb logcat -d VibeDropConsole:I "*:S"` ;
- Les cinq erreurs « Cannot redefine property » au démarrage sont un bruit sans gravité causé par la double exécution du script injecté par Tauri ; inutile de les analyser.

### Mac

- La simulation du clavier par enigo tourne dans un thread séparé ; le presse-papiers est interrogé toutes les 500 ms → broadcast channel → chaque connexion WS ;
- Le nom interne du binaire de bureau reste `voicedrop` (à retenir avec pgrep).

---

## Langues (i18n)

Le projet suit le modèle gettext : **le texte chinois original est la clé**. `t('发送并回车')` consulte le dictionnaire de la langue active et, si une traduction manque, revient au chinois original (une traduction partielle reste toujours publiable). Les variables emploient des paramètres comme `t('已改名为 {name}', {name})` ; la concaténation de chaînes est interdite.
Il existe actuellement 11 langues. En ajouter une signifie créer un fichier `locales/<lang>.json` + une ligne dans la table de correspondance de `i18n.js`.

- Contrôle qualité : `python3 scripts/i18n-check.py --strict` (couverture des clés/intégrité des paramètres) ;
- Validation sémantique : relire manuellement 30 termes essentiels par langue (une machine ne garantit pas le sens ; voir `docs/i18n-规范.md`) ;
- Le sélecteur affiche le **nom propre de chaque langue** accompagné d'aides de prononciation chinoises et anglaises, et aucun paquet ne les traduit.

---

## Compilation et déploiement

```bash
# Android(需 cargo + Android SDK 于 PATH)
./scripts/deploy-android.sh          # 构建签名 APK + adb 安装启动

# macOS 桌面端
./scripts/deploy-desktop.sh          # 构建 + 本地自签 + 装入 /Applications
#   --skip-build --skip-icons        # 复用现成产物只重装(异机编译后拷贝场景)

# iOS(必须走 Tauri 管线)
cd mobile/src-tauri && cargo tauri ios build --export-method debugging
xcrun devicectl device install app --device <UDID> gen/apple/build/arm64/VibeDrop.ipa
```

**Deux règles** :

1. Après toute modification de app.js / index.html / style.css / i18n.js / locales/ dans `mobile/src/`,
   **recopier impérativement vers `desktop/static/`** (version navigateur mobile servie par le HTTP de bureau) ;
2. **Les deux compilations Tauri ne peuvent pas s'exécuter en parallèle** (elles partagent un canal IPC local et entrent en conflit) ; elles doivent être séquentielles.

---

## Publications GitHub

L'envoi d'un tag `v*` déclenche `release.yml` : construction automatique d'un APK signé + dmg macOS, puis publication dans GitHub Release ;
`ci.yml` exécute les contrôles de compilation et les tests unitaires Python à chaque push.

```bash
git tag -a v0.x.y -m "说明" && git push origin v0.x.y
```

---

## message d'auto-apprentissage et rapport de fréquence des mots

Analysez votre propre corpus d'historique Home Vault : segmentation et fréquence des mots, tics de langage, expressions fréquentes, évolution mensuelle des sujets (TF-IDF) et tendances d'envoi (histogrammes par heure/jour à parcourir du doigt pour les détails). Un rapport HTML autonome est produit entièrement en local, sans transmission des données.

**Consultation directe dans l'application** : Historique → carte « message d'auto-apprentissage » → Ouvrir le rapport complet (endpoint Home Vault `/report/self-study`, ouverture instantanée depuis le cache SWR, recalcul en arrière-plan après expiration, `?refresh=1` force une nouvelle exécution).

Vous pouvez aussi le générer manuellement :

```bash
python3 -m venv .venv && .venv/bin/pip install jieba
.venv/bin/python scripts/message-self-study.py http://<你的vault地址>:8788
```

Le rapport est écrit dans `~/Downloads/`. Le contrat de mise en œuvre multilingue se trouve dans `docs/i18n-规范.md`.
