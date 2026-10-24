# -*- coding: utf-8 -*-
"""修复上游 unmaintained 机型的编译（不动新机型行为）：
1. raw.c: 无 EVF_STATE 的老机型（5D2/500D/550D/50D/7D）没有 BLACK_LEVEL 宏——
   把硬编码黑电平赋值包进 #ifdef，老机型维持"自动检测黑电平"的历史行为。
2. property.h: 70D（DIGIC5，与 5D3/6D 同世代）缺 PROP_HTP/PROP_MLU——
   按 5D3/6D 的同世代值补上（共享代码无条件调用 get_htp/get_mlu，无法守卫）。
   注意：未真机验证，标注待社区确认。
幂等。"""

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

ok = True
ok &= patch("/home/wsz/ml-src/src/raw.c",
    "        raw_info.black_level = BLACK_LEVEL;",
    "#ifdef BLACK_LEVEL\n"
    "        raw_info.black_level = BLACK_LEVEL;\n"
    "#endif")

ok &= patch("/home/wsz/ml-src/src/property.h",
    """#if defined(CONFIG_5D3)
#define PROP_HTP 0x8000004a
#define PROP_MULTIPLE_EXPOSURE 0x0202000c
#define PROP_MLU 0x80000047
#endif""",
    """#if defined(CONFIG_5D3)
#define PROP_HTP 0x8000004a
#define PROP_MULTIPLE_EXPOSURE 0x0202000c
#define PROP_MLU 0x80000047
#endif

#if defined(CONFIG_70D) && !defined(PROP_HTP)  /* [汉化项目] DIGIC5 同 5D3/6D 值，未真机验证 */
#define PROP_HTP 0x8000004a
#define PROP_MLU 0x80000047
#endif""")

import sys
sys.exit(0 if ok else 1)
