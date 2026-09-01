[简体中文](README.md) | [繁體中文](README.zh-TW.md) | [English](README.en.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Русский](README.ru.md) | [Kiswahili](README.sw.md) | [Runasimi](README.qu.md)

<div align="center">

<img src="docs/logo.png" width="120" alt="VibeDrop logo">

# VibeDrop

**Werkzeug zur Synchronisierung der Zwischenablage und zur Übertragung von Text und Dateien zwischen Smartphone und Mac — direkte Verbindung im LAN, unabhängig von der Cloud**

[![release](https://img.shields.io/github/v/release/gnehiur/VibeDrop?color=2f6fed)](https://github.com/gnehiur/VibeDrop/releases)
[![license](https://img.shields.io/github/license/gnehiur/VibeDrop?color=green)](LICENSE)
![platform](https://img.shields.io/badge/platform-macOS%20%7C%20Android%20%7C%20iOS-8a63d2)
![i18n](https://img.shields.io/badge/languages-11-2f6fed)
![tauri](https://img.shields.io/badge/Tauri-2.x-ffc131?logo=tauri&logoColor=white)
![rust](https://img.shields.io/badge/Rust-stable-e43717?logo=rust)

[Release herunterladen](https://github.com/gnehiur/VibeDrop/releases) · [Funktionsübersicht](#funktionsübersicht) · [Selbststudium der Nachricht](#selbststudium-der-nachricht-und-worthäufigkeitsbericht)

</div>

---

VibeDrop besteht aus drei Komponenten, die über **WebSocket** direkt im lokalen Netzwerk kommunizieren. Internet und Cloud-Dienste sind nicht erforderlich:

- **Mac-Desktop-App** (`desktop/`) — empfängt Text und Dateien, verteilt die Zwischenablage und bietet die Systemleiste
- **Mobile App** (`mobile/`, Android + iOS) — sendet Text, Bilder, Videos und Dateien und zeigt die Verlaufszeitleiste
- **Home Vault** (`scripts/`) — Heimserver zum Zusammenführen geräteübergreifender Verläufe, Speichern von Medienoriginalen und Sammeln von Probe-Protokollen

---

## Screenshots

**Intelligente Sendekarte „Folgendem Cursor senden“**——ins Smartphone sprechen, und der Text landet automatisch auf dem Computer, auf dem sich der Cursor befindet (für Universal-Control-Szenarien):

<div align="center">
<table>
  <tr>
    <td align="center" colspan="2"><img src="assets/screenshots/desktop-overview.jpg" width="680" alt="Übersicht der macOS-Desktop-App"><br><sub>macOS-Desktop-App — Geräteübersicht · Kopplung · zum Senden hineinziehen</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/screenshots/ios-smart-card.png" width="320" alt="Intelligente Sendekarte unter iOS"><br><sub>iOS (iPhone 17 Pro Max)</sub></td>
    <td align="center"><img src="assets/screenshots/android-smart-card.jpg" width="320" alt="Intelligente Sendekarte unter Android"><br><sub>Android (OnePlus Ace 5)</sub></td>
  </tr>
</table>
</div>

---

## Funktionsübersicht

| Funktion | Mac | Mobil (Android + iOS) |
|------|--------|------------------------|
| 🎯 Intelligente Sendekarte „Folgendem Cursor senden“ | ✅ Meldet Tastatur- und Mausaktivität (`CGEventSource`, keine Berechtigung) | ✅ Sendet Text/Bilder/Dateien automatisch an den Mac mit dem Cursor, folgt innerhalb 1 Sekunde, manuell umschaltbar |
| 📝 Textübertragung (Smartphone → Mac) | ✅ Empfängt Text und simuliert Tastatureingaben | ✅ Tastatur und Spracheingabe bleiben nach dem Senden aktiv, fortlaufendes Diktieren ohne Zusatzschritt |
| 📋 Synchronisierung der Zwischenablage (Mac → Smartphone) | ✅ Überwacht Änderungen und verteilt sie | ✅ Nativer Hintergrunddienst schreibt in die Zwischenablage |
| 🌍 Sprachen | ✅ Systemeinstellung | ✅ 11 Sprachen (vereinfachtes/traditionelles Chinesisch, Englisch, Japanisch, Koreanisch, Spanisch, Französisch, Deutsch, Russisch, Swahili und Quechua), gettext-Rückfall auf Chinesisch bei fehlender Übersetzung |
| 🤝 Automatische Erkennung und Kopplung | ✅ Zeigt ausstehende Kopplungen und verbundene Geräte | ✅ Sucht Macs in der Nähe und koppelt per Prüfcode; Geräte lassen sich umbenennen und zwischen Smartphones automatisch synchronisieren |
| 📜 Verlauf-Zeitleiste | ✅ Zusammengeführte Ansicht aller Geräte + Vorschaubilder | ✅ Führt alle Geräte zusammen, filtert nach Quelle/Ziel/Typ/Original/Zeit und hebt Suchtreffer hervor |
| 📈 Aktivitäts-Heatmap | ✅ Empfangs-Heatmap + Filter per Zelle | ✅ Sende-Heatmap + Filter per Zelle |
| 🔬 Selbststudium der Nachricht | — (Bericht wird von Home Vault erzeugt) | ✅ Vollständiger Bericht im Verlauf: Wortwolke/Redewendungen/Balkendiagramm des Sendeverlaufs, per Scrubbing mit Details |
| 📁 Bidirektionale Dateiübertragung | ✅ Drag-and-drop / Finder-Dienste / Finder-Freigabe | ✅ An Postfach / Bilder ins Fotoalbum, Stapel werden automatisch gepackt |
| 🗄 Home Vault | Heimserver: geräteübergreifende Verlaufszusammenführung · Speicher für Medienoriginale (Hash-Deduplizierung + Range-Streaming) · Sammlung von Probe-Protokollen | ✅ Inkrementeller Push + SSE-Echtzeitsynchronisierung |
| 🔒 PIN-Authentifizierung | ✅ Zufällig erzeugt und in Datei dauerhaft gespeichert | ✅ Nach Kopplung per Prüfcode automatisch gespeichert |
| 🕰 Anzeigezeitzone | ✅ Lokal/Peking/US-Westküste, einheitliche Basis für Anzeige und Statistik | — |
| 📡 Vordergrundbetrieb / Systemleiste | ✅ Systemleiste + Autostart bei Anmeldung | ✅ Permanente Android-Benachrichtigung |

---

## Technische Architektur im Überblick

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

Drei Kommunikationswege, alle direkt im LAN und unabhängig von der Cloud:

1. **Smartphone ↔ Mac**: WebSocket (`:9001/ws`) überträgt nach PIN-Authentifizierung Text, Dateien, Zwischenablage und Aktivitätsabfragen;
2. **Alle Endpunkte → Home Vault**: HTTP (`:8788`) sendet Verlaufsinkremente und Medien und ruft Berichte ab;
3. **Vault → Clients**: dauerhafte SSE-Verbindung (`/api/events`), sofortige Verteilung nach dem Speichern und Heartbeat alle 25 Sekunden.

---

## Kernabläufe im Detail

### Intelligente Sendekarte „Folgendem Cursor senden“

1. Empfängt die Desktop-App `activity_query`, ruft sie `CGEventSourceSecondsSinceLastEventType` auf,
   um „Sekunden seit der letzten Tastatur- oder Mausaktivität“ zu beantworten (keine Berechtigung, kein Thread — sie liest das vorhandene Systemprotokoll für den Bildschirmschoner);
2. Das Smartphone fragt alle verbundenen Macs jede Sekunde ab und vergleicht ihre **relativen Leerlaufsekunden** (unempfindlich gegenüber abweichenden Systemuhren).
   Der frischeste Mac trägt den Cursor: Universal Control liefert echte Tastatur- und Mausereignisse an genau diesen Rechner, weshalb Signal und Tatsache eng gekoppelt sind;
3. Beim Senden von Text, Bildern oder Dateien wird das Ziel sofort festgelegt; der Indikator wechselt auf Klick zwischen Automatik und Handbetrieb.

### Erkennung und Kopplung

Das Smartphone sucht parallel über zwei Wege: UDP-Broadcast + HTTP-Sondierung (`discover_desktops`). Nach Erkennung der Desktop-App beginnt die Kopplung per Prüfcode (der Desktop zeigt eine Bestätigungskarte, beide Seiten vergleichen denselben Code); nach Freigabe wird das Gerät gespeichert und automatisch verbunden.
Ein gespeicherter Gerätename wird über das Vault-Schwarze Brett (`/api/device-names`, serverId als Schlüssel, LWW) zwischen Smartphones synchronisiert.

### Text und Dateien

- Text: Die Aktionen `type` / `type_enter` lassen die Desktop-App mit enigo Tastatureingaben simulieren; der Abwesenheitsmodus verwendet stattdessen
  `clipboard_text` (schreibt nur in die Zwischenablage, für Fernsteuerungswerkzeuge wie UU Remote);
- Dateien: blockweises Übertragungsprotokoll (begin/append/finish/cancel). Auf dem Smartphone landen sie im Postfach oder Fotoalbum,
  auf dem Mac werden sie per Drag-and-drop/Finder-Dienst gesendet. Die gesamte Kette trägt eine `transferId`, sodass Sende- und Empfangsdatensätze exakt zusammengeführt werden;
- Sendeschaltflächen nehmen nicht den Fokus (mousedown preventDefault): Tastatur und Spracheingabe bleiben nach dem Senden aktiv,
  sodass fortlaufendes Diktieren ohne Zusatzschritt möglich ist.

### Verlaufssynchronisierung (inkrementell + Echtzeit)

- Jeder Endpunkt hält lokalen Verlauf + Push-Cursor (`lastPushedEntryId`) und sendet nur Inkremente (gemessen: 3 ms/188 B pro Eintrag);
- Vault führt die Zeitleiste aller Geräte zusammen (`/api/history/merged`). Clients laden normalerweise 2.000 leichte Einträge und einmal je Sitzung 10.000 Einträge tief; ein SSE-Ereignis aktualisiert sofort;
- Gleichnamige Identitäten werden automatisch zusammengeführt (die „frühere Existenz“ mit neuer Zufalls-ID nach Neuinstallation wird der lokalen Identität zugeschlagen); Namen sind Darstellung, Identität beruht auf Fingerabdrücken.

### Speicher für Medienoriginale

Originale werden nach SHA-256 gespeichert (`/api/media/upload`, Streaming + Deduplizierung, 2-GB-Grenze). Jedes Gerät kann ein Original per Hash online abrufen (`/api/media/blob/<hash>`, Range-Streaming) — „lokal verloren ≠ überall verloren“.

### Selbsttest-Sonde beim Start (Blackbox)

Am Anfang von `app.js` werden window.onerror-Erfassung und probe()-Messpunkte installiert. 6 Sekunden nach Start oder 1,5 Sekunden nach einem Fehler geht ein POST an Vault `/api/client-log` und wird nach Gerät gespeichert. Bei schwarzem oder weißem Bildschirm auf echten Geräten nicht raten, sondern das Protokoll lesen.

---

## Codeübersicht

### Mac-Desktop `desktop/`

| Datei | Zeilen | Aufgabe |
|------|------|------|
| `src-tauri/src/main.rs` | ~4900 | HTTP/WS-Server, PIN-Authentifizierung, enigo-Tastatur, arboard-Zwischenablage, Dateiübertragung, Systemleiste, Erkennungsantworten und Aktivitätsmeldung |
| `src/main.js` | ~2600 | Desktop-UI: Geräte, Kopplungsbestätigung, zusammengeführter Verlauf + Vorschaubilder, Empfangs-Heatmap, Zeitzone, Drag-and-drop-Versand |
| `src/style.css` | ~2000 | Desktop-Stile |
| `static/*` | — | Bytegenaue Spiegelung von `mobile/src/` (nach Änderungen am Mobilteil zwingend kopieren; siehe Build-Abschnitt) |

### Mobile App `mobile/` (gemeinsamer Code für Android + iOS)

| Datei | Zeilen | Aufgabe |
|------|------|------|
| `src/app.js` | ~11500 | Gesamte Frontend-Logik: Intelligente Sendekarte, mehrere Geräte, Verlauf (Filter/Suchhervorhebung/virtuelles Scrollen), Heatmap, Vault-Synchronisierung, Medienbetrachter und Sonden |
| `src/i18n.js` | ~110 | Mehrsprachen-Laufzeit nach gettext: t()/Rückfall/Interpolation/Spracherkennung/Wörterbuchcache |
| `src/locales/*.json` | ×10 | Sprachpakete (chinesischer Originaltext ist der Schlüssel; neue Sprache = eine neue Datei) |
| `src-tauri/src/lib.rs` | ~1900 | 16 native Befehle: Verlaufsspeicherung, blockweiser Dateiempfang, Erkennung und Kopplung, Modellerkennung, Vault-Medienupload und Pfadauflösung; iOS-Scrollsperre (KVO beobachtet contentOffset und setzt es vor dem Rendern zurück) |
| `gen/android/.../MainActivity.kt` | — | Konsolenweiterleitung (VibeDropConsole) + Delegation an den ursprünglichen WebChromeClient (Dateiauswahl usw.) |
| `gen/android/.../KeepAliveService.kt` | — | Vordergrundbetrieb |
| `gen/android/.../VideoPlayerActivity.kt` | — | Nativer ExoPlayer (Media3) im Vollbild |
| `gen/android/.../BackgroundClipboardSyncManager.kt` | — | Native Hintergrund-Schreibvorgänge der Zwischenablage |

### Home Vault und Werkzeuge `scripts/`

| Skript | Aufgabe |
|------|------|
| `home-vault-receiver.py` (~1000 Zeilen) | Alle Endpunkte des Heimservers (siehe folgende Tabelle), dauerhaft über launchd |
| `message-self-study.py` | Vollständige jieba-Korpusanalyse → eigenständiger HTML-Bericht (mit Balkendiagramm des Sendeverlaufs) |
| `vault-media-uploader.py` / `sync-home-vault.py` | Vorhandene Medien nachliefern / gespeicherten Verlauf synchronisieren |
| `i18n-check.py` | Mehrsprachen-Qualitätsprüfung: scannt alle t()/data-i18n-Schlüssel und meldet fehlende/überflüssige Paket-Einträge |
| `deploy-android.sh` / `deploy-desktop.sh` / `deploy-ios.sh` | Ein-Befehl-Build und -Bereitstellung für alle drei Plattformen |
| `generate-app-icons.py` / `generate-tray-frames.py` | Erzeugung der Markenressourcen |

### Home-Vault-Endpunkte im Überblick

| Endpunkt | Zweck |
|------|------|
| `POST /api/history/append` · `GET /api/history/merged` | Inkrementelle Aufnahme / zusammengeführte Zeitleiste |
| `GET /api/events` | SSE: sofortige Verteilung nach Speicherung |
| `POST /api/media/upload` · `/lookup` · `GET /api/media/blob/<hash>` | Medienspeicher: deduplizierte Aufnahme/Suche/Range-Streaming-Abruf |
| `GET/POST /api/device-names` | Schwarzes Brett für Gerätenamen (LWW) |
| `POST /api/client-log` | Sammlung der Sonden-Blackbox |
| `GET /report/self-study` | Selbststudiumsbericht (SWR: sofortiger Cache, Hintergrund-Neuberechnung nach Ablauf, `?refresh=1` erzwingt Aktualisierung) |

---

## Praxiserfahrungen nach Plattform

### Unterschiede der WebView-Engines (wichtig)

| | Android | iOS | macOS-Desktop |
|---|---------|-----|-----------|
| Engine | Chromium | **WKWebView** | **WKWebView (wie iOS!)** |
| `content-visibility: auto` | ✅ Native Virtualisierung | ❌ Schwarzer Bildschirm | ❌ Leerstellen beim Scrollen |
| Strategie für lange Listen | content-visibility | Virtuelles Scrollen mit JS | Abschnittsweises Einhängen |
| Chinesische Segmentierung mit `Intl.Segmenter` | ❌ Trennt Einzelzeichen | ✅ Vollständiges Wörterbuch | ✅ |

**Fazit: Engineübergreifende chinesische Segmentierung darf nur serverseitiges jieba verwenden; content-visibility ist ausschließlich unter Android erlaubt.**

### iOS

- **Festes Layout**: Das Scrollen des äußeren WKWebView ist durch die App-Hülle deaktiviert (`isScrollEnabled=false` blockiert nur Gesten;
  WebKit blendet die Tastatur durch programmgesteuertes Scrollen ein, daher muss **KVO zusätzlich contentOffset beobachten und vor dem Rendern zurücksetzen**;
  der fixierte „Ursprung“ ist die Systemruhelage `-adjustedContentInset`, nicht (0,0)); die Sperre bei jeder Rückkehr in den Vordergrund erneut installieren;
- Paketregel: `cargo tauri ios build --export-method debugging`, nicht direkt Xcode Run verwenden;
- Kostenlose Signaturen gelten 7 Tage ab Erstellung und brauchen eine automatische Erneuerungspipeline.

### Android

- Ein angepasster WebChromeClient **muss an den ursprünglichen Client delegieren** (onShowFileChooser usw.); vollständiges Ersetzen legt die Dateiauswahl still;
- Die echte Konsole liefert `adb logcat -d VibeDropConsole:I "*:S"`;
- Die fünf „Cannot redefine property“-Fehler beim Start sind harmloses Rauschen durch doppelte Ausführung des Tauri-Injektionsskripts und müssen nicht untersucht werden.

### Mac

- Die enigo-Tastatursimulation läuft in einem eigenen Thread; Zwischenablage alle 500 ms abfragen → broadcast channel → jede WS-Verbindung;
- Der interne Name der Desktop-Binärdatei bleibt `voicedrop` (bei pgrep beachten).

---

## Sprachen (i18n)

Das Projekt folgt gettext: **Der chinesische Originaltext ist der Schlüssel**. `t('发送并回车')` schlägt im Wörterbuch der aktuellen Sprache nach und fällt bei fehlender Übersetzung auf das chinesische Original zurück (auch teilweise übersetzt jederzeit veröffentlichbar). Variablen verwenden Platzhalter wie `t('已改名为 {name}', {name})`; Zeichenkettenverkettung ist verboten.
Derzeit gibt es 11 Sprachen. Eine neue Sprache bedeutet eine Datei `locales/<lang>.json` + eine Zeile in der Zuordnungstabelle von `i18n.js`.

- Qualitätsprüfung: `python3 scripts/i18n-check.py --strict` (Schlüsselabdeckung/Platzhalterintegrität);
- Semantische Abnahme: 30 Kernbegriffe pro Sprache manuell prüfen (Maschinen garantieren keine Bedeutung; siehe `docs/i18n-规范.md`);
- Im Sprachwähler stehen die **Eigenbezeichnungen der Sprachen** mit chinesischer und englischer Aussprachehilfe; kein Sprachpaket übersetzt sie.

---

## Build und Bereitstellung

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

**Zwei Regeln**:

1. Nach Änderungen an app.js / index.html / style.css / i18n.js / locales/ in `mobile/src/`
   **muss nach `desktop/static/` kopiert werden** (mobile Browserfassung des Desktop-HTTP-Dienstes);
2. **Die beiden Tauri-Builds dürfen nicht parallel laufen** (ihr gemeinsamer lokaler IPC-Kanal kollidiert); sie müssen nacheinander ausgeführt werden.

---

## GitHub-Veröffentlichungen

Ein Push eines `v*`-Tags löst `release.yml` aus: signierte APK + macOS-dmg automatisch bauen und als GitHub Release veröffentlichen;
`ci.yml` führt bei jedem Push Build-Prüfungen und Python-Unit-Tests aus.

```bash
git tag -a v0.x.y -m "说明" && git push origin v0.x.y
```

---

## Selbststudium der Nachricht und Worthäufigkeitsbericht

Analysiert den eigenen Home-Vault-Verlaufskorpus nach Wortsegmentierung und -häufigkeit, Redewendungen, häufigen Phrasen, monatlicher Themenentwicklung (TF-IDF) und Sendeverlauf (Balkendiagramme nach Stunde/Tag, per Finger-Scrubbing mit Details). Der eigenständige HTML-Bericht entsteht vollständig lokal; keine Daten verlassen das Gerät.

**Direkt in der App ansehen**: Verlauf → Karte „Selbststudium der Nachricht“ → Vollständigen Bericht öffnen (Home-Vault-Endpunkt `/report/self-study`, sofort aus SWR-Cache, nach Ablauf Neuberechnung im Hintergrund, `?refresh=1` erzwingt neuen Lauf).

Auch manuell erzeugbar:

```bash
python3 -m venv .venv && .venv/bin/pip install jieba
.venv/bin/python scripts/message-self-study.py http://<你的vault地址>:8788
```

Der Bericht wird in `~/Downloads/` ausgegeben. Der Vertrag für die Mehrsprachenarbeit steht in `docs/i18n-规范.md`.
