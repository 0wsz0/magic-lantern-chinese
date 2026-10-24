# Magic Lantern 中文汉化 · 全型号

> Magic Lantern (魔灯) 简体中文全量汉化——源码级实现，非二进制补丁。
> 覆盖 ML unified 2025-06 源码树支持的**全部 18 个构建目标**；真机验证于 Canon EOS 60D。

[English](#english) 见下方。

## 支持的型号

**编译产出 10 个型号**（`releases/autoexec-zh-<型号>.bin`，均已内置全部翻译与字库）：

| 相机 | 构建目标（固件） | 真机验证 |
|---|---|---|
| **60D** | 60D.111 | ✅ 已验证 |
| 5D Mark III | 5D3.113 / 5D3.123（按你固件选） | ⬜ 待社区反馈 |
| 6D | 6D.116 | ⬜ |
| 700D | 700D.115 | ⬜ |
| 650D | 650D.104 | ⬜ |
| 600D | 600D.102 | ⬜ |
| 100D | 100D.101 | ⬜ |
| 1100D | 1100D.105 | ⬜ |
| EOS M | EOSM.202 | ⬜ |

**未能编译的 7 个目标**（5D2 / 7D / 7D_MASTER / 50D / 70D / 500D / 550D）：上游源码树对这批老机型**本身就不维护**（见 `platform/README-unmaintained.txt`，编译在 `raw.c` 的 `BLACK_LEVEL`、`cfn-generic.h` 的 `PROP_HTP/PROP_MLU` 等机型常量缺失处失败，与汉化无关）。要支持它们需要先把端口修活——欢迎社区接手，修活后跑 `scripts/build_all.sh` 即可直接产出中文版。

**除 60D 外均为编译通过但未经真机验证**的社区构建——汉化层在共享源码里，理论上面板一致，但请各机型用户自担风险、反馈效果。

## 这是什么

给佳能相机的 Magic Lantern 提供**完整的简体中文界面**：

- **1550+ 条翻译**：全部页签、菜单条目、两行帮助文本、选项值（开/关/佳能/中央…）、动态提示
- **内置四档中文点阵字库**（12/23/28/32 px，847 字符，Noto Sans CJK SC 渲染），中英文同格显示、可混排
- **UTF-8 渲染管线**：魔灯原版按单字节绘制，本项目在其 RBF 字体引擎中加入 UTF-8 解码与码点查找，未命中自动回退英文
- 不依赖相机语言设置、不依赖卡上字体文件；纯 `autoexec.bin` 替换即用

## 使用方法（任意型号）

1. 从 [builds.magiclantern.fm](https://builds.magiclantern.fm) 下载**你相机型号的官方 ML 包**（选 2025-06 的 dev 构建，与本项目源码同期），按官方流程安装（相机内格式化卡 → 拷入 `ML-SETUP.FIR`+`ML/` → 固件升级开启动标志）
2. 装好后，用本仓库 `releases/` 里对应型号的 `autoexec-zh-<型号>.bin` **替换卡根目录的 `autoexec.bin`**，开机即中文
3. 升级/回滚都只须替换 `autoexec.bin`（换回官方 zip 里那个即回英文）

> 免责声明：Magic Lantern 与本项目均"可能损坏你的相机"，自担风险。仅供个人研究学习。

## 构建方法（WSL / Linux）

```bash
sudo apt install gcc-arm-none-eabi python3-pil fonts-noto-cjk
git clone --depth 1 https://github.com/dannephoto/magic-lantern_jip_hop.git ~/ml-src
bash scripts/build.sh              # 单机型（60D）：提取→翻译→字库→补丁→编译
bash scripts/build_all.sh          # 全部 18 个机型批量编译
# 产物: ~/ml-src/platform/<型号>/autoexec.bin 或 releases/autoexec-zh-*.bin
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
