# FDE 学习中心（FDE Learning Hub）

按目标重组的 FDE（Forward Deployed Engineer，前沿部署工程师）领域自适应学习站点。

静态站点，无后端依赖，可直接以 GitHub Pages 托管（仓库根目录即站点根）。

## 内容来源（5 个开源项目，版权归原作者所有）

| 来源 | 说明 |
|---|---|
| [FDE-Wiki](https://github.com/zhyese/fde-wiki) | 2026-06 生成的 32 万字 FDE 行业全景调研（93 篇） |
| [范冰《FDE 前沿部署工程师入门指南》](https://github.com/xdash/FDE-the-Guidance-Book-of-Forward-Deployed-Engineer) | 20 万字+ 开源入门书（免费阅读与非商业分享，转载注明出处） |
| [FDE-Handbook](https://github.com/goday-org/FDE-Handbook) | 11 章工程手册中文版（CC BY-NC-SA 4.0） |
| [Awesome-FDE-Roadmap](https://github.com/pierpaolo28/Awesome-FDE-Roadmap) | FDE 学习路线图（英文） |
| [Awesome-FDE](https://github.com/yzyunzhang/Awesome-FDE) | FDE 资源/公司/招聘清单（英文） |

本站为**学习用途的聚合与重组**：全部正文保留原文，仅做排版适配与站内链接改写；
知识图谱与学习路径为编辑性重组（标注深度层级 L1-L4 与前置依赖），未改动原文观点。
详细的来源与版权说明见站内 `about.html`。

## 功能

- **目标导向学习路径**：5 种目标（转行求职 / 在职提升 / 团队管理 / 售前顾问 / 业务决策者）× 4 阶段深度（认知 → 方法 → 实战 → 精通），每项带深度徽章、来源徽章与预计时长
- **交互式知识图谱**：45 个核心概念 × 51 条依赖/关联关系，力导向布局，点击节点直达内容
- **统一内容库**：5 来源 119 篇，全站全文搜索（1900+ 段落索引，⌘K / / 唤起）
- **学习进度**：打卡与已读标记保存在读者本机浏览器（localStorage），不上传任何数据

## 本地预览

```bash
python3 -m http.server 8000
# 打开 http://localhost:8000
```

## 说明

- 本仓库仅包含构建产物（静态 HTML/CSS/JS），构建脚本与原始 Markdown 源未包含在内
- 站点内所有出站链接与内容出处均已逐篇核对，如版权方要求下架相关内容，请联系仓库所有者
