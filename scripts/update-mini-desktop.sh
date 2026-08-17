#!/bin/bash
# 在 Mini 上运行:把 MacBook 上已用 VibeTech 固定证书签好名的成品 App 原样搬来安装。
# 关键:Mini 端【绝不重签名】——签名身份稳定,辅助功能(TCC)权限跨更新永续继承。
# (旧流程在 Mini 上 ad-hoc 重签,每次构建都是新身份,权限每次作废——2026-08-18 根治)
set -euo pipefail
MB="overlord@overlorddeMacBook-Air-4.local"
echo "[update-mini] 从 MacBook 拉取已签名成品..."
TMP=$(mktemp -d)
ssh "$MB" 'cd /Applications && tar cf - VibeDrop.app' | tar xf - -C "$TMP"
codesign -dv "$TMP/VibeDrop.app" 2>&1 | grep -q "VibeTech" || {
  echo "[update-mini] ⚠️ 成品不是 VibeTech 签名,中止(先在 MacBook 跑 deploy-desktop.sh)"; exit 1; }
echo "[update-mini] 停旧进程并替换..."
pkill -f "VibeDrop.app/Contents/MacOS" 2>/dev/null || true
sleep 1
rm -rf /Applications/VibeDrop.app
ditto "$TMP/VibeDrop.app" /Applications/VibeDrop.app
xattr -dr com.apple.quarantine /Applications/VibeDrop.app 2>/dev/null || true
rm -rf "$TMP"
open -a VibeDrop
echo "[update-mini] 完成。首次切换到 VibeTech 签名需重授一次辅助功能,此后永续。"
