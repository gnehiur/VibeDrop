#!/usr/bin/env python3
"""VibeDrop 消息语料自我研究:分词词频/口头禅/短语/月度话题/行为画像 → 自包含 HTML 报告。

用法: ~/.local/share/vibedrop-analysis/venv/bin/python scripts/message-self-study.py
输出: ~/Downloads/VibeDrop消息自我研究报告_<日期>.html
"""
import json, urllib.request, collections, datetime, math, pathlib, re, html

import jieba

VAULT = "http://127.0.0.1:8788"

STOPWORDS = set("""的 了 在 是 我 你 他 她 它 我们 你们 他们 这 那 这个 那个 有 和 与 或 就 都 要 也 还 不 没 没有
很 挺 太 更 最 被 把 让 给 对 向 从 到 于 之 而 且 及 等 啊 呀 吧 吗 呢 嘛 哦 哈 嗯 呃 诶 唉 咯 啦
一个 一下 什么 怎么 这样 那样 这些 那些 因为 所以 但是 如果 然后 就是 其实 现在 可以 应该 还是 或者 比如
不是 是不是 可能 感觉 好像 知道 觉得 时候 东西 问题 事情 直接 已经 需要 出来 起来 上去 下去 进去 回来
自己 别人 大家 这里 那里 哪里 上面 下面 里面 外面 中间 之前 之后 以后 以前 今天 明天 昨天 每次 一次
再 又 才 只 先 去 来 做 弄 搞 用 看 说 想 点 那 得 会 能 好 行 嗯嗯 哈哈 反正 真的 肯定""".split())

FILLERS = ["就是", "然后", "其实", "那个", "这个", "什么", "怎么", "是不是", "可以", "应该",
           "感觉", "好像", "反正", "要不", "还是", "直接", "肯定", "真的", "然后就是", "对吧",
           "呀", "啊", "吧", "吗", "呢", "哈哈", "嗯"]

def fetch():
    d = json.load(urllib.request.urlopen(f"{VAULT}/api/history/merged?limit=10000"))
    return [e for e in d["history"] if (e.get("kind") or "text") == "text" and (e.get("text") or "").strip()]

def tokens_of(text):
    text = re.sub(r"https?://\S+|[a-zA-Z0-9_.:/\\-]{12,}", " ", text)  # 去链接与长串编码
    return [t for t in jieba.cut(text) if t.strip()]

def main():
    entries = fetch()
    word_freq = collections.Counter()
    filler_freq = collections.Counter()
    bigram_freq = collections.Counter()
    month_words = collections.defaultdict(collections.Counter)
    hours = collections.Counter()
    targets = collections.Counter()
    total_chars = 0
    longest = max(entries, key=lambda e: len(e["text"]))

    for e in entries:
        text = e["text"]
        total_chars += len(text)
        ts = str(e.get("timestamp", ""))
        month = ts[:7]
        try:
            hours[datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).hour] += 1
        except Exception:
            pass
        targets[e.get("targetAlias") or e.get("targetName") or e.get("targetDeviceName") or e.get("target") or "未知"] += 1

        toks = tokens_of(text)
        for f in FILLERS:
            filler_freq[f] += text.count(f)
        kept = []
        for t in toks:
            # 英文词单独放行(2-15位纯字母,统一小写计数),数字与混合乱码仍排除
            if re.fullmatch(r"[A-Za-z][A-Za-z+#.]{1,14}", t):
                t = t.lower()
                if t in {"the", "to", "of", "and", "a", "in", "is", "it"}:
                    kept.append(None); continue
                word_freq[t] += 1
                month_words[month][t] += 1
                kept.append(t)
                continue
            if len(t) >= 2 and t not in STOPWORDS and not re.fullmatch(r"[\d\W_a-zA-Z]+", t):
                word_freq[t] += 1
                month_words[month][t] += 1
                kept.append(t)
            else:
                kept.append(None)
        for a, b in zip(kept, kept[1:]):
            if a and b:
                bigram_freq[f"{a}{b}"] += 1

    # 月度特征词(TF-IDF):该月词频 × log(月数/含该词的月数)
    months = sorted(m for m in month_words if m)
    doc_freq = collections.Counter()
    for m in months:
        for w in month_words[m]:
            doc_freq[w] += 1
    month_top = {}
    for m in months:
        scored = {w: c * math.log(len(months) / doc_freq[w] + 0.1) for w, c in month_words[m].items() if c >= 3}
        month_top[m] = sorted(scored.items(), key=lambda kv: -kv[1])[:8]

    top_words = word_freq.most_common(100)
    max_wc = top_words[0][1] if top_words else 1
    top_fillers = [(f, c) for f, c in filler_freq.most_common(20) if c > 5]
    top_bigrams = bigram_freq.most_common(30)
    max_hour = max(hours.values()) if hours else 1
    month_counts = collections.Counter(str(e.get("timestamp", ""))[:7] for e in entries)

    def esc(x):
        return html.escape(str(x))

    cloud = "".join(
        f'<span style="font-size:{12 + 30 * c / max_wc:.0f}px;opacity:{0.55 + 0.45 * c / max_wc:.2f}">{esc(w)}</span> '
        for w, c in top_words[:60])
    word_rows = "".join(f"<tr><td>{i+1}</td><td>{esc(w)}</td><td>{c}</td></tr>" for i, (w, c) in enumerate(top_words[:50]))
    filler_rows = "".join(f"<tr><td>{esc(w)}</td><td>{c}</td></tr>" for w, c in top_fillers)
    bigram_rows = "".join(f"<tr><td>{esc(w)}</td><td>{c}</td></tr>" for w, c in top_bigrams)
    month_rows = "".join(
        f"<tr><td>{m}</td><td>{month_counts.get(m,0)}条</td><td>{'、'.join(esc(w) for w,_ in month_top[m])}</td></tr>"
        for m in months)
    hour_bars = "".join(
        f'<div class="hb"><div class="hbar" style="height:{72 * hours.get(h,0) / max_hour:.0f}px"></div><span>{h}</span></div>'
        for h in range(24))
    target_rows = "".join(f"<tr><td>{esc(t)}</td><td>{c}</td></tr>" for t, c in targets.most_common(8))

    out = pathlib.Path.home() / "Downloads" / f"VibeDrop消息自我研究报告_{datetime.datetime.now():%y%m%d}.html"
    out.write_text(f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>VibeDrop 消息自我研究报告</title><style>
body{{font-family:-apple-system,'PingFang SC',sans-serif;max-width:860px;margin:32px auto;padding:0 20px;color:#1a2233;background:#f7f9fc}}
h1{{font-size:26px}} h2{{font-size:19px;margin-top:36px;border-left:4px solid #2f6fed;padding-left:10px}}
table{{border-collapse:collapse;width:100%;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px rgba(20,40,80,.08)}}
td,th{{padding:7px 12px;border-bottom:1px solid #eef1f6;text-align:left;font-size:14px}}
.cloud{{background:#fff;border-radius:12px;padding:22px;line-height:2.1;box-shadow:0 1px 4px rgba(20,40,80,.08);color:#2f6fed}}
.stats{{display:flex;gap:12px;flex-wrap:wrap}} .stat{{background:#fff;border-radius:10px;padding:12px 18px;box-shadow:0 1px 4px rgba(20,40,80,.08)}}
.stat b{{font-size:20px;display:block}} .hours{{display:flex;align-items:flex-end;gap:3px;background:#fff;padding:16px;border-radius:10px}}
.hb{{flex:1;text-align:center;font-size:10px;color:#8a94a6}} .hbar{{background:#2f6fed;border-radius:3px 3px 0 0;min-height:2px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}} @media(max-width:700px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body>
<h1>VibeDrop 消息自我研究报告</h1>
<p>语料:{len(entries)} 条文字消息 · 约 {total_chars:,} 字 · {months[0]} ~ {months[-1]} · 生成于 {datetime.datetime.now():%Y-%m-%d %H:%M}</p>
<div class="stats"><div class="stat"><b>{len(entries)}</b>消息总数</div><div class="stat"><b>{total_chars//len(entries)}</b>平均字数/条</div>
<div class="stat"><b>{len(longest['text'])}</b>最长一条字数</div><div class="stat"><b>{max(month_counts, key=month_counts.get)}</b>话最多的月份</div></div>
<h2>词云 · 你最常说的 60 个词</h2><div class="cloud">{cloud}</div>
<h2>发送时段分布(24小时)</h2><div class="hours">{hour_bars}</div>
<div class="grid"><div><h2>高频实义词 Top 50</h2><table><tr><th>#</th><th>词</th><th>次数</th></tr>{word_rows}</table></div>
<div><h2>口头禅榜</h2><table><tr><th>口头禅</th><th>次数</th></tr>{filler_rows}</table>
<h2>高频短语 Top 30</h2><table><tr><th>短语</th><th>次数</th></tr>{bigram_rows}</table></div></div>
<h2>月度话题演变(每月特征词,TF-IDF)</h2><table><tr><th>月份</th><th>消息量</th><th>该月特征词</th></tr>{month_rows}</table>
<h2>消息发往哪里</h2><table><tr><th>目标</th><th>条数</th></tr>{target_rows}</table>
<h2>最长的一条(节选)</h2><p style="background:#fff;padding:14px;border-radius:10px;font-size:13px;color:#4a5468">{esc(longest['text'][:400])}…<br><small>{esc(str(longest.get('timestamp',''))[:19])} · 全长 {len(longest['text'])} 字</small></p>
</body></html>""", encoding="utf-8")
    print(out)

if __name__ == "__main__":
    main()
