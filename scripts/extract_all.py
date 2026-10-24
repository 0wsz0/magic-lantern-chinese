# -*- coding: utf-8 -*-
"""从 ML 源码全量提取可翻译字符串：.name 与 .help 字段。
输出 TSV：en<TAB>zh（zh 留空待翻）。\\n 以字面 \n 序列保留。
用法: python3 extract_all.py <ml-src根目录> <输出tsv> [--with-modules-help]
"""
import re, sys, os, glob

root = sys.argv[1]
out = sys.argv[2]
with_mod_help = "--with-modules-help" in sys.argv

STR = r'"(?:[^"\\]|\\.)*"'
name_re = re.compile(r'\.name\s*=\s*(' + STR + r')')
help_re = re.compile(r'\.help\s*=\s*((?:' + STR + r'\s*)+)')
help2_re = re.compile(r'\.help2\s*=\s*((?:' + STR + r'\s*)+)')
choices_re = re.compile(r'\.choices[^\n]{0,300}')
dynhelp_re = re.compile(r'MENU_SET_(?:HELP|WARNING)\(\s*(?:MENU_WARN_[A-Z_]+\s*,\s*)?(' + STR + r')')

def collect(files):
    names, helps, extra = set(), set(), set()
    for f in files:
        try:
            src = open(f, encoding='utf-8', errors='replace').read()
        except Exception:
            continue
        for m in name_re.finditer(src):
            s = m.group(1)[1:-1]
            if s and '%' not in s and len(s) <= 48:
                names.add(s)
        for m in help_re.finditer(src):
            # 拼接相邻字面量
            parts = re.findall(STR, m.group(1))
            s = ''.join(p[1:-1] for p in parts)
            if s and len(s) <= 400 and s.count('\\n') <= 3:
                helps.add(s)
        for m in help2_re.finditer(src):
            parts = re.findall(STR, m.group(1))
            s = ''.join(p[1:-1] for p in parts)
            if s and len(s) <= 400 and s.count('\\n') <= 3:
                helps.add(s)
        for m in choices_re.finditer(src):
            for p in re.findall(STR, m.group(0)):
                s = p[1:-1]
                if s and '%' not in s and len(s) <= 28:
                    extra.add(s)
        for m in dynhelp_re.finditer(src):
            s = m.group(1)[1:-1]
            if s and '%' not in s and len(s) <= 300:
                helps.add(s)
    return names, helps, extra

src_files = [f for f in glob.glob(os.path.join(root, 'src', '*.c'))
             if not f.endswith(('zebra-5dc.c', 'audio-lapis.c'))]
mod_files = glob.glob(os.path.join(root, 'modules', '*', '*.c'))

n1, h1, e1 = collect(src_files)
n2, h2, e2 = collect(mod_files)
names = n1 | n2
helps = h1 | (h2 if with_mod_help else set())
extras = e1 | e2

def key(s):
    return (0, s.lower()) if s.isascii() else (1, s)

rows = [(s, '') for s in sorted(names | extras, key=key)]
rows += [(s, '') for s in sorted(helps, key=key)]
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    for en, zh in rows:
        f.write(en.replace('\t', ' ') + '\t' + zh + '\n')
print('names: %d (src %d + modules %d), helps: %d, 合计 %d 行 -> %s'
      % (len(names), len(n1), len(n2), len(helps), len(rows), out))
