# FDE 开放联盟（FDE Learning Hub）

按目标重组的 FDE（Forward Deployed Engineer，前沿部署工程师）领域自适应学习站点。

网站免费访问，无需注册账号；学习进度只保存在读者本机浏览器，不上传任何数据。

静态站点，无后端依赖，可直接以 GitHub Pages 托管（仓库根目录即站点根）。

## 内容来源（6 个来源，版权归原作者所有，授权状态各不相同）

| 来源 | 说明 |
|---|---|
| [FDE-Wiki](https://github.com/zhyese/fde-wiki) | 2026-06 生成的 32 万字 FDE 行业全景调研（93 篇） |
| [范冰《FDE 前沿部署工程师入门指南》](https://github.com/xdash/FDE-the-Guidance-Book-of-Forward-Deployed-Engineer) | 20 万字+ 入门书（作者声明：免费阅读与非商业分享，转载注明出处） |
| [FDE-Handbook](https://github.com/goday-org/FDE-Handbook) | 11 章工程手册中文版（正文 CC BY-NC-SA 4.0） |
| [Awesome-FDE-Roadmap](https://github.com/pierpaolo28/Awesome-FDE-Roadmap) | FDE 学习路线图（英文） |
| [Awesome-FDE](https://github.com/yzyunzhang/Awesome-FDE) | FDE 资源/公司/招聘清单（英文） |
| [OpenFDE](https://github.com/OpenFDEAI/OpenFDE) | 工具地图与实战蓝皮书两份文档 |

这些来源不宜统称为"开源项目"：各自授权条款不同（MIT、CC 系列、作者自定义声明、
尚未核实等），并非都允许自由再发布或商用。逐来源的授权核对见
`source/THIRD_PARTY_NOTICES.md`（稍后同步进本仓库）与站内 `about.html`；
**不要假设所有第三方文章均可商用**，商用前请按对应来源的条款确认或联系作者。

本站为**学习用途的聚合与重组**：全部正文保留原文，仅做排版适配与站内链接改写；
知识图谱与学习路径为编辑性重组（标注深度层级 L1-L4 与前置依赖），未改动原文观点。

## 功能

- **目标导向学习路径**：5 种目标（转行求职 / 在职提升 / 团队管理 / 售前顾问 / 业务决策者）× 4 阶段深度（认知 → 方法 → 实战 → 精通），每项带深度徽章、来源徽章与预计时长
- **交互式知识图谱**：45 个核心概念 × 51 条依赖/关联关系，力导向布局，点击节点直达内容
- **统一内容库**：多来源全文，全站全文搜索（1900+ 段落索引，⌘K / / 唤起）
- **学习进度**：打卡与已读标记保存在读者本机浏览器（localStorage），不上传任何数据

## 本地预览

```bash
python3 -m http.server 8000
# 打开 http://localhost:8000
```

## 说明

- 本仓库将逐步包含 `source/` 目录：第一方源码（构建脚本、前端代码等）以
  [LICENSE](LICENSE) 索引的 MIT 文本为准；构建站点仍需自行从上游来源取得
  有授权的内容素材
- 根目录 [LICENSE](LICENSE) 是授权索引：原创代码 MIT，第三方全文与素材
  以 `source/THIRD_PARTY_NOTICES.md`、站内 `about.html` 及原作者授权为准
- 站点内所有出站链接与内容出处均已逐篇核对，如版权方要求下架相关内容，请联系仓库所有者
