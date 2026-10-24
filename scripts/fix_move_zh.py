# -*- coding: utf-8 -*-
"""把 rbf_font.c 里的 zh 渲染块从 rbf_draw_char 前挪到文件头部 include 之后（修复声明顺序）"""
P = "/home/wsz/ml-src/src/rbf_font.c"
s = open(P, encoding="utf-8").read().replace("\r\n", "\n")

START = "/* ===== [汉化]"
MID = "static int FAST rbf_draw_char(font *rbf_font, int x, int y, int ch, int fontspec) {"
i0 = s.find(START)
assert i0 >= 0, "找不到 zh 块起点"
i1 = s.find(MID)
assert i1 > i0, "找不到 zh 块终点"
block = s[i0:i1].rstrip() + "\n"
s2 = s[:i0] + s[i1:]
anchor = '#include "rbf_font.h"\n'
assert anchor in s2, "找不到插入锚点"
s2 = s2.replace(anchor, anchor + "\n" + block, 1)
open(P, "w", encoding="utf-8", newline="\n").write(s2)
print("已上移 zh 块：cut=%d..%d, 插入到 include 之后" % (i0, i1))
