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
├── index.json          # 索引(采集程序负责写;请写临时文件再原子改名)
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

FLAC 请写成完整文件(不要从管道直接输出),否则缺总采样数和 seektable,浏览器里时长显示为无穷、进度条拖不动。

## Vault 接口

| 接口 | 说明 |
|---|---|
| `GET /api/voice/index[?v=<版本>][&limit=N]` | 返回 `{enabled, version, count, items}`,每条多一个 `ts`(毫秒时间戳);`v` 与当前版本相同时只回 `{unchanged:true}` |
| `GET /api/voice/audio/<f>` | 音频流,支持 Range(iOS 播放必需) |
| SSE `/api/events` | 索引变化时广播 `{"type":"voice-updated","version":…}` |

未配置 `--voice-dir` 时,`/api/voice/index` 返回 `{"enabled": false}`,客户端据此隐藏全部语音界面。
