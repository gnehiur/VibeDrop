[简体中文](README.md) | [繁體中文](README.zh-TW.md) | [English](README.en.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Русский](README.ru.md) | [Kiswahili](README.sw.md) | [Runasimi](README.qu.md)

<div align="center">

<img src="docs/logo.png" width="120" alt="VibeDrop logo">

# VibeDrop

**Telefonowan Macwan portapapelesta tinkuchinapaq, qillqatawan archivokunatawan apachinapaq yanapakuy — local redpi chiqalla tinkun, mana cloudta munaspa**

[![release](https://img.shields.io/github/v/release/jncdke/VibeDrop?color=2f6fed)](https://github.com/jncdke/VibeDrop/releases)
[![license](https://img.shields.io/github/license/jncdke/VibeDrop?color=green)](LICENSE)
![platform](https://img.shields.io/badge/platform-macOS%20%7C%20Android%20%7C%20iOS-8a63d2)
![i18n](https://img.shields.io/badge/languages-11-2f6fed)
![tauri](https://img.shields.io/badge/Tauri-2.x-ffc131?logo=tauri&logoColor=white)
![rust](https://img.shields.io/badge/Rust-stable-e43717?logo=rust)

[Release urquy](https://github.com/jncdke/VibeDrop/releases) · [Ruraykuna](#ruraykuna) · [Willay kikillanmanta taqwiy](#willay-kikillanmanta-taqwiy-hinaspa-simi-kuti-yupay-informe)

</div>

---

VibeDropqa kimsa t'aqayuqmi; **WebSocket** nisqawan local red ukhupi chiqalla riman, mana Internetta nitaq cloud yanapakuyta munaspa:

- **Mac computadorapa programa** (`desktop/`) — qillqata/archivokunata chaskiy, portapapelesta willay, sistema bandeja
- **Telefonopa programa** (`mobile/`, Android + iOS) — qillqata/rikch'ata/videota/archivokunata kachay, pacha ñanpi Historial
- **Home Vault** (`scripts/`) — wasipi servidor: dispozitivokunapa Historialninta huñuy, qallariy midya waqaychana, sonda logkunata chaskiy

---

## Pantalla rikchakuna

**Yuyayniyuq kachana tarjeta «Cursorta qatispa kachay»** — telefonopi rimay; qillqaqa cursor may computadorapi kachkan chayman kikillanmanta chayan (Control Universalwan llamk'ananpaq):

<div align="center">
<table>
  <tr>
    <td align="center" colspan="2"><img src="assets/screenshots/desktop-overview.jpg" width="680" alt="macOS computadorapa programa tukuy rikuy"><br><sub>macOS computadorapa programa — dispozitivokunapa tukuy rikuy · masichay · aysaspa kachay</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/screenshots/ios-smart-card.png" width="320" alt="iOS Yuyayniyuq kachana tarjeta"><br><sub>iOS (iPhone 17 Pro Max)</sub></td>
    <td align="center"><img src="assets/screenshots/android-smart-card.jpg" width="320" alt="Android Yuyayniyuq kachana tarjeta"><br><sub>Android (OnePlus Ace 5)</sub></td>
  </tr>
</table>
</div>

---

## Ruraykuna

| Ruray | Mac computadorapa programa | Telefonopa programa (Android + iOS) |
|------|--------|------------------------|
| 🎯 Yuyayniyuq kachana tarjeta «Cursorta qatispa kachay» | ✅ Teclado/mouse kuyusqanta willan (`CGEventSource`, mana atiyta mañakuspa) | ✅ Qillqata/rikch'ata/archivota cursor may Mac-pi kachkan chayman kikillanmanta kachan; sapa 1 segundopi qatin, makiwanpas tikray atikun |
| 📝 Qillqa apachiy (telefono → Mac) | ✅ Chaskispa teclado qillqayta rikch'achin | ✅ Kachasqaña kaptinpas tecladowan vozwan qillqay kichasqalla qhipan; mana huk rurayta yapaspa qatipalla rimay atikun |
| 📋 Portapapeles tinkuchiy (Mac → telefono) | ✅ Tikrasqanta uyarin hinaspa willan | ✅ Sistema qhipa servicio portapapelespi qillqan |
| 🌍 Achka simi | ✅ Sistemata qatiy | ✅ 11 simikuna (chino simplificado/tradicional, inglés, japonés, coreano, español, francés, alemán, ruso, kiswahili, Runasimi); gettext hina, mana tikrasqa kaptin chinoman kutin |
| 🤝 Kikillanmanta taripay hinaspa masichay | ✅ Arí ninapaq suyaq masichayta, tinkisqa dispositivokunata rikuchin | ✅ Qaylla computadorakunata maskan, chiqapchana yupaywan masichan; dispositivo sutinta tikray atikun, hinaspa telefonokunapura kikillanmanta tinkuchikun |
| 📜 Historialpa pacha ñan | ✅ Llapan dispositivokunata huñuspa rikuchin + uchuy rikch'a | ✅ Llapan dispositivokunata huñun; maymanta/mayman/rikchaq/qallariy archivo/pacha nisqawan suyun; maskasqanta sut'ita rikuchin |
| 📈 Kallpa mapa | ✅ Mapata chaskin + puntokunawan suyun | ✅ Mapata kachan + puntokunawan suyun |
| 🔬 Willay kikillanmanta t'aqwiy | — (Home Vaultmi informeta ruran) | ✅ Historial ukhupi hunt'asqa informe: simi phuyu/sapa kuti nisqa rimay/kachay puriyninpa sayaq siq'in (scrub nisqawan ñut'u willayta maskay) |
| 📁 Archivo apachiy (iskayninman) | ✅ Aysay / Finder servicio / Findermanta rakiy | ✅ Chaskinaman kachay / rikch'akuna albumman rin, achka archivo kikillanmanta q'ipikun |
| 🗄 Home Vault | Wasipi servidor: dispozitivokunapura Historial huñuy · qallariy midya waqaychana (hashwan iskay kutita harkay + Rangewan purichiy) · sonda logkunata chaskiy | ✅ Yapasqallata kachay + SSEwan kunan pacha tinkuchiy |
| 🔒 PIN yupaywan chiqapchay | ✅ Munasqan hina paqarichin, archivopi wiñaypaq waqaychan | ✅ Chiqapchana yupaywan masichaspa kikillanmanta waqaychan |
| 🕰 Rikuchina pachamarka tupachiy | ✅ Kay computadorapa/Beijing/Estados Unidospa inti haykuna pachan; rikuchiywan yupaywan huk kikin kamachiyta qatin | — |
| 📡 Ñawpaq llamk'aypi kawsachiy / bandeja | ✅ Sistema bandeja + sistema qallariywan kichakuy | ✅ Android willana barrapi wiñaypaq |

---

## Tecnica sayayninpa pisiyachisqa rikuy

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

Kimsa rimanakuy ñanmi kan; llapanmi local red ukhupi chiqalla tinkun, mana cloudta munaspa:

1. **Telefono ↔ Mac**: WebSocket (`:9001/ws`), PIN chiqapchasqamanta qillqata/archivota/portapapelesta/kallpa tapuyta apachin;
2. **Llapan programa → Home Vault**: HTTP (`:8788`), Historialpa yapasqallanta kachay, midyata wichachiy, informeta chaskiy;
3. **Vault → programas**: SSE suni tinkuy (`/api/events`), Historial disco-pi churasqa ratulla willan, sapa 25s sunqu kuyuchiywan kawsachin.

---

## Hatun ruraykunapa sutichaynin

### Yuyayniyuq kachana tarjeta «Cursorta qatispa kachay»

1. Computadorapa programa `activity_query` chaskispa `CGEventSourceSecondsSinceLastEventType` nisqata waqyan
   (mana atiyta nitaq threadta munaspa — pantalla waqaychanapaq sistema ñam waqaychasqan yupayta ñawinchan), hinaspa «qhipa teclado/mouse kuyusqanmanta hayk'a segundo» nisqata kutichin;
2. Telefonoqa sapa 1 segundopi llapan tinkisqa Macta tapun, **wak computadoraq samasqan segundokunata** tupachin (iskay computadorapa reloj pantaynin mana nanachinchu);
   aswan musuq kuyusqayuqmi cursorpa computadoran — Control Universalmi teclado/mouse kuyuyta cursorpa chiqap kasqan computadoraman chayachin, chaymi señalwan chiqap ruraywan sinchi tinkisqa;
3. Kachay pachapi (qillqa/rikch'a/archivo) taripana hark'asqa qhipan; rikuchiqta ñit'ispa automático/manual chawpipi muyuchiy atikun.

### Taripay hinaspa masichay

Telefonopa programa iskay ñanpi kuska maskan: UDP broadcast + HTTP sonda (`discover_desktops`); computadorapa programata tarispa
chiqapchana yupaywan masichan (computadorapi arí ninapaq tarjeta rikurin, iskayninku kikin yupayta qhawanku), arí nisqa kaptin waqaychaspa kikillanmanta tinkun.
Dispositivopa sapanchasqa sutin waqaychasqamanta Vaultpa sutinkuna tablónninwan (`/api/device-names`, serverIdmi llave, LWW) telefonokunapura tinkuchikun.

### Qillqawan archivokunawan

- Qillqa: `type` / `type_enter` ruraykuna; computadorapa programapi enigo teclado qillqayta rikch'achin; hawa kaypiqa
  `clipboard_text` ñanta purin (portapapelesllapi qillqan, UU Remote hina karumanta kamachina yanapakuykunawan llamk'ananpaq);
- Archivo: t'aqakama apachina protocolo (begin/append/finish/cancel); telefonopi Chaskinaman utaq albumman yaykun,
  computadorapi aysaspa/Finder serviciowan kachakun; tukuy ñanpi `transferId` apachina yupayta apamun, chaymi kachaqpa chaskiqpa registroykunata chiqap huñuyta atichin;
- Kachana botónqa focusta mana qichunchu (mousedown preventDefault): kachasqamanta tecladowan vozwan qillqay sesionqa kichasqalla qhipan,
  mana huk rurayta yapaspa qatipalla rimay atikun.

### Historial tinkuchiy (yapasqalla + kunan pacha)

- Sapa programapi local Historial + kachana cursor (`lastPushedEntryId`); yapasqallanta kachan (pruebapi sapa registro 3ms/188B);
- Vaultqa llapan dispositivokunapa pacha ñanninta huñun (`/api/history/merged`); programaqa sapa kuti 2000 pisilla registroykunata urqun,
  sapa sesionpi huk kutilla 10000 registroyuq ukhunchasqa urquyta ruran; SSE chayamullaptin musuqchan;
- Kikin sutiyuq identidadkuna kikillanmanta huñukun (yapamanta churaspa musuq random IDniyuq «ñawpaq kawsaynin» kay computadoraman p'istukun); sutiqa rikuchinapaqlla, identidadqa huellaswan riqsikun.

### Qallariy midya waqaychana

Qallariy archivokuna SHA-256 nisqanman hina waqaychanaman yaykun (`/api/media/upload`, purispa + iskay kutita harkaspa, 2GB kama); mayqin dispositivopas hashwan
Internet ukhupi qallariy archivota urqun (`/api/media/blob/<hash>`, Range purichiyta yanapan) — «kay dispositivopi chinkay ≠ llapan redpi chinkay».

### Qallariypi kikillanmanta qhawana sonda (yana caja)

`app.js` qallariyninpi window.onerror hapiqta + probe() chimpuyta churan; qallarispa 6 segundomanta/pantay kaptin 1.5 segundomanta
Vaultpa `/api/client-log` nisqanman POST ruran, sapa dispositivopaq archivopi waqaychan. Chiqap telefonopi yana/yuraq pantalla kaptin mana musyayllachu; logta ñawinchaspam tarikun.

---

## Codigo mapa

### Mac computadorapa programa `desktop/`

| Archivo | Siq'ikuna | Ruraynin |
|------|------|------|
| `src-tauri/src/main.rs` | ~4900 | HTTP/WS servidor, PIN chiqapchay, enigo teclado, arboard portapapeles, archivo kachay/chaskiy, bandeja, taripay kutichiy, kallpa willay |
| `src/main.js` | ~2600 | Computadorapa interfaznin: dispositivokunapa tukuy rikuy, masichay arí niy, huñusqa Historial + uchuy rikch'akuna, Kallpa mapata chaskiy, pachamarka tupachiy, aysaspa kachay |
| `src/style.css` | ~2000 | Computadorapa estilokuna |
| `static/*` | — | `mobile/src/` nisqapa byte-byte espejo (telefonopa programanta tikraspa kuskanchasqa copiayta atipaq, ruray t'aqapi qhaway) |

### Telefonopa programa `mobile/` (Android + iOS huk kikin codigo)

| Archivo | Siq'ikuna | Ruraynin |
|------|------|------|
| `src/app.js` | ~11500 | Llapan interfazpa logican: yuyayniyuq tarjeta, achka dispositivowan tinkuy, Historialpa pacha ñan (suyuy/maskasqanta sut'ita rikuchiy/virtual kuyuchiy), Kallpa mapa, vault tinkuchiy, midya qhawana, sonda |
| `src/i18n.js` | ~110 | gettext hina achka simi runtime: t()/kutiy/interpolación/simi taripay/diccionario cache |
| `src/locales/*.json` | ×10 | Simi paquetekuna (chino qillqalla llavem, musuq simi = huk archivota yapay) |
| `src-tauri/src/lib.rs` | ~1900 | 16 sistema kamachiykuna: Historial waqaychay, archivota t'aqakama chaskiy, taripay masichay, modelo riqsiy, vaultman midya wichachiy, ñanta tariy; iOS kuyuchiy hark'ay (KVO contentOffsetta qhawaspa dibujaypa ñawpaqninpi ch'usaqyachin) |
| `gen/android/.../MainActivity.kt` | — | Consolata apachiy (VibeDropConsole) + ñawpaq WebChromeClientman delegay (archivo akllana hukkuna) |
| `gen/android/.../KeepAliveService.kt` | — | Ñawpaq llamk'aypi kawsachiy |
| `gen/android/.../VideoPlayerActivity.kt` | — | ExoPlayer (Media3) sistema hunt'a pantalla video pukllachiq |
| `gen/android/.../BackgroundClipboardSyncManager.kt` | — | Sistema qhipa llamk'aypi portapapeles qillqay |

### Home Vault hinaspa yanapakuykuna `scripts/`

| Script | Ruraynin |
|------|------|
| `home-vault-receiver.py` (~1000 siq'i) | Wasipi servidorpa llapan endpointninkuna (uray tablapi qhaway); launchdwan wiñaypaq llamk'an |
| `message-self-study.py` | jieba nisqawan llapan corpus t'aqwiy → kikillanpi hunt'asqa HTML informe (kachay puriyninpa sayaq siq'inpas kan) |
| `vault-media-uploader.py` / `sync-home-vault.py` | Ñawpa midyata hunt'achispa wichachiy / Historialta discopi tinkuchiy |
| `i18n-check.py` | Achka simi calidad punku: llapan t()/data-i18n llaveta maskan, simi paquetekunawan tupachispa pisi utaq mana necesario kaqta willan |
| `deploy-android.sh` / `deploy-desktop.sh` / `deploy-ios.sh` | Kimsa plataformata huk kamachiywan ruray hinaspa churay |
| `generate-app-icons.py` / `generate-tray-frames.py` | Marca imakunata paqarichiy |

### Home Vault endpointkunapa utqay rikuy

| Endpoint | Ruraynin |
|------|------|
| `POST /api/history/append` · `GET /api/history/merged` | Yapasqallata waqaychanaman churay / pacha ñanta huñuy |
| `GET /api/events` | SSE: discopi churasqa ratulla willay |
| `POST /api/media/upload` · `/lookup` · `GET /api/media/blob/<hash>` | Midya waqaychana: iskay kutita harkaspa yaykuchiy/maskay/Rangewan purispa urquy |
| `GET/POST /api/device-names` | Dispositivopa sutinkuna tablón (LWW) |
| `POST /api/client-log` | Sonda yana cajata chaskiy |
| `GET /report/self-study` | Kikillanmanta t'aqwiy informe (SWR: cachemanta ratulla kichakun, mawk'a kaptin qhipapi yapamanta ruran, `?refresh=1` kallpawan musuqchan) |

---

## Plataformakama llamkaspa yachasqakuna

### WebView motorpa hukniray kaynin (ancha chanin)

| | Android | iOS | macOS computadorapa programa |
|---|---------|-----|-----------|
| Motor | Chromium | **WKWebView** | **WKWebView (iOS hina!)** |
| `content-visibility: auto` | ✅ Sistema virtualización | ❌ Yana pantalla | ❌ Kuyuchispa ch'usaq |
| Suni listapa ñan | content-visibility | JS virtual kuyuchiy | T'aqakama churay |
| `Intl.Segmenter` chinopi simikunata t'aqay | ❌ Sapanka qillqaman t'aqan | ✅ Hunt'asqa diccionario | ✅ |

**Tukuchiy: motorpurapa chinopi simi t'aqayninqa servidorpi jiebawanlla kanan; content-visibilityqa Androidpillam llamk'achina.**

### iOS

- **Hark'asqa diseño**: hawa WKWebView kuyuchiyninqa programa qaranpa arquitecturanpi wañuchisqa (`isScrollEnabled=false` maki kuyuchiyllata harkan;
  WebKitpa teclado rikuchinanqa programawan kuyuchin, chayrayku **KVOwan contentOffsetta qhawaspa dibujaypa ñawpaqninpi ch'usaqyachina**;
  hark'asqa «qallariy punto»qa sistemapa samana `-adjustedContentInset` nisqanmi, mana (0,0)chu); programa ñawpaqman kutimullaptin sapa kuti yapamanta churan;
- Paquete ruranapaq mana p'akinapaq kamachiy: `cargo tauri ios build --export-method debugging`; mana Xcode Runta chiqalla llamk'achinachu;
- Mana qullqiyuq firmaqa 7 p'unchayllam allin (paqarichisqa p'unchaymanta yupaspa), chayrayku kikillanmanta musuqchana ñanwan kuska llamk'achina.

### Android

- Sapanchasqa WebChromeClientqa **ñawpaq clientman delegananmi** (onShowFileChooser hukkuna); hunt'ata rantiyqa archivo akllanata upallachin;
- Consolepa chiqap logninta `adb logcat -d VibeDropConsole:I "*:S"` nisqawan qhaway;
- Qallariypi 5 «Cannot redefine property» pantaykunaqa Tauri inyección iskay kuti purisqanpa mana dañoyuq qapariyninmi; ama qatikuychu.

### Mac

- enigo teclado rikch'achiyqa sapanchasqa threadpi purin; portapapeles sapa 500ms qhawana → broadcast channel → sapa WS tinkuy;
- Computadorapa programa binariopa ukhu sutinraqmi `voicedrop` (pgrep ruraypi yuyariy).

---

## Achka simi (i18n)

gettext ñan: **chino qillqalla llavem**, `t('发送并回车')` kunan simipa diccionarionpi maskan; mana tikrasqa kaptin chino qillqaman kutin
(kuskanlla tikrasqapas maypachapas lluqsichiy atikun). Variableyuq qillqapi `t('已改名为 {name}', {name})` marcador llamk'achiy; qillqakunata huñuspa ama ruranachu.
Kunan 11 simikuna kan; musuq simi = `locales/<lang>.json` huk archivo + `i18n.js` mapa tablapi huk siq'i.

- Calidad punku: `python3 scripts/i18n-check.py --strict` (llave hunt'asqa kay/marcadorkuna hunt'asqa kay);
- Significado qhawariy: sapa simipi 30 hatun rimaykunata runa ñawinchaywan sut'ita qhawana (maquinaqa significadota mana garantizanchu; `docs/i18n-规范.md` nisqapi hunt'ata qhaway);
- Simi akllanapi simipa sutin **kikin siminpi** kanan, chino/inglés ñawinchayninwan; mayqin simi paquetepas ama tikrachunchu.

---

## Ruray hinaspa churay

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

**Iskay kamachiy**:

1. `mobile/src/` nisqapi app.js / index.html / style.css / i18n.js / locales/ tikrasqamanta
   **`desktop/static/` nisqaman kuskanchasqa copiaymi kanan** (computadorapa HTTP servicionpa telefono navegadorpaq versión);
2. **Iskay Tauri rurayta kuska purichiy mana atikunchu** (local IPC canalta kuska llamk'achispa takanakun); qatillapim purichina.

---

## GitHub lluqsichiykuna

`v*` tagta push rurayqa `release.yml` nisqata hap'ichin: firmayuq APK + macOS dmg kikillanmanta ruraspa GitHub Releasepi lluqsichin;
`ci.yml`qa sapa pushpi ruray qhawariytawan Python pruebakunatawan purichin.

```bash
git tag -a v0.x.y -m "说明" && git push origin v0.x.y
```

---

## Willay kikillanmanta taqwiy hinaspa simi kuti yupay informe

Qampa Home Vault Historialniykipa corpusninta simikunaman t'aqaspa, simi kuti yupayta/sapa kuti nisqa rimayta/sapa kuti rikuriq rimaykunata/killa-killapi tema tikrayta (TF-IDF)/kachay puriyta (hora/p'unchay sayaq siq'ikuna; dedowan scrub ruraspa ñut'u willayta maskay) t'aqwin; kikillanpi hunt'asqa HTML informeta paqarichin (llapanmi localpi, datakuna mana hawaman lluqsinchu).

**App ukhupi chiqalla qhaway**: Historial p'anqa → «Willay kikillanmanta t'aqwiy» tarjeta → Hunt'asqa informeta kichay (Home Vault endpoint `/report/self-study`; SWR cachemanta ratulla kichakun, mawk'a kaptin qhipapi yapamanta ruran, `?refresh=1` kallpawan yapamanta purichin).

Makiwanpas paqarichiy atikun:

```bash
python3 -m venv .venv && .venv/bin/pip install jieba
.venv/bin/python scripts/message-self-study.py http://<你的vault地址>:8788
```

Informeqa `~/Downloads/` nisqaman lluqsin. Achka simi llamk'aypa contratoqa `docs/i18n-规范.md` nisqapi kachkan.
