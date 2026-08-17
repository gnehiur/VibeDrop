#!/usr/bin/env python3
"""i18n 质检门:扫代码里的全部翻译钥匙,对照每个语言包报缺漏/冗余。

用法: python3 scripts/i18n-check.py [--strict]
  --strict: 有缺漏时退出码非零(供 CI 用)

钥匙来源:
  1. JS 里的 t('...') / t("...") 调用(mobile/src/app.js, desktop/src/main.js, desktop/static/app.js)
  2. HTML 里 data-i18n 元素的文本、data-i18n-placeholder/title 的属性值
语言包: mobile/src/locales/*.json 与 desktop/src/locales/*.json
"""
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent

JS_FILES = [
    ROOT / "mobile/src/app.js",
    ROOT / "desktop/src/main.js",
]
HTML_FILES = [
    ROOT / "mobile/src/index.html",
    ROOT / "desktop/src/index.html",
]
LOCALE_DIRS = [
    ROOT / "mobile/src/locales",
    ROOT / "desktop/src/locales",
]

# t('...') / t("...")——不处理跨行与模板字符串钥匙(规范禁止那样写钥匙)
T_CALL = re.compile(r"""(?<![\w$])t\(\s*(['"])((?:\\.|(?!\1).)*)\1""")


class I18nHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.keys = set()
        self._capture_depth = 0
        self._buf = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "data-i18n" in d:
            self._capture_depth += 1
            self._buf.append("")
        for attr in ("data-i18n-placeholder", "data-i18n-title"):
            if attr in d:
                src = d.get(attr.replace("data-i18n-", "")) or d.get(attr) or ""
                if src:
                    self.keys.add(src.strip())
        if "data-i18n-placeholder" in d and d.get("placeholder"):
            self.keys.add(d["placeholder"].strip())
        if "data-i18n-title" in d and d.get("title"):
            self.keys.add(d["title"].strip())

    def handle_data(self, data):
        if self._capture_depth:
            self._buf[-1] += data

    def handle_endtag(self, tag):
        if self._capture_depth:
            text = self._buf.pop().strip()
            if text:
                self.keys.add(text)
            self._capture_depth -= 1


def collect_code_keys() -> set[str]:
    keys: set[str] = set()
    for f in JS_FILES:
        if not f.exists():
            continue
        for m in T_CALL.finditer(f.read_text(encoding="utf-8")):
            key = m.group(2).replace("\\'", "'").replace('\\"', '"')
            keys.add(key)
    for f in HTML_FILES:
        if not f.exists():
            continue
        parser = I18nHTMLParser()
        parser.feed(f.read_text(encoding="utf-8"))
        keys.update(parser.keys)
    return keys


def main() -> int:
    strict = "--strict" in sys.argv
    code_keys = collect_code_keys()
    print(f"代码中共 {len(code_keys)} 个翻译钥匙\n")

    problems = False
    for locale_dir in LOCALE_DIRS:
        if not locale_dir.exists():
            continue
        for lf in sorted(locale_dir.glob("*.json")):
            data = json.loads(lf.read_text(encoding="utf-8"))
            missing = sorted(code_keys - set(data))
            unused = sorted(set(data) - code_keys)
            rel = lf.relative_to(ROOT)
            print(f"== {rel}: 已译 {len(data)} | 缺 {len(missing)} | 冗余 {len(unused)}")
            for k in missing:
                print(f"   缺: {k}")
            for k in unused:
                print(f"   冗余: {k}")
            if missing:
                problems = True
            print()

    if problems and strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
