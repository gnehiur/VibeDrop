[简体中文](README.md) | [繁體中文](README.zh-TW.md) | [English](README.en.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Русский](README.ru.md) | [Kiswahili](README.sw.md) | [Runasimi](README.qu.md)

<div align="center">

<img src="docs/logo.png" width="120" alt="VibeDrop logo">

# VibeDrop

**Herramienta para sincronizar el portapapeles y transferir texto y archivos entre el teléfono y el Mac — conexión directa por la red local, sin depender de la nube**

[![release](https://img.shields.io/github/v/release/jncdke/VibeDrop?color=2f6fed)](https://github.com/jncdke/VibeDrop/releases)
[![license](https://img.shields.io/github/license/jncdke/VibeDrop?color=green)](LICENSE)
![platform](https://img.shields.io/badge/platform-macOS%20%7C%20Android%20%7C%20iOS-8a63d2)
![i18n](https://img.shields.io/badge/languages-11-2f6fed)
![tauri](https://img.shields.io/badge/Tauri-2.x-ffc131?logo=tauri&logoColor=white)
![rust](https://img.shields.io/badge/Rust-stable-e43717?logo=rust)

[Descargar Release](https://github.com/jncdke/VibeDrop/releases) · [Funciones](#funciones) · [mensaje de autoestudio](#mensaje-de-autoestudio-e-informe-de-frecuencia-de-palabras)

</div>

---

VibeDrop consta de tres componentes que se comunican directamente dentro de la red local mediante **WebSocket**, sin necesidad de Internet ni de servicios en la nube:

- **Aplicación de escritorio para Mac** (`desktop/`) — recibe texto y archivos, difunde el portapapeles y ofrece integración con la bandeja del sistema
- **Aplicación móvil** (`mobile/`, Android + iOS) — envía texto, imágenes, vídeos y archivos, y muestra la cronología del historial
- **Home Vault** (`scripts/`) — servidor doméstico que combina el historial de varios dispositivos, almacena los originales multimedia y recoge los registros de las sondas

---

## Capturas de pantalla

**Tarjeta de envío inteligente «Enviar siguiente cursor»**——habla al teléfono y el texto aparecerá automáticamente en el ordenador donde se encuentre el cursor (para escenarios con Control Universal):

<div align="center">
<table>
  <tr>
    <td align="center" colspan="2"><img src="assets/screenshots/desktop-overview.jpg" width="680" alt="Vista general de la aplicación de escritorio para macOS"><br><sub>Aplicación de escritorio para macOS — dispositivos · enlace · arrastrar para enviar</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/screenshots/ios-smart-card.png" width="320" alt="Tarjeta de envío inteligente de iOS"><br><sub>iOS (iPhone 17 Pro Max)</sub></td>
    <td align="center"><img src="assets/screenshots/android-smart-card.jpg" width="320" alt="Tarjeta de envío inteligente de Android"><br><sub>Android (OnePlus Ace 5)</sub></td>
  </tr>
</table>
</div>

---

## Funciones

| Función | Mac | Móvil (Android + iOS) |
|------|--------|------------------------|
| 🎯 Tarjeta de envío inteligente «Enviar siguiente cursor» | ✅ Informa de la actividad del teclado y el ratón (`CGEventSource`, sin permisos) | ✅ Envía automáticamente texto, imágenes y archivos al Mac donde está el cursor, lo sigue en 1 segundo y permite cambiar manualmente |
| 📝 Transferencia de texto (teléfono → Mac) | ✅ Recibe y simula la entrada de teclado | ✅ Mantiene el teclado y la entrada de voz después del envío para dictar de forma continua sin pasos adicionales |
| 📋 Sincronización del portapapeles (Mac → teléfono) | ✅ Detecta los cambios y los difunde | ✅ Un servicio nativo en segundo plano escribe en el portapapeles |
| 🌍 Idiomas | ✅ Usar sistema | ✅ 11 idiomas (chino simplificado/tradicional, inglés, japonés, coreano, español, francés, alemán, ruso, suajili y quechua), con retorno al chino al estilo gettext cuando falta una traducción |
| 🤝 Detección automática y enlace | ✅ Muestra enlaces pendientes de confirmación y dispositivos conectados | ✅ Busca Mac cercanos y enlaza mediante un código de verificación; permite cambiar el nombre del dispositivo y sincronizarlo automáticamente entre teléfonos |
| 📜 Cronología del Historial | ✅ Vista combinada de todos los dispositivos + miniaturas | ✅ Combina todos los dispositivos, filtra por origen/destino/tipo/original/hora y resalta las búsquedas |
| 📈 Mapa de calor de actividad | ✅ Mapa de recepción + filtro al pulsar una celda | ✅ Mapa de envío + filtro al pulsar una celda |
| 🔬 mensaje de autoestudio | — (Home Vault genera el informe) | ✅ Informe completo integrado en Historial: nube de palabras/muletillas/gráfico de barras de tendencias de envío con navegación por arrastre |
| 📁 Transferencia bidireccional de archivos | ✅ Arrastrar y soltar / servicios de Finder / compartir desde Finder | ✅ Enviar a Recibidos / las imágenes van al álbum de fotos y los lotes se empaquetan automáticamente |
| 🗄 Home Vault | Servidor doméstico: historial combinado entre dispositivos · almacén de originales multimedia (deduplicación por hash + streaming Range) · recogida de registros de sondas | ✅ Envío incremental + sincronización SSE en tiempo real |
| 🔒 Autenticación por PIN | ✅ Se genera al azar y se conserva en un archivo | ✅ Se guarda automáticamente tras enlazar con el código de verificación |
| 🕰 Ajuste de zona horaria de visualización | ✅ Local/Pekín/costa oeste de EE. UU., con el mismo criterio para mostrar y calcular estadísticas | — |
| 📡 Primer plano persistente / bandeja | ✅ Bandeja del sistema + inicio de sesión automático | ✅ Notificación permanente en Android |

---

## Vista general de la arquitectura técnica

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

Hay tres vías de comunicación, todas directas dentro de la red local y sin depender de la nube:

1. **Teléfono ↔ Mac**: WebSocket (`:9001/ws`) transfiere texto, archivos, portapapeles y consultas de actividad tras autenticar el PIN;
2. **Todos los dispositivos → Home Vault**: HTTP (`:8788`) envía incrementos del historial y archivos multimedia y obtiene informes;
3. **Vault → clientes**: una conexión SSE persistente (`/api/events`) difunde los datos en cuanto se guardan y envía un latido cada 25 segundos.

---

## Descripción detallada de los flujos principales

### Tarjeta de envío inteligente «Enviar siguiente cursor»

1. Cuando la aplicación de escritorio recibe `activity_query`, llama a `CGEventSourceSecondsSinceLastEventType`
   para responder «cuántos segundos han pasado desde la última actividad del teclado o el ratón» (sin permisos ni hilos: solo lee el registro que el sistema ya mantiene para el salvapantallas);
2. El teléfono consulta cada segundo todos los Mac conectados y compara sus **segundos de inactividad relativos** (sin verse afectado por las diferencias entre sus relojes).
   El más reciente es el Mac con el cursor: Control Universal envía los eventos reales de teclado y ratón al equipo donde está el cursor, por lo que la señal está estrechamente vinculada al hecho observado;
3. El destino se fija en el instante en que se envía texto, imágenes o archivos; al pulsar el indicador se alterna entre los modos automático y manual.

### Detección y enlace

El teléfono explora dos vías en paralelo: difusión UDP + sondeo HTTP (`discover_desktops`). Cuando descubre la aplicación de escritorio, inicia el enlace mediante código de verificación (el escritorio muestra una tarjeta pendiente y ambos lados comparan el mismo código); tras aprobarlo, se guarda y se conecta automáticamente.
Al guardar un nombre personalizado, el tablón de Vault (`/api/device-names`, serverId como clave, LWW) lo sincroniza entre teléfonos.

### Texto y archivos

- Texto: las acciones `type` / `type_enter` hacen que la aplicación de escritorio simule el teclado con enigo; el Modo ausente utiliza en su lugar
  `clipboard_text` (solo escribe en el portapapeles, para combinarlo con herramientas de control remoto como UU Remote);
- Archivos: protocolo de transferencia por bloques (begin/append/finish/cancel). En el teléfono llegan a Recibidos o al álbum de fotos,
  mientras que el Mac envía al arrastrar o mediante un servicio de Finder. Toda la ruta lleva un número `transferId`, por lo que los registros de envío y recepción se pueden combinar con precisión;
- Los botones de envío no roban el foco (mousedown preventDefault): el teclado y la sesión de entrada de voz permanecen después del envío,
  lo que permite dictar de forma continua sin pasos adicionales.

### Sincronización del historial (incremental + tiempo real)

- Cada dispositivo mantiene su historial local + un cursor de envío (`lastPushedEntryId`) y solo envía incrementos (medición real: 3 ms/188 B por entrada);
- Vault combina la cronología de todos los dispositivos (`/api/history/merged`). Los clientes suelen obtener 2.000 entradas ligeras y una vez por sesión realizan una lectura profunda de 10.000; al llegar un evento SSE se actualiza inmediatamente;
- Las identidades con el mismo nombre se combinan automáticamente (la «vida anterior» con ID aleatorio tras una reinstalación se incorpora a la identidad local); el nombre es una capa de presentación y la identidad depende de la huella.

### Almacén de originales multimedia

Los originales se almacenan por SHA-256 (`/api/media/upload`, streaming + deduplicación, límite de 2 GB). Cualquier dispositivo puede recuperar el original en línea mediante su hash (`/api/media/blob/<hash>`, compatible con streaming Range): «perdido localmente ≠ perdido en toda la red».

### Sonda de autocomprobación al iniciar (caja negra)

Al principio de `app.js` se instalan la captura window.onerror y los puntos de medición probe(). Se envía un POST a Vault `/api/client-log` 6 segundos después de iniciar o 1,5 segundos después de un error, y se guarda por dispositivo. Ante una pantalla negra o blanca en un equipo real, no hay que adivinar: los registros permiten localizar el fallo.

---

## Mapa del código

### Aplicación de escritorio para Mac `desktop/`

| Archivo | Líneas | Responsabilidad |
|------|------|------|
| `src-tauri/src/main.rs` | ~4900 | Servidor HTTP/WS, autenticación PIN, teclado enigo, portapapeles arboard, envío y recepción de archivos, bandeja, respuestas de detección e informes de actividad |
| `src/main.js` | ~2600 | UI de escritorio: dispositivos, confirmación de enlace, historial combinado + miniaturas, mapa de recepción, zona horaria y envío al arrastrar |
| `src/style.css` | ~2000 | Estilos de escritorio |
| `static/*` | — | Copia idéntica byte a byte de `mobile/src/` (debe copiarse después de modificar el móvil; consulta la sección de compilación) |

### Aplicación móvil `mobile/` (mismo código para Android + iOS)

| Archivo | Líneas | Responsabilidad |
|------|------|------|
| `src/app.js` | ~11500 | Toda la lógica del front-end: Tarjeta de envío inteligente, conexiones múltiples, cronología (filtros/búsqueda resaltada/desplazamiento virtual), mapa de calor, sincronización con Vault, visor multimedia y sondas |
| `src/i18n.js` | ~110 | Entorno multilingüe al estilo gettext: t()/retorno/interpolación/detección de idioma/caché de diccionarios |
| `src/locales/*.json` | ×10 | Paquetes de idioma (el texto original chino es la clave; un idioma nuevo equivale a añadir un archivo) |
| `src-tauri/src/lib.rs` | ~1900 | 16 comandos nativos: persistencia del historial, recepción de archivos por bloques, detección y enlace, identificación del modelo, carga de medios a Vault y resolución de rutas; bloqueo de desplazamiento en iOS (KVO observa contentOffset y lo devuelve a cero antes de renderizar) |
| `gen/android/.../MainActivity.kt` | — | Reenvío de consola (VibeDropConsole) + delegación al WebChromeClient original (selector de archivos, etc.) |
| `gen/android/.../KeepAliveService.kt` | — | Persistencia en primer plano |
| `gen/android/.../VideoPlayerActivity.kt` | — | Reproductor nativo ExoPlayer (Media3) a pantalla completa |
| `gen/android/.../BackgroundClipboardSyncManager.kt` | — | Escritura nativa del portapapeles en segundo plano |

### Home Vault y herramientas `scripts/`

| Script | Responsabilidad |
|------|------|
| `home-vault-receiver.py` (~1000 líneas) | Todos los endpoints del servidor doméstico (véase la tabla siguiente); permanece activo mediante launchd |
| `message-self-study.py` | Análisis completo del corpus con jieba → informe HTML autocontenido (incluye gráfico de barras de tendencias de envío) |
| `vault-media-uploader.py` / `sync-home-vault.py` | Carga de originales multimedia existentes / sincronización del historial persistido |
| `i18n-check.py` | Control de calidad multilingüe: busca todas las claves t()/data-i18n e informa de ausencias y excedentes en los paquetes |
| `deploy-android.sh` / `deploy-desktop.sh` / `deploy-ios.sh` | Compilación y despliegue de los tres destinos con un comando |
| `generate-app-icons.py` / `generate-tray-frames.py` | Generación de recursos de marca |

### Referencia rápida de endpoints de Home Vault

| Endpoint | Función |
|------|------|
| `POST /api/history/append` · `GET /api/history/merged` | Entrada incremental / cronología combinada |
| `GET /api/events` | SSE: difusión inmediata tras guardar |
| `POST /api/media/upload` · `/lookup` · `GET /api/media/blob/<hash>` | Almacén multimedia: entrada sin duplicados/consulta/lectura mediante streaming Range |
| `GET/POST /api/device-names` | Tablón de nombres de dispositivos (LWW) |
| `POST /api/client-log` | Recogida de la caja negra de las sondas |
| `GET /report/self-study` | Informe de autoestudio (SWR: caché instantánea, recálculo en segundo plano al caducar, `?refresh=1` fuerza la actualización) |

---

## Lecciones prácticas por plataforma

### Diferencias entre motores WebView (importante)

| | Android | iOS | Escritorio macOS |
|---|---------|-----|-----------|
| Motor | Chromium | **WKWebView** | **WKWebView (¡el mismo que iOS!)** |
| `content-visibility: auto` | ✅ Virtualización nativa | ❌ Pantalla negra | ❌ Espacios en blanco al desplazar |
| Estrategia para listas largas | content-visibility | Desplazamiento virtual JS | Montaje por fragmentos |
| Segmentación china con `Intl.Segmenter` | ❌ Separa cada carácter | ✅ Diccionario completo | ✅ |

**Conclusión: la segmentación china entre motores solo puede usar jieba en el servidor; content-visibility solo está permitido en Android.**

### iOS

- **Diseño fijo**: el desplazamiento del WKWebView exterior se desactiva como parte de la arquitectura del contenedor (`isScrollEnabled=false` solo bloquea los gestos;
  WebKit revela el teclado mediante desplazamiento programático, por lo que también hay que **observar contentOffset con KVO y devolverlo antes de renderizar**;
  el «origen» fijado es la posición de reposo del sistema `-adjustedContentInset`, no (0,0)); el bloqueo se reinstala cada vez que la aplicación vuelve al primer plano;
- Regla de empaquetado: `cargo tauri ios build --export-method debugging`; no se debe usar Xcode Run directamente;
- La firma gratuita dura 7 días desde su creación y necesita una canalización de renovación automática.

### Android

- Un WebChromeClient personalizado **debe delegar en el cliente original** (onShowFileChooser, etc.); sustituirlo por completo inutiliza el selector de archivos;
- La consola real se consulta con `adb logcat -d VibeDropConsole:I "*:S"`;
- Los cinco errores «Cannot redefine property» al iniciar son ruido inofensivo causado por la doble ejecución del script inyectado por Tauri; no deben investigarse.

### Mac

- La simulación de teclado con enigo se ejecuta en un hilo independiente; el portapapeles se consulta cada 500 ms → broadcast channel → cada conexión WS;
- El nombre interno del binario de escritorio sigue siendo `voicedrop` (téngase en cuenta al usar pgrep).

---

## Idiomas (i18n)

Se sigue el modelo gettext: **el texto original chino es la clave**. `t('发送并回车')` consulta el diccionario del idioma actual y, si falta una traducción, vuelve al original chino (una traducción parcial siempre se puede publicar). Las variables usan marcadores como `t('已改名为 {name}', {name})`; se prohíbe concatenar cadenas.
Actualmente hay 11 idiomas. Añadir uno equivale a un archivo `locales/<lang>.json` + una línea en la tabla de `i18n.js`.

- Control de calidad: `python3 scripts/i18n-check.py --strict` (cobertura de claves/integridad de marcadores);
- Revisión semántica: lectura manual de 30 términos esenciales por idioma (las máquinas no garantizan el significado; véase `docs/i18n-规范.md`);
- Los nombres del selector usan el **nombre propio del idioma** con ayudas de pronunciación en chino e inglés, y ningún paquete los traduce.

---

## Compilación y despliegue

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

**Dos reglas**:

1. Después de modificar app.js / index.html / style.css / i18n.js / locales/ en `mobile/src/`,
   **hay que copiarlo a `desktop/static/`** (versión para navegadores móviles servida por el HTTP de escritorio);
2. **Las dos compilaciones de Tauri no pueden ejecutarse en paralelo** (comparten un canal IPC local y chocan); deben ejecutarse en serie.

---

## Publicaciones de GitHub

Al enviar una etiqueta `v*` se activa `release.yml`: compila automáticamente un APK firmado + un dmg de macOS y publica una GitHub Release;
`ci.yml` ejecuta comprobaciones de compilación y pruebas unitarias de Python con cada push.

```bash
git tag -a v0.x.y -m "说明" && git push origin v0.x.y
```

---

## mensaje de autoestudio e informe de frecuencia de palabras

Analiza el corpus del historial propio de Home Vault: segmentación y frecuencia de palabras, muletillas, frases frecuentes, evolución mensual de temas (TF-IDF) y tendencias de envío (gráficos de barras por hora/día que se pueden recorrer con el dedo). Genera un informe HTML autocontenido; todo se procesa localmente y los datos no salen del equipo.

**Consulta directa en la aplicación**: Historial → tarjeta «mensaje de autoestudio» → Abrir informe completo (endpoint de Home Vault `/report/self-study`; la caché SWR se abre al instante, los datos caducados se recalculan en segundo plano y `?refresh=1` fuerza una nueva ejecución).

También puede generarse manualmente:

```bash
python3 -m venv .venv && .venv/bin/pip install jieba
.venv/bin/python scripts/message-self-study.py http://<你的vault地址>:8788
```

El informe se guarda en `~/Downloads/`. El contrato de implementación multilingüe está en `docs/i18n-规范.md`.
