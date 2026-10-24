# -*- coding: utf-8 -*-
"""阶段2补丁：rbf_str_clipped_width / rbf_strlen_clipped 支持 UTF-8 中文宽度。幂等。"""
P = "/home/wsz/ml-src/src/rbf_font.c"
s = open(P, encoding="utf-8").read().replace("\r\n", "\n")

OLD = """    while (*str && l+rbf_char_width(rbf_font, *str)<=maxlen)
        l+=rbf_char_width(rbf_font, *str++);"""
NEW = """    while (*str)
    {
        if ((unsigned char) *str & 0x80)
        {
            int adv = 1;
            int cp = zh_utf8_decode(str, &adv);
            if (cp >= 0 && zh_lookup(cp) >= 0)
            {
                if (l + ZH_GLYPH_W > maxlen) break;
                l += ZH_GLYPH_W;
                str += adv;
                continue;
            }
        }
        if (l + rbf_char_width(rbf_font, *str) > maxlen) break;
        l += rbf_char_width(rbf_font, *str++);
    }"""

if NEW in s:
    print("[跳过] 已打过")
elif OLD not in s:
    print("[失败] 找不到裁剪循环锚点")
    raise SystemExit(1)
else:
    n = s.count(OLD)
    assert n == 2, "预期出现2次，实际 %d 次" % n
    s = s.replace(OLD, NEW)
    open(P, "w", encoding="utf-8", newline="\n").write(s)
    print("[OK] 两处裁剪循环已替换")
