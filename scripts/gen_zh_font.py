# -*- coding: utf-8 -*-
"""生成 ML 内置中文字库 zh_font.c/.h —— 四档字号（12/23/28/32px，1bpp，LSB-first）。
用法: python3 gen_zh_font.py <chars.txt> <输出目录> [预览.png]
"""
import sys, os
from PIL import Image, ImageDraw, ImageFont

TIERS = [(12, 12), (23, 23), (28, 28), (32, 32)]   # (cell_h, cell_w)
TTC = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

def pick_face(size):
    for idx in (2, 3, 4, 0, 1):
        try:
            f = ImageFont.truetype(TTC, size, index=idx)
        except Exception:
            continue
        img = Image.new("1", (size * 2, size * 2), 0)
        d = ImageDraw.Draw(img)
        try:
            d.text((2, 2), "永", font=f, fill=1)
        except Exception:
            continue
        if sum(img.getdata()) > 8:
            return f, idx
    raise SystemExit("找不到可用 CJK face")

def render(ch, font, cw, chh):
    img = Image.new("1", (cw * 3, chh * 3), 0)
    d = ImageDraw.Draw(img)
    d.text((cw, chh), ch, font=font, fill=1)
    bbox = img.getbbox()
    if not bbox:
        return bytes(((cw + 7) // 8) * chh), 0
    x0, y0, x1, y1 = bbox
    w, h = x1 - x0, y1 - y0
    ox, oy = (cw - w) // 2, (chh - h) // 2
    grid = bytearray(cw * chh)
    px = img.load()
    for yy in range(h):
        for xx in range(w):
            if px[x0 + xx, y0 + yy]:
                tx, ty = ox + xx, oy + yy
                if 0 <= tx < cw and 0 <= ty < chh:
                    grid[ty * cw + tx] = 1
    stride = (cw + 7) // 8
    glyph = bytearray(stride * chh)
    for yy in range(chh):
        for xx in range(cw):
            if grid[yy * cw + xx]:
                glyph[yy * stride + xx // 8] |= (1 << (xx % 8))
    return bytes(glyph), sum(grid)

def main(chars_path, out_dir, preview_png=None):
    chars = sorted(set(open(chars_path, encoding='utf-8').read()) - {'\n', '\r', ' '})
    cps = [ord(c) for c in chars]
    assert cps == sorted(cps)
    fonts = {}
    for th, tw in TIERS:
        fonts[th], idx = pick_face(max(6, th - 2))
    sys.stderr.write("face index=%d, %d 字, %d 档\n" % (idx, len(chars), len(TIERS)))

    tiers_data = []
    for ti, (th, tw) in enumerate(TIERS):
        stride = (tw + 7) // 8
        per = stride * th
        blobs = []
        zero = 0
        for c in chars:
            g, ink = render(c, fonts[th], tw, th)
            if ink == 0:
                zero += 1
            blobs.append(g)
        assert all(len(b) == per for b in blobs)
        if zero:
            sys.stderr.write("警告: %d 档有 %d 字无墨迹\n" % (th, zero))
        tiers_data.append((tw, th, per, blobs))

    with open(os.path.join(out_dir, "zh_font.h"), "w", encoding='utf-8', newline='\n') as f:
        f.write("#ifndef ZH_FONT_H\n#define ZH_FONT_H\n")
        f.write("/* 自动生成：内置中文点阵（四档 1bpp，LSB-first），勿手改 */\n")
        f.write("#define ZH_TIERS %d\n" % len(TIERS))
        f.write("extern const int zh_char_count;\n")
        f.write("extern const unsigned short zh_codepoints[];\n")
        f.write("extern const unsigned char zh_tier_w[ZH_TIERS];\n")
        f.write("extern const unsigned char zh_tier_h[ZH_TIERS];\n")
        f.write("extern const unsigned short zh_tier_bytes[ZH_TIERS];\n")
        f.write("extern const unsigned char* const zh_tier_glyphs[ZH_TIERS];\n")
        f.write("#endif\n")

    with open(os.path.join(out_dir, "zh_font.c"), "w", encoding='utf-8', newline='\n') as f:
        f.write("/* 自动生成：内置中文点阵（Noto Sans CJK SC, 四档 12/23/28/32px, 1bpp, LSB-first）*/\n")
        f.write('#include "zh_font.h"\n\n')
        f.write("const int zh_char_count = %d;\n" % len(cps))
        f.write("const unsigned short zh_codepoints[] = {\n")
        for i in range(0, len(cps), 12):
            f.write("    " + ", ".join("0x%04x" % c for c in cps[i:i + 12]) + ",\n")
        f.write("};\n")
        f.write("const unsigned char zh_tier_w[ZH_TIERS] = { %s };\n"
                % ", ".join(str(t[0]) for t in TIERS))
        f.write("const unsigned char zh_tier_h[ZH_TIERS] = { %s };\n"
                % ", ".join(str(t[1]) for t in TIERS))
        f.write("const unsigned short zh_tier_bytes[ZH_TIERS] = { %s };\n"
                % ", ".join(str(t[2]) for t in tiers_data))
        names = []
        for ti, (tw, th, per, blobs) in enumerate(tiers_data):
            name = "zh_glyphs_%d" % ti
            names.append(name)
            f.write("static const unsigned char %s[] = {\n" % name)
            for ci, (c, g) in enumerate(zip(chars, blobs)):
                if ci % 4 == 0:
                    f.write("    /* %s */\n" % c)
                f.write("    " + ",".join(str(b) for b in g) + ",\n")
            f.write("};\n")
        f.write("const unsigned char* const zh_tier_glyphs[ZH_TIERS] = { %s };\n"
                % ", ".join(names))
    sys.stderr.write("已生成 zh_font.c/.h -> %s\n" % out_dir)

    if preview_png:
        from PIL import Image as I
        tw, th, per, blobs = tiers_data[3]
        scale = 2
        pv = I.new("L", (tw * scale * len(chars), th * scale), 255)
        for gi, g in enumerate(blobs):
            stride = (tw + 7) // 8
            for yy in range(th):
                for xx in range(tw):
                    if (g[yy * stride + xx // 8] >> (xx % 8)) & 1:
                        for sy in range(scale):
                            for sx in range(scale):
                                pv.putpixel((gi * tw * scale + xx * scale + sx,
                                             yy * scale + sy), 0)
        pv.save(preview_png)
        sys.stderr.write("预览图: %s\n" % preview_png)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
