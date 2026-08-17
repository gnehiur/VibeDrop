[简体中文](README.md) | [繁體中文](README.zh-TW.md) | [English](README.en.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Русский](README.ru.md) | [Kiswahili](README.sw.md) | [Runasimi](README.qu.md)

<div align="center">

<img src="docs/logo.png" width="120" alt="VibeDrop logo">

# VibeDrop

**スマートフォンと Mac の間でクリップボードを同期し、テキストやファイルを転送するツール — LAN で直接接続し、クラウドに依存しません**

[![release](https://img.shields.io/github/v/release/jncdke/VibeDrop?color=2f6fed)](https://github.com/jncdke/VibeDrop/releases)
[![license](https://img.shields.io/github/license/jncdke/VibeDrop?color=green)](LICENSE)
![platform](https://img.shields.io/badge/platform-macOS%20%7C%20Android%20%7C%20iOS-8a63d2)
![i18n](https://img.shields.io/badge/languages-11-2f6fed)
![tauri](https://img.shields.io/badge/Tauri-2.x-ffc131?logo=tauri&logoColor=white)
![rust](https://img.shields.io/badge/Rust-stable-e43717?logo=rust)

[Release をダウンロード](https://github.com/jncdke/VibeDrop/releases) · [機能一覧](#機能一覧) · [メッセージ自習](#メッセージ自習と単語頻度統計レポート)

</div>

---

VibeDrop は 3 つのコンポーネントで構成され、**WebSocket** を通じて LAN 内で直接通信します。インターネットもクラウドサービスも必要ありません。

- **Mac デスクトップ版**（`desktop/`）— テキスト／ファイルの受信、クリップボードのブロードキャスト、システムトレイ
- **モバイル版**（`mobile/`、Android + iOS）— テキスト／画像／動画／ファイルの送信、履歴タイムライン
- **Home Vault**（`scripts/`）— 複数デバイスの履歴統合、元メディアの保管、プローブログの回収を担うホームサーバー

---

## スクリーンショット

**スマート送信カード「カーソル追従送信」**——スマートフォンに話しかけると、カーソルがあるコンピューターへテキストが自動入力されます（ユニバーサルコントロールの利用場面）：

<div align="center">
<table>
  <tr>
    <td align="center" colspan="2"><img src="assets/screenshots/desktop-overview.jpg" width="680" alt="macOS デスクトップ版の概要"><br><sub>macOS デスクトップ版 — デバイス一覧 · ペアリング · ドロップして送信</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/screenshots/ios-smart-card.png" width="320" alt="iOS スマート送信カード"><br><sub>iOS (iPhone 17 Pro Max)</sub></td>
    <td align="center"><img src="assets/screenshots/android-smart-card.jpg" width="320" alt="Android スマート送信カード"><br><sub>Android (OnePlus Ace 5)</sub></td>
  </tr>
</table>
</div>

---

## 機能一覧

| 機能 | Mac 側 | モバイル側（Android + iOS） |
|------|--------|------------------------|
| 🎯 スマート送信カード「カーソル追従送信」 | ✅ キーボード／マウスのアクティビティを報告（`CGEventSource`、権限不要） | ✅ テキスト／画像／ファイルをカーソルがある Mac へ自動送信。1 秒で追従し、手動切り替えも可能 |
| 📝 テキスト転送（スマートフォン → Mac） | ✅ 受信してキーボード入力をシミュレート | ✅ 送信後もキーボードと音声入力を維持し、余分な操作なしで連続して口述可能 |
| 📋 クリップボード同期（Mac → スマートフォン） | ✅ 変更を監視してブロードキャスト | ✅ ネイティブのバックグラウンドサービスがクリップボードへ書き込み |
| 🌍 多言語 | ✅ システムに従う | ✅ 11 言語（中国語簡体字／繁体字、英語、日本語、韓国語、スペイン語、フランス語、ドイツ語、ロシア語、スワヒリ語、ケチュア語）。gettext 方式で未翻訳箇所は中国語へフォールバック |
| 🤝 自動検出とペアリング | ✅ 確認待ちのペアリングと接続済みデバイスを表示 | ✅ 近くの Mac をスキャンして確認コードでペアリング。デバイス名を変更でき、複数のスマートフォン間で自動同期 |
| 📜 履歴タイムライン | ✅ 全デバイス統合表示 + サムネイル | ✅ 全デバイスを統合し、送信元／送信先／種類／元ファイル／時間で絞り込み、検索結果をハイライト |
| 📈 アクティビティヒートマップ | ✅ 受信ヒートマップ + セルを押して絞り込み | ✅ 送信ヒートマップ + セルを押して絞り込み |
| 🔬 メッセージ自習 | —（レポートは Home Vault が生成） | ✅ 履歴ページに完全なレポートを埋め込み：ワードクラウド／口癖／送信傾向の棒グラフ（スクラブして詳細を確認） |
| 📁 双方向ファイル転送 | ✅ ドラッグ＆ドロップ / Finder サービス / Finder 共有 | ✅ 受信箱へ送信 / 画像はフォトアルバムへ保存、複数項目は自動でパッケージ化 |
| 🗄 Home Vault | ホームサーバー：複数デバイスの履歴統合 · 元メディア保管庫（ハッシュ重複排除 + Range ストリーミング）· プローブログ回収 | ✅ 差分プッシュ + SSE リアルタイム同期 |
| 🔒 PIN 認証 | ✅ ランダム生成し、ファイルへ永続化 | ✅ 確認コードでペアリング後に自動保存 |
| 🕰 表示タイムゾーン設定 | ✅ ローカル／北京／米国西部。表示と集計の基準を統一 | — |
| 📡 フォアグラウンド維持 / トレイ | ✅ システムトレイ + ログイン時に起動 | ✅ Android の通知領域に常駐 |

---

## 技術アーキテクチャ概要

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

通信経路は 3 本あり、すべて LAN 内で直接接続され、クラウドには依存しません。

1. **スマートフォン ↔ Mac**：WebSocket（`:9001/ws`）。PIN 認証後、テキスト／ファイル／クリップボード／アクティビティ照会を転送します。
2. **すべての端末 → Home Vault**：HTTP（`:8788`）。履歴の差分プッシュ、メディアのアップロード、レポートの取得を行います。
3. **Vault → クライアント**：SSE の長時間接続（`/api/events`）。履歴が保存されると即座にブロードキャストし、25 秒ごとにハートビートを送ります。

---

## コアフローの詳細

### スマート送信カード「カーソル追従送信」

1. デスクトップ版は `activity_query` を受け取ると `CGEventSourceSecondsSinceLastEventType` を呼び出し、
   「最後のキーボード／マウス操作から何秒経過したか」を返します（権限もスレッドも不要——スクリーンセーバー用にシステムが管理している既存の記録を読むだけです）。
2. スマートフォンは接続中のすべての Mac を 1 秒ごとにポーリングし、**相対的なアイドル秒数**を比較します（2 台の時計のずれに影響されません）。
   最も新しい Mac がカーソルのある端末です。ユニバーサルコントロールは実際のキーボード／マウスイベントをカーソルのある端末へ届けるため、信号と事実が強く結び付いています。
3. テキスト／画像／ファイルを送信する瞬間に送信先を固定します。インジケーターを押すと自動／手動を順に切り替えられます。

### 検出とペアリング

スマートフォンは UDP ブロードキャスト + HTTP プローブ（`discover_desktops`）の 2 経路を並行してスキャンします。デスクトップ版を検出すると確認コードによるペアリングへ進みます（デスクトップ版に確認待ちカードが表示され、双方で同じコードを照合）。承認されると保存され、自動接続します。
カスタムデバイス名を保存すると、Vault の掲示板（`/api/device-names`、serverId をキーとする LWW）を通じて複数のスマートフォン間で同期されます。

### テキストとファイル

- テキスト：`type` / `type_enter` アクションにより、デスクトップ版が enigo でキーボード入力をシミュレートします。アウェイモードでは代わりに
  `clipboard_text` を使用します（クリップボードへの書き込みのみ。UU Remote などの遠隔操作ツールと併用）。
- ファイル：分割転送プロトコル（begin/append/finish/cancel）。モバイル側では受信箱またはフォトアルバムへ保存し、
  Mac 側ではドラッグ＆ドロップ／Finder サービスから送信します。転送全体に `transferId` を付与するため、送受信側の記録を正確に統合できます。
- 送信ボタンはフォーカスを奪いません（mousedown preventDefault）。送信後もキーボードと音声入力のセッションが維持され、
  余分な操作なしで連続して口述できます。

### 履歴同期（差分 + リアルタイム）

- 各端末はローカル履歴とプッシュカーソル（`lastPushedEntryId`）を保持し、差分だけをプッシュします（実測で 1 件 3 ms/188 B）。
- Vault は全デバイスのタイムライン（`/api/history/merged`）を統合します。クライアントは通常 2,000 件を軽量取得し、セッションごとに一度だけ 10,000 件を深く取得します。SSE が届くと即座に更新します。
- 同じ名前の ID は自動統合されます（再インストールで生成されたランダム ID という「前世」をローカル端末へ統合）。名前は表示層であり、同一性はフィンガープリントで判断します。

### 元メディア保管庫

元ファイルは SHA-256 単位で保管庫へ格納されます（`/api/media/upload`、ストリーミング + 重複排除、上限 2 GB）。どのデバイスからでもハッシュを使ってオンラインで元ファイルを取得できます（`/api/media/blob/<hash>`、Range ストリーミング対応）——「ローカルで消失 ≠ すべての端末で消失」です。

### 起動時セルフテストプローブ（ブラックボックス）

`app.js` の先頭で window.onerror の捕捉と probe() の計測を導入しています。起動 6 秒後／エラー 1.5 秒後に Vault の `/api/client-log` へ POST し、デバイス別に保存します。実機の黒画面／白画面問題を推測で追わず、ログから特定できます。

---

## コードマップ

### Mac デスクトップ版 `desktop/`

| ファイル | 行数 | 役割 |
|------|------|------|
| `src-tauri/src/main.rs` | ~4900 | HTTP/WS サーバー、PIN 認証、enigo キーボード、arboard クリップボード、ファイル送受信、トレイ、検出応答、アクティビティ報告 |
| `src/main.js` | ~2600 | デスクトップ UI：デバイス一覧、ペアリング確認、統合履歴 + サムネイル、受信ヒートマップ、タイムゾーン設定、ドラッグ送信 |
| `src/style.css` | ~2000 | デスクトップ版のスタイル |
| `static/*` | — | `mobile/src/` のバイト単位のミラー（モバイル側を変更した後は必ずコピー。ビルドの節を参照） |

### モバイル版 `mobile/`（Android + iOS で同じコードを共有）

| ファイル | 行数 | 役割 |
|------|------|------|
| `src/app.js` | ~11500 | フロントエンドの全ロジック：スマート送信カード、複数デバイス接続、履歴タイムライン（絞り込み／検索ハイライト／仮想スクロール）、ヒートマップ、Vault 同期、メディアビューアー、プローブ |
| `src/i18n.js` | ~110 | gettext 方式の多言語ランタイム：t()/フォールバック/補間/言語検出/辞書キャッシュ |
| `src/locales/*.json` | ×10 | 言語パック（中国語原文をキーとし、新しい言語はファイルを 1 つ追加） |
| `src-tauri/src/lib.rs` | ~1900 | 16 個のネイティブコマンド：履歴の永続化、ファイルの分割受信、検出とペアリング、機種判定、Vault へのメディアアップロード、パス解決。iOS スクロールロック（KVO で contentOffset を監視し、レンダリング前にゼロへ戻す） |
| `gen/android/.../MainActivity.kt` | — | コンソール転送（VibeDropConsole）+ 元の WebChromeClient への委譲（ファイルピッカーなど） |
| `gen/android/.../KeepAliveService.kt` | — | フォアグラウンド維持 |
| `gen/android/.../VideoPlayerActivity.kt` | — | ExoPlayer（Media3）によるネイティブ全画面プレーヤー |
| `gen/android/.../BackgroundClipboardSyncManager.kt` | — | ネイティブのバックグラウンドクリップボード書き込み |

### Home Vault とツール `scripts/`

| スクリプト | 役割 |
|------|------|
| `home-vault-receiver.py`（約 1000 行） | ホームサーバーの全エンドポイント（下表を参照）。launchd で常駐 |
| `message-self-study.py` | jieba による完全なコーパス分析 → 自己完結型 HTML レポート（送信傾向の棒グラフを含む） |
| `vault-media-uploader.py` / `sync-home-vault.py` | 既存メディアの追加送信 / 履歴の永続化同期 |
| `i18n-check.py` | 多言語品質ゲート：すべての t()/data-i18n キーをスキャンし、言語パックの不足／余剰を報告 |
| `deploy-android.sh` / `deploy-desktop.sh` / `deploy-ios.sh` | 3 プラットフォームのワンコマンドビルド／デプロイ |
| `generate-app-icons.py` / `generate-tray-frames.py` | ブランドアセットの生成 |

### Home Vault エンドポイント早見表

| エンドポイント | 用途 |
|------|------|
| `POST /api/history/append` · `GET /api/history/merged` | 差分登録 / 統合タイムライン |
| `GET /api/events` | SSE：永続化と同時にブロードキャスト |
| `POST /api/media/upload` · `/lookup` · `GET /api/media/blob/<hash>` | メディア保管庫：重複排除して登録／照会／Range ストリーミング取得 |
| `GET/POST /api/device-names` | デバイス名掲示板（LWW） |
| `POST /api/client-log` | プローブのブラックボックス回収 |
| `GET /report/self-study` | 自習レポート（SWR：キャッシュを即時表示し、期限切れ後はバックグラウンド再計算。`?refresh=1` で強制更新） |

---

## プラットフォーム別の実践知

### WebView エンジンの差異（重要）

| | Android | iOS | macOS デスクトップ |
|---|---------|-----|-----------|
| エンジン | Chromium | **WKWebView** | **WKWebView（iOS と同じ！）** |
| `content-visibility: auto` | ✅ ネイティブ仮想化 | ❌ 黒画面 | ❌ スクロール時に空白 |
| 長いリストへの対策 | content-visibility | JS 仮想スクロール | 分割マウント |
| `Intl.Segmenter` による中国語分かち書き | ❌ 1 文字ずつ分割 | ✅ 完全な辞書 | ✅ |

**結論：エンジンをまたぐ中国語の分かち書きにはサーバー側の jieba だけを使い、content-visibility は Android でのみ使用します。**

### iOS

- **固定レイアウト**：アプリシェルの設計として外側の WKWebView のスクロールを無効化します（`isScrollEnabled=false` で止められるのはジェスチャーだけで、
  WebKit がキーボード表示時に行うプログラム的スクロールには、さらに **KVO で contentOffset を監視し、レンダリング前に元へ戻す**必要があります。
  固定する「原点」は (0,0) ではなく、`-adjustedContentInset` によるシステムの静止位置です）。フォアグラウンドへ戻るたびにロックを再設定します。
- パッケージ作成の鉄則：`cargo tauri ios build --export-method debugging`。Xcode Run を直接使用してはいけません。
- 無料署名は作成日から 7 日間有効で、自動再署名パイプラインとの併用が必要です。

### Android

- カスタム WebChromeClient は**必ず元の client へ委譲**します（onShowFileChooser など）。全体を置き換えるとファイルピッカーが動作しなくなります。
- 実際の console は `adb logcat -d VibeDropConsole:I "*:S"` で確認します。
- 起動時の 5 件の「Cannot redefine property」エラーは、Tauri の注入スクリプトが二重実行されることによる無害なノイズです。調査する必要はありません。

### Mac

- enigo によるキーボードシミュレーションは独立スレッドで実行。クリップボードを 500 ms ごとにポーリング → broadcast channel → 各 WS 接続へ配信します。
- デスクトップ版バイナリの内部名は現在も `voicedrop` です（pgrep 使用時に注意）。

---

## 多言語（i18n）

gettext 方式を採用し、**中国語原文そのものをキー**にします。`t('发送并回车')` で現在の言語の辞書を引き、未翻訳なら中国語原文へフォールバックします（途中までの翻訳でも常にリリース可能）。変数には `t('已改名为 {name}', {name})` のようなプレースホルダーを使い、文字列の連結は禁止です。
現在は 11 言語に対応。新しい言語は `locales/<lang>.json` ファイル 1 つ + `i18n.js` マッピング表 1 行で追加できます。

- 品質ゲート：`python3 scripts/i18n-check.py --strict`（キーの網羅性／プレースホルダーの完全性）。
- 意味の検収：各言語の中核 30 語を人手で精読します（機械では意味を保証できません。`docs/i18n-规范.md` を参照）。
- 言語選択欄の言語名には**各言語の自称**と中国語／英語の読みを添え、どの言語パックでも翻訳しません。

---

## ビルドとデプロイ

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

**2 つの規律**：

1. `mobile/src/` の app.js / index.html / style.css / i18n.js / locales/ を変更した後は、
   **必ず `desktop/static/` へコピー**します（デスクトップ版 HTTP サービスが提供するモバイルブラウザ版）。
2. **2 つの Tauri ビルドを並行実行してはいけません**（ローカル IPC チャンネルを共有するため衝突します）。必ず直列で実行します。

---

## GitHub リリース

`v*` タグを push すると `release.yml` が起動し、署名済み APK + macOS dmg を自動ビルドして GitHub Release に公開します。
`ci.yml` は push ごとにビルドチェックと Python 単体テストを実行します。

```bash
git tag -a v0.x.y -m "说明" && git push origin v0.x.y
```

---

## メッセージ自習と単語頻度統計レポート

自分の Home Vault 履歴コーパスに対し、分かち書きした単語の頻度／口癖／頻出フレーズ／月ごとの話題変化（TF-IDF）／送信傾向（時／日単位の棒グラフ、指でスクラブして詳細を確認）を分析し、自己完結型 HTML レポートを生成します。すべてローカルで処理され、データは外部へ送信されません。

**App 内で直接表示**：履歴 →「メッセージ自習」カード → 完全なレポートを開く（Home Vault エンドポイント `/report/self-study`。SWR キャッシュですぐに開き、期限切れならバックグラウンドで再計算。`?refresh=1` で強制再実行）。

手動で生成することもできます。

```bash
python3 -m venv .venv && .venv/bin/pip install jieba
.venv/bin/python scripts/message-self-study.py http://<你的vault地址>:8788
```

レポートは `~/Downloads/` へ出力されます。多言語実装の契約については `docs/i18n-规范.md` を参照してください。
