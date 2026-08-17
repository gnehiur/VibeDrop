// ============================================
// VibeDrop i18n 骨架 — gettext 流派:中文原文即钥匙
// 契约见 docs/i18n-规范.md;翻译只填 locales/<lang>.json,本文件不再改
// ============================================
(function () {
    const LANG_KEY = 'vibedrop-language';           // 'system' | 'zh-CN' | 'en' | ...
    const CACHE_PREFIX = 'vibedrop-i18n-cache-';    // 词典本地缓存,启动零延迟
    let dict = {};                                   // 当前语言词典:中文原文 → 译文
    let currentLang = 'zh-CN';

    function detectLang() {
        const saved = localStorage.getItem(LANG_KEY);
        if (saved && saved !== 'system') return saved;
        const nav = String(navigator.language || 'zh').toLowerCase();
        if (nav.startsWith('zh')) return 'zh-CN';
        return 'en';
    }

    // 中文是源语言,词典恒为空(原文直出);其他语言查表,缺译回退原文
    function t(source, vars) {
        let out = Object.prototype.hasOwnProperty.call(dict, source) ? dict[source] : source;
        if (vars) {
            Object.keys(vars).forEach((k) => {
                out = out.split('{' + k + '}').join(String(vars[k]));
            });
        }
        return out;
    }

    // 静态 HTML 翻译:
    //   <h3 data-i18n>智能发送卡</h3>            → 以自身文本为钥匙翻译文本
    //   <textarea data-i18n-placeholder>          → 翻译 placeholder 属性
    //   <button data-i18n-title>                  → 翻译 title 属性
    function applyStaticTranslations(root) {
        const scope = root || document;
        scope.querySelectorAll('[data-i18n]').forEach((el) => {
            const key = el.getAttribute('data-i18n-key') || el.textContent.trim();
            if (!el.getAttribute('data-i18n-key')) el.setAttribute('data-i18n-key', key);
            el.textContent = t(key);
        });
        scope.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
            const key = el.getAttribute('data-i18n-placeholder-key') || el.getAttribute('placeholder') || '';
            if (!el.getAttribute('data-i18n-placeholder-key')) el.setAttribute('data-i18n-placeholder-key', key);
            if (key) el.setAttribute('placeholder', t(key));
        });
        scope.querySelectorAll('[data-i18n-title]').forEach((el) => {
            const key = el.getAttribute('data-i18n-title-key') || el.getAttribute('title') || '';
            if (!el.getAttribute('data-i18n-title-key')) el.setAttribute('data-i18n-title-key', key);
            if (key) el.setAttribute('title', t(key));
        });
    }

    async function loadDict(lang) {
        if (lang === 'zh-CN') {
            dict = {};
            return;
        }
        // 先用本地缓存立即生效,再后台拉新
        try {
            const cached = localStorage.getItem(CACHE_PREFIX + lang);
            if (cached) dict = JSON.parse(cached);
        } catch (_) { /* 缓存坏了就等网络 */ }
        try {
            const res = await fetch('locales/' + lang + '.json');
            if (res.ok) {
                dict = await res.json();
                localStorage.setItem(CACHE_PREFIX + lang, JSON.stringify(dict));
                applyStaticTranslations();
                window.dispatchEvent(new Event('i18n-updated'));
            }
        } catch (_) { /* 离线:用缓存或原文 */ }
    }

    currentLang = detectLang();
    const ready = loadDict(currentLang);

    document.addEventListener('DOMContentLoaded', () => {
        ready.then(() => applyStaticTranslations());
    });

    window.t = t;
    window.vibeI18n = {
        get lang() { return currentLang; },
        LANG_KEY,
        applyStaticTranslations,
        setLanguage(value) {
            localStorage.setItem(LANG_KEY, value || 'system');
            window.location.reload(); // 全量重载是最诚实的切换方式
        },
    };
})();
