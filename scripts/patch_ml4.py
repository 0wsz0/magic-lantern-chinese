# -*- coding: utf-8 -*-
"""M4 补丁：选项值翻译（主值 + 选框）+ 底部署名改 made by wsz@Gavin。幂等。"""

def patch(path, old, new):
    old = old.replace("\r\n", "\n")
    new = new.replace("\r\n", "\n")
    s = open(path, encoding="utf-8").read()
    if new in s:
        print("[跳过] %s" % path)
        return True
    if old not in s:
        print("[失败] %s 找不到锚点 %r" % (path, old[:60]))
        return False
    open(path, "w", encoding="utf-8", newline="\n").write(s.replace(old, new, 1))
    print("[OK] %s" % path)
    return True

MENU = "/home/wsz/ml-src/src/menu.c"
ok = True

# 值显示：entry->choices[...] → ml_tr
ok &= patch(MENU,
    'STR_APPEND(value, "%s", entry->choices[SELECTED_INDEX(entry)]);',
    'STR_APPEND(value, "%s", ml_tr(entry->choices[SELECTED_INDEX(entry)]));')

# 选框宽度：按翻译后的串计算像素宽
ok &= patch(MENU,
    "w = MAX(w, font_large.width * strlen(pickbox_string(entry, i)));",
    "w = MAX(w, bmp_string_width(FONT_LARGE, ml_tr(pickbox_string(entry, i))));")

# 选框绘制：翻译
ok &= patch(MENU,
    "bmp_printf(fnt, x0, y, pickbox_string(entry, i));",
    "bmp_printf(fnt, x0, y, \"%s\", ml_tr(pickbox_string(entry, i)));")

# 底部署名
ok &= patch(MENU,
    '"Built on %s by %s.",\n'
    '        build_version,\n'
    '        build_id,\n'
    '        build_date,\n'
    '        build_user);',
    '"made by wsz@Gavin.",\n'
    '        build_version,\n'
    '        build_id);')

import sys
sys.exit(0 if ok else 1)
