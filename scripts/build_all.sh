#!/usr/bin/env bash
# 全型号批量构建魔灯中文版。
# 用法: bash build_all.sh [ml-src路径] [输出目录]
# 前置: 已对 ml-src 跑过一次 build.sh（翻译表/字库/补丁就位），且已装 gcc-arm-none-eabi
set -u
ML="${1:-$HOME/ml-src}"
OUT="${2:-$(cd "$(dirname "$0")/.." && pwd)/releases}"
LOG="$HOME/build_all.log"

CAMS="5D2.212 5D3.113 5D3.123 6D.116 7D.203 7D_MASTER.203 40D.111 50D.109 60D.111 70D.112 100D.101 450D.111 500D.111 550D.109 600D.102 650D.104 700D.115 1100D.105 EOSM.202"

mkdir -p "$OUT"
: > "$LOG"
ok=0; fail=0
for cam in $CAMS; do
    dir="$ML/platform/$cam"
    if [ ! -d "$dir" ]; then
        echo "[跳过] $cam（源码树无此目标）" | tee -a "$LOG"
        continue
    fi
    echo "== 构建 $cam ==" | tee -a "$LOG"
    if (cd "$dir" && make clean >/dev/null 2>&1; make >> "$LOG" 2>&1) && [ -f "$dir/autoexec.bin" ]; then
        cp "$dir/autoexec.bin" "$OUT/autoexec-zh-$cam.bin"
        echo "[OK] $cam -> releases/autoexec-zh-$cam.bin" | tee -a "$LOG"
        ok=$((ok+1))
    else
        echo "[失败] $cam（详见 $LOG）" | tee -a "$LOG"
        fail=$((fail+1))
    fi
done
echo "完成: 成功 $ok / 失败 $fail（失败多为源码树未适配该型号，见日志）"
