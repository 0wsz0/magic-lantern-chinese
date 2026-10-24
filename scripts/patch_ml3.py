# -*- coding: utf-8 -*-
"""M3 补丁：字库四档化（按字体高度选档）+ justified 循环中文支持 + help 文本挂钩。幂等。"""

def patch(path, old, new, count=1):
    old = old.replace("\r\n", "\n")
    new = new.replace("\r\n", "\n")
    s = open(path, encoding="utf-8").read()
    if new in s:
        print("[跳过] %s" % path)
        return True
    if old not in s:
        print("[失败] %s 找不到锚点 %r" % (path, old[:60]))
        return False
    assert s.count(old) == count, "锚点出现 %d 次（预期 %d）" % (s.count(old), count)
    s = s.replace(old, new)
    open(path, "w", encoding="utf-8", newline="\n").write(s)
    print("[OK] %s" % path)
    return True

RBF = "/home/wsz/ml-src/src/rbf_font.c"
MENU = "/home/wsz/ml-src/src/menu.c"
ok = True

# ---------- A. 整体替换 zh 渲染块（include 之后到 macros 之前）----------
NEW_BLOCK = '''/* ===== [汉化] UTF-8 中文渲染（内置点阵字库 zh_font：12/23/28/32 四档）===== */
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

/* 码点二分查找；返回字形下标或 -1 */
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

/* 按当前字体高度选字号档 */
static int FAST zh_pick_tier(int font_h)
{
    if (font_h <= 14) return 0;
    if (font_h <= 25) return 1;
    if (font_h <= 30) return 2;
    return 3;
}

static int FAST zh_tier_width(int font_h)
{
    return zh_tier_w[zh_pick_tier(font_h)];
}

static int FAST zh_draw_glyph(int tier, int idx, int x, int y, int fontspec)
{
    uint8_t * bmp = bmp_vram();
    const unsigned char* g = zh_tier_glyphs[tier] + (uint32_t) idx * zh_tier_bytes[tier];
    int fg = FONT_FG(fontspec);
    int bg = FONT_BG(fontspec);
    int w = zh_tier_w[tier];
    int h = zh_tier_h[tier];
    int stride = zh_tier_bytes[tier] / h;
    for (int yy = 0; yy < h; ++yy)
    {
        if (y + yy <= BMP_H_MINUS || y + yy >= BMP_H_PLUS) break;
        for (int xx = 0; xx < w; ++xx)
            bmp_putpixel_fast(bmp, x + xx, y + yy, (g[yy * stride + xx / 8] & (1 << (xx % 8))) ? fg : bg);
    }
    return w;
}

/* 尝试画 UTF-8 中文；命中返回像素宽且 *adv 为字节数，否则返回 -1 */
static int FAST zh_try_draw(const font* rbf_font, const char* s, int x, int y, int fontspec, int* adv)
{
    *adv = 1;
    int cp = zh_utf8_decode(s, adv);
    if (cp < 0) return -1;
    int idx = zh_lookup(cp);
    if (idx < 0) return -1;
    return zh_draw_glyph(zh_pick_tier(rbf_font->hdr.height), idx, x, y, fontspec);
}

'''
s = open(RBF, encoding="utf-8").read()
if NEW_BLOCK in s:
    print("[跳过] zh 块已是 v3")
else:
    i0 = s.find("/* ===== [汉化]")
    i1 = s.find("/* here some macros")
    assert 0 <= i0 < i1, "找不到 zh 块范围"
    s2 = s[:i0] + NEW_BLOCK + s[i1:]
    open(RBF, "w", encoding="utf-8", newline="\n").write(s2)
    print("[OK] zh 块替换为四档版")

# ---------- B. draw_string_c 循环：加 rbf_font 参数 ----------
ok &= patch(RBF,
    "int wl = zh_try_draw(str, x+l, y, (i==c)?fontspec1:fontspec2, &adv);",
    "int wl = zh_try_draw(rbf_font, str, x+l, y, (i==c)?fontspec1:fontspec2, &adv);")

# ---------- C. clipped 非对齐循环：加 rbf_font 参数 ----------
ok &= patch(RBF,
    "int wl = zh_try_draw(str, x+l, y, fontspec, &adv);",
    "int wl = zh_try_draw(rbf_font, str, x+l, y, fontspec, &adv);")

# ---------- D. rbf_str_width：宽度改为按档 ----------
ok &= patch(RBF,
    "                if (cp >= 0 && zh_lookup(cp) >= 0)\n"
    "                {\n"
    "                    l += ZH_GLYPH_W;\n"
    "                    str += adv;\n"
    "                    continue;\n"
    "                }",
    "                if (cp >= 0 && zh_lookup(cp) >= 0)\n"
    "                {\n"
    "                    l += zh_tier_width(rbf_font->hdr.height);\n"
    "                    str += adv;\n"
    "                    continue;\n"
    "                }")

# ---------- E. 两个裁剪宽度函数：宽度按档（出现 2 次）----------
ok &= patch(RBF,
    "            if (cp >= 0 && zh_lookup(cp) >= 0)\n"
    "            {\n"
    "                if (l + ZH_GLYPH_W > maxlen) break;\n"
    "                l += ZH_GLYPH_W;\n"
    "                str += adv;\n"
    "                continue;\n"
    "            }",
    "            if (cp >= 0 && zh_lookup(cp) >= 0)\n"
    "            {\n"
    "                int zw = zh_tier_width(rbf_font->hdr.height);\n"
    "                if (l + zw > maxlen) break;\n"
    "                l += zw;\n"
    "                str += adv;\n"
    "                continue;\n"
    "            }",
    count=2)

# ---------- F. justified 主循环：加中文分支 ----------
ok &= patch(RBF,
    "        while (*str && l+rbf_char_width(rbf_font, *str)<=maxlen)\n"
    "        {\n"
    "            l += rbf_draw_char(rbf_font, x+l, y, *str, fontspec | (condensed ? FONT_CONDENSED : 0) );\n"
    "            int l0 = l;",
    "        while (*str)\n"
    "        {\n"
    "            {\n"
    "                int adv = 1;\n"
    "                int wl = zh_try_draw(rbf_font, str, x+l, y, fontspec | (condensed ? FONT_CONDENSED : 0), &adv);\n"
    "                if (wl >= 0)\n"
    "                {\n"
    "                    if (l + wl > maxlen) break;\n"
    "                    l += wl; str += adv; i++;\n"
    "                    continue;\n"
    "                }\n"
    "            }\n"
    "            if (l + rbf_char_width(rbf_font, *str) > maxlen) break;\n"
    "            l += rbf_draw_char(rbf_font, x+l, y, *str, fontspec | (condensed ? FONT_CONDENSED : 0) );\n"
    "            int l0 = l;")

# ---------- G. menu.c：帮助文本挂钩 ----------
ok &= patch(MENU,
    "char* help1 = (char*)entry->help;",
    "char* help1 = (char*)ml_tr(entry->help);")
ok &= patch(MENU,
    "help1 = menu_help_get_line(entry->help, SELECTED_INDEX(entry), help1_buf);",
    "help1 = menu_help_get_line(ml_tr(entry->help), SELECTED_INDEX(entry), help1_buf);")
ok &= patch(MENU,
    "help2 = menu_help_get_line(entry->help2, SELECTED_INDEX(entry), help2_buf);",
    "help2 = menu_help_get_line(ml_tr(entry->help2), SELECTED_INDEX(entry), help2_buf);")

import sys
sys.exit(0 if ok else 1)
