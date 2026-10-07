#!/usr/bin/env python3
"""VibeDrop 消息语料自我研究:分词词频/口头禅/短语/月度话题/行为画像 → 自包含 HTML 报告。

用法: ~/.local/share/vibedrop-analysis/venv/bin/python scripts/message-self-study.py
输出: ~/Downloads/VibeDrop消息自我研究报告_<日期>.html
"""
import json, urllib.request, collections, datetime, math, pathlib, re, html

import jieba

import os, sys
VAULT = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("VIBEDROP_VAULT", "http://127.0.0.1:8788")).rstrip("/")

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

def machine_fingerprint(name: str) -> str:
    """同一台电脑的历代主机名归并成一个指纹:去 .local、去尾部 -数字、小写。"""
    n = re.sub(r"\.local$", "", str(name or "").strip(), flags=re.I)
    n = re.sub(r"-\d+$", "", n)
    return n.lower()


_BOARD_NAMES = None  # serverId -> 短名(设备名公告板,全家手机改名的权威)
_FP_LABELS = {}      # 机器指纹 -> 展示名


def load_target_aliases():
    global _BOARD_NAMES
    try:
        d = json.load(urllib.request.urlopen(f"{VAULT}/api/device-names", timeout=5))
        _BOARD_NAMES = {sid: v.get("name") for sid, v in (d.get("names") or {}).items() if v.get("name")}
    except Exception:
        _BOARD_NAMES = {}


def resolve_target_label(e) -> str:
    raw = e.get("targetAlias") or e.get("targetName") or e.get("targetDeviceName") or e.get("target") or "未知"
    sid = e.get("targetServerId") or ""
    if _BOARD_NAMES and sid and _BOARD_NAMES.get(sid):
        label = _BOARD_NAMES[sid]
    else:
        label = raw
    fp = machine_fingerprint(label if "." not in str(label) else raw)
    # 同指纹的历代名字统一用短名(公告板名或首个非主机名样式的名字)
    known = _FP_LABELS.get(fp)
    if known:
        return known
    if _BOARD_NAMES and sid and _BOARD_NAMES.get(sid):
        _FP_LABELS[fp] = _BOARD_NAMES[sid]
    elif "." not in str(label):
        _FP_LABELS[fp] = str(label)
    else:
        return str(label)  # 暂无短名,先记原名,等遇到短名的同指纹条目再归并不了——两遍扫描解决
    return _FP_LABELS[fp]


TREND_JS = """
<script>
(function () {
  var D = window.TREND_DATA || { days: {}, todayHours: {}, latestDay: "" };
  var state = { range: "30d", metric: 0 };

  function dayKeysSorted() { return Object.keys(D.days).sort(); }
  function shiftDay(key, delta) {
    var p = key.split("-").map(Number);
    var dt = new Date(Date.UTC(p[0], p[1] - 1, p[2] + delta));
    return dt.toISOString().slice(0, 10);
  }
  function sumRangeDays(fromKey) {
    var out = [];
    var k = fromKey;
    while (k <= D.latestDay) { out.push(k); k = shiftDay(k, 1); }
    return out;
  }
  function hourBars(days, m, tickEvery) {
    var arr = [];
    days.forEach(function (k) {
      var hs = D.hours[k] || {};
      for (var h = 0; h < 24; h++) {
        var v = hs[h] || hs[String(h)] || [0, 0];
        arr.push({
          label: k.slice(5) + " " + h + "时",
          value: v[m],
          tick: h === 0 ? k.slice(5) : "",
        });
      }
    });
    return arr;
  }
  function dayBars(days, m, tickFn) {
    return days.map(function (k, i) {
      var v = D.days[k] || [0, 0];
      return { label: k.slice(5), value: v[m], tick: tickFn(k, i) };
    });
  }
  function buckets() {
    var m = state.metric;
    if (state.range === "today") {
      return { bars: hourBars([D.latestDay], m).map(function (b, h) {
        b.tick = h % 6 === 0 ? String(h) : "";
        return b;
      }), caption: D.latestDay + " · 每小时" };
    }
    if (state.range === "7d") {
      var d7 = sumRangeDays(shiftDay(D.latestDay, -6));
      return { bars: hourBars(d7, m), caption: "近 7 天 · 每小时" };
    }
    if (state.range === "30d") {
      var d30 = sumRangeDays(shiftDay(D.latestDay, -29));
      return { bars: dayBars(d30, m, function (k, i) { return i % 5 === 0 ? k.slice(5) : ""; }),
               caption: "近 30 天 · 每天" };
    }
    if (state.range === "3m") {
      var d90 = sumRangeDays(shiftDay(D.latestDay, -89));
      return { bars: dayBars(d90, m, function (k, i) { return i % 15 === 0 ? k.slice(5) : ""; }),
               caption: "近 3 个月 · 每天" };
    }
    var all = dayKeysSorted();
    var first = all[0];
    var span = sumRangeDays(first);
    return { bars: dayBars(span, m, function (k) { return k.slice(8) === "01" ? k.slice(2, 7) : ""; }),
             caption: "全部时间 · 每天" };
  }

  function fmt(n) { return n >= 10000 ? (n / 10000).toFixed(1) + "万" : String(n); }

  function render() {
    var chart = document.getElementById("trend-chart");
    var xaxis = document.getElementById("trend-xaxis");
    var cap = document.getElementById("trend-caption");
    if (!chart) return;
    var b = buckets();
    currentBars = b.bars;
    var detail = document.getElementById("trend-detail");
    if (detail) detail.textContent = "点或滑动柱子查看明细";
    var unit = state.metric === 0 ? "条" : "字";
    var max = 1, total = 0;
    b.bars.forEach(function (x) { if (x.value > max) max = x.value; total += x.value; });
    cap.textContent = b.caption + " · 共 " + fmt(total) + " " + unit;
    chart.innerHTML = "";
    xaxis.innerHTML = "";
    b.bars.forEach(function (x) {
      var col = document.createElement("div");
      col.className = "trend-bar" + (x.value === max && x.value > 0 ? " max" : "");
      col.style.height = Math.max(2, Math.round(x.value / max * 100)) + "%";
      col.title = x.label + " · " + fmt(x.value) + " " + unit;
      chart.appendChild(col);
      var t = document.createElement("span");
      t.textContent = x.tick;
      xaxis.appendChild(t);
    });
  }

  var currentBars = [];
  function scrubTo(clientX) {
    var chart = document.getElementById("trend-chart");
    var detail = document.getElementById("trend-detail");
    if (!chart || !currentBars.length) return;
    var rect = chart.getBoundingClientRect();
    var idx = Math.floor((clientX - rect.left) / rect.width * currentBars.length);
    idx = Math.max(0, Math.min(currentBars.length - 1, idx));
    var kids = chart.children;
    for (var i = 0; i < kids.length; i++) kids[i].classList.remove("sel");
    if (kids[idx]) kids[idx].classList.add("sel");
    var b = currentBars[idx];
    var unit = state.metric === 0 ? "条" : "字";
    detail.textContent = b.label + " · " + fmt(b.value) + " " + unit;
  }
  function wireScrub() {
    var chart = document.getElementById("trend-chart");
    if (!chart) return;
    var down = false;
    chart.addEventListener("pointerdown", function (e) { down = true; scrubTo(e.clientX); });
    chart.addEventListener("pointermove", function (e) { if (down || e.pointerType === "mouse") scrubTo(e.clientX); });
    window.addEventListener("pointerup", function () { down = false; });
  }

  function wire(groupId, key) {
    var el = document.getElementById(groupId);
    if (!el) return;
    el.addEventListener("click", function (e) {
      var btn = e.target.closest("button");
      if (!btn) return;
      el.querySelectorAll("button").forEach(function (x) { x.classList.remove("on"); });
      btn.classList.add("on");
      state[key] = key === "metric" ? Number(btn.dataset.metric) : btn.dataset.range;
      render();
    });
  }
  wire("trend-ranges", "range");
  wire("trend-metrics", "metric");
  wireScrub();
  render();
})();
</script>
<style>
.trend-wrap { background: #fff; border-radius: 10px; padding: 16px; }
.trend-controls { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
.trend-group button { border: 1px solid #c9d4e5; background: #fff; color: #4a5468; font-size: 12px;
  padding: 4px 10px; border-radius: 999px; cursor: pointer; margin-right: 4px; }
.trend-group button.on { background: #2f6fed; border-color: #2f6fed; color: #fff; }
.trend-caption { font-size: 12px; color: #8a94a6; margin: 10px 0 6px; }
.trend-chart { display: flex; align-items: flex-end; gap: 1px; height: 150px; touch-action: none; }
.trend-detail { font-size: 14px; font-weight: 700; color: #1d3557; margin: 2px 0 8px; min-height: 20px; }
.trend-bar.sel { background: #1d4ed8; outline: 1px solid #1d4ed8; }
.trend-bar { flex: 1; min-width: 0; background: #9db9f4; border-radius: 2px 2px 0 0; min-height: 2px; }
.trend-bar.max { background: #2f6fed; }
.trend-xaxis { display: flex; gap: 1px; margin-top: 4px; }
.trend-xaxis span { flex: 1; min-width: 0; font-size: 10px; color: #8a94a6; text-align: left; overflow: visible; white-space: nowrap; }
</style>
"""


# ---- 输入法:语音存档 + 用户词库(金库配了 --voice-dir 才有,见 docs/voice-archive-spec.md)----
VOICE_APP_LABELS = {"com.vibedrop.mobile": "VibeDrop", "com.tencent.mm": "微信", "com.ss.android.ugc.aweme": "抖音",
                    "com.android.chrome": "Chrome", "org.telegram.messenger": "Telegram", "com.twitter.android": "X"}


def fetch_optional(path):
    try:
        d = json.load(urllib.request.urlopen(f"{VAULT}{path}", timeout=15))
    except Exception:
        return None
    return d if d.get("ok") and d.get("enabled") else None


def fmt_dur(seconds):
    s = int(round(seconds))
    if s < 60:
        return f"{s} 秒"
    m, s = divmod(s, 60)
    if m < 60:
        return f"{m} 分" + (f" {s} 秒" if s else "")
    h, m = divmod(m, 60)
    return f"{h} 小时" + (f" {m} 分" if m else "")


def short_day(iso):
    return iso[2:10] if len(iso) >= 10 else iso   # 显示层两位年


def bars_html(values, labels, unit, height=72):
    top = max(values) if values and max(values) > 0 else 1
    return "".join(
        f'<div class="hb" title="{html.escape(full)} · {v:g}{unit}"><div class="hbar" style="height:{height * v / top:.0f}px"></div><span>{html.escape(lab)}</span></div>'
        for v, (lab, full) in zip(values, labels))


def input_method_section():
    voice = fetch_optional("/api/voice/index")
    lex = fetch_optional("/api/voice/lexicon")
    items = (voice or {}).get("items") or []
    words = (lex or {}).get("words") or []
    if not items and not words:
        return ""
    esc = html.escape
    out = ["<h1 style='margin-top:56px'>输入法</h1>",
           "<p>上面分析的是发出去的定稿;这里是输入法这一侧:你口述的原始录音,和输入法替你攒的个人词库。</p>"]

    if items:
        total = sum(i.get("dur") or 0 for i in items)
        silent = sum(sum(e - s for s, e in (i.get("sk") or [])) for i in items)
        voiced = max(total - silent, 0)
        texted = [i for i in items if i.get("tx")]
        chars = sum(len(i["tx"]) for i in texted)
        texted_voiced = sum((i.get("dur") or 0) - sum(e - s for s, e in (i.get("sk") or [])) for i in texted)
        speed = chars / (texted_voiced / 60) if texted_voiced > 0 else 0
        days = sorted({i["t"][:10] for i in items})
        out.append(f"<h2>语音 · 从 {short_day(days[0])} 起</h2>")
        out.append('<div class="stats">'
                   f'<div class="stat"><b>{len(items)}</b>录音条数</div>'
                   f'<div class="stat"><b>{fmt_dur(total)}</b>总时长</div>'
                   f'<div class="stat"><b>{fmt_dur(voiced)}</b>人声(停顿占 {silent / total * 100 if total else 0:.0f}%)</div>'
                   f'<div class="stat"><b>{fmt_dur(total / len(items))}</b>平均每条</div>'
                   f'<div class="stat"><b>{chars:,}</b>口述字数</div>'
                   f'<div class="stat"><b>{speed:.0f}</b>字/分钟(按人声算的语速)</div>'
                   '</div>')
        # 近 30 天每天说了多久(分钟)
        last = datetime.date.fromisoformat(days[-1])
        span = [last - datetime.timedelta(days=n) for n in range(29, -1, -1)]
        per_day = collections.Counter()
        for i in items:
            per_day[i["t"][:10]] += (i.get("dur") or 0) / 60
        vals = [round(per_day.get(d.isoformat(), 0), 1) for d in span]
        labs = [(d.strftime("%m-%d") if n % 5 == 0 else "", d.isoformat()[2:]) for n, d in enumerate(span)]
        out.append(f"<h2>近 30 天每天说了多久(分钟)</h2><div class='hours'>{bars_html(vals, labs, ' 分钟')}</div>")
        per_hour = collections.Counter(int(i["t"][11:13]) for i in items)
        out.append("<h2>一天中什么时候在说</h2><div class='hours'>"
                   + bars_html([per_hour.get(h, 0) for h in range(24)], [(str(h), f"{h} 点") for h in range(24)], " 条") + "</div>")
        apps = collections.defaultdict(lambda: [0, 0.0])
        for i in items:
            pkg = i.get("app") or ""
            label = VOICE_APP_LABELS.get(pkg) or (pkg.split(".")[-1] if pkg else "未知")
            apps[label][0] += 1
            apps[label][1] += i.get("dur") or 0
        app_rows = "".join(f"<tr><td>{esc(a)}</td><td>{n}</td><td>{fmt_dur(d)}</td></tr>"
                           for a, (n, d) in sorted(apps.items(), key=lambda kv: -kv[1][1]))
        spoken = collections.Counter()
        for i in texted:
            for tok in tokens_of(i["tx"]):
                if len(tok) >= 2 and tok not in STOPWORDS and not re.fullmatch(r"[\d\W_]+", tok):
                    spoken[tok.lower() if tok.isascii() else tok] += 1
        spoken_rows = "".join(f"<tr><td>{n + 1}</td><td>{esc(w)}</td><td>{c}</td></tr>" for n, (w, c) in enumerate(spoken.most_common(30)))
        out.append('<div class="grid">'
                   f"<div><h2>在哪些 App 里说</h2><table><tr><th>App</th><th>条数</th><th>时长</th></tr>{app_rows}</table></div>"
                   f"<div><h2>口述高频词 Top 30</h2><table><tr><th>#</th><th>词</th><th>次数</th></tr>{spoken_rows}</table></div>"
                   "</div>")

    if words:
        baseline = (lex or {}).get("baseline") or ""
        updated = (lex or {}).get("updated") or ""
        uses = sum(w.get("f") or 0 for w in words)
        recent_cut = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        used_recent = sum(1 for w in words if (w.get("t") or "") >= recent_cut)
        fresh = sorted((w for w in words if w.get("first")), key=lambda w: (w["first"], w.get("t") or ""), reverse=True)
        fresh_30 = sum(1 for w in fresh if w["first"] >= recent_cut)
        out.append(f"<h2>个人词库 · 更新于 {short_day(updated)}</h2>")
        out.append('<div class="stats">'
                   f'<div class="stat"><b>{len(words):,}</b>词条</div>'
                   f'<div class="stat"><b>{uses:,}</b>累计使用次数</div>'
                   f'<div class="stat"><b>{used_recent:,}</b>近 30 天用过</div>'
                   f'<div class="stat"><b>{len(fresh):,}</b>{short_day(baseline)} 以来新增</div>'
                   + (f'<div class="stat"><b>{fresh_30:,}</b>近 30 天新增</div>' if baseline and baseline < recent_cut else '')
                   + '</div>')
        top_rows = "".join(f"<tr><td>{n + 1}</td><td>{esc(w['w'])}</td><td>{esc(w.get('k') or '')}</td><td>{w.get('f') or 0}</td></tr>"
                           for n, w in enumerate(sorted(words, key=lambda w: -(w.get("f") or 0))[:50]))
        fresh_rows = "".join(f"<tr><td>{esc(w['w'])}</td><td>{esc(w.get('k') or '')}</td><td>{short_day(w['first'])}</td></tr>"
                             for w in fresh[:50])
        out.append('<div class="grid">'
                   f"<div><h2>词库里用得最多的 50 个词</h2><table><tr><th>#</th><th>词</th><th>编码</th><th>次数</th></tr>{top_rows}</table></div>"
                   f"<div><h2>最近新造的 50 个词</h2><table><tr><th>词</th><th>编码</th><th>首次出现</th></tr>{fresh_rows}</table></div>"
                   "</div>")
        last_hour = collections.Counter(int(w["t"][11:13]) for w in words if len(w.get("t") or "") >= 13)
        out.append("<h2>词库词最后一次被用是在几点</h2><div class='hours'>"
                   + bars_html([last_hour.get(h, 0) for h in range(24)], [(str(h), f"{h} 点") for h in range(24)], " 个词") + "</div>")
    return "".join(out)


def main():
    entries = fetch()
    word_freq = collections.Counter()
    filler_freq = collections.Counter()
    bigram_freq = collections.Counter()
    month_words = collections.defaultdict(collections.Counter)
    hours = collections.Counter()
    load_target_aliases()
    for e in entries:
        resolve_target_label(e)  # 预扫描:先让所有机器指纹学到短名,计数那遍才能全归并
    targets = collections.Counter()
    day_stats = {}
    hour_stats = {}
    total_chars = 0
    longest = max(entries, key=lambda e: len(e["text"]))
    seen_texts = set()
    top_longest = []
    for e in sorted(entries, key=lambda e: len(e["text"]), reverse=True):
        key = e["text"][:200]  # 同文发多台/多端镜像只算一条
        if key in seen_texts:
            continue
        seen_texts.add(key)
        top_longest.append(e)
        if len(top_longest) == 10:
            break

    for e in entries:
        text = e["text"]
        total_chars += len(text)
        ts = str(e.get("timestamp", ""))
        month = ts[:7]
        try:
            hours[datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).hour] += 1
        except Exception:
            pass
        dkey = ts[:10]
        if len(dkey) == 10:
            day_stats.setdefault(dkey, [0, 0])
            day_stats[dkey][0] += 1
            day_stats[dkey][1] += len(text)
            try:
                h = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).hour
                hour_stats.setdefault(dkey, {}).setdefault(h, [0, 0])
                hour_stats[dkey][h][0] += 1
                hour_stats[dkey][h][1] += len(text)
            except Exception:
                pass
        targets[resolve_target_label(e)] += 1

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
    longest_blocks = "".join(
        f"<p style='background:#fff;padding:14px;border-radius:10px;font-size:13px;color:#4a5468;margin:10px 0'>"
        f"<b style='color:#2f6fed'>No.{i + 1} · {len(e['text'])} 字</b><br>"
        f"{esc(e['text'][:280])}…<br>"
        f"<small>{esc(str(e.get('timestamp', ''))[:19])}</small></p>"
        for i, e in enumerate(top_longest)
    )
    latest_day = max(day_stats) if day_stats else ""
    trend_data_json = json.dumps({
        "days": day_stats,
        "hours": hour_stats,
        "latestDay": latest_day,
    }, ensure_ascii=False)
    trend_section = (
        "<h2>发送趋势</h2>"
        "<div class='trend-wrap'>"
        "<div class='trend-controls'>"
        "<span class='trend-group' id='trend-ranges'>"
        "<button data-range='today'>今天</button>"
        "<button data-range='7d'>近7天</button>"
        "<button data-range='30d' class='on'>近30天</button>"
        "<button data-range='3m'>近3月</button>"
        "<button data-range='all'>全部</button>"
        "</span>"
        "<span class='trend-group' id='trend-metrics'>"
        "<button data-metric='0' class='on'>条数</button>"
        "<button data-metric='1'>字数</button>"
        "</span>"
        "</div>"
        "<div class='trend-caption' id='trend-caption'></div>"
        "<div class='trend-detail' id='trend-detail'>点或滑动柱子查看明细</div>"
        "<div class='trend-chart' id='trend-chart'></div>"
        "<div class='trend-xaxis' id='trend-xaxis'></div>"
        "</div>"
        "<script>window.TREND_DATA = " + trend_data_json + ";</script>"
        + TREND_JS
    )
    target_rows = "".join(f"<tr><td>{esc(t)}</td><td>{c}</td></tr>" for t, c in targets.most_common(8))
    input_method = input_method_section()

    out_arg = os.environ.get("SELF_STUDY_OUTPUT", "")
    out = pathlib.Path(out_arg) if out_arg else (pathlib.Path.home() / "Downloads" / f"VibeDrop消息自我研究报告_{datetime.datetime.now():%y%m%d}.html")
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
<div class="stat"><b>{len(longest['text'])}</b>最长一条字数</div><div class="stat"><b>{max(month_counts, key=month_counts.get)}</b>话最多的月份</div>
<div class="stat"><b>{total_chars/189106:.2f} 本</b>相当于《三体》第一部(189,106字·微信读书)</div>
<div class="stat"><b>{total_chars/884061:.2f} 本</b>相当于《三体》全集(884,061字·微信读书)</div></div>
{trend_section}
<h2>词云 · 你最常说的 60 个词</h2><div class="cloud">{cloud}</div>
<h2>发送时段分布(24小时)</h2><div class="hours">{hour_bars}</div>
<div class="grid"><div><h2>高频实义词 Top 50</h2><table><tr><th>#</th><th>词</th><th>次数</th></tr>{word_rows}</table></div>
<div><h2>口头禅榜</h2><table><tr><th>口头禅</th><th>次数</th></tr>{filler_rows}</table>
<h2>高频短语 Top 30</h2><table><tr><th>短语</th><th>次数</th></tr>{bigram_rows}</table></div></div>
<h2>月度话题演变(每月特征词,TF-IDF)</h2><table><tr><th>月份</th><th>消息量</th><th>该月特征词</th></tr>{month_rows}</table>
<h2>消息发往哪里</h2><table><tr><th>目标</th><th>条数</th></tr>{target_rows}</table>
<h2>最长的十条(各取节选)</h2>{longest_blocks}
{input_method}
<script>
document.querySelectorAll('h2').forEach(h => {{
  const table = h.nextElementSibling && h.nextElementSibling.tagName === 'TABLE' ? h.nextElementSibling
    : (h.nextElementSibling && h.nextElementSibling.querySelector ? h.nextElementSibling.querySelector('table') : null);
  if (!table) return;
  const btn = document.createElement('button');
  btn.textContent = '复制';
  btn.style.cssText = 'margin-left:10px;font-size:12px;padding:2px 12px;border:1px solid #c9d4e5;border-radius:6px;background:#fff;color:#2f6fed;cursor:pointer;vertical-align:middle';
  btn.onclick = async () => {{
    const lines = [...table.rows].map(r => [...r.cells].map(c => c.textContent.trim()).join('\t'));
    await navigator.clipboard.writeText(h.firstChild.textContent.trim() + '\n' + lines.join('\n'));
    btn.textContent = '已复制 ✓';
    setTimeout(() => btn.textContent = '复制', 1500);
  }};
  h.appendChild(btn);
}});
</script></body></html>""", encoding="utf-8")
    print(out)

if __name__ == "__main__":
    main()
