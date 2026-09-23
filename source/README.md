# FDE 学习站 — 第一方公开源码

本目录包含 [FDE 学习站](https://fde.wuyou.com.cn/) 的第一方源代码，供社区浏览与参考。

## 包含什么

- 站点构建脚本（`build_hub.py`）
- 测试与验证脚本（`test_site.py`, `test_workbench.mjs`）
- 数据定义（`wb_data.py`, `wb_packs.py`, `yq_data.py`）
- 站点前端资源（`assets/`）
- 离线练习（`labs/kb-assistant/`）
- 依赖声明（`package.json`, `requirements.txt`）

## 不包含什么

**第三方全文内容未随本源码授权。** `fde-wiki/`、`fde-sources/` 等源材料目录不在此处，
构建站点须用户自行从各原仓库获取合法来源，按许可条款使用。

- 构建产物（站点页面、ZIP 包）—— 请运行 `python3 build_hub.py` 自行构建。
- 配置文件与 Agent 指令（`AGENTS.md`、`CLAUDE.md`、`.workbuddy/`）。

## 构建需求

1. Python 3.10+ 与 Node.js 20+
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   npm install
   ```
3. **第三方资料**：站点引用的第三方文章全文（`fde-wiki/`、`fde-sources/` 等）不在本源码目录中，需用户自行从各原仓库取得具有授权的副本，否则构建脚本无法直接成功。
4. 构建站点（需第三方资料就位）：
   ```bash
   python3 build_hub.py
   npm test
   ```

## 许可

本目录中的原创构建脚本、前端代码和虚构练习按 [LICENSE-CODE](LICENSE-CODE)（MIT）授权。
第三方全文、摘录和素材不属于该许可，请根据各原仓库的许可条款使用。
