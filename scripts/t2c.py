# -*- coding: utf-8 -*-
"""TSV 翻译表 → i18n_zh.c。TSV 中的 C 转义序列(\\n \\" \\\\)原样进入 C 字面量（语义一致）。
用法: python3 t2c.py <输入1.tsv> <输入2.tsv> ... <all_strings.tsv> <输出.c>
"""
import sys

inputs, alltsv, outc = sys.argv[1:-2], sys.argv[-2], sys.argv[-1]
pairs = {}
for f in inputs:
    for line in open(f, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line:
            continue
        en, _, zh = line.partition('\t')
        if zh:
            pairs[en] = zh

allset = set()
for line in open(alltsv, encoding='utf-8'):
    allset.add(line.rstrip('\n').partition('\t')[0])

unknown = [k for k in pairs if k not in allset]
uncovered = [k for k in allset if k not in pairs]
print('翻译 %d 条 / 提取 %d 条；不在提取集的键 %d 个：%s' %
      (len(pairs), len(allset), len(unknown), unknown[:8]))
print('未翻译（保留英文）%d 条' % len(uncovered))

def key_sort(en):
    return (0, len(en), en) if '\\n' in en else (1, len(en), en)

with open(outc, 'w', encoding='utf-8', newline='\n') as f:
    f.write('/* [汉化] 菜单文案翻译表——由 t2c.py 从 TSV 生成，勿手改 */\n')
    f.write('#include <string.h>\n#include "i18n_zh.h"\n\n')
    f.write('typedef struct { const char* en; const char* zh; } ml_tr_entry_t;\n\n')
    f.write('static const ml_tr_entry_t ml_tr_table[] = {\n')
    for en in sorted(pairs, key=key_sort):
        f.write('    { "%s", "%s" },\n' % (en, pairs[en]))
    f.write('};\n\n')
    f.write('''const char* ml_tr(const char* en)
{
    if (!en || !*en) return en;
    for (unsigned int i = 0; i < sizeof(ml_tr_table) / sizeof(ml_tr_table[0]); i++)
    {
        if (strcmp(ml_tr_table[i].en, en) == 0)
            return ml_tr_table[i].zh;
    }
    return en;
}
''')
print('已生成', outc)
