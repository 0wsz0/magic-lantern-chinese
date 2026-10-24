# -*- coding: utf-8 -*-
"""把汉化补丁精确打进 ml-src 源码树（幂等：已打过则跳过，找不到锚点则报错退出）。
在 WSL 里运行: python3 /mnt/d/stocks/eos60d/_build/mlzh/patch_ml.py
"""
import sys

SRC = "/home/wsz/ml-src/src"

def patch(path, old, new):
    old = old.replace("\r\n", "\n")
    new = new.replace("\r\n", "\n")
    with open(path, encoding="utf-8") as f:
        s = f.read()
    if new in s:
        print("[跳过] %s: 已打过" % path)
        return True
    if old not in s:
        print("[失败] %s: 找不到锚点 %r" % (path, old[:70]))
        return False
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(s.replace(old, new, 1))
    print("[OK] %s" % path)
    return True

ok = True
rbf = SRC + "/rbf_font.c"
menu = SRC + "/menu.c"
mk = SRC + "/Makefile.src"

# ---------- rbf_font.c：注入 UTF-8 中文渲染块 ----------
ZH_BLOCK = '''/* ===== [汉化] UTF-8 中文渲染（内置点阵字库 zh_font，见 zh_font.c）===== */
#include "zh_font.h"

/* 解码 UTF-8 首字符；返回码点（ASCII/无效返回 -1），*adv 为字节数 */
static int FAST zh_utf8_decode(const char* s, int* adv)
{
    unsigned char c0 = (unsigned char) s[0];
    if (c0 < 0x80) { *adv = 1; return -1; }
    if ((c0 & 0xE0) == 0xC0 && ((unsigned char) s[1] & 0xC0) == 0x80)
    { *adv = 2; return ((c0 & 0x1F) << 6) | ((unsigned char) s[1] & 0x3F); }
    if ((c0 & 0xF0) == 0xE0 && ((unsigned char) s[1] & 0xC0) == 0x80 && ((unsigned char) s[2] & 0xC0) == 0x80)
    { *adv = 3; return ((c0 & 0x0F) << 12) | (((unsigned char) s[1] & 0x3F) << 6) | ((unsigned char) s[2] & 0x3F); }
    *adv = 1; return -1;
}

/* 码点二分查找（zh_codepoints 已升序）；返回字形下标或 -1 */
static int FAST zh_lookup(int cp)
{
    int lo = 0, hi = zh_char_count - 1;
    while (lo <= hi)
    {
        int mid = (lo + hi) / 2;
        if (zh_codepoints[mid] == cp) return mid;
        if (zh_codepoints[mid] < cp) lo = mid + 1; else hi = mid - 1;
    }
    return -1;
}

/* 画一个中文字形（1bpp、LSB-first，与 rbf 字形同一套解包方式）*/
static int FAST zh_draw_glyph(int idx, int x, int y, int fontspec)
{
    uint8_t * bmp = bmp_vram();
    const unsigned char* g = zh_glyphs + idx * (ZH_GLYPH_H * 2);
    int fg = FG_COLOR(fontspec);
    int bg = BG_COLOR(fontspec);
    for (int yy = 0; yy < ZH_GLYPH_H; ++yy)
    {
        if (y + yy <= BMP_H_MINUS || y + yy >= BMP_H_PLUS) break;
        for (int xx = 0; xx < ZH_GLYPH_W; ++xx)
            bmp_putpixel_fast(bmp, x + xx, y + yy, (g[yy * 2 + xx / 8] & (1 << (xx % 8))) ? fg : bg);
    }
    return ZH_GLYPH_W;
}

/* 尝试画 UTF-8 中文；命中返回像素宽并把 *adv 置为字节数，否则返回 -1 */
static int FAST zh_try_draw(const char* s, int x, int y, int fontspec, int* adv)
{
    *adv = 1;
    int cp = zh_utf8_decode(s, adv);
    if (cp < 0) return -1;
    int idx = zh_lookup(cp);
    if (idx < 0) return -1;
    return zh_draw_glyph(idx, x, y, fontspec);
}

//-------------------------------------------------------------------
static int FAST rbf_draw_char(font *rbf_font, int x, int y, int ch, int fontspec) {'''

ok &= patch(rbf,
    "//-------------------------------------------------------------------\n"
    "static int FAST rbf_draw_char(font *rbf_font, int x, int y, int ch, int fontspec) {",
    ZH_BLOCK)

# ---------- rbf_draw_string_c 主循环 ----------
ok &= patch(rbf,
    "          l+=rbf_draw_char(rbf_font, x+l, y, *str++, (i==c)?fontspec1:fontspec2);\n"
    "          ++i;",
    "          {\n"
    "              int adv = 1;\n"
    "              int wl = zh_try_draw(str, x+l, y, (i==c)?fontspec1:fontspec2, &adv);\n"
    "              if (wl >= 0) { l += wl; str += adv; ++i; continue; }\n"
    "          }\n"
    "          l+=rbf_draw_char(rbf_font, x+l, y, *str++, (i==c)?fontspec1:fontspec2);\n"
    "          ++i;")

# ---------- rbf_draw_clipped_string 非对齐分支循环 ----------
ok &= patch(rbf,
    "        // Draw chars from string up to max pixel length\n"
    "        while (*str && l+rbf_char_width(rbf_font, *str)<=maxlen)\n"
    "        {\n"
    "            l+=rbf_draw_char(rbf_font, x+l, y, *str++, fontspec);\n"
    "            i++;\n"
    "        }",
    "        // Draw chars from string up to max pixel length\n"
    "        while (*str)\n"
    "        {\n"
    "            {\n"
    "                int adv = 1;\n"
    "                int wl = zh_try_draw(str, x+l, y, fontspec, &adv);\n"
    "                if (wl >= 0)\n"
    "                {\n"
    "                    if (l + wl > maxlen) break;\n"
    "                    l += wl; str += adv; i++;\n"
    "                    continue;\n"
    "                }\n"
    "            }\n"
    "            if (l + rbf_char_width(rbf_font, *str) > maxlen) break;\n"
    "            l += rbf_draw_char(rbf_font, x+l, y, *str++, fontspec);\n"
    "            i++;\n"
    "        }")

# ---------- rbf_str_width ----------
ok &= patch(rbf,
    "        else\n"
    "        {\n"
    "            l += rbf_char_width(rbf_font, *str);\n"
    "        }\n"
    "        str++;",
    "        else\n"
    "        {\n"
    "            if ((unsigned char) *str & 0x80)\n"
    "            {\n"
    "                int adv = 1;\n"
    "                int cp = zh_utf8_decode(str, &adv);\n"
    "                if (cp >= 0 && zh_lookup(cp) >= 0)\n"
    "                {\n"
    "                    l += ZH_GLYPH_W;\n"
    "                    str += adv;\n"
    "                    continue;\n"
    "                }\n"
    "            }\n"
    "            l += rbf_char_width(rbf_font, *str);\n"
    "        }\n"
    "        str++;")

# ---------- menu.c ----------
ok &= patch(menu,
    '#include "menu.h"',
    '#include "menu.h"\n#include "i18n_zh.h"')
ok &= patch(menu,
    'snprintf(name, sizeof(name), "%s", entry->name);',
    'snprintf(name, sizeof(name), "%s", ml_tr(entry->name));')
ok &= patch(menu,
    'bmp_printf(FONT(FONT_CANON, fg, NO_BG_ERASE), 5, y, "%s", menu->name);',
    'bmp_printf(FONT(FONT_CANON, fg, NO_BG_ERASE), 5, y, "%s", ml_tr(menu->name));')
ok &= patch(menu,
    'bmp_printf(FONT(FONT_CANON, COLOR_WHITE, NO_BG_ERASE),  bx + 15,  by+2, "%s", submenu->name);',
    'bmp_printf(FONT(FONT_CANON, COLOR_WHITE, NO_BG_ERASE),  bx + 15,  by+2, "%s", ml_tr(submenu->name));')

# ---------- Makefile.src（注意：要加进 ML_SRC_OBJS 核心清单，不是 installer 清单）----------
ok &= patch(mk,
    "\tmenu.o \\",
    "\tmenu.o \\\n\tzh_font.o \\\n\ti18n_zh.o \\")

print("全部成功" if ok else "有失败项")
sys.exit(0 if ok else 1)
