# -*- coding: utf-8 -*-
"""修复对象清单位置（加进 ML_SRC_OBJS）与 zh 块的字体宏（FONT_FG/FONT_BG）。幂等。"""
MK = "/home/wsz/ml-src/src/Makefile.src"
RBF = "/home/wsz/ml-src/src/rbf_font.c"

s = open(MK, encoding="utf-8").read()
lines = [l for l in s.split("\n") if l not in ("\tzh_font.o \\", "\ti18n_zh.o \\")]
s = "\n".join(lines)
if "\tzh_font.o \\" not in s:
    assert "\tmenu.o \\" in s, "找不到 menu.o 锚点"
    s = s.replace("\tmenu.o \\", "\tmenu.o \\\n\tzh_font.o \\\n\ti18n_zh.o \\", 1)
open(MK, "w", encoding="utf-8", newline="\n").write(s)
print("Makefile.src OK")

t = open(RBF, encoding="utf-8").read()
t2 = (t.replace("int fg = FG_COLOR(fontspec)", "int fg = FONT_FG(fontspec)")
       .replace("int bg = BG_COLOR(fontspec)", "int bg = FONT_BG(fontspec)"))
open(RBF, "w", encoding="utf-8", newline="\n").write(t2)
print("rbf_font.c 宏替换%s" % ("（有变化）" if t2 != t else "（已是目标状态）"))
