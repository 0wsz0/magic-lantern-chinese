# -*- coding: utf-8 -*-
"""7D_MASTER 修正：不链完整 patch.c（master 精简运行时无 stdio，会被拖垮），
改为在 master_boot.c 提供 gdb.c 所需的两个最小桩——主核断点补丁本就不支持，
桩返回失败即正确语义。幂等（并撤销此前加入清单的 patch.o）。"""

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
# 撤销 patch.o（若在）
mk = "/home/wsz/ml-src/platform/7D_MASTER.203/Makefile.setup.default"
s = open(mk, encoding="utf-8").read()
if "\tpatch.o \\\n" in s:
    open(mk, "w", encoding="utf-8", newline="\n").write(s.replace("\tgdb.o \\\n\tpatch.o \\\n", "\tgdb.o \\\n", 1))
    print("[OK] 撤销 patch.o %s" % mk)
else:
    print("[跳过] patch.o 不在清单")

# master_boot.c 补桩（挂在 clean_d_cache 桥接之后）
ok &= patch("/home/wsz/ml-src/platform/7D_MASTER.203/master_boot.c",
    "static inline void clean_d_cache(void) { _clean_d_cache(); }",
    "static inline void clean_d_cache(void) { _clean_d_cache(); }\n\n"
    "/* [汉化项目] master 精简环境不含 patch.c（无 stdio）。\n"
    " * gdb.c 引用的两个补丁函数在此提供最小桩：主核不支持断点补丁，返回失败。 */\n"
    "int unpatch_memory(uintptr_t _addr) { (void) _addr; return 0; }\n"
    "int patch_instruction(uintptr_t addr, uint32_t old_value, uint32_t new_value, const char * description)\n"
    "{ (void) addr; (void) old_value; (void) new_value; (void) description; return 0; }")

import sys
sys.exit(0 if ok else 1)
