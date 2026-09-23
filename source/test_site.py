#!/usr/bin/env python3
"""Check a completed fde-hub-site build. Run: python3 test_site.py [site_dir]."""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

DEFAULT_SITE = Path(__file__).resolve().parent / "fde-hub-site"
KEY_PAGES = (
    "index.html", "learn.html", "orientation.html", "paths.html", "workbench.html", "profile.html", "library.html",
    "about.html", "path-career.html", "path-engineer.html",
    "path-manager.html", "path-presales.html", "path-exec.html",
)
LOCAL_EXTENSIONS = {".html", ".css", ".js"}
PATH_PAGES = (
    "path-career.html", "path-engineer.html", "path-manager.html",
    "path-presales.html", "path-exec.html",
)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.main_links = []
        self.toplists = []
        self._toplist_depths = []
        self._ul_depth = 0
        self._in_main = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "main":
            self._in_main = True
        for attr in ("href", "src"):
            if values.get(attr):
                self.links.append(values[attr])
        if tag == "a" and self._in_main and values.get("href"):
            self.main_links.append(values["href"])
        if tag == "ul":
            self._ul_depth += 1
            classes = set(values.get("class", "").split())
            if "toplist" in classes or "main-nav" in classes:
                self.toplists.append([])
                self._toplist_depths.append((self._ul_depth, len(self.toplists) - 1))
        elif tag == "a" and self._toplist_depths:
            self.toplists[self._toplist_depths[-1][1]].append(values.get("href", ""))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == "main":
            self._in_main = False
        if tag == "ul":
            if self._toplist_depths and self._toplist_depths[-1][0] == self._ul_depth:
                self._toplist_depths.pop()
            self._ul_depth = max(0, self._ul_depth - 1)


def local_target(site, source, raw):
    raw = raw.strip()
    if not raw or raw.startswith(("#", "//")):
        return None
    url = urlsplit(raw)
    if url.scheme or url.netloc:
        return None
    target = unquote(url.path)
    if not target:
        return None
    candidate = (site / target.lstrip("/")) if target.startswith("/") else (source.parent / target)
    if candidate.suffix.lower() not in LOCAL_EXTENSIONS:
        return None
    return candidate.resolve()


def main():
    site = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else DEFAULT_SITE.resolve()
    if len(sys.argv) > 2:
        raise SystemExit("用法：python3 test_site.py [site_dir]")
    problems = []
    pages = sorted(site.rglob("*.html")) if site.is_dir() else []
    if not pages:
        raise SystemExit(f"找不到构建后的 HTML 页面：{site}")

    for name in KEY_PAGES:
        if not (site / name).is_file():
            problems.append(f"关键页面缺失：{name}")

    home = site / "index.html"
    if home.is_file() and re.search(r"135\s*篇", home.read_text(encoding="utf-8")):
        problems.append("首页仍含过时的“135 篇”硬编码")

    missing_nav = []
    oversized_nav = []
    misplaced_nav = []
    for source in pages:
        parser = PageParser()
        parser.feed(source.read_text(encoding="utf-8"))
        for raw in parser.links:
            target = local_target(site, source, raw)
            if target is None:
                continue
            if not target.is_relative_to(site) or not target.is_file():
                problems.append(f"站内链接失效：{source.relative_to(site)} → {raw}")
        if not parser.toplists:
            missing_nav.append(str(source.relative_to(site)))
        for nav in parser.toplists:
            if len(nav) > 4:
                oversized_nav.append(f"{source.relative_to(site)}（{len(nav)} 项）")
            for href in nav:
                if urlsplit(href).path.lower().endswith(("radar.html", "sentiment.html")):
                    misplaced_nav.append(f"{source.relative_to(site)} → {href}")

    for title, affected in (
        ("缺少主导航列表", missing_nav),
        ("主导航超过 4 项", oversized_nav),
        ("招聘或舆情位于主导航", misplaced_nav),
    ):
        if affected:
            problems.append(f"{title}：{len(affected)} 处；例如 {', '.join(affected[:3])}")

    # The workbench receives its project data as JSON in the generated page.
    workbench = site / "workbench.html"
    if workbench.is_file():
        markup = workbench.read_text(encoding="utf-8")
        match = re.search(r"window\.WB_DATA\s*=\s*(\{.*?\})\s*;\s*</script>", markup, re.S)
        if not match:
            problems.append("实战工作台缺少可解析的项目数据")
        else:
            try:
                wb_data = json.loads(match.group(1))
                projects = wb_data["projects"]
                if len(projects) != 5 or len({p["id"] for p in projects}) != 5:
                    problems.append(f"实训项目应为 5 个且 ID 唯一，当前为 {len(projects)} 个")
                for project in projects:
                    if not project.get("stages") or not project.get("quiz"):
                        problems.append(f"实训项目缺少任务或诊断：{project.get('id', '?')}")

                # ---- G8 规则-内容一致性校验（个性化一期）----
                mis_map = wb_data.get("misconceptions", {})
                routing = wb_data.get("routing", {})
                p1 = projects[0]
                page_ids = {p.stem for p in pages}

                # 1) P1 分层题库：误区 id 必须存在、dim 匹配、不得挂在正确项上；src 须命中产物页
                for q in p1.get("quiz", []):
                    if "level" not in q:
                        problems.append(f"P1 诊断题缺少 level 字段：{q.get('id', '?')}")
                        continue
                    if q.get("src") and q["src"] not in page_ids:
                        problems.append(f"P1 诊断题 {q['id']} 的资料出处无对应页面：{q['src']}")
                    for idx, mid in q.get("mis", {}).items():
                        if int(idx) == q["ans"]:
                            problems.append(f"P1 诊断题 {q['id']} 把误区挂在了正确项上")
                        if mid not in mis_map:
                            problems.append(f"P1 诊断题 {q['id']} 引用不存在的误区：{mid}")
                        elif mis_map[mid].get("dim") != q["dim"]:
                            problems.append(f"P1 诊断题 {q['id']} 的误区 {mid} 维度不匹配")

                # 2) 误区定向资料 slug 必须命中产物页
                for mid, m in mis_map.items():
                    for res in m.get("resources", []):
                        if res.get("u") not in page_ids:
                            problems.append(f"误区 {mid} 的资料链接无对应页面：{res.get('u')}")

                # 3) 路由规则引用的项目 id 必须存在
                proj_ids = {p["id"] for p in projects}
                for pid in routing.get("default", {}).get("order", []):
                    if pid not in proj_ids:
                        problems.append(f"ROUTING 默认顺序引用不存在的项目：{pid}")
            except (ValueError, KeyError, TypeError) as error:
                problems.append(f"实训项目数据解析失败：{error}")

    if home.is_file():
        home_parser = PageParser()
        home_parser.feed(home.read_text(encoding="utf-8"))
        home_links = {urlsplit(link).path for link in home_parser.links}
        for name in ("orientation.html", "paths.html", "workbench.html", "library.html", "about.html"):
            if name not in home_links:
                problems.append(f"首页没有通向 {name} 的入口")

    for name in PATH_PAGES:
        page = site / name
        if not page.is_file():
            continue
        parser = PageParser()
        markup = page.read_text(encoding="utf-8")
        parser.feed(markup)
        if "workbench.html" not in {urlsplit(link).path for link in parser.main_links}:
            problems.append(f"学习路径没有通向实战工作台的下一步链接：{name}")

        # 检查行动卡：每条路径 4 阶段应有 4 个 action-card
        ac_count = len(re.findall(r'<div class="action-card">', markup))
        if ac_count != 4:
            problems.append(f"路径页面应有 4 个行动卡（每阶段 1 个），{name} 当前为 {ac_count} 个")

        # 检查每个 action-card 包含 goal 和按钮
        action_blocks = re.findall(
            r'<div class="action-card">.*?<div class="action-g">(.*?)</div>.*?<div class="action-b">(.*?)</div>',
            markup, re.S
        )
        for i, (goal, btns) in enumerate(action_blocks):
            goal_text = re.sub(r'<[^>]+>', '', goal).strip()
            if not goal_text or not goal_text.startswith('💡'):
                problems.append(f"{name} 阶段 {i+1} 行动卡缺少有效的 goal")
            btn_links = re.findall(r'<a class="action-btn" href="(.*?)">', btns)
            if not btn_links:
                problems.append(f"{name} 阶段 {i+1} 行动卡缺少动作按钮")
            for href in btn_links:
                # 检查 workbench 深链格式
                if href.startswith("workbench.html"):
                    if "#p/" not in href:
                        problems.append(f"{name} 阶段 {i+1} 按钮链接应为 workbench 深链，当前为 {href}")
                    elif not re.match(r'^workbench\.html#p/kb-assistant/task-s[1-7]$', href):
                        problems.append(f"{name} 阶段 {i+1} 按钮深链格式异常：{href}")
                # 检查非 workbench 站内链接有效性
                elif href.endswith(".html"):
                    target = (site / href).resolve()
                    if not target.is_file():
                        problems.append(f"{name} 阶段 {i+1} 按钮链接失效：{href}")

    # 检查离线练习 ZIP
    lab_zip = site / "downloads" / "kb-assistant-lab.zip"
    if not lab_zip.is_file():
        problems.append("缺少离线练习 ZIP 包：downloads/kb-assistant-lab.zip")
    else:
        import zipfile
        try:
            with zipfile.ZipFile(lab_zip) as zf:
                names = set(zf.namelist())
                expected = {"README.md", "kb_assistant.py", "kb_docs/manifest.json",
                            "tests/test_kb_assistant.py"}
                missing = expected - names
                if missing:
                    problems.append(f"离线练习 ZIP 缺少关键文件：{', '.join(sorted(missing))}")
                # 确认排除了 pycache
                pycache_files = [n for n in names if "__pycache__" in n or n.endswith(".pyc")]
                if pycache_files:
                    problems.append(f"离线练习 ZIP 不应含 __pycache__ 或 .pyc：{', '.join(pycache_files)}")
        except (zipfile.BadZipFile, OSError) as error:
            problems.append(f"离线练习 ZIP 读取失败：{error}")

    if problems:
        print(f"构建产物检查失败：{len(problems)} 项（共检查 {len(pages)} 个 HTML 页面）")
        for problem in problems:
            print("  ✗", problem)
        return 1
    print(f"构建产物检查通过：{len(pages)} 个 HTML 页面，链接、导航、项目和关键页面均有效")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
