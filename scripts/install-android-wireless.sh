#!/bin/bash
# 在 Mini 上运行:mDNS 自动发现两台一加的无线 adb 端口,取 MacBook 最新 APK 安装。
# 前提只有一个:手机开着"无线调试"(重启后该开关会自动关,需手动再开;配对信任永久)。
# 端口/IP 全自动发现,无需任何参数。怪癖:adb pair 报 protocol fault 无害,connect 直通。
# 注意:macOS 自带 bash 3.2,不可用 declare -A/mapfile(踩过)。
set -euo pipefail
SERIALS="3B6F4FE910B8KRLS 3B15B8017W600000"
name_of() {
  case "$1" in
    3B6F4FE910B8KRLS) echo "一加 Ace 5" ;;
    3B15B8017W600000) echo "一加 Ace 5 竞速版" ;;
    *) echo "$1" ;;
  esac
}
APK=/tmp/vibedrop-latest.apk
echo "[wireless] 取最新 APK..."
scp -q overlord@overlorddeMacBook-Air-4.local:"~/Documents/安卓发送mac输入文字app/mobile/src-tauri/gen/android/app/build/outputs/apk/universal/release/VibeDrop-signed.apk" "$APK"
echo "[wireless] mDNS 扫描无线调试设备..."
SERVICES=$(adb mdns services 2>/dev/null | grep "_adb-tls-connect" || true)
OK=0
TOTAL=0
for serial in $SERIALS; do
  TOTAL=$((TOTAL+1))
  name=$(name_of "$serial")
  addr=$(echo "$SERVICES" | grep "$serial" | awk '{print $3}' | head -1)
  if [ -z "$addr" ]; then
    echo "[wireless] $name ⚠️ 未发现(无线调试没开?)"
    continue
  fi
  echo "[wireless] $name @ $addr"
  if adb connect "$addr" 2>&1 | grep -q "connected"; then
    adb -s "$addr" install -r "$APK" 2>&1 | tail -1
    adb -s "$addr" shell am start -n com.vibedrop.mobile/.MainActivity >/dev/null 2>&1 || true
    echo "[wireless] $name ✅"
    OK=$((OK+1))
  else
    echo "[wireless] $name ⚠️ 连接失败"
  fi
done
echo "[wireless] 完成:$OK/$TOTAL 台"
