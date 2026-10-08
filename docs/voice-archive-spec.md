# 语音存档接入规范(可选功能)

VibeDrop 本身不录音。如果你另有程序把自己口述的原始录音存了下来(来源不限:输入法、录音 App、自制脚本),
可以按本规范交给 Home Vault,手机端「历史」页就会把录音并进时间线:可播放、看波形、跳过静音,
并按时间挂到对应的发送记录下面。不配置时这部分功能完全不出现。

## 启用

```bash
python3 scripts/home-vault-receiver.py --voice-dir /path/to/voice-archive
# 或环境变量 VIBEDROP_VOICE_DIR=/path/to/voice-archive
```

## 目录结构

```
voice-archive/
├── index.json          # 录音索引(采集程序负责写;请写临时文件再原子改名)
├── lexicon.json        # 可选:输入法用户词库
└── <audioRoot>/        # 音频文件,默认目录名 audio
    └── 2026/10/xxx.flac
```

## index.json

```json
{
  "audioRoot": "audio",
  "items": [
    {
      "id": "84b26243-…",
      "t": "2026-10-07T20:15:00",
      "dur": 6.64,
      "f": "2026/10/20261007-201500_84b26243.flac",
      "wv": "0004bfh…",
      "sk": [[1.2, 2.6]],
      "tx": "识别出的文字",
      "app": "com.vibedrop.mobile"
    }
  ]
}
```

| 字段 | 必填 | 含义 |
|---|---|---|
| `id` | ✅ | 录音唯一编号 |
| `t` | ✅ | 录音开始的本地钟点(ISO,不带时区;Vault 按自己所在机器的时区换算) |
| `f` | ✅ | 音频文件相对 `audioRoot` 的路径;支持 flac / m4a / mp3 / wav / ogg / opus |
| `dur` | | 时长(秒) |
| `wv` | | 波形:48 个字符,每个是 `0-9a-z` 表示的 36 级音量,不下载音频也能画波形 |
| `sk` | | 停顿区间 `[[开始秒, 结束秒], …]`,播放器「跳过静音」用 |
| `tx` | | 识别文字(可后补;采集程序更新索引即可) |
| `app` | | 录音时所在 App 的包名 |
| `wt` | | 有逐字时间(`words/<id>.json`)时为 1 |

FLAC 请写成完整文件(不要从管道直接输出),否则缺总采样数和 seektable,浏览器里时长显示为无穷、进度条拖不动。

## lexicon.json(可选:输入法用户词库)

放在同一目录下,自我研究报告的「输入法」部分会读它。由采集程序定期刷新。

```json
{
  "updated": "2026-10-07T20:43:56",
  "baseline": "2026-09-09",
  "words": [{"w": "营业额", "k": "yye", "f": 3, "t": "2026-10-05 14:02", "first": "2026-09-21"}]
}
```

| 字段 | 含义 |
|---|---|
| `w` / `k` | 词 / 输入编码 |
| `f` | 累计使用次数 |
| `t` | 最后一次使用(本地钟点,`YYYY-MM-DD HH:MM`) |
| `first` | 采集程序第一次见到这个词的日期;`baseline` 那天已存在的词不带此字段 |
| `baseline` | 开始追踪「新增」的日期 |

## words/<id>.json(可选:逐字时间)

```json
{"text": "我觉得…", "w": [["我", 240, 540], ["觉", 540, 660]]}
```

每段是 `[文字, 起毫秒, 止毫秒]`。有它时,跟读高亮按逐字时间推进(否则按停顿与字数估算);
采集程序也应据它生成 `sk`:只跳字与字之间超过约 1 秒的空档、两侧留一点静音,保证不吃字。
参考实现用 macOS 自带的离线语音识别(SpeechTranscriber),识别文字本身只取时间,显示仍用输入法的识别结果。

## 录音怎么挂到消息上

手机端输入框会记下输入法每次把一段文字落进来的时刻(`dictation: [{t, text}]`,毫秒时间戳),随历史条目一起保存、推给 Vault。
历史页按两条规则把录音挂到消息下面,对不上的单独成一条「语音」:

1. **时间对齐(优先,秒级)**:录音期间到录音结束后 6 秒内有片段上屏,且这条消息在录音结束之后才发出 → 就是它。
   录音时间与片段时间来自同一台手机的同一个钟,`t`(录音文件落地时刻≈说完话的时刻)精确到秒就够用。
2. **文字比对(兜底)**:没有片段的旧消息,用识别文字 `tx` 的双字组和消息比对,重合 ≥60% 即挂上。

识别文字还没到时,播放条先显示对上的片段文字。

## Vault 接口

| 接口 | 说明 |
|---|---|
| `GET /api/voice/index[?v=<版本>][&limit=N]` | 返回 `{enabled, version, count, items}`,每条多一个 `ts`(毫秒时间戳);`v` 与当前版本相同时只回 `{unchanged:true}` |
| `GET /api/voice/audio/<f>` | 音频流,支持 Range(iOS 播放必需) |
| `GET /api/voice/words/<id>` | 逐字时间;没有时 404 |
| `GET /api/voice/lexicon` | 返回 `{enabled, updated, baseline, count, words}`;没有 lexicon.json 时 `enabled:false` |
| SSE `/api/events` | 索引变化时广播 `{"type":"voice-updated","version":…}` |

未配置 `--voice-dir` 时,`/api/voice/index` 返回 `{"enabled": false}`,客户端据此隐藏全部语音界面。
