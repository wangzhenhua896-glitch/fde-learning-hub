# 第三方素材授权清单（THIRD PARTY NOTICES）

> 本清单面向国内读者，说明 FDE 学习网站聚合内容中**第三方素材**的来源与本地可验证的授权状态。
>
> - 核实范围：仅基于本地仓库可见材料（`fde-wiki/`、`fde-sources/` 及发布仓库 `fde-github-repo/about.html`），核实日期 2026-09-23。
> - 本清单不构成任何权利授予：**第三方文章的版权归各自作者/权利人所有**，本站未将其以 MIT 或其他开源协议再授权，整个网站也不存在"整体 MIT / 整体开放源码"的声明。
> - 本清单只是信息整理，不构成法律意见；如需商用或深度转载，请按各来源标注的条件联系权利人。

## 来源总览

| # | 来源 | 本地路径 | 授权状态（本地可验证部分） |
|---|------|----------|---------------------------|
| 1 | FDE-Wiki 调研报告 | `fde-wiki/`（llms.txt / llms-full.txt） | 本地未核实，见下 |
| 2 | 范冰《FDE 前沿部署工程师入门指南》 | `fde-sources/FDE-the-Guidance-Book-of-Forward-Deployed-Engineer-main/` | 免费阅读 / 非商业分享 |
| 3 | FDE-Handbook | `fde-sources/FDE-Handbook-main/` | 正文 CC BY-NC-SA 4.0 |
| 4 | Awesome-FDE-Roadmap | `fde-sources/Awesome-FDE-Roadmap-main/` | MIT（本地有 LICENSE 文件） |
| 5 | Awesome-FDE | `fde-sources/Awesome-FDE-main/` | README 声称 MIT，本地无 LICENSE 文件 |
| 6 | OpenFDE（工具地图 + 实战蓝皮书） | `fde-sources/OpenFDE/` | 本地未核实，见下 |

## 1. FDE-Wiki 调研报告

- 原仓库：<https://github.com/zhyese/fde-wiki>
- 本地材料：`fde-wiki/llms.txt`（目录）、`fde-wiki/llms-full.txt`（全文，93 篇，约 35 万字）。
- 本地可验证信息：发布仓库 about.html 记载其 2026-06-21 由 zhyese（adewdew）发布，AI 辅助深度调研生成。
- **授权状态：本地未核实。** 本地两份 txt 中均未见许可声明。转载/使用条件以原仓库公示为准，使用前请自行到原仓库确认。

## 2. 范冰《FDE 前沿部署工程师入门指南》

- 原仓库：<https://github.com/xdash/FDE-the-Guidance-Book-of-Forward-Deployed-Engineer> · 官网 <https://fde4.ai>
- 本地材料：`fde-sources/FDE-the-Guidance-Book-of-Forward-Deployed-Engineer-main/`（13 个章节 md，VERSION 1.0.24）。
- 本地可验证信息：原书 README「版权声明」明确——**著作权归作者范冰所有；授权公开，供读者免费阅读与非商业性分享；转载须注明出处与作者；任何商业用途须事先获得作者书面许可。**
- 性质说明：这是作者的**自定义免费分享声明**，不是 MIT 等开源协议；不要将其内容视为开源/公共领域素材。

## 3. FDE-Handbook

- 原仓库：<https://github.com/goday-org/FDE-Handbook>
- 本地材料：`fde-sources/FDE-Handbook-main/`（`book_en/`、`book_zh/` 章节、`compile_pdf.py` 等）。
- 本地可验证信息：原仓库 README「License」节明确分两部分——
  - `compile_pdf.py`（编译脚本）：MIT（本地 `LICENSE` 文件，Copyright 2026 Nicole Li & Antigravity AI）；
  - **正文（`book_en/`、`book_zh/` 各章）：CC BY-NC-SA 4.0**（署名-非商业性使用-相同方式共享）。
- 注意：本地 `LICENSE` 文件虽为 MIT 文本，但按原仓库 README 的说明，MIT 仅覆盖编译脚本，**不覆盖手册正文**。

## 4. Awesome-FDE-Roadmap

- 原仓库：<https://github.com/pierpaolo28/Awesome-FDE-Roadmap>
- 本地材料：`fde-sources/Awesome-FDE-Roadmap-main/`。
- 本地可验证信息：本地 `LICENSE` 文件为 **MIT License，Copyright (c) 2026 Pier Paolo Ippolito**。
- 这是 6 个来源中本地授权材料最完整的一个；再使用时应保留其版权与许可声明。

## 5. Awesome-FDE

- 原仓库：<https://github.com/yzyunzhang/Awesome-FDE>（README 徽章指向 libaice/awesome-fde）
- 本地材料：`fde-sources/Awesome-FDE-main/`（README.md / README_CN.md）。
- 本地可验证信息：README「License」节写有 "[MIT](LICENSE) © awesome-fde contributors"，徽章亦为 License: MIT。
- **注意：本地副本中不存在 LICENSE 文件**，MIT 结论目前仅来自 README 文字；使用前建议到原仓库核对 LICENSE 文件原文，并保留其署名。

## 6. OpenFDE（工具地图 + 实战蓝皮书）

- 原仓库：<https://github.com/OpenFDEAI/OpenFDE> · 社区 open-fde.com
- 本地材料：`fde-sources/OpenFDE/`（《FDE 所需工具地图.md》《FDE 实战蓝皮书.md》两篇）。
- 本地可验证信息：两篇文档正文内**均未附许可声明**。
- **授权状态：本地未核实。** 发布仓库 about.html 称其以 CC BY-SA 4.0 授权，但该说法在本地材料中找不到对应依据，属未经本地证实的转述；使用条件请以原仓库公示为准并自行核实。

## 附：阅读提示

- "可以免费阅读"不等于"可以按 MIT 再发布"。上表中仅 Awesome-FDE-Roadmap 在本地有完整的 MIT 授权文件；Awesome-FDE 为 README 声称；其余来源或为自定义分享声明，或为未核实状态。
- 站内各页面出处与署名说明见发布仓库的 `about.html`（来源与版权页）。
