# -*- coding: utf-8 -*-
"""从 i18n_zh.c 的中文列提取全部不重复字符，生成 chars 文件给 gen_zh_font.py 用。"""
import re, sys

src = open(sys.argv[1], encoding="utf-8").read()
pairs = re.findall(r'\{\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"\s*\}', src)
chars = set()
for en, zh in pairs:
    chars.update(zh)
chars.discard(" ")
out = "".join(sorted(chars))
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(out + "\n")
print("翻译条目 %d 条，不重复汉字 %d 个" % (len(pairs), len(out)))
