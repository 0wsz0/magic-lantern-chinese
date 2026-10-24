# -*- coding: utf-8 -*-
"""把 M2 已有翻译合并进 strings_all.tsv，生成待翻清单 strings_todo.tsv。"""
import re

src = open('/mnt/d/stocks/eos60d/_build/mlzh/i18n_zh.c', encoding='utf-8').read()
pairs = re.findall(r'\{\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"\s*\}', src)
have = {}
for en, zh in pairs:
    if zh:
        have[en] = zh

todo, done = [], 0
lines_out = []
for line in open('/mnt/d/stocks/eos60d/_build/mlzh/strings_all.tsv', encoding='utf-8'):
    en = line.rstrip('\n').split('\t')[0]
    if en in have:
        lines_out.append(en + '\t' + have[en])
        done += 1
    else:
        lines_out.append(en + '\t')
        todo.append(en)

with open('/mnt/d/stocks/eos60d/_build/mlzh/strings_merged.tsv', 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines_out) + '\n')
with open('/mnt/d/stocks/eos60d/_build/mlzh/strings_todo.tsv', 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(todo) + '\n')
print('已有翻译 %d 条，待翻 %d 条' % (done, len(todo)))
