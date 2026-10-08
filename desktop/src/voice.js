// VibeDrop 桌面端 · 实时同步 + 语音存档(2026-10-08)
// 1) 接 Home Vault 实时推送:手机一发完,所有 Mac 立刻显示(原来启动 3 秒拉一次、之后每 5 分钟一次)
// 2) 历史里的录音:挂到对应消息下 / 对不上的单独成条,底部播放条、跟读高亮、跳过静音,与手机端同一套规则
// 依赖 main.js 的全局:VAULT_ENDPOINT、vaultRemoteEntries、convertVaultEntry、refreshVaultRemoteEntries、
// markLogModelDirty、isHistoryTabVisible、scheduleLogRerenderIfVisible、logListMounted、mountLogListChunk、
// t、escapeHtml、formatLogTime、highlightLogText

const DV_RATES = [1, 1.5, 2];
const DV_PREFS_KEY = 'vibedrop_voice_prefs';
const DV_ATTACH_WINDOW_MS = 60 * 60 * 1000;
const DV_PUNCT = /[，。！？；、,.!?;:：…\n]/;
const DV_ICONS = {
    play: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M8 5.5v13a1 1 0 0 0 1.5.86l10.6-6.5a1 1 0 0 0 0-1.72L9.5 4.64A1 1 0 0 0 8 5.5z"/></svg>',
    pause: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><rect fill="currentColor" x="6.5" y="5" width="4" height="14" rx="1.2"/><rect fill="currentColor" x="13.5" y="5" width="4" height="14" rx="1.2"/></svg>',
    prev: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="currentColor" d="M7 5h2v14H7zM19 6.2v11.6a.8.8 0 0 1-1.22.68L10 13.2a1.4 1.4 0 0 1 0-2.4l7.78-5.28A.8.8 0 0 1 19 6.2z"/></svg>',
    next: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="currentColor" d="M15 5h2v14h-2zM5 6.2v11.6a.8.8 0 0 0 1.22.68L14 13.2a1.4 1.4 0 0 0 0-2.4L6.22 5.52A.8.8 0 0 0 5 6.2z"/></svg>',
    locate: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><circle cx="12" cy="12" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="2.2" fill="currentColor"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
};
const DV_APP_LABELS = {
    'com.vibedrop.mobile': () => 'VibeDrop',
    'com.tencent.mm': () => t('微信'),
    'com.ss.android.ugc.aweme': () => t('抖音'),
    'com.android.chrome': () => 'Chrome',
};

const dv = { enabled: false, version: '', items: [], byId: new Map(), fetching: false };
const dvPlayer = { cur: null, playlist: [], shown: [], drag: null, pendingFrac: 0, raf: false, prefs: { rate: 1, auto: true, skip: true } };
let dvAttach = new Map();             // 模型里的消息 → 挂在它下面的录音(时间正序)
const dvDictText = new Map();         // 录音 id → 对上的口述片段文字
const dvBigrams = new Map();
const dvWords = new Map();            // 录音 id → {text, w} | null(加载中) | false
const dvCharTimes = new Map();
const dvSpans = new Map();
const dvKaraoke = { key: '', ctxKey: '', ctx: null, el: null, cardSig: '', playerSig: '' };
let dvEventSource = null;
try {
    dvPlayer.prefs = { ...dvPlayer.prefs, ...JSON.parse(localStorage.getItem(DV_PREFS_KEY) || '{}') };
} catch (_) { /* 偏好损坏用默认 */ }

const $dv = (id) => document.getElementById(id);

// ================= 实时同步 =================

function dvConnectEvents() {
    if (dvEventSource || typeof EventSource === 'undefined') return;
    let source;
    try {
        source = new EventSource(`${VAULT_ENDPOINT}/api/events`);
    } catch (_) {
        setTimeout(dvConnectEvents, 15000);
        return;
    }
    dvEventSource = source;
    source.onmessage = (event) => {
        let payload = {};
        try { payload = JSON.parse(event.data || '{}') || {}; } catch (_) { payload = {}; }
        if (payload.type === 'voice-updated') {
            dvRefreshIndex();
            return;
        }
        if (Array.isArray(payload.entries) && payload.entries.length) {
            dvUpsertRemote(payload.entries); // 新版金库直接带条目:并入即可
        } else {
            refreshVaultRemoteEntries();
        }
    };
    source.onerror = () => {
        source.close();
        if (dvEventSource === source) dvEventSource = null;
        setTimeout(dvConnectEvents, 15000);
    };
}

function dvUpsertRemote(entries) {
    entries.forEach((raw) => {
        const converted = convertVaultEntry(raw);
        const index = vaultRemoteEntries.findIndex((entry) => entry.vault_key && entry.vault_key === converted.vault_key);
        if (index >= 0) vaultRemoteEntries[index] = converted;
        else vaultRemoteEntries.unshift(converted);
    });
    markLogModelDirty();
    scheduleLogRerenderIfVisible();
}

// ================= 录音索引与对齐 =================

async function dvRefreshIndex() {
    if (dv.fetching) return;
    dv.fetching = true;
    try {
        const url = new URL(`${VAULT_ENDPOINT}/api/voice/index`);
        if (dv.version) url.searchParams.set('v', dv.version);
        url.searchParams.set('fine', '1'); // 桌面端要细波形 wf(手机端不要,省流量)
        const response = await fetch(url.toString());
        if (!response.ok) return;
        const data = await response.json();
        if (!data?.ok) return;
        if (data.enabled && data.unchanged && dv.enabled) return;
        dv.enabled = Boolean(data.enabled);
        dv.version = dv.enabled ? String(data.version || '') : '';
        if (!data.unchanged) {
            dv.items = dv.enabled ? (data.items || []).filter((item) => item && item.id && item.f && Number.isFinite(item.ts)) : [];
        }
        dv.byId = new Map(dv.items.map((item) => [item.id, item]));
        dvBigrams.clear();
        markLogModelDirty();
        scheduleLogRerenderIfVisible();
    } catch (_) {
        /* 金库不在线就先不显示语音 */
    } finally {
        dv.fetching = false;
    }
}

function dvEntryKey(entry) {
    if (entry.kind === 'voice') return `voice:${entry.voice.id}`;
    return entry.transfer_id || entry.vault_key || `${entry.client_id || ''}|${entry.timestamp || ''}`;
}

function dvBigramSet(key, text) {
    let set = dvBigrams.get(key);
    if (set) return set;
    const normalized = String(text || '').toLowerCase().replace(/[\s\p{P}\p{S}]/gu, '');
    set = new Set();
    for (let i = 0; i < normalized.length - 1; i += 1) set.add(normalized.slice(i, i + 2));
    dvBigrams.set(key, set);
    return set;
}

function dvText(item) {
    return item?.tx || dvDictText.get(item?.id) || '';
}

// main.js 的 getLogModel 调它:把录音并进时间线(模型已按 _ts 倒序)
function mergeDesktopVoice(model) {
    dvAttach = new Map();
    dvDictText.clear();
    if (!dv.enabled || !dv.items.length) return model;
    const candidates = model
        .filter((entry) => (entry.kind || 'text') === 'text' && entry.direction !== 'desktop_to_mobile' && entry.text && entry._ts > 0)
        .map((entry) => ({ entry, ts: entry._ts }))
        .sort((a, b) => a.ts - b.ts);
    const segments = [];
    candidates.forEach((candidate) => {
        if (!Array.isArray(candidate.entry.dictation)) return;
        candidate.entry.dictation.forEach((seg) => {
            const tsec = Number(seg?.t);
            if (Number.isFinite(tsec)) segments.push({ t: tsec, text: String(seg?.text || ''), candidate });
        });
    });
    segments.sort((a, b) => a.t - b.t);
    const firstAtOrAfter = (list, value, key) => {
        let lo = 0;
        let hi = list.length;
        while (lo < hi) {
            const mid = (lo + hi) >> 1;
            if (list[mid][key] < value) lo = mid + 1; else hi = mid;
        }
        return lo;
    };
    const standalone = [];
    dv.items.forEach((item) => {
        let matched = null;
        if (segments.length) { // 1) 口述片段时间对齐
            const from = item.ts - (item.dur || 0) * 1000 - 1000;
            const to = item.ts + 6000;
            const hits = [];
            for (let i = firstAtOrAfter(segments, from, 't'); i < segments.length && segments[i].t <= to; i += 1) {
                const seg = segments[i];
                if (seg.candidate.ts < item.ts - 1000) continue;
                hits.push(seg);
                if (!matched || seg.candidate.ts < matched.ts) matched = seg.candidate;
            }
            if (matched) {
                const text = hits.filter((seg) => seg.candidate === matched).map((seg) => seg.text).join('');
                if (text) dvDictText.set(item.id, text);
                matched = matched.entry;
            }
        }
        if (!matched && item.tx) { // 2) 识别文字比对
            const spoken = dvBigramSet(`v:${item.id}:${item.tx.length}`, item.tx);
            if (spoken.size) {
                const deadline = item.ts + DV_ATTACH_WINDOW_MS;
                for (let i = firstAtOrAfter(candidates, item.ts, 'ts'); i < candidates.length && candidates[i].ts <= deadline; i += 1) {
                    const entry = candidates[i].entry;
                    const sent = dvBigramSet(`e:${dvEntryKey(entry)}:${entry.text.length}`, entry.text);
                    let hit = 0;
                    spoken.forEach((gram) => { if (sent.has(gram)) hit += 1; });
                    if (hit / spoken.size >= 0.6) { matched = entry; break; }
                }
            }
        }
        if (matched) {
            if (!dvAttach.has(matched)) dvAttach.set(matched, []);
            dvAttach.get(matched).push(item);
        } else {
            standalone.push({
                kind: 'voice', voice: item, text: item.tx || '', timestamp: new Date(item.ts).toISOString(), _ts: item.ts,
                _normalized: true, client_id: 'voice', client_name: t('语音'), status: 'success', items: [], direction: '',
            });
        }
    });
    dvAttach.forEach((list) => list.sort((a, b) => a.ts - b.ts));
    if (!standalone.length) return model;
    return model.concat(standalone).sort((a, b) => b._ts - a._ts);
}

// main.js 的 renderLog 调它:当前筛选后要显示的条目(决定播放顺序与定位)
function setDesktopVoicePlaylist(entries) {
    dvPlayer.shown = entries;
    const playlist = [];
    if (dv.enabled) {
        entries.forEach((entry) => {
            if (entry.kind === 'voice') playlist.push(entry.voice.id);
            else (dvAttach.get(entry) || []).forEach((item) => playlist.push(item.id));
        });
    }
    dvPlayer.playlist = playlist;
    dvSyncState();
    if (dvPlayer.cur) requestAnimationFrame(dvPaintKaraoke);
}

// ================= 列表元素 =================

function dvClock(seconds) {
    const s = Math.max(0, Math.floor(seconds || 0));
    return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
}

function dvAppLabel(pkg) {
    if (!pkg) return '';
    const known = DV_APP_LABELS[pkg];
    return known ? known() : pkg.split('.').pop();
}

// 波形条数跟着宽度走:桌面窗口宽,48 条太粗。数据优先用细波形 wf(按时长每秒 12 段),
// 比可画条数多就分组取最大值缩下来,比可画条数少就按原样画(不凭空插值)。
const DV_CLIP_PITCH = 3;    // 列表里每条占 3px(2px 条 + 1px 缝)
const DV_PLAYER_PITCH = 4;  // 底部播放条每条占 4px(3px 条 + 1px 缝)
let dvClipBars = 0;         // 列表波形条数,0 = 还没量过
let dvFitQueued = false;

function dvLevels(item) {
    const src = item.wf || item.wv;
    return src ? [...src].map((c) => parseInt(c, 36) || 0) : new Array(48).fill(3);
}

function dvResample(levels, bars) {
    if (!bars || levels.length <= bars) return levels;
    const out = [];
    for (let i = 0; i < bars; i += 1) {
        const start = Math.floor((i * levels.length) / bars);
        const end = Math.max(start + 1, Math.floor(((i + 1) * levels.length) / bars));
        let peak = 0;
        for (let j = start; j < end; j += 1) if (levels[j] > peak) peak = levels[j];
        out.push(peak);
    }
    return out;
}

function dvBarsFor(element, pitch) {
    const width = element?.clientWidth || 0;
    return width > 0 ? Math.max(24, Math.floor(width / pitch)) : 0;
}

// 量一次列表波形和播放条的实际宽度,条数变了才重画(新挂上的卡片、窗口改宽窄都走这里)
function dvFitWaves() {
    const clipBars = dvBarsFor(document.querySelector('#log-list .voice-clip .voice-wave'), DV_CLIP_PITCH);
    if (clipBars) {
        dvClipBars = clipBars;
        document.querySelectorAll('#log-list .voice-clip').forEach((clip) => {
            const wave = clip.querySelector('.voice-wave');
            if (!wave || Number(wave.dataset.bars) === clipBars) return;
            const item = dv.byId.get(clip.dataset.voiceId);
            if (!item) return;
            wave.innerHTML = dvWaveHTML(item, clipBars);
            wave.dataset.bars = String(clipBars);
        });
    }
    const playerWave = $dv('dv-wave');
    const playerBars = dvBarsFor(playerWave, DV_PLAYER_PITCH);
    const current = dv.byId.get(dvPlayer.cur);
    if (playerWave && playerBars && current && Number(playerWave.dataset.bars) !== playerBars) {
        playerWave.innerHTML = dvWaveHTML(current, playerBars);
        playerWave.dataset.bars = String(playerBars);
    }
    dvPaintProgress();
}

function dvQueueFit() {
    if (dvFitQueued) return;
    dvFitQueued = true;
    requestAnimationFrame(() => {
        dvFitQueued = false;
        dvFitWaves();
    });
}

let dvResizeTimer = null;
window.addEventListener('resize', () => {
    clearTimeout(dvResizeTimer);
    dvResizeTimer = setTimeout(dvFitWaves, 120);
});

function dvWaveHTML(item, bars) {
    const levels = dvResample(dvLevels(item), bars || dvClipBars || 96);
    const duration = item.dur || 0;
    const silences = Array.isArray(item.sk) ? item.sk : [];
    return levels.map((level, i) => {
        const at = ((i + 0.5) / levels.length) * duration;
        const silent = duration && silences.some(([s, e]) => at >= s && at < e);
        return `<i${silent ? ' class="s"' : ''} style="height:${Math.max(7, Math.round((level / 35) * 100))}%"></i>`;
    }).join('');
}

function dvClipHTML(item) {
    const isCur = item.id === dvPlayer.cur;
    const playing = isCur && !$dv('dv-audio')?.paused;
    return `
        <div class="voice-clip${isCur ? ' cur' : ''}" data-voice-id="${escapeHtml(item.id)}">
            <span class="voice-clip-btn">${playing ? DV_ICONS.pause : DV_ICONS.play}</span>
            <span class="voice-wave" data-bars="${dvClipBars || ''}">${dvWaveHTML(item)}</span>
            <span class="voice-clip-dur">${dvClock(Math.round(item.dur || 0))}</span>
        </div>
    `;
}

function dvBindClips(container) {
    container.querySelectorAll('.voice-clip').forEach((clip) => {
        clip.addEventListener('click', (event) => {
            event.stopPropagation(); // 别触发卡片的「复制」
            dvHandleClip(clip.dataset.voiceId);
        });
    });
    dvQueueFit(); // 这时卡片多半还没插进页面,下一帧再量宽度
}

// main.js 的 createLogElement 对文字条目调它:有挂着的录音就加在文字下面
function appendVoiceClips(element, entry) {
    element.dataset.vkey = dvEntryKey(entry);
    const list = dvAttach.get(entry);
    if (!list || !list.length) return;
    const wrap = document.createElement('div');
    wrap.className = 'voice-clips';
    wrap.innerHTML = list.map(dvClipHTML).join('');
    element.appendChild(wrap);
    dvBindClips(wrap);
}

// main.js 的 createLogElement 对单独成条的录音调它
function createVoiceLogElement(entry) {
    const item = entry.voice;
    const app = dvAppLabel(item.app);
    const element = document.createElement('div');
    element.className = 'log-item log-item-voice';
    element.dataset.vkey = dvEntryKey(entry);
    element.title = t('点击播放');
    element.style.cursor = 'pointer';
    element.innerHTML = `
        <div class="log-item-top">
            <div class="log-time">${escapeHtml(formatLogTime(entry.timestamp))}</div>
            <div class="log-source-row">
                <span class="log-source-chip">${escapeHtml(t('语音'))}</span>
                ${app ? `<span class="log-source-detail">${escapeHtml(app)}</span>` : ''}
                <span class="log-kind-chip">${dvClock(Math.round(item.dur || 0))}</span>
            </div>
        </div>
        ${dvClipHTML(item)}
        ${item.tx ? `<div class="log-text">${highlightLogText(item.tx)}</div>` : `<div class="voice-tx-none">${escapeHtml(t('暂无识别文字'))}</div>`}
    `;
    dvBindClips(element);
    element.addEventListener('click', () => dvHandleClip(item.id));
    return element;
}

// ================= 播放 =================

function dvHandleClip(voiceId) {
    const item = dv.byId.get(voiceId);
    if (!item) return;
    if (item.id === dvPlayer.cur) {
        dvTogglePlay();
        return;
    }
    dvPlay(item); // 换一条一律从头播
}

function dvCurItem() {
    return dvPlayer.cur ? dv.byId.get(dvPlayer.cur) : null;
}

function dvDuration() {
    const audio = $dv('dv-audio');
    const item = dvCurItem();
    return audio && Number.isFinite(audio.duration) && audio.duration > 0 ? audio.duration : (item?.dur || 0);
}

function dvClipEl(voiceId) {
    return document.querySelector(`#log-list .voice-clip[data-voice-id="${CSS.escape(voiceId)}"]`);
}

function dvIsVisible(voiceId) {
    const clip = voiceId && isHistoryTabVisible() ? dvClipEl(voiceId) : null;
    const scroller = $dv('desktop-scroll');
    if (!clip || !scroller) return false;
    const rect = clip.getBoundingClientRect();
    const view = scroller.getBoundingClientRect();
    return rect.bottom > view.top && rect.top < view.bottom;
}

function dvIndexOf(voiceId) {
    return dvPlayer.shown.findIndex((entry) => (entry.kind === 'voice'
        ? entry.voice?.id === voiceId
        : (dvAttach.get(entry) || []).some((item) => item.id === voiceId)));
}

// 居中:卡片放得下就居中卡片,放不下就居中录音那一行;还没挂进页面的先挂上
function dvCenter(voiceId, onDone) {
    if (!voiceId || !isHistoryTabVisible()) return false;
    const index = dvIndexOf(voiceId);
    if (index < 0) return false;
    if (index >= logListMounted) mountLogListChunk(index - logListMounted + 40);
    const settle = (pass) => {
        const card = document.querySelector(`#log-list [data-vkey="${CSS.escape(dvEntryKey(dvPlayer.shown[index]))}"]`);
        const scroller = $dv('desktop-scroll');
        if (card && scroller) {
            const view = scroller.getBoundingClientRect();
            const cardRect = card.getBoundingClientRect();
            const clip = card.querySelector(`.voice-clip[data-voice-id="${CSS.escape(voiceId)}"]`);
            const target = !clip || cardRect.height <= view.height - 24 ? cardRect : clip.getBoundingClientRect();
            const delta = target.top + target.height / 2 - (view.top + view.height / 2);
            if (Math.abs(delta) > 1) scroller.scrollTop += delta;
        }
        if (pass < 1) requestAnimationFrame(() => settle(pass + 1));
        else if (onDone) onDone();
    };
    settle(0);
    return true;
}

function dvFlash(voiceId) {
    const clip = dvClipEl(voiceId);
    if (!clip) return;
    clip.classList.remove('voice-locate-flash');
    void clip.offsetWidth;
    clip.classList.add('voice-locate-flash');
    setTimeout(() => clip.classList.remove('voice-locate-flash'), 1500);
}

function dvLocate() {
    const id = dvPlayer.cur;
    if (!id) return;
    if (dvIndexOf(id) < 0) {
        showToast(t('当前筛选条件下看不到这条录音'));
        return;
    }
    dvCenter(id, () => dvFlash(id));
}

function dvPlay(item, { reveal = 'nearest' } = {}) {
    const audio = $dv('dv-audio');
    if (!item || !audio) return;
    if (dvPlayer.cur !== item.id) {
        const wasWatching = reveal === 'follow' && dvIsVisible(dvPlayer.cur);
        dvRestoreKaraokeCard();
        dvPlayer.cur = item.id;
        dvEnsureWords(item);
        const path = String(item.f).split('/').map(encodeURIComponent).join('/');
        audio.src = `${VAULT_ENDPOINT}/api/voice/audio/${path}`;
        audio.playbackRate = dvPlayer.prefs.rate;
        const playerWave = $dv('dv-wave');
        const playerBars = dvBarsFor(playerWave, DV_PLAYER_PITCH);
        playerWave.innerHTML = dvWaveHTML(item, playerBars || 160);
        playerWave.dataset.bars = playerBars ? String(playerBars) : '';
        $dv('dv-time').textContent = formatLogTime(new Date(item.ts).toISOString());
        $dv('dv-total').textContent = dvClock(Math.round(item.dur || 0));
        $dv('dv-text').textContent = dvText(item);
        document.querySelectorAll('#log-list .voice-clip').forEach((clip) => clip.classList.toggle('cur', clip.dataset.voiceId === item.id));
        if ('mediaSession' in navigator && typeof MediaMetadata !== 'undefined') {
            navigator.mediaSession.metadata = new MediaMetadata({ title: dvText(item).slice(0, 40) || t('语音'), artist: 'VibeDrop' });
        }
        dvPlayer.pendingFrac = 0;
        dvSyncChips();
        dvSyncVisibility();
        dvQueueFit(); // 播放条刚显示出来时宽度才量得准
        if (reveal === 'center' || (reveal === 'follow' && wasWatching)) dvCenter(item.id);
        else if (reveal === 'nearest') dvClipEl(item.id)?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
    audio.play().catch(() => {});
}

function dvTogglePlay() {
    const audio = $dv('dv-audio');
    if (!audio) return;
    if (!dvPlayer.cur) {
        dvPlay(dv.byId.get(dvPlayer.playlist[0]), { reveal: 'center' });
        return;
    }
    if (audio.paused) audio.play().catch(() => {}); else audio.pause();
}

function dvStep(direction) {
    const audio = $dv('dv-audio');
    const index = dvPlayer.playlist.indexOf(dvPlayer.cur);
    if (index < 0 || !audio) return;
    if (direction < 0 && audio.currentTime > 3) {
        audio.currentTime = 0;
        dvCenter(dvPlayer.cur);
        return;
    }
    dvPlay(dv.byId.get(dvPlayer.playlist[index + (direction > 0 ? 1 : -1)]), { reveal: 'center' });
}

function dvSeekFrac(frac) {
    const audio = $dv('dv-audio');
    const duration = dvDuration();
    if (audio && duration) audio.currentTime = Math.min(1, Math.max(0, frac)) * duration;
    dvPaintProgress();
}

function dvClose() {
    const audio = $dv('dv-audio');
    if (audio) {
        audio.pause();
        audio.removeAttribute('src');
        audio.load();
    }
    dvRestoreKaraokeCard();
    dvPlayer.cur = null;
    document.querySelectorAll('#log-list .voice-clip.cur').forEach((clip) => clip.classList.remove('cur'));
    dvSyncVisibility();
    dvSyncState();
}

function dvSyncVisibility() {
    const show = isHistoryTabVisible() && Boolean(dvPlayer.cur);
    $dv('dv-player')?.classList.toggle('hidden', !show);
    document.body.classList.toggle('dv-player-on', show);
}

// main.js 的 showDesktopTab 调它:离开历史页暂停,回来再显示播放条
function onDesktopVoiceTabChange() {
    if (!isHistoryTabVisible()) $dv('dv-audio')?.pause();
    else dvRefreshIndex();
    dvSyncVisibility();
}

function dvSavePrefs() {
    try { localStorage.setItem(DV_PREFS_KEY, JSON.stringify(dvPlayer.prefs)); } catch (_) { /* 忽略 */ }
}

function dvSyncChips() {
    const { prefs } = dvPlayer;
    $dv('dv-auto')?.classList.toggle('active', prefs.auto);
    $dv('dv-skip')?.classList.toggle('active', prefs.skip);
    document.body.classList.toggle('voice-skip-on', prefs.skip);
    const rates = $dv('dv-rates');
    if (rates) rates.innerHTML = DV_RATES.map((rate) => `<button type="button" role="radio" aria-checked="${rate === prefs.rate}" class="voice-rate${rate === prefs.rate ? ' active' : ''}" data-rate="${rate}">${rate}×</button>`).join('');
    const item = dvCurItem();
    const meta = $dv('dv-meta');
    if (item && meta) {
        const saved = (item.sk || []).reduce((sum, [s, e]) => sum + (e - s), 0);
        const parts = [dvAppLabel(item.app)].filter(Boolean);
        if (prefs.skip && saved >= 1) parts.push(t('跳过停顿省 {time}', { time: dvClock(Math.round(saved)) }));
        meta.textContent = parts.join(' · ');
    }
}

function dvSyncState() {
    const audio = $dv('dv-audio');
    if (!audio) return;
    const playing = Boolean(dvPlayer.cur) && !audio.paused;
    const btn = $dv('dv-play');
    if (btn) {
        btn.innerHTML = playing ? DV_ICONS.pause : DV_ICONS.play;
        btn.setAttribute('aria-label', playing ? t('暂停') : t('播放'));
    }
    document.querySelectorAll('#log-list .voice-clip').forEach((clip) => {
        const icon = clip.querySelector('.voice-clip-btn');
        if (icon) icon.innerHTML = clip.dataset.voiceId === dvPlayer.cur && playing ? DV_ICONS.pause : DV_ICONS.play;
    });
    const index = dvPlayer.playlist.indexOf(dvPlayer.cur);
    if ($dv('dv-prev')) $dv('dv-prev').disabled = index < 0;
    if ($dv('dv-next')) $dv('dv-next').disabled = index < 0 || index >= dvPlayer.playlist.length - 1;
    if ('mediaSession' in navigator) navigator.mediaSession.playbackState = playing ? 'playing' : 'paused';
    if (playing) dvLoop();
}

// 跳过静音:sk 由 Mac mini 按逐字时间算好(只含字与字之间超过约 1 秒的空档),落进去就跳到末尾
function dvSkipCheck() {
    const audio = $dv('dv-audio');
    if (!dvPlayer.prefs.skip || dvPlayer.drag != null || !dvPlayer.cur || !audio || audio.seeking) return;
    const item = dvCurItem();
    if (!item?.sk) return;
    for (const [s, e] of item.sk) {
        if (audio.currentTime >= s && audio.currentTime < e - 0.05) {
            audio.currentTime = Math.min(e, dvDuration());
            return;
        }
    }
}

function dvPaintBars(container, frac) {
    if (!container) return;
    const bars = container.children;
    const played = Math.round(frac * bars.length);
    for (let i = 0; i < bars.length; i += 1) bars[i].classList.toggle('p', i < played);
}

function dvPaintProgress() {
    if (!dvPlayer.cur) return;
    const audio = $dv('dv-audio');
    const duration = dvDuration();
    const frac = dvPlayer.drag != null ? dvPlayer.drag : (duration && audio ? audio.currentTime / duration : 0);
    dvPaintBars($dv('dv-wave'), frac);
    const head = $dv('dv-head');
    if (head) head.style.left = `${frac * 100}%`;
    const cur = $dv('dv-cur');
    if (cur) cur.textContent = dvClock(frac * duration);
    dvPaintBars(dvClipEl(dvPlayer.cur)?.querySelector('.voice-wave'), frac);
    dvPaintKaraoke();
}

function dvLoop() {
    if (dvPlayer.raf) return;
    dvPlayer.raf = true;
    const tick = () => {
        const audio = $dv('dv-audio');
        dvSkipCheck();
        dvPaintProgress();
        if (audio && (!audio.paused || dvPlayer.drag != null)) requestAnimationFrame(tick);
        else dvPlayer.raf = false;
    };
    requestAnimationFrame(tick);
}

// ================= 跟读高亮(与手机端同一套算法) =================

function dvEnsureWords(item) {
    if (!item?.wt || dvWords.has(item.id)) return;
    dvWords.set(item.id, null);
    fetch(`${VAULT_ENDPOINT}/api/voice/words/${encodeURIComponent(item.id)}`)
        .then((response) => response.json())
        .then((data) => dvWords.set(item.id, data?.ok ? data : false))
        .catch(() => dvWords.delete(item.id))
        .finally(() => {
            dvKaraoke.playerSig = '';
            dvKaraoke.cardSig = '';
            if (dvPlayer.cur === item.id) dvPaintKaraoke();
        });
}

function dvWeights(text) {
    const weights = new Float32Array(text.length);
    for (let i = 0; i < text.length; i += 1) {
        const ch = text[i];
        if (DV_PUNCT.test(ch) || /\s/.test(ch)) weights[i] = 0;
        else if (/[A-Za-z]/.test(ch)) weights[i] = 0.3;
        else if (/[0-9]/.test(ch)) weights[i] = 0.6;
        else weights[i] = 1;
    }
    return weights;
}

function dvClauses(text, weights) {
    const clauses = [];
    let start = 0;
    const push = (end) => {
        let w = 0;
        for (let i = start; i < end; i += 1) w += weights[i];
        if (w > 0) clauses.push([start, end]);
        else if (clauses.length) clauses[clauses.length - 1][1] = end;
        start = end;
    };
    for (let i = 0; i < text.length; i += 1) if (DV_PUNCT.test(text[i])) push(i + 1);
    if (start < text.length) push(text.length);
    return clauses;
}

function dvCharTimesFor(item, text) {
    const words = dvWords.get(item?.id);
    if (!words || !Array.isArray(words.w) || !words.w.length || !text) return null;
    const key = `${item.id}|${text}`;
    if (dvCharTimes.has(key)) return dvCharTimes.get(key);
    const ref = [];
    const refTimes = [];
    words.w.forEach(([piece, start, end]) => {
        const chars = String(piece).toLowerCase().split('');
        chars.forEach((ch, k) => { ref.push(ch); refTimes.push((start + ((end - start) * k) / chars.length) / 1000); });
    });
    const shown = text.toLowerCase();
    const n = shown.length;
    const m = ref.length;
    if (!m || n * m > 4e6) { dvCharTimes.set(key, null); return null; }
    const width = m + 1;
    const dp = new Uint16Array((n + 1) * width);
    for (let i = 1; i <= n; i += 1) {
        for (let j = 1; j <= m; j += 1) {
            dp[i * width + j] = shown[i - 1] === ref[j - 1] ? dp[(i - 1) * width + j - 1] + 1 : Math.max(dp[(i - 1) * width + j], dp[i * width + j - 1]);
        }
    }
    const times = new Float64Array(n).fill(NaN);
    let matched = 0;
    for (let i = n, j = m; i > 0 && j > 0;) {
        if (shown[i - 1] === ref[j - 1]) { times[i - 1] = refTimes[j - 1]; matched += 1; i -= 1; j -= 1; }
        else if (dp[(i - 1) * width + j] >= dp[i * width + j - 1]) i -= 1;
        else j -= 1;
    }
    let content = 0;
    for (const ch of text) if (!DV_PUNCT.test(ch) && !/\s/.test(ch)) content += 1;
    if (!content || matched < content * 0.4) { dvCharTimes.set(key, null); return null; }
    const known = [];
    for (let k = 0; k < n; k += 1) if (!Number.isNaN(times[k])) known.push(k);
    for (let q = 0; q < known.length - 1; q += 1) {
        const a = known[q];
        const b = known[q + 1];
        for (let k = a + 1; k < b; k += 1) times[k] = times[a] + ((times[b] - times[a]) * (k - a)) / (b - a);
    }
    for (let k = 0; k < known[0]; k += 1) times[k] = times[known[0]];
    for (let k = known[known.length - 1] + 1; k < n; k += 1) times[k] = times[known[known.length - 1]];
    for (let k = 1; k < n; k += 1) if (times[k] < times[k - 1]) times[k] = times[k - 1];
    dvCharTimes.set(key, times);
    return times;
}

function dvReadingPosition(text, item, time, duration) {
    const weights = dvWeights(text);
    const clauses = dvClauses(text, weights);
    const clauseOf = (done) => (done < text.length ? (clauses.find(([, b]) => done < b) || null) : null);
    const times = dvCharTimesFor(item, text);
    if (times) {
        let lo = 0;
        let hi = times.length;
        while (lo < hi) { const mid = (lo + hi) >> 1; if (times[mid] <= time + 0.05) lo = mid + 1; else hi = mid; }
        const done = time >= duration - 0.05 ? text.length : lo;
        return { done, clause: clauseOf(done) };
    }
    let total = 0;
    for (let i = 0; i < weights.length; i += 1) total += weights[i];
    if (!total || !duration) return { done: 0, clause: null };
    const before = (end) => { let w = 0; for (let i = 0; i < end; i += 1) w += weights[i]; return w; };
    const chunks = [];
    let cursor = 0;
    for (const [s, e] of item.sk || []) { if (s > cursor + 0.05) chunks.push([cursor, Math.min(s, duration)]); cursor = Math.max(cursor, e); }
    if (duration > cursor + 0.05) chunks.push([cursor, duration]);
    let target;
    if (chunks.length > 1 && chunks.length === clauses.length) {
        let k = chunks.findIndex(([, b]) => time < b);
        if (k < 0) k = chunks.length - 1;
        const [a, b] = chunks[k];
        const local = Math.min(1, Math.max(0, (time - a) / Math.max(0.05, b - a)));
        target = before(clauses[k][0]) + local * (before(clauses[k][1]) - before(clauses[k][0]));
    } else {
        let silentBefore = 0;
        let silentTotal = 0;
        for (const [s, e] of item.sk || []) { silentTotal += e - s; if (time > s) silentBefore += Math.min(time, e) - s; }
        target = Math.min(1, Math.max(0, (time - silentBefore) / Math.max(0.1, duration - silentTotal))) * total;
    }
    let acc = 0;
    let done = 0;
    while (done < text.length && acc + weights[done] <= target + 1e-6) { acc += weights[done]; done += 1; }
    if (time >= duration - 0.05) done = text.length;
    return { done, clause: clauseOf(done) };
}

function dvAlignSpan(message, spoken) {
    const a = spoken.toLowerCase();
    const b = message.toLowerCase();
    const m = a.length;
    const n = b.length;
    if (!m || !n) return null;
    let prev = new Int32Array(n + 1);
    let cur = new Int32Array(n + 1);
    let prevStart = new Int32Array(n + 1);
    let curStart = new Int32Array(n + 1);
    let best = 0;
    let bestStart = 0;
    let bestEnd = 0;
    for (let i = 1; i <= m; i += 1) {
        const ca = a.charCodeAt(i - 1);
        cur[0] = 0;
        for (let j = 1; j <= n; j += 1) {
            let score = 0;
            let start = j - 1;
            const diag = prev[j - 1] + (ca === b.charCodeAt(j - 1) ? 2 : -1);
            if (diag > score) { score = diag; start = prev[j - 1] > 0 ? prevStart[j - 1] : j - 1; }
            if (prev[j] - 1 > score) { score = prev[j] - 1; start = prevStart[j]; }
            if (cur[j - 1] - 1 > score) { score = cur[j - 1] - 1; start = curStart[j - 1]; }
            cur[j] = score;
            curStart[j] = start;
            if (score > best) { best = score; bestStart = start; bestEnd = j; }
        }
        [prev, cur] = [cur, prev];
        [prevStart, curStart] = [curStart, prevStart];
    }
    let content = 0;
    for (const ch of spoken) if (!DV_PUNCT.test(ch) && !/\s/.test(ch)) content += 1;
    return best >= Math.max(4, content * 0.9) ? [bestStart, bestEnd] : null;
}

function dvKaraokeHTML(text, doneRanges, now) {
    const n = text.length;
    const marks = new Uint8Array(n);
    doneRanges.forEach(([a, b]) => { for (let i = Math.max(0, a); i < Math.min(n, b); i += 1) marks[i] |= 1; });
    if (now) for (let i = Math.max(0, now[0]); i < Math.min(n, now[1]); i += 1) marks[i] |= 2;
    let html = '';
    let i = 0;
    while (i < n) {
        const mark = marks[i];
        let j = i + 1;
        while (j < n && marks[j] === mark) j += 1;
        const piece = escapeHtml(text.slice(i, j));
        html += mark ? `<span class="${[mark & 1 ? 'vk-done' : '', mark & 2 ? 'vk-now' : ''].join(' ').trim()}">${piece}</span>` : piece;
        i = j;
    }
    return html;
}

function dvKeepNowVisible(box) {
    const now = box?.querySelector('.vk-now');
    if (!now) return;
    const top = now.offsetTop;
    if (top < box.scrollTop || top + now.offsetHeight > box.scrollTop + box.clientHeight) box.scrollTop = Math.max(0, top - 4);
}

function dvBuildContext(item) {
    const index = dvIndexOf(item.id);
    const entry = dvPlayer.shown[index];
    if (!entry) return null;
    const key = dvEntryKey(entry);
    if (entry.kind === 'voice') {
        const text = dvText(item);
        return { key, text, order: [item.id], spans: new Map([[item.id, [0, text.length]]]) };
    }
    const list = dvAttach.get(entry) || [];
    const text = String(entry.text || '');
    const cacheKey = `${key}|${text.length}|${list.map((v) => `${v.id}:${dvText(v).length}`).join(',')}`;
    let spans = dvSpans.get(cacheKey);
    if (!spans) {
        spans = new Map();
        list.forEach((v) => { const spoken = dvText(v); const span = spoken ? dvAlignSpan(text, spoken) : null; if (span) spans.set(v.id, span); });
        dvSpans.set(cacheKey, spans);
    }
    return { key, text, order: list.map((v) => v.id), spans };
}

function dvRestoreKaraokeCard() {
    const { el, ctx } = dvKaraoke;
    if (el && el.isConnected && ctx) el.innerHTML = highlightLogText(ctx.text);
    Object.assign(dvKaraoke, { key: '', ctx: null, el: null, cardSig: '', playerSig: '' });
}

function dvPaintKaraoke() {
    const item = dvCurItem();
    const audio = $dv('dv-audio');
    if (!item || !audio) return;
    const duration = dvDuration();
    const time = dvPlayer.drag != null ? dvPlayer.drag * duration : (audio.currentTime || 0);
    const own = dvText(item);
    const box = $dv('dv-text');
    if (own && box) {
        const pos = dvReadingPosition(own, item, time, duration);
        const sig = `${item.id}|${pos.done}|${pos.clause}`;
        if (sig !== dvKaraoke.playerSig) {
            box.innerHTML = dvKaraokeHTML(own, [[0, pos.done]], pos.clause);
            dvKaraoke.playerSig = sig;
            dvKeepNowVisible(box);
        }
    }
    if (!dvKaraoke.ctx || dvKaraoke.key !== item.id) {
        dvKaraoke.ctx = dvBuildContext(item);
        dvKaraoke.key = item.id;
    }
    const ctx = dvKaraoke.ctx;
    if (!ctx) return;
    const el = document.querySelector(`#log-list [data-vkey="${CSS.escape(ctx.key)}"] .log-text`);
    if (!el) return;
    const position = ctx.order.indexOf(item.id);
    const doneRanges = [];
    let now = null;
    ctx.order.forEach((id, k) => { const span = ctx.spans.get(id); if (span && k < position) doneRanges.push(span); });
    const span = ctx.spans.get(item.id);
    if (span) {
        const pos = dvReadingPosition(ctx.text.slice(span[0], span[1]), item, time, duration);
        doneRanges.push([span[0], span[0] + pos.done]);
        if (pos.clause) now = [span[0] + pos.clause[0], span[0] + pos.clause[1]];
    }
    const sig = `${doneRanges.map((r) => r.join('-')).join(',')}|${now}`;
    if (el !== dvKaraoke.el || sig !== dvKaraoke.cardSig) {
        el.innerHTML = dvKaraokeHTML(ctx.text, doneRanges, now);
        dvKaraoke.el = el;
        dvKaraoke.cardSig = sig;
        dvKeepNowVisible(el);
    }
}

// ================= 初始化 =================

function initDesktopVoice() {
    const audio = $dv('dv-audio');
    if (!audio) return;
    $dv('dv-prev').innerHTML = DV_ICONS.prev;
    $dv('dv-next').innerHTML = DV_ICONS.next;
    $dv('dv-locate').innerHTML = DV_ICONS.locate;
    $dv('dv-prev').setAttribute('aria-label', t('上一条'));
    $dv('dv-next').setAttribute('aria-label', t('下一条'));
    $dv('dv-locate').setAttribute('aria-label', t('定位到这条'));
    $dv('dv-close').setAttribute('aria-label', t('关闭'));
    $dv('dv-play').addEventListener('click', dvTogglePlay);
    $dv('dv-prev').addEventListener('click', () => dvStep(-1));
    $dv('dv-next').addEventListener('click', () => dvStep(1));
    $dv('dv-locate').addEventListener('click', dvLocate);
    $dv('dv-close').addEventListener('click', dvClose);
    document.querySelector('#dv-player .voice-player-title')?.addEventListener('click', dvLocate);
    $dv('dv-text').addEventListener('click', dvLocate);
    $dv('dv-auto').addEventListener('click', () => { dvPlayer.prefs.auto = !dvPlayer.prefs.auto; dvSavePrefs(); dvSyncChips(); });
    $dv('dv-skip').addEventListener('click', () => { dvPlayer.prefs.skip = !dvPlayer.prefs.skip; dvSavePrefs(); dvSyncChips(); dvSkipCheck(); });
    $dv('dv-rates').addEventListener('click', (event) => {
        const chip = event.target.closest('[data-rate]');
        if (!chip) return;
        dvPlayer.prefs.rate = Number(chip.dataset.rate) || 1;
        audio.playbackRate = dvPlayer.prefs.rate;
        dvSavePrefs();
        dvSyncChips();
    });
    ['play', 'pause', 'ended', 'emptied'].forEach((type) => audio.addEventListener(type, dvSyncState));
    audio.addEventListener('waiting', () => $dv('dv-play')?.classList.add('wait'));
    ['playing', 'pause', 'error'].forEach((type) => audio.addEventListener(type, () => $dv('dv-play')?.classList.remove('wait')));
    audio.addEventListener('error', () => { if (dvPlayer.cur && audio.getAttribute('src')) $dv('dv-meta').textContent = t('播放失败，稍后再试'); });
    audio.addEventListener('ended', () => {
        if (!dvPlayer.prefs.auto) return;
        const index = dvPlayer.playlist.indexOf(dvPlayer.cur);
        if (index >= 0 && index < dvPlayer.playlist.length - 1) dvPlay(dv.byId.get(dvPlayer.playlist[index + 1]), { reveal: 'follow' });
    });
    audio.addEventListener('timeupdate', dvSkipCheck);
    audio.addEventListener('play', dvSkipCheck);
    audio.addEventListener('seeked', () => { dvSkipCheck(); dvPaintProgress(); });

    const bar = $dv('dv-bar');
    const barFrac = (event) => { const rect = bar.getBoundingClientRect(); return Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width)); };
    bar.addEventListener('pointerdown', (event) => {
        if (!dvPlayer.cur) return;
        dvPlayer.drag = barFrac(event);
        try { bar.setPointerCapture(event.pointerId); } catch (_) { /* 忽略 */ }
        dvPaintProgress();
        dvLoop();
    });
    bar.addEventListener('pointermove', (event) => { if (dvPlayer.drag == null) return; dvPlayer.drag = barFrac(event); dvPaintProgress(); });
    bar.addEventListener('pointerup', () => { if (dvPlayer.drag == null) return; const frac = dvPlayer.drag; dvPlayer.drag = null; dvSeekFrac(frac); });
    bar.addEventListener('pointercancel', () => { dvPlayer.drag = null; dvPaintProgress(); });

    // 桌面快捷键:空格播放/暂停,←/→ 快退/快进 5 秒(历史页、焦点不在输入框时)
    window.addEventListener('keydown', (event) => {
        if (!isHistoryTabVisible() || !dvPlayer.cur || /INPUT|SELECT|TEXTAREA/.test(document.activeElement?.tagName || '')) return;
        if (event.code === 'Space') { event.preventDefault(); dvTogglePlay(); }
        else if (event.code === 'ArrowRight') audio.currentTime = Math.min(dvDuration(), audio.currentTime + 5);
        else if (event.code === 'ArrowLeft') audio.currentTime = Math.max(0, audio.currentTime - 5);
    });
    if ('mediaSession' in navigator) {
        const handle = (action, fn) => { try { navigator.mediaSession.setActionHandler(action, fn); } catch (_) { /* 不支持 */ } };
        handle('play', () => audio.play().catch(() => {}));
        handle('pause', () => audio.pause());
        handle('previoustrack', () => dvStep(-1));
        handle('nexttrack', () => dvStep(1));
    }
    dvSyncChips();
    dvConnectEvents();
    dvRefreshIndex();
}

initDesktopVoice();
