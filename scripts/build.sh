#!/usr/bin/env bash
# 一键构建魔灯 60D 中文版。前置：
#   sudo apt install gcc-arm-none-eabi python3-pil fonts-noto-cjk git make
#   git clone --depth 1 https://github.com/dannephoto/magic-lantern_jip_hop.git ~/ml-src
# 用法: bash build.sh [ml-src路径，默认~/ml-src]
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ML="${1:-$HOME/ml-src}"

echo "== 0/6 GCC14 兼容 flags（幂等）=="
grep -q '汉化项目' "$ML/Makefile.setup" 2>/dev/null || printf '\n# [汉化项目] GCC14 兼容\nCFLAGS += -fcommon -Wno-error=int-conversion -Wno-error=implicit-function-declaration -Wno-error=implicit-int -Wno-error=incompatible-pointer-types -Wno-error=return-mismatch\n' >> "$ML/Makefile.setup"
grep -q '汉化项目' "$ML/tcc/Makefile" 2>/dev/null || printf '\n# [汉化项目] GCC14 兼容\nCFLAGS += -fcommon -Wno-error=int-conversion -Wno-error=implicit-function-declaration -Wno-error=implicit-int -Wno-error=incompatible-pointer-types -Wno-error=return-mismatch\n' >> "$ML/tcc/Makefile"

echo "== 1/6 提取源码字符串 =="
python3 "$HERE/extract_all.py" "$ML" "$HERE/../translations/strings_all.tsv"
cp "$HERE/../translations/strings_all.tsv" /tmp/zh_all.tsv

echo "== 2/6 生成翻译表 i18n_zh.c =="
cd "$HERE/../translations"
python3 "$HERE/t2c.py" strings_merged.tsv strings_todo_translated.tsv strings_todo3_translated.tsv /tmp/zh_all.tsv "$ML/src/i18n_zh.c"
cp "$HERE/i18n_zh.h" "$ML/src/i18n_zh.h"

echo "== 3/6 生成四档中文点阵 zh_font.c/.h =="
python3 "$HERE/gen_chars.py" "$ML/src/i18n_zh.c" /tmp/zh_chars.txt
python3 "$HERE/gen_zh_font.py" /tmp/zh_chars.txt "$ML/src/"

echo "== 4/6 打补丁（幂等）=="
python3 "$HERE/patch_ml3.py"
python3 "$HERE/patch_ml4.py"

echo "== 5/6 编译 =="
cd "$ML/platform/60D.111"
make

echo "完成: $ML/platform/60D.111/autoexec.bin"
