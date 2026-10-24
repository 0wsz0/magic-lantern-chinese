# Magic Lantern 中文汉化 · EOS 60D

> Magic Lantern (魔灯) 简体中文全量汉化——源码级实现，非二进制补丁。
> Canon EOS 60D (固件 1.1.1) · ML unified 2025-06 源码树

[English](#english) 见下方。

## 这是什么

给佳能 EOS 60D 的 Magic Lantern 提供**完整的简体中文界面**：

- **1550 条翻译**：全部页签、菜单条目、两行帮助文本、选项值（开/关/佳能/中央…）、动态提示
- **内置四档中文点阵字库**（12/23/28/32 px，773+ 字符，Noto Sans CJK SC 渲染），中英文同格显示、可混排
- **UTF-8 渲染管线**：魔灯原版按单字节绘制，本项目在其 RBF 字体引擎中加入 UTF-8 解码与码点查找，未命中自动回退英文
- 不依赖相机语言设置、不依赖卡上字体文件；纯 `autoexec.bin` 替换即用

## 使用方法

1. 按魔灯官方流程安装（对应固件 1.1.1）：`releases/autoexec-zh-60d-m4.bin` 改名为 `autoexec.bin`，与 `ML-SETUP.FIR`、`ML/` 目录一起放到 FAT32 卡根目录，相机内先格式化存储卡，再执行"固件升级"开启启动标志
2. 之后升级/回滚只须替换卡上 `autoexec.bin`，无需重跑安装
3. 回滚官方英文版：换回官方 zip 里的 `autoexec.bin` 即可

> 免责声明：Magic Lantern 与本项目均"可能损坏你的相机"，自担风险。仅供个人研究学习。

## 构建方法（WSL / Linux）

```bash
sudo apt install gcc-arm-none-eabi python3-pil fonts-noto-cjk
git clone --depth 1 https://github.com/dannephoto/magic-lantern_jip_hop.git ~/ml-src
bash scripts/build.sh          # 提取→合并翻译→生成字库→打补丁→编译
# 产物: ~/ml-src/platform/60D.111/autoexec.bin
```

`build.sh` 内部流程（每步都是可独立重跑的幂等脚本）：

| 脚本 | 作用 |
|---|---|
| `extract_all.py` | 从 ML 源码提取 `.name` `.help` `.help2` `.choices` 与 `MENU_SET_HELP/WARNING` 常量串 |
| `t2c.py` | 合并 `translations/*.tsv` 生成 `src/i18n_zh.c`（`ml_tr()` 查表，未命中返回原文） |
| `gen_chars.py` + `gen_zh_font.py` | 由译文提取字符集，用 PIL + Noto Sans CJK 烘 4 档 1bpp 点阵，生成 `zh_font.c/.h` |
| `patch_ml*.py` | 对 `rbf_font.c`（UTF-8 解码、四档选档、5 个绘制/宽度循环）与 `menu.c`（条目名/帮助/页签名/选项值挂钩）打幂等补丁 |
| Makefile 兼容 | GCC 14 构建需 `-fcommon` 与若干 `-Wno-error`（见 `build.sh`） |

## 翻译

- 词条：`translations/*.tsv`（tab 分隔：英文原文<TAB>中文）。英文键必须与源码字符串逐字节一致（含空格与 `\n`），改翻译后重跑 `build.sh` 即可
- 保留英文的部分：寄存器名（`reg_83dc`）、纯数字/单位选项（`0 dB`、`1/2...1/125`）、运行时拼出的含 `%` 动态文本
- 术语对照参考社区惯例（峰值对焦 / 斑马纹 / 假色 / 魔放大镜 / 曝光越界 / 反光镜预升 …）

## 许可

- 本项目以 **GPL-2.0** 发布（与 Magic Lantern 上游一致），见 `LICENSE`
- 字形由 [Noto Sans CJK SC](https://github.com/notofonts/noto-cjk) 渲染（SIL OFL 1.1）
- 上游：[Magic Lantern](https://magiclantern.fm)（GPL-2.0）· 源码树 [dannephoto/magic-lantern_jip_hop](https://github.com/dannephoto/magic-lantern_jip_hop)
- 感谢 Magic Lantern 团队十余年的开源工作

## English

Full Simplified Chinese localization for Magic Lantern on Canon EOS 60D, implemented at source level: a 1,550-entry translation table, a built-in 4-tier (12/23/28/32 px) bitmap CJK font rendered from Noto Sans CJK SC, and a UTF-8 decode layer added to ML's RBF font engine. Build pipeline: extract strings from ML source → merge TSV translations → generate font → apply idempotent patches → cross-compile with `gcc-arm-none-eabi`. GPL-2.0, same as upstream. See 构建方法 above for the build steps and 使用方法 for installation.

made by wsz@Gavin
