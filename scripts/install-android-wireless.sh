#!/bin/bash
# 在 Mini 上运行:从 MacBook 取最新 APK,经无线 adb 装到两台一加(免数据线)。
# 前提:手机开着"无线调试"。配对关系已持久(Mini 名下),只需 connect。
# 端口每次开关无线调试会轮换:连不上时看手机无线调试页当前端口,作为参数传入。
#   用法: ./install-android-wireless.sh [Ace5端口] [竞速版端口]
# 已知怪癖:adb pair 会报 protocol fault,但不影响——信任已存在,直接 connect 即可。
set -euo pipefail
ACE5="192.168.3.6:${1:-40511}"
RACING="192.168.3.46:${2:-40247}"
APK=/tmp/vibedrop-latest.apk
echo "[wireless] 取最新 APK..."
scp -q overlord@overlorddeMacBook-Air-4.local:"~/Documents/安卓发送mac输入文字app/mobile/src-tauri/gen/android/app/build/outputs/apk/universal/release/VibeDrop-signed.apk" "$APK"
for target in "$ACE5" "$RACING"; do
  echo "[wireless] $target ..."
  if adb connect "$target" 2>&1 | grep -q "connected"; then
    adb -s "$target" install -r "$APK" 2>&1 | tail -1
    adb -s "$target" shell am start -n com.vibedrop.mobile/.MainActivity >/dev/null 2>&1 || true
    echo "[wireless] $target ✅"
  else
    echo "[wireless] $target ⚠️ 连不上(手机没开无线调试或端口已轮换,看手机报新端口)"
  fi
done
