[简体中文](README.md) | [繁體中文](README.zh-TW.md) | [English](README.en.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Русский](README.ru.md) | [Kiswahili](README.sw.md) | [Runasimi](README.qu.md)

<div align="center">

<img src="docs/logo.png" width="120" alt="VibeDrop logo">

# VibeDrop

**휴대폰과 Mac 사이에서 클립보드를 동기화하고 텍스트와 파일을 전송하는 도구 — 로컬 네트워크에서 직접 연결하며 클라우드가 필요 없습니다**

[![release](https://img.shields.io/github/v/release/gnehiur/VibeDrop?color=2f6fed)](https://github.com/gnehiur/VibeDrop/releases)
[![license](https://img.shields.io/github/license/gnehiur/VibeDrop?color=green)](LICENSE)
![platform](https://img.shields.io/badge/platform-macOS%20%7C%20Android%20%7C%20iOS-8a63d2)
![i18n](https://img.shields.io/badge/languages-11-2f6fed)
![tauri](https://img.shields.io/badge/Tauri-2.x-ffc131?logo=tauri&logoColor=white)
![rust](https://img.shields.io/badge/Rust-stable-e43717?logo=rust)

[Release 다운로드](https://github.com/gnehiur/VibeDrop/releases) · [기능 개요](#기능-개요) · [메시지 독학](#메시지-독학-및-단어-빈도-통계-보고서)

</div>

---

VibeDrop은 세 구성 요소로 이루어지며 **WebSocket**을 통해 로컬 네트워크에서 직접 통신합니다. 인터넷이나 클라우드 서비스가 필요 없습니다.

- **Mac 데스크톱 앱**(`desktop/`) — 텍스트/파일 수신, 클립보드 브로드캐스트, 시스템 트레이
- **모바일 앱**(`mobile/`, Android + iOS) — 텍스트/이미지/동영상/파일 전송, 기록 타임라인
- **Home Vault**(`scripts/`) — 기기 간 기록 병합, 원본 미디어 저장소, 프로브 로그 수집을 담당하는 홈 서버

---

## 스크린샷

**스마트송신카드 “다음 커서 보내기”**——휴대폰에 말하면 커서가 있는 컴퓨터로 텍스트가 자동 입력됩니다(유니버설 컨트롤 사용 환경).

<div align="center">
<table>
  <tr>
    <td align="center" colspan="2"><img src="assets/screenshots/desktop-overview.jpg" width="680" alt="macOS 데스크톱 앱 개요"><br><sub>macOS 데스크톱 앱 — 기기 개요 · 페어링 · 끌어다 놓아 전송</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/screenshots/ios-smart-card.png" width="320" alt="iOS 스마트송신카드"><br><sub>iOS (iPhone 17 Pro Max)</sub></td>
    <td align="center"><img src="assets/screenshots/android-smart-card.jpg" width="320" alt="Android 스마트송신카드"><br><sub>Android (OnePlus Ace 5)</sub></td>
  </tr>
</table>
</div>

---

## 기능 개요

| 기능 | Mac | 모바일(Android + iOS) |
|------|--------|------------------------|
| 🎯 스마트송신카드 “다음 커서 보내기” | ✅ 키보드와 마우스 활동 보고(`CGEventSource`, 권한 불필요) | ✅ 텍스트/이미지/파일을 커서가 있는 Mac으로 자동 전송, 1초 내 추적, 수동 전환 가능 |
| 📝 텍스트 전송(휴대폰 → Mac) | ✅ 수신 후 키보드 입력 시뮬레이션 | ✅ 전송 후에도 키보드와 음성 입력을 유지하여 추가 동작 없이 계속 받아쓰기 가능 |
| 📋 클립보드 동기화(Mac → 휴대폰) | ✅ 변경 감지 후 브로드캐스트 | ✅ 네이티브 백그라운드 서비스가 클립보드에 기록 |
| 🌍 다국어 | ✅ 시스템 따르기 | ✅ 11개 언어(중국어 간체/번체, 영어, 일본어, 한국어, 스페인어, 프랑스어, 독일어, 러시아어, 스와힐리어, 케추아어), gettext 방식으로 번역이 없으면 중국어로 대체 |
| 🤝 자동 검색과 페어링 | ✅ 확인 대기 중인 페어링과 연결된 기기 표시 | ✅ 주변 Mac 검색 및 인증 코드 페어링, 기기 이름 변경과 휴대폰 간 자동 동기화 지원 |
| 📜 기록 타임라인 | ✅ 모든 기기의 통합 보기 + 썸네일 | ✅ 모든 기기 통합, 출처/대상/유형/원본/시간 필터, 검색 결과 강조 |
| 📈 활동 히트맵 | ✅ 수신 히트맵 + 셀을 눌러 필터링 | ✅ 전송 히트맵 + 셀을 눌러 필터링 |
| 🔬 메시지 독학 | —(보고서는 Home Vault에서 생성) | ✅ 기록 페이지에 전체 보고서 내장: 워드 클라우드/말버릇/전송 추세 막대그래프(스크럽하여 세부 정보 확인) |
| 📁 양방향 파일 전송 | ✅ 드래그 앤 드롭 / Finder 서비스 / Finder 공유 | ✅ 받은 편지함으로 / 이미지는 사진 앨범으로 저장, 여러 항목은 자동 패키징 |
| 🗄 Home Vault | 홈 서버: 기기 간 기록 병합 · 원본 미디어 저장소(해시 중복 제거 + Range 스트리밍) · 프로브 로그 수집 | ✅ 증분 푸시 + SSE 실시간 동기화 |
| 🔒 PIN 인증 | ✅ 무작위 생성 후 파일에 영구 저장 | ✅ 인증 코드 페어링 후 자동 저장 |
| 🕰 표시 시간대 설정 | ✅ 로컬/베이징/미국 서부, 표시와 통계 기준 통일 | — |
| 📡 포그라운드 유지 / 트레이 | ✅ 시스템 트레이 + 로그인 시 자동 실행 | ✅ Android 알림 영역에 상주 |

---

## 기술 아키텍처 개요

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

세 가지 통신 경로는 모두 로컬 네트워크에서 직접 연결되며 클라우드에 의존하지 않습니다.

1. **휴대폰 ↔ Mac**: WebSocket(`:9001/ws`). PIN 인증 후 텍스트/파일/클립보드/활동 조회 전송
2. **모든 단말 → Home Vault**: HTTP(`:8788`). 기록 증분 푸시, 미디어 업로드, 보고서 가져오기
3. **Vault → 클라이언트**: SSE 장기 연결(`/api/events`). 기록이 디스크에 저장되는 즉시 브로드캐스트하고 25초 하트비트로 연결 유지

---

## 핵심 흐름 상세 설명

### 스마트송신카드 “다음 커서 보내기”

1. 데스크톱 앱은 `activity_query`를 받으면 `CGEventSourceSecondsSinceLastEventType`을 호출하여
   “마지막 키보드/마우스 활동 이후 몇 초가 지났는지” 응답합니다(권한과 스레드가 전혀 필요 없으며 화면 보호기를 위해 시스템이 관리하는 기존 기록을 읽음).
2. 휴대폰은 연결된 모든 Mac을 1초마다 폴링하고 **상대 유휴 시간(초)**을 비교합니다(두 컴퓨터의 시계 오차에 영향받지 않음).
   가장 최근에 활동한 Mac이 커서가 있는 기기입니다. 유니버설 컨트롤이 실제 키보드와 마우스 이벤트를 커서가 있는 컴퓨터에 전달하므로 신호와 사실이 강하게 결합됩니다.
3. 텍스트/이미지/파일을 보내는 순간 대상을 고정합니다. 표시기를 누르면 자동/수동 모드를 순환 전환할 수 있습니다.

### 검색과 페어링

휴대폰은 UDP 브로드캐스트 + HTTP 탐색(`discover_desktops`)의 두 경로를 동시에 스캔합니다. 데스크톱 앱을 찾으면 인증 코드 페어링을 진행합니다(데스크톱 앱에 확인 대기 카드가 나타나고 양쪽에서 같은 코드를 대조). 승인되면 저장 후 자동 연결됩니다.
사용자 지정 기기 이름을 저장하면 Vault 게시판(`/api/device-names`, serverId를 키로 사용하는 LWW)을 통해 여러 휴대폰에 동기화됩니다.

### 텍스트와 파일

- 텍스트: `type` / `type_enter` 동작을 통해 데스크톱 앱이 enigo로 키보드 입력을 시뮬레이션합니다. 자리 비움 모드에서는
  `clipboard_text`를 사용합니다(클립보드에만 기록하며 UU Remote 같은 원격 제어 도구와 함께 사용).
- 파일: 분할 전송 프로토콜(begin/append/finish/cancel). 모바일에서는 받은 편지함이나 사진 앨범으로 들어가고
  Mac에서는 드래그 앤 드롭/Finder 서비스로 즉시 전송합니다. 전 구간에 `transferId` 전송 번호가 있어 송수신 기록을 정확히 병합할 수 있습니다.
- 전송 버튼은 포커스를 빼앗지 않습니다(mousedown preventDefault). 전송 후에도 키보드와 음성 입력 세션이 유지되어
  추가 동작 없이 계속 받아쓸 수 있습니다.

### 기록 동기화(증분 + 실시간)

- 각 단말은 로컬 기록 + 푸시 커서(`lastPushedEntryId`)를 유지하며 증분만 푸시합니다(실측 단일 항목 3ms/188B).
- Vault는 모든 기기의 타임라인(`/api/history/merged`)을 병합합니다. 클라이언트는 평소 2,000개를 가볍게 가져오고
  세션마다 한 번 10,000개를 깊게 가져옵니다. SSE가 도착하면 즉시 새로 고칩니다.
- 이름이 같은 ID는 자동 병합됩니다(재설치 후 새 무작위 ID라는 “전생”을 로컬 ID에 통합). 이름은 표시 계층이며 신원은 지문으로 판별합니다.

### 원본 미디어 저장소

원본은 SHA-256 기준으로 저장소에 들어갑니다(`/api/media/upload`, 스트리밍 + 중복 제거, 2GB 제한). 어떤 기기든 해시로 원본을 온라인에서 가져올 수 있습니다(`/api/media/blob/<hash>`, Range 스트리밍 지원). 즉 “로컬에서 사라짐 ≠ 전체에서 사라짐”입니다.

### 시작 자체 점검 프로브(블랙박스)

`app.js` 상단에서 window.onerror 캡처와 probe() 계측을 설치합니다. 시작 6초 후 또는 오류 1.5초 후 Vault의 `/api/client-log`로 POST하여 기기별로 저장합니다. 실제 기기의 검은 화면/흰 화면 문제를 추측하지 말고 로그로 찾습니다.

---

## 코드 맵

### Mac 데스크톱 `desktop/`

| 파일 | 줄 수 | 역할 |
|------|------|------|
| `src-tauri/src/main.rs` | ~4900 | HTTP/WS 서버, PIN 인증, enigo 키보드, arboard 클립보드, 파일 송수신, 트레이, 검색 응답, 활동 보고 |
| `src/main.js` | ~2600 | 데스크톱 UI: 기기 개요, 페어링 확인, 병합 기록 + 썸네일, 수신 히트맵, 시간대 설정, 드래그 전송 |
| `src/style.css` | ~2000 | 데스크톱 스타일 |
| `static/*` | — | `mobile/src/`의 바이트 단위 미러(모바일 변경 후 반드시 복사, 빌드 절 참조) |

### 모바일 `mobile/`(Android + iOS 공용 코드)

| 파일 | 줄 수 | 역할 |
|------|------|------|
| `src/app.js` | ~11500 | 전체 프런트엔드 로직: 스마트송신카드, 다중 기기 연결, 기록 타임라인(필터/검색 강조/가상 스크롤), 히트맵, Vault 동기화, 미디어 뷰어, 프로브 |
| `src/i18n.js` | ~110 | gettext 방식 다국어 런타임: t()/대체/보간/언어 감지/사전 캐시 |
| `src/locales/*.json` | ×10 | 언어 팩(중국어 원문이 키이며 새 언어는 파일 하나 추가) |
| `src-tauri/src/lib.rs` | ~1900 | 16개 네이티브 명령: 기록 영구 저장, 분할 파일 수신, 검색과 페어링, 기종 식별, Vault 미디어 업로드, 경로 해석. iOS 스크롤 잠금(KVO로 contentOffset을 관찰하여 렌더링 전에 0으로 복원) |
| `gen/android/.../MainActivity.kt` | — | 콘솔 전달(VibeDropConsole) + 기존 WebChromeClient에 위임(파일 선택기 등) |
| `gen/android/.../KeepAliveService.kt` | — | 포그라운드 유지 |
| `gen/android/.../VideoPlayerActivity.kt` | — | ExoPlayer(Media3) 네이티브 전체 화면 플레이어 |
| `gen/android/.../BackgroundClipboardSyncManager.kt` | — | 네이티브 백그라운드 클립보드 쓰기 |

### Home Vault와 도구 `scripts/`

| 스크립트 | 역할 |
|------|------|
| `home-vault-receiver.py`(~1000줄) | 홈 서버의 모든 엔드포인트(아래 표 참조), launchd 상주 |
| `message-self-study.py` | jieba 전체 말뭉치 분석 → 자체 포함 HTML 보고서(전송 추세 막대그래프 포함) |
| `vault-media-uploader.py` / `sync-home-vault.py` | 기존 미디어 추가 전송 / 기록 디스크 저장 동기화 |
| `i18n-check.py` | 다국어 품질 게이트: 모든 t()/data-i18n 키를 스캔하고 언어 팩의 누락과 잉여 보고 |
| `deploy-android.sh` / `deploy-desktop.sh` / `deploy-ios.sh` | 세 플랫폼 원클릭 빌드 및 배포 |
| `generate-app-icons.py` / `generate-tray-frames.py` | 브랜드 자산 생성 |

### Home Vault 엔드포인트 빠른 참조

| 엔드포인트 | 기능 |
|------|------|
| `POST /api/history/append` · `GET /api/history/merged` | 증분 저장 / 병합 타임라인 |
| `GET /api/events` | SSE: 디스크 저장 즉시 브로드캐스트 |
| `POST /api/media/upload` · `/lookup` · `GET /api/media/blob/<hash>` | 미디어 저장소: 중복 제거 저장/조회/Range 스트리밍 가져오기 |
| `GET/POST /api/device-names` | 기기 이름 게시판(LWW) |
| `POST /api/client-log` | 프로브 블랙박스 수집 |
| `GET /report/self-study` | 독학 보고서(SWR: 캐시 즉시 표시, 만료 후 백그라운드 재계산, `?refresh=1` 강제 새로 고침) |

---

## 플랫폼별 실전 노하우

### WebView 엔진 차이(중요)

| | Android | iOS | macOS 데스크톱 |
|---|---------|-----|-----------|
| 엔진 | Chromium | **WKWebView** | **WKWebView(iOS와 동일!)** |
| `content-visibility: auto` | ✅ 네이티브 가상화 | ❌ 검은 화면 | ❌ 스크롤 시 공백 |
| 긴 목록 전략 | content-visibility | JS 가상 스크롤 | 분할 마운트 |
| `Intl.Segmenter` 중국어 단어 분리 | ❌ 글자 단위로 분리 | ✅ 전체 사전 | ✅ |

**결론: 엔진을 넘나드는 중국어 단어 분리는 서버 측 jieba만 사용해야 하며 content-visibility는 Android에서만 허용됩니다.**

### iOS

- **고정 레이아웃**: 앱 셸 구조상 외부 WKWebView 스크롤을 비활성화합니다(`isScrollEnabled=false`는 제스처만 차단하고
  WebKit의 키보드 표시는 프로그래밍 방식 스크롤을 사용하므로 **KVO로 contentOffset을 관찰해 렌더링 전에 원위치로 복원**해야 합니다.
  고정할 “원점”은 (0,0)이 아니라 `-adjustedContentInset`이 가리키는 시스템 정지 위치입니다). 포그라운드로 돌아올 때마다 잠금을 다시 설치합니다.
- 패키징 원칙: `cargo tauri ios build --export-method debugging`. Xcode Run을 직접 사용하면 안 됩니다.
- 무료 서명은 생성일부터 7일간 유효하므로 자동 재서명 파이프라인이 필요합니다.

### Android

- 사용자 지정 WebChromeClient는 **반드시 원래 client에 위임**해야 합니다(onShowFileChooser 등). 전체를 교체하면 파일 선택기가 작동하지 않습니다.
- 실제 console은 `adb logcat -d VibeDropConsole:I "*:S"`로 확인합니다.
- 시작할 때 나오는 5개의 “Cannot redefine property” 오류는 Tauri 주입 스크립트가 두 번 실행되면서 생기는 무해한 잡음이므로 추적하지 않습니다.

### Mac

- enigo 키보드 시뮬레이션은 독립 스레드에서 실행됩니다. 클립보드를 500ms마다 폴링 → broadcast channel → 각 WS 연결로 전달합니다.
- 데스크톱 바이너리 내부 이름은 여전히 `voicedrop`입니다(pgrep 사용 시 주의).

---

## 다국어(i18n)

gettext 방식을 따릅니다. **중국어 원문 자체가 키**이며 `t('发送并回车')`는 현재 언어 사전을 조회하고 번역이 없으면 중국어 원문으로 대체합니다(일부만 번역해도 언제든 릴리스 가능). 변수에는 `t('已改名为 {name}', {name})` 같은 자리표시자를 사용하며 문자열 연결은 금지됩니다.
현재 11개 언어가 있습니다. 새 언어는 `locales/<lang>.json` 파일 하나 + `i18n.js` 매핑 표 한 줄로 추가합니다.

- 품질 게이트: `python3 scripts/i18n-check.py --strict`(키 범위/자리표시자 무결성)
- 의미 검수: 언어마다 핵심 용어 30개를 사람이 정독(기계는 의미를 보장할 수 없음, `docs/i18n-规范.md` 참조)
- 언어 선택기의 언어 이름은 **해당 언어의 자칭**과 중국어/영어 발음을 함께 표시하며 어떤 언어 팩도 이를 번역하지 않음

---

## 빌드 및 배포

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

**두 가지 규칙**:

1. `mobile/src/`의 app.js / index.html / style.css / i18n.js / locales/를 변경한 뒤에는
   **반드시 `desktop/static/`에 복사**해야 합니다(데스크톱 HTTP 서비스의 모바일 브라우저 버전).
2. **두 Tauri 빌드는 동시에 실행할 수 없습니다**(공유하는 로컬 IPC 채널이 충돌함). 반드시 순차 실행합니다.

---

## GitHub 릴리스

`v*` 태그를 push하면 `release.yml`이 실행되어 서명된 APK + macOS dmg를 자동으로 빌드하고 GitHub Release에 게시합니다.
`ci.yml`은 push할 때마다 빌드 검사와 Python 단위 테스트를 실행합니다.

```bash
git tag -a v0.x.y -m "说明" && git push origin v0.x.y
```

---

## 메시지 독학 및 단어 빈도 통계 보고서

자신의 Home Vault 기록 말뭉치를 대상으로 단어 분리 빈도/말버릇/자주 쓰는 구문/월별 주제 변화(TF-IDF)/전송 추세(시간/일 단위 막대그래프, 손가락으로 스크럽하여 세부 정보 확인)를 분석하고 자체 포함 HTML 보고서를 생성합니다. 모든 처리는 로컬에서 이루어지며 데이터는 외부로 전송되지 않습니다.

**앱에서 바로 보기**: 기록 → “메시지 독학” 카드 → 전체 보고서 열기(Home Vault 엔드포인트 `/report/self-study`, SWR 캐시로 즉시 열고 만료 시 백그라운드에서 재계산하며 `?refresh=1`로 강제 재실행).

수동으로 생성할 수도 있습니다.

```bash
python3 -m venv .venv && .venv/bin/pip install jieba
.venv/bin/python scripts/message-self-study.py http://<你的vault地址>:8788
```

보고서는 `~/Downloads/`에 출력됩니다. 다국어 구현 계약은 `docs/i18n-规范.md`를 참조하세요.
