# -*- coding: utf-8 -*-
"""修复 7D.203（其构建递归依赖 7D_MASTER.203 主处理器组件）：
1. 7D_MASTER 精简对象清单有 gdb.o 却漏了 patch.o —— gdb.c 调用的
   unpatch_memory/patch_instruction 在 patch.c 里，补链。
2. master_boot.c 调用的 clean_d_cache() 上游别名缺失 —— 桥接到
   arm-mcr.h 的 _clean_d_cache() 内联实现。
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
ok &= patch("/home/wsz/ml-src/platform/7D_MASTER.203/Makefile.setup.default",
    "\tgdb.o \\\n",
    "\tgdb.o \\\n\tpatch.o \\\n")

ok &= patch("/home/wsz/ml-src/platform/7D_MASTER.203/master_boot.c",
    '#include "cache_hacks.h"',
    '#include "cache_hacks.h"\n'
    '#include "arm-mcr.h"\n'
    '/* [汉化项目] 上游别名缺失：clean_d_cache 桥接到内联实现 */\n'
    'static inline void clean_d_cache(void) { _clean_d_cache(); }')

import sys
sys.exit(0 if ok else 1)
