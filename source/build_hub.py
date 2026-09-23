#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FDE 开放联盟：整合 6 个来源内容 + 目标导向学习路径 + 知识图谱。"""
import re, json, html, pathlib, shutil, zipfile

ROOT = pathlib.Path(__file__).resolve().parent  # 工程根 = 本脚本所在目录（2026-09-23 迁移后改为自适应，不再硬编码会话路径）
SRC = ROOT / 'fde-wiki'
BK = ROOT / 'fde-sources/FDE-the-Guidance-Book-of-Forward-Deployed-Engineer-main'
HB = ROOT / 'fde-sources/FDE-Handbook-main'
RM = ROOT / 'fde-sources/Awesome-FDE-Roadmap-main'
AF = ROOT / 'fde-sources/Awesome-FDE-main'
OF = ROOT / 'fde-sources/OpenFDE'
OUT = ROOT / 'fde-hub-site'

FULL = (SRC / 'llms-full.txt').read_text(encoding='utf-8')
TOC = (SRC / 'llms.txt').read_text(encoding='utf-8')

# ================================================================ 解析工具（与 build_site.py 同源）
FRONT = re.compile(r'(?m)^---[ \t]*\nurl:[ \t]*(/\S+?\.md)[ \t]*\ndescription:[ \t]*(.*?)\n---[ \t]*\n', re.S)
matches = list(FRONT.finditer(FULL))
WIKI = {}
for i, m in enumerate(matches):
    slug = m.group(1).lstrip('/').replace('.md', '')
    desc = re.sub(r'\s+', ' ', m.group(2)).strip()
    desc = re.sub(r'^>-?\s*', '', desc).strip()
    end = matches[i + 1].start() if i + 1 < len(matches) else len(FULL)
    body = FULL[m.end():end].strip()
    body = re.sub(r'\n+---\s*$', '', body).strip()
    body = re.sub(r'^\s*---\s*\n+', '', body).strip()
    WIKI[slug] = {'desc': desc, 'body': body}

TITLE = {}
line_re = re.compile(r'^-\s*\[(.+?)\]\(/([^)]+?)\.md\)')
TOPIC_SUBS, OTHER_ITEMS = [], []
cur = None; cur_sub = None
for line in TOC.splitlines():
    if line.startswith('### '):
        cur = {'name': line[4:].strip(), 'items': [], 'subs': []}
    elif line.startswith('#### '):
        cur_sub = {'name': line[5:].strip(), 'items': []}
        cur['subs'].append(cur_sub)
    else:
        m = line_re.match(line)
        if m and cur:
            TITLE[m.group(2)] = m.group(1).strip()
            if cur['name'].startswith('深度专题'):
                (cur_sub or cur)['items'].append(m.group(2))
            elif cur['name'].startswith('Other'):
                OTHER_ITEMS.append(m.group(2))
for sub in cur['subs']:
    TOPIC_SUBS.append(sub)

PART_TITLES = {'part1': '第一篇 · 范式与市场全景', 'part2': '第二篇 · 工作方法论与最新工作方式',
               'part3': '第三篇 · 全行业落地', 'part4': '第四篇 · 能力、商业与未来'}
TITLE.update(PART_TITLES)

def cn_num(s):
    C = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
    if s == '十': return 10
    if '十' in s:
        a, b = s.split('十')
        return (C.get(a, 1) if a else 1) * 10 + (C.get(b, 0) if b else 0)
    return C.get(s, 0)

def short_title(slug):
    t = TITLE.get(slug, slug)
    t = re.sub(r'^深度专题(?=[一二三四五六七八九十百]+)', '专题', t)
    t = re.sub(r'^第\s*(\d+)\s*章\s*', r'\1. ', t)
    t = re.sub(r'[（(][^)）]{6,}$', '', t).strip()
    if len(t) > 32:
        t = t[:31].rstrip() + '…'
    return t

# ---------------------------------------------------------------- Markdown 渲染
import markdown
def slug_zh(value, separator):
    v = re.sub(r'[^\w\u4e00-\u9fff]+', '-', value, flags=re.U).strip('-')
    v = re.sub(r'-{2,}', '-', v)
    return v[:60] or 'sec'

MD = markdown.Markdown(extensions=['extra', 'toc', 'sane_lists', 'admonition', 'md_in_html'])
FENCE = re.compile(r'^\s*(```|~~~)')
EXPLICIT_ANCHOR = re.compile(r'\{#([^}\s]+)\}')

def fix_bq_fences(body):
    """把引用块内的围栏代码（> ```lang ... > ```）改写为 md_in_html 包裹的普通围栏，
    python-markdown 不解析引用块内围栏，会输出字面反引号。"""
    lines = body.split('\n')
    out, i, n = [], 0, len(lines)
    while i < n:
        m = re.match(r'^\s*>\s*(`{3,}|~{3,})\s*([\w+-]*)\s*$', lines[i])
        if m:
            tok, lang = m.group(1)[:3], m.group(2)
            block, i = [], i + 1
            while i < n and not re.match(r'^\s*>\s*' + re.escape(tok) + r'\s*$', lines[i]):
                block.append(re.sub(r'^\s*>\s?', '', lines[i]))
                i += 1
            i += 1  # 跳过结束围栏
            out.append('<div class="bq-code" markdown="1">')
            out.append('```' + lang)
            out.extend(block)
            out.append('```')
            out.append('</div>')
            continue
        out.append(lines[i])
        i += 1
    return '\n'.join(out)


SLUG_MODE = 'zh'


def github_slug(t):
    # 对齐 GitHub 锚点算法：小写、去标点，但保留变体选择符(U+FE0F)/零宽连接符(U+200D)
    v = re.sub(r'[^\w\- \u200d\ufe0f]+', '', t.strip().lower(), flags=re.U)
    return re.sub(r' ', '-', v)[:80] or 'sec'


def walk(body):
    items, used, infence, fence_tok = [], {}, False, ''
    for line in body.split('\n'):
        m = FENCE.match(line)
        if m:
            tok = m.group(1)
            if not infence:
                infence, fence_tok = True, tok
            elif line.strip().startswith(fence_tok):
                infence = False
            items.append({'kind': 'raw', 'text': line}); continue
        hm = None if infence else re.match(r'^(#{2,4})\s+(.*?)\s*$', line)
        if hm:
            text = hm.group(2)
            pre = EXPLICIT_ANCHOR.search(text)
            if pre:
                items.append({'kind': 'h', 'level': len(hm.group(1)), 'text': text[:pre.start()].strip(),
                              'anchor': pre.group(1), 'raw': line})
            else:
                sid = github_slug(text) if SLUG_MODE == 'gh' else slug_zh(text, '-')
                n = used.get(sid, 0); used[sid] = n + 1
                if n: sid = f'{sid}-{n}'
                items.append({'kind': 'h', 'level': len(hm.group(1)), 'text': text, 'anchor': sid})
        elif not infence and re.match(r'^#{1,6}\s', line):
            items.append({'kind': 'raw', 'text': line})
        else:
            items.append({'kind': 't', 'text': line})
    return items

def add_heading_ids(body):
    return '\n'.join(
        (it.get('raw') if it['kind'] == 'h' and it.get('raw') else
         (f'{"#" * it["level"]} {it["text"]} {{: #{it["anchor"]} }}' if it['kind'] == 'h' else it['text']))
        for it in walk(body))

def render(body, mode='zh'):
    global SLUG_MODE
    SLUG_MODE = mode
    MD.reset()
    out = MD.convert(fix_bq_fences(add_heading_ids(body)))
    def _strip_vs(s):  # 剔除锚点中的变体选择符/零宽连接符（含 %编码），保证 id 与 href 一致
        return (s.replace('\ufe0f', '').replace('\u200d', '')
                 .replace('%EF%B8%8F', '').replace('%E2%80%8D', ''))
    out = re.sub(r'id="([^"]*)"', lambda m: 'id="' + _strip_vs(m.group(1)) + '"', out)
    out = re.sub(r'href="#([^"]*)"', lambda m: 'href="#' + _strip_vs(m.group(1)) + '"', out)
    return out

def extract_toc(rendered):
    return [{'level': int(m.group(1)), 'id': m.group(2),
             'text': re.sub(r'<[^>]+>', '', m.group(3)).strip()}
            for m in re.finditer(r'<h([23])[^>]*id="([^"]+)"[^>]*>(.*?)</h\1>', rendered, re.S)]

def enhance(rendered):
    rendered = re.sub(r'<table>', '<div class="table-wrap"><table>', rendered)
    rendered = rendered.replace('</table>', '</table></div>')
    rendered = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', rendered)
    def rw(m):
        path, frag = m.group(1) or '', m.group(2) or ''
        slug = path.lstrip('/')
        if slug.endswith('.md'): slug = slug[:-3]
        if not slug: return f'href="index.html{frag}"'
        return f'href="{slug}.html{frag}"'
    rendered = re.sub(r'href="(/[^"]*?)(#[^"]*)?"', rw, rendered)
    return rendered

def cjk(s):
    return len(re.findall(r'[\u4e00-\u9fff]', s))

# ================================================================ 外部来源内容
BOOK_FILES = [
    ('book00', '00-自序.md', '自序'), ('book01', '01-第1章-FDE的崛起.md', '第 1 章 FDE 的崛起'),
    ('book02', '02-第2章-解决正确的问题.md', '第 2 章 解决正确的问题'),
    ('book03', '03-第3章-赢得客户.md', '第 3 章 赢得客户'),
    ('book04', '04-第4章-激活部署.md', '第 4 章 激活部署'),
    ('book05', '05-第5章-守住续约.md', '第 5 章 守住续约'),
    ('book06', '06-第6章-扩大收入.md', '第 6 章 扩大收入'),
    ('book07', '07-第7章-规模化复制.md', '第 7 章 规模化复制'),
    ('book08', '08-第8章-完整案例集.md', '第 8 章 完整案例集'),
    ('book09', '09-后记-FDE的职业道德.md', '后记 FDE 的职业道德'),
    ('book10', '10-附录A-FDE应当关注的常用指标.md', '附录 A FDE 应当关注的常用指标'),
    ('book11', '11-附录B-FDE人物与团队名单.md', '附录 B FDE 人物与团队名单'),
    ('book12', '12-附录C-全书案例索引与资料出处.md', '附录 C 全书案例索引与资料出处'),
]
BOOK = {}
for slug, fn, title in BOOK_FILES:
    p = BK / fn
    body = p.read_text(encoding='utf-8').strip().replace(' height="auto"', '')  # SVG height=auto 非法，viewBox+width 自适应
    first = re.match(r'^#\s+(.+)$', body)
    if first: body = re.sub(r'^#\s+.+\n', '', body, count=1).strip()  # 标题放入页面 h1
    BOOK[slug] = {'title': title, 'desc': re.sub(r'\s+', ' ', re.sub(r'[#>*`|]', ' ', body))[:120], 'body': body}

HB_TITLES = {}
for i in range(1, 12):
    raw = (HB / f'book_zh/chapter{i}.md').read_text(encoding='utf-8-sig').lstrip('\ufeff').replace(' height="auto"', '')
    m = re.search(r'^#\s+(.+?)\s*$', raw, re.M)
    if not m:
        raise SystemExit(f'hb{i} 标题解析失败')
    HB_TITLES[f'hb{i}'] = m.group(1).strip()
HBODY = {}
for i in range(1, 12):
    raw = (HB / f'book_zh/chapter{i}.md').read_text(encoding='utf-8-sig').lstrip('\ufeff').replace(' height="auto"', '')
    HBODY[f'hb{i}'] = re.sub(r'^#\s+.+?\s*$', '', raw, count=1, flags=re.M).strip()

EXT = {}
for slug, d in BOOK.items():
    EXT[slug] = {'src': 'book', 'title': d['title'], 'desc': d['desc'], 'body': d['body'],
                 'origin': '范冰《FDE 前沿部署工程师入门指南》（github.com/xdash）'}
for i in range(1, 12):
    EXT[f'hb{i}'] = {'src': 'handbook', 'title': HB_TITLES[f'hb{i}'],
                     'desc': re.sub(r'\s+', ' ', re.sub(r'[#>*`|]', ' ', HBODY[f'hb{i}']))[:120],
                     'body': HBODY[f'hb{i}'],
                     'origin': 'FDE-Handbook 中文版（github.com/goday-org，CC BY-NC-SA 4.0）'}
EXT['roadmap'] = {'src': 'roadmap', 'title': 'Awesome-FDE-Roadmap · FDE 学习路线图（英文）',
                  'desc': '数据工程 → 云架构 → 顾问思维 → AI Agent → 面试准备的分阶段课程（GCP 向）',
                  'body': re.sub(r'\]\(CONTRIBUTING\.md\)',
                                 '](https://github.com/pierpaolo28/Awesome-FDE-Roadmap/blob/main/CONTRIBUTING.md)',
                                 (RM / 'README.md').read_text(encoding='utf-8')),
                  'origin': 'Awesome-FDE-Roadmap（github.com/pierpaolo28，1.1k★）'}
EXT['awesome-fde'] = {'src': 'awesome', 'title': 'Awesome-FDE · 资源与招聘清单（英文）',
                      'desc': 'FDE 资源、公司、招聘渠道与技能清单（含 crypto→FDE 转型指南）',
                      'body': re.sub(r'\]\(LICENSE\)',
                                     '](https://github.com/yzyunzhang/Awesome-FDE/blob/main/LICENSE)',
                                     (AF / 'README.md').read_text(encoding='utf-8')),
                      'origin': 'Awesome-FDE（github.com/yzyunzhang）'}
# OpenFDE 社区两篇（CC BY-SA 4.0）：站内互链改为本站页面
_of_tools = (OF / 'FDE 所需工具地图.md').read_text(encoding='utf-8').replace(
    '](./FDE%20实战蓝皮书.md)', '](playbook.html)')
_of_play = (OF / 'FDE 实战蓝皮书.md').read_text(encoding='utf-8').replace(
    '](./FDE%20所需工具地图.md)', '](tools.html)')
EXT['tools'] = {'src': 'openfde', 'title': 'FDE 工具地图 · AI-native 交付底座与客户 AI 选型地图',
                'desc': '「小人类核心 + agent 舰队」：全生命周期工具链（市场→合同→设计→构建→上线→运营），交付侧与采购侧双读者框架',
                'body': _of_tools,
                'origin': 'OpenFDE（github.com/OpenFDEAI/OpenFDE，CC BY-SA 4.0，整理于 2026-06-30）'}
EXT['playbook'] = {'src': 'openfde', 'title': 'FDE 实战蓝皮书 · 客户分层 × 行业打法 × 切入点方法论',
                   'desc': 'SMB/中型/央国企三档打法、六大行业落地场景与合规红线、进门→生产→扩张→产品化阈值的完整方法论',
                   'body': _of_play,
                   'origin': 'OpenFDE（github.com/OpenFDEAI/OpenFDE，CC BY-SA 4.0，整理于 2026-07）'}

ALL = {}   # slug -> {title, src, desc, body, origin}
for s in WIKI:
    ALL[s] = {'src': 'wiki', 'title': TITLE.get(s, s), 'desc': WIKI[s]['desc'], 'body': WIKI[s]['body'], 'origin': None}
ALL.update(EXT)
CHARS = {s: cjk(d['body']) for s, d in ALL.items()}

# ================================================================ 知识图谱（手工策划）
# 域: cog 认知 / met 方法论 / tec 技术 / ind 行业 / biz 商业 / soft 软技能
G_NODES = [
 # 认知
 ('fde', 'FDE 定义与起源', 'cog', '对业务结果负责、嵌入客户现场的前沿部署工程师，源自 Palantir 2003 伊拉克战场实践', 'L1',
  [('ch01', '第 1 章 起源与定义演进'), ('book01', '范冰·第 1 章 FDE 的崛起')]),
 ('market', '市场与薪酬', 'cog', '2026 全球 FDE 招聘增长、薪酬带与人才缺口', 'L1',
  [('ch02', '第 2 章 全球市场全景'), ('book10', '范冰·附录 A 常用指标')]),
 ('companies', '头部公司模式', 'cog', 'Palantir / OpenAI / Anthropic / Databricks / 国内云的 FDE 变体', 'L1',
  [('ch03', '第 3 章 头部公司拆解'), ('topic29', '专题 29 海外 FDE 运营')]),
 ('roles', '相邻岗位辨析', 'cog', 'FDE vs 解决方案架构师 / 应用工程师 / 咨询顾问', 'L1',
  [('ch04', '第 4 章 岗位辨析'), ('hb1', 'Handbook·第 1 章 FDE 角色与使命')]),
 ('china', '中国 FDE 市场', 'cog', '信创约束、央国企决策链、国内薪酬与机会', 'L2',
  [('topic28', '专题 28 中国市场拆解'), ('book02', '范冰·第 2 章')]),
 # 方法论
 ('edd', 'Echo-Delta-Dev', 'met', 'Palantir 三角编队：Echo 售前 / Delta 现场 / Dev 平台', 'L2',
  [('ch05', '第 5 章 三角编队')]),
 ('discovery', 'Discovery-first', 'met', '先发现真问题再动手，拒绝拿着锤子找钉子', 'L2',
  [('ch06', '第 6 章 方法论内核'), ('book02', '范冰·第 2 章 解决正确的问题')]),
 ('backwards', 'Working Backwards', 'met', '从业务结果倒推系统设计', 'L2', [('ch06', '第 6 章 方法论内核')]),
 ('cdef', 'CDEF 四阶段', 'met', 'Context 勘探 → Design 设计 → Engineer 工程 → Feedback 反馈', 'L2',
  [('ch07', '第 7 章 CDEF 方法论'), ('hb2', 'Handbook·第 2 章 顾问式思维')]),
 ('fdce', 'FDCE 上下文工程', 'met', '前沿部署上下文工程：把客户领域知识变成系统资产', 'L3',
  [('ch06', '第 6 章'), ('topic01', '专题 1 RAG 与上下文工程')]),
 ('mvd', 'MVD 最小可行交付', 'met', '用最小可交付物快速建立信任', 'L2', [('ch10', '第 10 章 交付节奏')]),
 ('rollout', '灰度与上线', 'met', '灰度策略、回滚预案、现场生存', 'L3', [('ch10', '第 10 章'), ('topic08', '专题 8 踩坑总集')]),
 ('kt', '知识转移', 'met', '让客户撤场后用得起来，防止能力折损', 'L3', [('topic60', '专题 60 知识转移'), ('book05', '范冰·第 5 章 守住续约')]),
 # 技术
 ('llm', 'LLM 选型', 'tec', '模型能力/成本/合规三角权衡', 'L2', [('ch09', '第 9 章 技术栈'), ('topic14', '专题 14 选型与微调')]),
 ('prompt', 'Prompt 工程', 'tec', '从咒语到有版本管理和评估的工程学科', 'L2', [('topic04', '专题 4'), ('topic13', '专题 13 模板库')]),
 ('rag', 'RAG', 'tec', '检索增强生成：分块/嵌入/混合检索/重排', 'L3', [('topic01', '专题 1 RAG 实战'), ('hb7', 'Handbook·第 7 章 企业级 RAG')]),
 ('graphrag', 'GraphRAG', 'tec', '知识图谱增强检索，回答实体关系类问题', 'L4', [('topic21', '专题 21 GraphRAG')]),
 ('agent', 'Agent 编排', 'tec', '六种拓扑、HITL、状态契约与故障应对', 'L3', [('topic02', '专题 2'), ('topic17', '专题 17 多 Agent 代码实战')]),
 ('multiagent', '多 Agent 系统', 'tec', '把多个 Agent 串成可控可观测的流水线', 'L4', [('topic17', '专题 17'), ('hb8', 'Handbook·第 8 章 多智能体协同')]),
 ('mcp', 'MCP 协议', 'tec', '模型上下文协议：Agent 连接企业系统的标准接口', 'L2', [('ch08', '第 8 章 Agent 时代 FDE')]),
 ('eval', '评估体系 EDD', 'tec', '评估驱动开发：LLM-as-Judge、线上校验', 'L3', [('topic03', '专题 3'), ('topic30', '专题 30 红队'), ('hb9', 'Handbook·第 9 章 科学评估')]),
 ('inference', '推理优化与量化', 'tec', 'vLLM、量化、生产级推理服务', 'L4', [('topic06', '专题 6'), ('topic46', '专题 46 性能调优')]),
 ('dataeng', '数据工程', 'tec', '企业 AI 的 70% 工作量：清洗/脱敏/管道', 'L3', [('topic05', '专题 5'), ('hb3', 'Handbook·第 3 章 数据审计')]),
 ('mlops', 'MLOps 与持续交付', 'tec', 'LLM 应用的 CI/CD、版本管理与回滚', 'L4', [('topic09', '专题 9')]),
 ('observ', '可观测性与 SRE', 'tec', 'LLM 系统的监控、告警与事故复盘', 'L4', [('topic20', '专题 20')]),
 ('security', '安全与合规', 'tec', 'OWASP MCP Top10、等保、个保法、数据不出域', 'L3', [('ch22', '第 22 章'), ('topic10', '专题 10 数据安全'), ('hb6', 'Handbook·第 6 章 VPC-SC')]),
 ('cloud', '云原生与基础设施', 'tec', 'GPU 调度、K8s、私有化部署', 'L3', [('topic33', '专题 33'), ('hb5', 'Handbook·第 5 章 混合云着陆区')]),
 ('finetune', '微调 LoRA/QLoRA', 'tec', '何时微调、怎么不踩坑', 'L4', [('topic14', '专题 14')]),
 # 行业
 ('fin', '金融落地', 'ind', '风控、尽调自动化、反金融犯罪', 'L3', [('ch11', '第 11 章 金融')]),
 ('med', '医疗落地', 'ind', '病历质控、DRG、PHI 保护', 'L3', [('ch12', '第 12 章 医疗')]),
 ('mfg', '制造落地', 'ind', '视觉质检、预测性维护', 'L3', [('ch13', '第 13 章 制造')]),
 ('gov', '政务落地', 'ind', '12345 热线、信创全栈、数据不出域', 'L3', [('ch14', '第 14 章 政务')]),
 ('retail', '零售电商', 'ind', '个性化、库存、智能客服', 'L2', [('ch15', '第 15 章')]),
 ('energy', '能源电力', 'ind', '电网、油气、新能源场景', 'L3', [('ch17', '第 17 章')]),
 # 商业
 ('bizmodel', '商业模式与定价', 'biz', '卖人头 vs 卖结果，价值折现与谈判', 'L3', [('ch21', '第 21 章'), ('topic16', '专题 16 定价谈判')]),
 ('roi', 'ROI 测算', 'biz', '让财务部门能入账的价值证明', 'L3', [('topic23', '专题 23'), ('book06', '范冰·第 6 章 扩大收入')]),
 ('presale', '售前与招投标', 'biz', '技术方案、可行性论证、PoC 竞标', 'L3', [('topic44', '专题 44')]),
 ('cs', '客户成功与续约', 'biz', '验收不是终点，是价值折损的起点', 'L3', [('topic38', '专题 38'), ('book05', '范冰·第 5 章')]),
 ('scale', '规模化复制', 'biz', '从单点交付到可复制的交付体系', 'L4', [('book07', '范冰·第 7 章 规模化复制'), ('topic40', '专题 40 产品化')]),
 # 软技能
 ('consult', '顾问式沟通', 'soft', '干系人外交、向上管理与预期管理', 'L2', [('topic18', '专题 18 现场沟通软技能'), ('hb2', 'Handbook·第 2 章')]),
 ('thinking', '结构化思维', 'soft', 'MECE、金字塔原理、80/20 裁剪', 'L1', [('hb2', 'Handbook·第 2 章'), ('topic45', '专题 45 底层思维模型')]),
 ('writing', '写作与文档', 'soft', '方案、周报、runbook 的工程写作', 'L2', [('topic49', '专题 49')]),
 ('demo', 'Demo 与汇报', 'soft', '做出来、看得见、说得清', 'L2', [('topic58', '专题 58')]),
 ('org', '团队与组织', 'soft', 'FDE 团队组建、沙盘培养、组织变革', 'L3', [('topic12', '专题 12'), ('topic27', '专题 27'), ('topic48', '专题 48')]),
 ('career', '职业发展', 'soft', '成长路径、持续学习、可持续工作', 'L2', [('topic19', '专题 19'), ('book09', '范冰·后记 职业道德')]),
]
DOMAINS = {'cog': ('认知与市场', '#2563eb'), 'met': ('方法论', '#7c3aed'), 'tec': ('技术栈', '#0d9488'),
           'ind': ('行业落地', '#d97706'), 'biz': ('商业', '#db2777'), 'soft': ('软技能', '#64748b')}

G_EDGES = [  # (from, to, type)  pre=前置 depends-on, rel=相关
 ('fde', 'edd', 'pre'), ('fde', 'discovery', 'pre'), ('fde', 'market', 'rel'), ('fde', 'roles', 'rel'),
 ('market', 'china', 'rel'), ('companies', 'china', 'rel'),
 ('edd', 'cdef', 'pre'), ('discovery', 'cdef', 'pre'), ('backwards', 'cdef', 'pre'),
 ('cdef', 'mvd', 'pre'), ('cdef', 'rollout', 'pre'), ('cdef', 'fdce', 'pre'), ('cdef', 'kt', 'pre'),
 ('discovery', 'thinking', 'rel'), ('thinking', 'consult', 'pre'), ('consult', 'presale', 'pre'),
 ('llm', 'rag', 'pre'), ('llm', 'finetune', 'rel'), ('llm', 'inference', 'pre'), ('llm', 'prompt', 'rel'),
 ('prompt', 'rag', 'pre'), ('dataeng', 'rag', 'pre'), ('rag', 'graphrag', 'pre'), ('rag', 'eval', 'pre'),
 ('mcp', 'agent', 'pre'), ('agent', 'multiagent', 'pre'), ('multiagent', 'eval', 'pre'), ('agent', 'eval', 'pre'),
 ('cloud', 'inference', 'pre'), ('cloud', 'security', 'rel'), ('mlops', 'observ', 'rel'), ('mlops', 'eval', 'rel'),
 ('rag', 'fin', 'pre'), ('agent', 'fin', 'rel'), ('rag', 'med', 'pre'), ('agent', 'mfg', 'rel'),
 ('security', 'gov', 'pre'), ('rag', 'retail', 'pre'), ('mcp', 'energy', 'rel'), ('rag', 'energy', 'pre'),
 ('mvd', 'roi', 'pre'), ('roi', 'bizmodel', 'rel'), ('consult', 'demo', 'rel'), ('writing', 'demo', 'pre'),
 ('kt', 'cs', 'pre'), ('cs', 'scale', 'pre'), ('presale', 'bizmodel', 'rel'), ('org', 'scale', 'rel'),
 ('career', 'consult', 'rel'), ('kt', 'org', 'rel'), ('security', 'fin', 'pre'),
]
NODES_JS = json.dumps([
    {'id': n[0], 'l': n[1], 'd': n[2], 'x': n[3], 'lv': n[4],
     'r': [{'t': t, 'u': f'{u}.html'} for u, t in n[5]]} for n in G_NODES
], ensure_ascii=False)
EDGES_JS = json.dumps(G_EDGES)

# ================================================================ 学习路径（5 目标 × 4 阶段）
SRC_META = {'wiki': ('FDE-Wiki', '#2563eb'), 'book': ('范冰指南', '#7c3aed'), 'handbook': ('Handbook', '#0d9488'),
            'roadmap': ('Roadmap', '#d97706'), 'awesome': ('Awesome-FDE', '#db2777'),
            'openfde': ('OpenFDE', '#0369a1')}
LV = {'L1': ('L1 认知', '#94a3b8'), 'L2': ('L2 方法', '#2563eb'), 'L3': ('L3 实战', '#d97706'), 'L4': ('L4 精通', '#db2777')}

def I(u, lv, note=''):
    d = ALL[u]
    return {'u': u, 'lv': lv, 'note': note, 'm': max(5, round(CHARS[u] / 400))}

GOALS = [
 {'id': 'career', 'icon': '🎯', 'name': '转行求职 FDE', 'who': '工程师 / 应届生想拿到 FDE offer',
  'desc': '先建立对岗位的正确认知，再补方法论与技术栈，最后用案例和面试准备收口。',
  'stages': [
   ('建立认知', '这个岗位是什么、市场要什么人', [I('ch01', 'L1'), I('book01', 'L1'), I('ch02', 'L1'), I('ch04', 'L1')]),
   ('核心方法', 'Palantir 打法与交付节奏', [I('book02', 'L2'), I('ch05', 'L2'), I('ch07', 'L2'), I('book03', 'L2')]),
   ('技术栈补课', '能搭出可运行的 AI 系统', [I('topic07', 'L3'), I('topic01', 'L3'), I('topic02', 'L3'), I('hb7', 'L3')]),
   ('实战与求职', '案例 + 面试 + 投递渠道', [I('ch11', 'L4', '选自己熟悉的行业读'), I('book08', 'L4'), I('awesome-fde', 'L4'), I('topic08', 'L4')])]},
 {'id': 'engineer', 'icon': '🛠', 'name': '在职工程师·AI 落地能力', 'who': '后端/算法/数据工程师，想把 AI 真正落进业务',
  'desc': '跳过市场叙事，直接进技术纵深与方法论，最后用行业案例校准。',
  'stages': [
   ('认知速览', 'FDE 与 Agent 时代的定位', [I('ch01', 'L1'), I('ch08', 'L2')]),
   ('技术纵深', 'RAG / Agent / 评估 / 数据', [I('topic01', 'L3'), I('topic02', 'L3'), I('topic03', 'L3'), I('topic05', 'L3'), I('topic06', 'L4')]),
   ('方法论与工程化', '从 demo 到生产', [I('ch07', 'L2'), I('ch06', 'L2'), I('topic09', 'L4'), I('hb9', 'L3')]),
   ('行业实战', '挑一个行业打穿', [I('topic42', 'L4'), I('topic08', 'L3'), I('ch15', 'L3', '或选自己行业章节'), I('topic46', 'L4')])]},
 {'id': 'manager', 'icon': '🧭', 'name': '技术管理者·组建 FDE 团队', 'who': '技术负责人 / 团队 Leader',
  'desc': '先看市场与公司模式定战略，再落组织与培养，最后用商业指标证明价值。',
  'stages': [
   ('战略认知', '范式、公司与未来趋势', [I('ch01', 'L1'), I('ch03', 'L2'), I('ch23', 'L2')]),
   ('组织设计', '编队、能力模型与变革', [I('ch05', 'L2'), I('ch20', 'L2'), I('topic12', 'L3'), I('topic48', 'L3')]),
   ('商业闭环', '定价、ROI 与客户成功', [I('ch21', 'L3'), I('topic23', 'L3'), I('topic16', 'L4'), I('book06', 'L3')]),
   ('体系沉淀', '知识资产与失败复盘', [I('topic35', 'L4'), I('topic60', 'L3'), I('topic56', 'L3'), I('topic27', 'L4')])]},
 {'id': 'presales', 'icon': '🤝', 'name': '售前 / 解决方案顾问', 'who': '售前、解决方案架构师、交付顾问',
  'desc': '强化结构化思维与沟通，补招投标、需求工程与现场演示。',
  'stages': [
   ('角色定位', 'FDE 与相邻岗位的差异', [I('ch04', 'L1'), I('ch01', 'L1')]),
   ('售前主线', '招投标、公司模式与市场', [I('topic44', 'L3'), I('ch03', 'L2'), I('ch02', 'L1'), I('hb2', 'L2')]),
   ('需求与方案', '把模糊问题变成可签方案', [I('topic36', 'L3'), I('topic59', 'L4'), I('topic13', 'L3'), I('ch09', 'L3')]),
   ('现场成单', '沟通、演示与行业弹药', [I('topic58', 'L2'), I('topic18', 'L2'), I('topic26', 'L3'), I('ch14', 'L3')])]},
 {'id': 'exec', 'icon': '📈', 'name': '业务决策者 / 创业者', 'who': '想判断 AI 投入与组织布局的管理层',
  'desc': '只读必要的认知与商业内容，重点在 ROI、合规与失败案例。',
  'stages': [
   ('趋势判断', '范式崛起与 3-5 年展望', [I('ch01', 'L1'), I('book01', 'L1'), I('ch23', 'L2')]),
   ('商业判断', '市场、模式与中国市场', [I('ch02', 'L1'), I('ch21', 'L2'), I('topic28', 'L2')]),
   ('价值与风险', 'ROI、合规与伦理', [I('topic23', 'L3'), I('topic24', 'L3'), I('ch22', 'L3')]),
   ('组织落地', '变革、就业影响与复盘', [I('topic48', 'L3'), I('topic52', 'L2'), I('topic56', 'L2'), I('book07', 'L3')])]},
]
for g in GOALS:
    g['total_m'] = sum(it['m'] for st in g['stages'] for it in st[2])
    g['total_n'] = sum(len(st[2]) for st in g['stages'])

# ---------------------------------------------------------------- 每条路线每阶段的行动卡（本阶段练什么）
# goal 一句目标，actions 一到两个按钮，(url) 不增加新页面；related_workbench 标注对应实训阶段（可选）
ACTION_CARDS = {
    'career': [
        {'goal': '用一个比喻向朋友解释 FDE 在做什么，写在一页纸上。',
         'actions': [('📝 读岗位概述', 'orientation.html')],
         'related_workbench': None},
        {'goal': '用 CDEF 四阶段分析你最近的一个项目，哪个阶段做得最多？',
         'actions': [('📐 阅读方法论参考', 'ch07.html')],
         'related_workbench': 's1 业务发现'},
        {'goal': '搭一个最小 RAG 检索原型：读完技术材料后，跑通检索→回答基线。',
         'actions': [('🛠 完成 s3 检索基线', 'workbench.html#p/kb-assistant/task-s3'), ('🛠 完成 s4 回答与拒答', 'workbench.html#p/kb-assistant/task-s4')],
         'related_workbench': 's3 检索基线 + s4 回答与拒答'},
        {'goal': '选一个行业案例，写出完整复盘：客户问题→方案→结果→取舍。',
         'actions': [('🎯 完成入门项目全部 7 阶段', 'workbench.html#p/kb-assistant/task-s1')],
         'related_workbench': 's1-s7 完整实训'},
    ],
    'engineer': [
        {'goal': '用一句话对比 FDE 和你当前岗位的职责边界，写出来。',
         'actions': [('📝 读岗位辨析', 'ch04.html')],
         'related_workbench': None},
        {'goal': '练习检索与拒答：跑通检索→回答基线的完整调用链路。',
         'actions': [('🛠 完成 s3 检索基线', 'workbench.html#p/kb-assistant/task-s3'), ('🛠 完成 s4 回答与拒答', 'workbench.html#p/kb-assistant/task-s4')],
         'related_workbench': 's3 检索基线 + s4 回答与拒答'},
        {'goal': '把你上一个项目画成 CDEF 流程图，并写一份可复现的启动说明。',
         'actions': [('📐 完成 s2 数据审计', 'workbench.html#p/kb-assistant/task-s2'), ('📐 完成 s6 交付运维', 'workbench.html#p/kb-assistant/task-s6')],
         'related_workbench': 's2 数据审计 + s6 交付运维'},
        {'goal': '在你最熟悉的行业场景中写一份 AI 落地一页方案与评估报告。',
         'actions': [('📋 完成 s1 业务发现', 'workbench.html#p/kb-assistant/task-s1'), ('📋 完成 s5 质量评估', 'workbench.html#p/kb-assistant/task-s5')],
         'related_workbench': 's1 业务发现 + s5 质量评估'},
    ],
    'manager': [
        {'goal': '为公司写一份 FDE 岗位定义：角色、绩效指标、适用场景。',
         'actions': [('📖 研究头部公司模式', 'ch03.html')],
         'related_workbench': None},
        {'goal': '画出你设想的 FDE 团队编队与能力模型，标注考核方式。',
         'actions': [('📖 读组织设计专题', 'topic12.html')],
         'related_workbench': None},
        {'goal': '为一个虚构项目写 ROI 测算一页纸：投入、收益、回收期、风险。',
         'actions': [('📊 参考 ROI 测算', 'topic23.html')],
         'related_workbench': '参考 s1 需求说明中的价值度量'},
        {'goal': '写一份知识资产沉淀模板与项目复盘框架（含验收标准）。',
         'actions': [('📋 参考复盘模板', 'topic60.html')],
         'related_workbench': '参考 s7 客户验收中的复盘结构'},
    ],
    'presales': [
        {'goal': '列出 FDE 与售前的 3 个关键差异，各用一句话说明。',
         'actions': [('📝 读岗位辨析', 'ch04.html')],
         'related_workbench': None},
        {'goal': '为一家虚构企业写一份技术方案大纲，不超过 3 页。',
         'actions': [('📖 研究招投标流程', 'topic44.html')],
         'related_workbench': None},
        {'goal': '把一段客户原始对话转化为需求清单，标注优先级与风险。',
         'actions': [('📋 完成 s1 业务发现', 'workbench.html#p/kb-assistant/task-s1')],
         'related_workbench': 's1 业务发现'},
        {'goal': '写一份 10 分钟演示脚本，含 3 个变式追问的应答预案。',
         'actions': [('🎤 完成 s7 客户验收', 'workbench.html#p/kb-assistant/task-s7')],
         'related_workbench': 's7 客户验收'},
    ],
    'exec': [
        {'goal': '用 200 字向董事会解释 FDE 范式：做什么、为什么重要、三年影响。',
         'actions': [('📖 读趋势判断', 'ch23.html')],
         'related_workbench': None},
        {'goal': '估算你所在行业引入 FDE 的投入产出，列出三个关键假设。',
         'actions': [('📊 读 ROI 测算', 'topic23.html')],
         'related_workbench': '参考 s1 需求中的价值定义'},
        {'goal': '列出 AI 项目必须规避的 3 个合规风险与对应的缓解措施。',
         'actions': [('🔒 读安全合规', 'ch22.html')],
         'related_workbench': None},
        {'goal': '写一页 FDE 团队组建与变革计划：规模、时间线、关键里程碑。',
         'actions': [('📋 读组织落地', 'topic48.html')],
         'related_workbench': '参考 s7 验收中的交接与复盘'},
    ],
}

# ================================================================ 站点生成
if OUT.exists():
    shutil.rmtree(OUT)
(OUT / 'assets').mkdir(parents=True)
shutil.copy(ROOT / 'assets' / 'hub.css', OUT / 'assets' / 'hub.css')
shutil.copy(ROOT / 'assets' / 'hub.js', OUT / 'assets' / 'hub.js')
shutil.copy(ROOT / 'assets' / 'graph.js', OUT / 'assets' / 'graph.js')
shutil.copy(ROOT / 'assets' / 'workbench.css', OUT / 'assets' / 'workbench.css')
shutil.copy(ROOT / 'assets' / 'workbench.js', OUT / 'assets' / 'workbench.js')
shutil.copy(ROOT / 'assets' / 'profile.css', OUT / 'assets' / 'profile.css')
shutil.copy(ROOT / 'assets' / 'profile.js', OUT / 'assets' / 'profile.js')
shutil.copy(ROOT / 'assets' / 'sentiment.css', OUT / 'assets' / 'sentiment.css')

# P0 打包离线练习（构建时从 labs/ 生成，放到 downloads/ 下）
LAB_SRC = ROOT / 'labs' / 'kb-assistant'
LAB_ZIP = OUT / 'downloads' / 'kb-assistant-lab.zip'
if LAB_SRC.is_dir():
    (OUT / 'downloads').mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(LAB_ZIP, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(LAB_SRC.rglob('*')):
            if '__pycache__' in f.parts or f.suffix == '.pyc':
                continue
            arcname = f.relative_to(LAB_SRC)
            zf.write(f, arcname)
    print(f'✓ 打包离线练习：{LAB_ZIP}（{LAB_ZIP.stat().st_size / 1024:.0f} KB）')
else:
    print(f'⚠ 未找到 labs/kb-assistant，跳过离线练习打包')

# P1 学习工作台数据（wb_data.py 与本脚本同目录）
import wb_data as WB
# 行业舆情报告数据（yq_data.py 与本脚本同目录）
import yq_data as YQ

SITE_NAME = 'FDE 开放联盟'
SRC_LABEL = {'wiki': 'FDE-Wiki 调研报告', 'book': '范冰《FDE 入门指南》', 'handbook': 'FDE-Handbook 中文版',
             'roadmap': 'Awesome-FDE-Roadmap', 'awesome': 'Awesome-FDE', 'openfde': 'OpenFDE'}

def page_head(title, desc):
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape((desc or '')[:150])}">
<link rel="stylesheet" href="assets/hub.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='%232563eb'/><text x='16' y='22' font-size='15' font-family='monospace' fill='white' text-anchor='middle'>F</text></svg>">
</head>
<body>'''

def topbar():
    return f'''<header class="topbar">
  <button class="icon-btn menu-btn" type="button" aria-label="目录">☰</button>
  <a class="brand" href="index.html"><span class="brand-mark">F</span>
    <span class="brand-txt"><b>FDE 开放联盟</b><i>开放实训平台 · 6 源底座</i></span></a>
  <div class="search" role="search">
    <svg viewBox="0 0 20 20" width="15" height="15" aria-hidden="true"><circle cx="9" cy="9" r="6" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M13.5 13.5L17 17" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
    <input id="q" type="search" placeholder="搜索 {len(ALL)} 篇内容…" autocomplete="off" aria-label="全站搜索">
    <kbd>/</kbd>
  </div>
  <a class="top-link" href="index.html">首页</a>
</header>
<div id="search-panel" class="search-panel" hidden></div>'''

NAV_HUB = [('index.html', '🏠 开始学习'), ('paths.html', '🧭 学习路线'), ('workbench.html', '🛠 交付实训'), ('library.html', '📚 知识库')]

def sidebar(active):
    parts = ['<nav class="snav" aria-label="导航">']
    parts.append('<section class="sgroup open"><div class="sgroup-b">')
    parts.append('<ul class="slist toplist">')
    for u, t in NAV_HUB:
        cls = ' class="on"' if active == u.replace('.html', '') else ''
        parts.append(f'<li><a{cls} href="{u}">{t}</a></li>')
    parts.append('</ul>')
    parts.append('</div></section>')
    # 页面相关工具放在次级区，完整原文目录集中在知识库。
    secondary = [('about', '来源与版权'), ('profile', '能力档案'), ('graph', '知识图谱'),
                 ('videos', '视频资源'), ('tools', '工具地图'), ('playbook', '实战蓝皮书')]
    links = []
    for slug, label in secondary:
        cls = ' class="on"' if active == slug else ''
        links.append(f'<li><a{cls} href="{slug}.html">{label}</a></li>')
    parts.append('<section class="sgroup"><button class="sgroup-h" type="button" aria-expanded="false"><span class="dot" style="background:#64748b"></span><span class="sgroup-t">更多工具</span><span class="chev">⌄</span></button><div class="sgroup-b"><ul class="slist">')
    parts.append(''.join(links))
    parts.append('<li><a href="library.html">全部原文与专题</a></li></ul></div></section>')
    parts.append('<div class="side-progress" id="side-progress"></div>')
    parts.append('</nav>')
    return '\n'.join(parts)

SEARCH = []

def gen_content_page(slug):
    d = ALL[slug]
    rendered = enhance(render(d['body'], 'gh' if slug in ('roadmap', 'awesome-fde') else 'zh'))
    # 编辑勘误：Handbook 原文中 VPC-SC 的绝对化安全表述（不改原文，加编者注）
    if slug == 'hb6' and '绝对无法跨越网络边界' in rendered:
        rendered = rendered.replace(
            '数据也绝对无法跨越网络边界进行传输。',
            '数据也绝对无法跨越网络边界进行传输。'
            '<span class="ed-note">编者注（本站）：原文此处表述过强——VPC-SC 能大幅降低数据外泄风险，'
            '但任何边界控制都不能等同于绝对防护，仍需配合最小权限、审计与密钥管理。</span>')
    toc = extract_toc(rendered)
    src_id, (src_name, src_color) = d['src'], SRC_META[d['src']]
    toc_html = ''
    if len(toc) >= 2:
        lis = ''.join(f'<li class="lv{t["level"]}"><a href="#{t["id"]}">{html.escape(t["text"])}</a></li>' for t in toc)
        toc_html = f'<div class="ptoc"><div class="ptoc-t">本页目录</div><ul>{lis}</ul></div>'
    origin = f'<div class="origin">来源：{html.escape(d["origin"])}</div>' if d['origin'] else ''
    core = f'''<div class="crumb"><a href="index.html">首页</a><span>/</span><a href="library.html" style="color:{src_color}">{src_name}</a></div>
<article class="doc">
  <h1 class="doc-title">{html.escape(d['title'])}</h1>
  <div class="doc-meta"><span style="color:{src_color}">{src_name}</span><span class="sep">·</span><span>约 {CHARS[slug]:,} 字</span><span class="sep">·</span><span>阅读约 {max(1, round(CHARS[slug]/400))} 分钟</span></div>
  {origin}
  <div class="prose" id="prose">{rendered}</div>
</article>
<div class="mark-bar"><button class="mark-btn" type="button" data-mark="{slug}">✓ 标记为已读</button></div>'''
    out = page_head(f'{d["title"]} · {SITE_NAME}', d['desc']) + topbar() + \
        f'<div class="layout"><aside class="side" id="side">{sidebar(slug)}</aside><main class="main">{core}</main></div><div class="mask" id="mask"></div>' + \
        toc_html + '<div class="reading-bar" id="rbar"></div><button class="totop" id="totop" type="button" aria-label="回到顶部">↑</button>' + \
        '<script src="assets/hub.js"></script>\n</body></html>'
    (OUT / f'{slug}.html').write_text(out, encoding='utf-8')
    cur_h, cur_a, buf = d['title'], '', []
    for it in walk(d['body']):
        if it['kind'] == 'h':
            if buf:
                SEARCH.append({'u': slug, 't': d['title'], 'h': cur_h, 'a': cur_a,
                               'x': re.sub(r'\s+', ' ', ' '.join(buf))[:400]}); buf = []
            cur_h, cur_a = it['text'], it['anchor']
        elif it['kind'] == 't':
            l = re.sub(r'[`*>#|\[\]()\-]+', ' ', it['text']).strip()
            if l: buf.append(l)
    if buf:
        SEARCH.append({'u': slug, 't': d['title'], 'h': cur_h, 'a': cur_a,
                       'x': re.sub(r'\s+', ' ', ' '.join(buf))[:400]})

order = ['part1'] + [f'ch{n:02d}' for n in range(1, 24)] + ['part2'] + [f'ch{n:02d}' for n in range(5, 11)]
# wiki 全部（含专题与附录页）
for s in WIKI:
    if s in ('part1', 'part2', 'part3', 'part4') or s.startswith('ch'):
        gen_content_page(s)
for s in list(BOOK) + [f'hb{i}' for i in range(1, 12)] + ['roadmap', 'awesome-fde', 'tools', 'playbook']:
    gen_content_page(s)
for s in WIKI:
    if s.startswith('topic'):
        gen_content_page(s)
for s in ('companies', 'tags', 'guestbook', 'appendix'):
    if s in WIKI:
        gen_content_page(s)
print(f'✓ 内容页 {len(list(OUT.glob("*.html"))) - 0} 个（含框架页前）')

# ================================================================ 学习路径页
PATHS_JS = json.dumps([{'id': g['id'], 'name': g['name'], 'total': g['total_n']} for g in GOALS], ensure_ascii=False)

def gen_path(g):
    stages = []
    cards = ACTION_CARDS.get(g['id'], [])
    for si, (sname, sdesc, items) in enumerate(g['stages']):
        rows = []
        for ii, it in enumerate(items):
            src_name, src_color = SRC_META[ALL[it['u']]['src']]
            lv_name, lv_color = LV[it['lv']]
            iid = f'path-{g["id"]}-{si}-{ii}'
            rows.append(f'''<div class="item-row" data-iid="{iid}">
  <button class="ckb" type="button" data-iid="{iid}" aria-label="标记完成"></button>
  <span class="lvb" style="--c:{lv_color}">{lv_name}</span>
  <a class="item-t" href="{it['u']}.html">{html.escape(ALL[it['u']]['title'])}</a>
  {f'<span class="item-note">{html.escape(it["note"])}</span>' if it['note'] else ''}
  <span class="item-meta"><span class="srcb" style="--c:{src_color}">{src_name}</span><span class="mins">{it['m']} 分钟</span></span>
</div>''')
        n = len(items)
        ac = cards[si] if si < len(cards) else None
        action_html = ''
        if ac:
            btns = ''.join(f'<a class="action-btn" href="{u}">{html.escape(t)}</a>' for t, u in ac['actions'])
            related = ''
            if ac.get('related_workbench'):
                related = f'<div class="action-related">→ 对应实训阶段：{html.escape(ac["related_workbench"])}</div>'
            action_html = f'''<div class="action-card">
  <div class="action-g">💡 本阶段练什么：{html.escape(ac['goal'])}</div>
  <div class="action-b">{btns}</div>
  {related}
</div>'''
        stages.append(f'''<section class="stage">
  <div class="stage-head"><span class="stage-no">阶段 {si+1}</span>
    <div><h3>{sname}</h3><p>{sdesc}</p></div>
    <div class="stage-prog"><div class="sp-bar"><span data-sp="path-{g['id']}-{si}"></span></div><em data-spn="path-{g['id']}-{si}">0/{n}</em></div>
  </div>
  {''.join(rows)}
  {action_html}
</section>''')
    core = f'''<div class="crumb"><a href="index.html">首页</a><span>/</span><span>学习路径</span></div>
<section class="path-hero">
  <div class="path-icon">{g['icon']}</div>
  <div><h1>{g['name']}</h1><p class="who">适合：{g['who']}</p><p class="pdesc">{g['desc']}</p>
  <div class="path-stats"><span>4 个阶段</span><span>{g['total_n']} 个学习项</span><span>约 {g['total_m']//60} 小时 {g['total_m']%60} 分钟</span></div></div>
  <div class="path-ring"><svg viewBox="0 0 84 84" width="84" height="84"><circle cx="42" cy="42" r="36" fill="none" stroke="#e8ecf3" stroke-width="8"/><circle id="ring-path-{g['id']}" cx="42" cy="42" r="36" fill="none" stroke="#2563eb" stroke-width="8" stroke-linecap="round" stroke-dasharray="226.2" stroke-dashoffset="226.2" transform="rotate(-90 42 42)"/></svg><b id="ringtxt-path-{g['id']}">0%</b></div>
</section>
{''.join(stages)}
<div class="path-tip">进度保存在本机浏览器（localStorage）。点击条目左侧方框即可打卡，随时回来继续。</div>'''
    out = page_head(f'{g["name"]} · 学习路径 · {SITE_NAME}', g['desc']) + topbar() + \
        f'<div class="layout"><aside class="side" id="side">{sidebar("paths")}</aside><main class="main">{core}</main></div><div class="mask" id="mask"></div>' + \
        '<div class="reading-bar" id="rbar"></div><script src="assets/hub.js"></script>\n</body></html>'
    (OUT / f'path-{g["id"]}.html').write_text(out, encoding='utf-8')

for g in GOALS:
    gen_path(g)
for g in GOALS:
    # 在每条路径末尾给出下一步实训入口。
    p = OUT / f'path-{g["id"]}.html'
    page = p.read_text(encoding='utf-8')
    marker = '<div class="path-tip">'
    page = page.replace(marker, '<div class="path-next"><b>学完路线后，进入交付实训</b><p>建议先完成企业知识助手入门项目的七阶段任务，再用自评检查证据并导出作品记录。</p><a class="primary-btn" href="workbench.html">开始入门实训 →</a>　<a href="paths.html">返回路线选择</a></div>' + marker)
    p.write_text(page, encoding='utf-8')

primary_goals = [next(g for g in GOALS if g['id'] == gid) for gid in ('career', 'engineer', 'presales')]
secondary_goals = [g for g in GOALS if g['id'] not in ('career', 'engineer', 'presales')]
path_cards = ''.join(f'''<a class="goal-card" href="path-{g['id']}.html" data-gk="path-{g['id']}">
  <div class="gc-top"><span class="gc-icon">{g['icon']}</span><span class="gc-prog" data-gp="path-{g['id']}"></span></div>
  <div class="gc-t">{g['name']}</div><div class="gc-who">{g['who']}</div>
  <div class="gc-m">{g['total_n']} 个学习项 · 约 {g['total_m']//60}h{g['total_m']%60}m →</div>
</a>''' for g in primary_goals)
paths_core = f'''<div class="crumb"><a href="index.html">首页</a><span>/</span><span>学习路线</span></div>
<section class="path-hero slim"><div><h1>选择适合你的学习路线</h1><p class="pdesc">每条路线都从岗位认知走向业务与技术实践，最后进入同一套企业知识助手入门实训。完成后可自评证据并导出作品记录。</p></div></section>
<div class="goal-grid">{path_cards}</div>
<details class="secondary-paths"><summary>管理者与决策者路线</summary><div class="goal-grid">{''.join(f'<a class="goal-card" href="path-{g["id"]}.html"><div class="gc-top"><span class="gc-icon">{g["icon"]}</span></div><div class="gc-t">{g["name"]}</div><div class="gc-who">{g["who"]}</div></a>' for g in secondary_goals)}</div></details>
<div class="path-next"><b>不确定从哪条开始？</b><p>建议按默认路径：认识 FDE 岗位 → 完成企业知识助手入门项目 → 自评检查并导出作品。</p><a class="primary-btn" href="index.html">回到开始学习 →</a></div>'''
paths_out = page_head(f'学习路线 · {SITE_NAME}', '为转行求职、在职工程师和售前交付从业者设计的 FDE 学习路线') + topbar() + \
    f'<div class="layout"><aside class="side" id="side">{sidebar("paths")}</aside><main class="main">{paths_core}</main></div><div class="mask" id="mask"></div>' + \
    f'<script>window.HUB_PATHS={PATHS_JS};</script><script src="assets/hub.js"></script>\n</body></html>'
(OUT / 'paths.html').write_text(paths_out, encoding='utf-8')
print('✓ 学习路线总览 + 5 条详细路径')

# ================================================================ 知识图谱页
graph_core = f'''<div class="crumb"><a href="index.html">首页</a><span>/</span><span>知识图谱</span></div>
<section class="path-hero slim"><div><h1>FDE 知识图谱</h1>
<p class="pdesc">{len(G_NODES)} 个核心概念 · {len(G_EDGES)} 条关系。实线箭头 = 前置依赖（建议先学），虚线 = 相关联。拖拽节点调整布局，点击节点查看释义与对应内容。</p></div></section>
<div class="domain-chips" id="chips"></div>
<div class="graph-wrap"><canvas id="gcanvas"></canvas>
  <aside class="node-panel" id="npanel" hidden></aside>
  <div class="graph-legend" id="legend"></div>
</div>'''
graph_out = page_head(f'知识图谱 · {SITE_NAME}', 'FDE 领域交互式知识图谱') + topbar() + \
    f'<div class="layout"><aside class="side" id="side">{sidebar("graph")}</aside><main class="main">{graph_core}</main></div><div class="mask" id="mask"></div>' + \
    f'''<script>
const NODES = {NODES_JS};
const EDGES = {EDGES_JS};
const DOMAINS = {json.dumps(DOMAINS, ensure_ascii=False)};
const PATHKEYS = {PATHS_JS};
</script>
<script src="assets/graph.js"></script>
<script src="assets/hub.js"></script>
</body></html>'''
(OUT / 'graph.html').write_text(graph_out, encoding='utf-8')
print('✓ 知识图谱页')

# ================================================================ library / about / index
def card(s):
    d = ALL[s]
    _, c = SRC_META[d['src']]
    return f'''<a class="card" href="{s}.html"><div class="card-top"><span class="srcb" style="--c:{c}">{SRC_META[d['src']][0]}</span><span class="mins">{CHARS[s]:,} 字</span></div>
<div class="card-t">{html.escape(d['title'])}</div><div class="card-d">{html.escape(d['desc'][:110])}</div></a>'''

RADAR_SNAP = ROOT / 'data/radar/china_2026-09-17.json'
if not RADAR_SNAP.is_file():
    raise SystemExit(f'缺少历史招聘快照：{RADAR_SNAP}')
RADAR_PERIOD = json.loads(RADAR_SNAP.read_text(encoding='utf-8')).get('period', '日期未提供')

curated = ['ch04', 'book02', 'topic05', 'hb7', 'hb9', 'playbook']
curated = [s for s in curated if s in ALL]
source_groups = [
    ('FDE-Wiki 调研报告', ['part1','part2','part3','part4'] + [f'ch{n:02d}' for n in range(1,24)]),
    ('范冰《FDE 入门指南》', list(BOOK)),
    ('FDE-Handbook 中文版', [f'hb{i}' for i in range(1,12)]),
    ('英文路线图与资源', ['roadmap','awesome-fde']),
    ('OpenFDE 方法资料', ['tools','playbook']),
    ('深度专题', [s for s in WIKI if s.startswith('topic')]),
    ('报告附属页', ['appendix','tags','companies','guestbook']),
]
all_library_sections = ''.join(f'<details class="library-source"><summary>{title} · {len([s for s in slugs if s in ALL])} 项</summary><div class="cards">{"".join(card(s) for s in slugs if s in ALL)}</div></details>' for title, slugs in source_groups)
lib_core = f'''<div class="crumb"><a href="index.html">首页</a><span>/</span><span>知识库</span></div>
<section class="path-hero slim"><div><h1>知识库 · {len(ALL)} 篇内容</h1>
<p class="pdesc">先按手头任务查精选资料；需要完整原文时展开下方来源目录。也可用顶部搜索直达任意文章。</p></div></section>
<h2 class="sec-h">按任务精选</h2>
<div class="cards">{''.join(card(s) for s in curated)}</div>
<details class="library-source"><summary>招聘与行业历史快照 · 非实时数据</summary>
<p class="snapshot-note">招聘雷达：{html.escape(RADAR_PERIOD)}；行业舆情采集日：{html.escape(YQ.SOURCE['collected'])}。两者都是静态快照，不代表实时岗位或当前舆情。</p>
<div class="cards"><a class="card" href="radar.html"><div class="card-t">FDE 中国招聘雷达</div><div class="card-d">历史静态快照 · {html.escape(RADAR_PERIOD)}；页面内附统计口径与限制。</div></a><a class="card" href="sentiment.html"><div class="card-t">FDE 行业舆情</div><div class="card-d">历史静态快照 · 采集日 {html.escape(YQ.SOURCE['collected'])}；样本不代表全体从业者。</div></a></div></details>
<h2 class="sec-h">完整原文与专题</h2>{all_library_sections}
<p class="foot-note">更多辅助页面：<a href="graph.html">知识图谱</a> · <a href="videos.html">视频资源</a> · <a href="about.html">来源与版权</a> · <a href="profile.html">能力档案</a></p>'''
lib_out = page_head(f'知识库 · {SITE_NAME}', '') + topbar() + \
    f'<div class="layout"><aside class="side" id="side">{sidebar("library")}</aside><main class="main">{lib_core}</main></div><div class="mask" id="mask"></div>' + \
    '<script src="assets/hub.js"></script>\n</body></html>'
(OUT / 'library.html').write_text(lib_out, encoding='utf-8')

about_core = f'''<div class="crumb"><a href="index.html">首页</a><span>/</span><span>来源与版权</span></div>
<section class="path-hero slim"><div><h1>内容来源与版权说明</h1><p class="pdesc">本站是学习用途的聚合与重组，全部正文版权归原作方所有。</p></div></section>
<div class="about-list">
<div class="about-card"><h3>本站定位：免费FDE实训平台</h3>
<p>FDE 开放联盟是一个<b>开放的 FDE 学习与模拟实训平台</b>：以「交付实训」为核心（{len(WB.PROJECTS)} 个虚构企业项目 × 7 阶段任务包，含诊断、带出处辅导、作品提交与逐项证据自评），并支持通过 <a href="profile.html">能力档案</a>导出本机学习记录。项目用于模拟交付练习，不是客户案例或第三方认证。下方 6 个内容来源构成可搜索知识底座。平台不设账号、不上传任何数据，进度与档案仅存于读者本机浏览器。网站当前免费、无需注册。</p></div>
<div class="about-card"><h3>授权说明</h3><p>原创代码的公开许可将在源码仓库标明；转载的第三方文章以原作者声明为准（下方逐项说明）。其中范冰《入门指南》为非商业转载，FDE-Handbook 以 CC BY-NC-SA 4.0 引用；OpenFDE 本站此前标注 CC BY-SA 4.0，本地材料尚未核实，待确认。建议使用前核对各原仓库的最新授权。</p></div>
<div class="about-card"><h3><a href="https://github.com/zhyese/fde-wiki" target="_blank" rel="noopener">FDE-Wiki 调研报告</a></h3>
<p>2026-06-21 由 zhyese（adewdew）发布，AI 辅助深度调研生成（与 Claude 共同署名），约 35 万中文字（原报告自述，本站实测正文 35 万+ 字相符）。93 篇 = 4 篇章导语 + 23 章 + 62 专题 + 4 篇附属页（附录、标签、公司索引、留言板）。</p></div>
<div class="about-card"><h3><a href="https://github.com/xdash/FDE-the-Guidance-Book-of-Forward-Deployed-Engineer" target="_blank" rel="noopener">范冰《FDE 前沿部署工程师入门指南》</a></h3>
<p>《增长黑客》作者范冰基于原书框架、以 AI 深度调研生成的开源手册（含 165 个真实案例，原书自述），官网 fde4.ai。原仓库声明：免费阅读与非商业分享，转载需注明出处；商业用途须经作者书面许可。本站为公开学习站点，转载范围与用途须遵守原作者声明；本站不据此主张或暗示获得商业授权。请在使用前核对原仓库当前授权。</p></div>
<div class="about-card"><h3><a href="https://github.com/goday-org/FDE-Handbook" target="_blank" rel="noopener">FDE-Handbook（中文版）</a></h3>
<p>11 章工程手册：企业数据审计、混合云、VPC-SC、企业 RAG、多 Agent、LLM 评估。正文以 CC BY-NC-SA 4.0 授权，本站按同方式引用并注明。</p></div>
<div class="about-card"><h3><a href="https://github.com/pierpaolo28/Awesome-FDE-Roadmap" target="_blank" rel="noopener">Awesome-FDE-Roadmap</a></h3>
<p>1.1k★ 的 FDE 学习路线图（英文），数据工程 → GCP 云架构 → 顾问思维 → AI Agent → 面试准备。以原仓库 LICENSE 为准。</p></div>
<div class="about-card"><h3><a href="https://github.com/yzyunzhang/Awesome-FDE" target="_blank" rel="noopener">Awesome-FDE</a></h3>
<p>FDE 资源、公司与招聘渠道清单（英文）。以原仓库 LICENSE 为准。</p></div>
<div class="about-card"><h3><a href="https://github.com/OpenFDEAI/OpenFDE" target="_blank" rel="noopener">OpenFDE（工具地图 + 实战蓝皮书）</a></h3>
<p>FDE 开源知识社区（open-fde.com）的两份核心文档：《FDE 所需工具地图》（AI-native 交付底座与客户选型地图）与《FDE 实战蓝皮书》（客户分层 × 行业打法 × 切入点方法论）。文档内容本站此前标注 <b>CC BY-SA 4.0</b>，本地材料尚未核实，待确认；站内互链已改为本站页面，并保留原文与出处标注。</p></div>
</div>
<p class="foot-note">本站知识图谱与学习路径为编辑性重组（标注了每项内容的深度层级与前置关系），未改动原文观点。学习进度数据仅保存在读者本机浏览器，不上传。</p>'''
about_out = page_head(f'来源与版权 · {SITE_NAME}', '') + topbar() + \
    f'<div class="layout"><aside class="side" id="side">{sidebar("about")}</aside><main class="main">{about_core}</main></div><div class="mask" id="mask"></div>' + \
    '<script src="assets/hub.js"></script>\n</body></html>'
(OUT / 'about.html').write_text(about_out, encoding='utf-8')
print('✓ 总览 + 版权页')

# ================================================================ 视频资源页
V_SECTIONS = [
    ('#2563eb', '🥇 系统直播课（免费）', [
        ('Datawhale「AI+X 创造节 · FDE 实战营」', 'https://www.datawhale.cn/',
         '首推。围绕真实 AI 项目从业务理解→需求拆解→方案设计→原型构建→交付运营的完整链路，规划 20 场系列直播，还在进行中。嘉宾含 Cherry Studio 商业化&FDE 负责人、零一万物解决方案负责人、一线 FDE 工程师等。配套组队实战营与多城线下课，报名与回放见官网「活动」页或公众号「Datawhale」。'),
        ('Datawhale「FDE 来碰头」线下活动', 'https://www.datawhale.cn/',
         '杭州云谷中心，500 人报名、6 位一线 FDE 实践者分享（企业服务/消费品/法律/企业级 Agent），九组圆桌讨论落地门槛。相关纪要与后续场次见 Datawhale 官网与公众号。'),
    ]),
    ('#7c3aed', '🥈 B 站录播（免费，直接搜标题）', [
        ('《FDE 模式保姆级教程：前 Palantir 研发负责人谈 FDE 三大纪律八项注意》', 'https://search.bilibili.com/all?keyword=FDE%E6%A8%A1%E5%BC%8F%20%E4%BF%9D%E5%A7%86%E7%BA%A7%E6%95%99%E7%A8%8B',
         '首推入门。Bob McGrew（Palantir 第二号员工、前 OpenAI 首席研究官）亲述 FDE 模式由来、Echo-Delta 编队、碎石路与高速公路比喻、产品化沉淀逻辑。约 50 分钟，中英字幕。'),
        ('《揭秘年薪百万美元的 AI 工作：FDE》（Greg Isenberg × Vas）', 'https://www.youtube.com/watch?v=zXysLUTLjw4',
         '审计→评测→部署三步方法论 + 30 天学习计划。约 51 分钟，YouTube 有中英双语版，B 站可搜到中文搬运。'),
        ('B 站专栏《AI 越会写代码，企业越容易制造垃圾》+ 免费交互教程《阿一 FDE 从入门到精通》', 'https://www.bilibili.com/read/cv52868434',
         '图文专栏：FDE 五层组织能力拆解 + 真假 FDE 经济账；文末附八堂课交互教程（拆解旧金山八场顶级实战演讲）。'),
    ]),
    ('#0d9488', '🎧 音频 / 播客（免费，通勤可听）', [
        ('蜻蜓 FM《前线部署工程师(FDE) 有声版｜范冰著》', 'https://www.qingting.fm/',
         '范冰开源书的有声版（平台页标注「20 万字·全本」），10 集全（自序、第 1-8 章含完整案例集、后记；不含附录 A-C）。入口：蜻蜓FM 网站或 App 内搜索「前线部署工程师」，节目频道页以平台内实际结果为准。'),
        ('Apple 播客 / 小宇宙《光华 David：FDE 开源版全书精华》', 'https://podcasts.apple.com/cn/podcast/claude-fable-5%E5%AE%98%E6%96%B9%E5%8D%9A%E6%96%87%E7%B2%BE%E5%8D%8E/id1827758935',
         '39 分钟全书精华解读，小宇宙有文字稿。金句：「驻场卖的是人头，FDE 卖的是结果」「上线只是行政事件，激活才是行为事件」。'),
    ]),
    ('#d97706', '📚 免费文字配套', [
        ('范冰《FDE 入门指南》官网 fde4.ai / GitHub 开源全书', 'https://fde4.ai',
         '165 个真实可查案例（原书自述），本站「范冰《FDE 入门指南》」分组即全文转载。'),
        ('FDE 学习路线图 guoyanan.cn/fde 与 lingmo.fun', 'https://guoyanan.cn/fde',
         '两个免费 FDE 学习路线图，内含大量 B 站免费视频资源索引（Linux / RAG / Agent 等基础课）。'),
    ]),
    ('#dc2626', '⚠️ 注意甄别（非免费）', [
        ('极客时间《FDE 业务落地实战》（神策数据 CTO 曹犟，26 讲）', 'https://time.geekbang.org/column/intro/101180001/intro',
         '约 ¥59-99。质量口碑好，免费试读部分章节；预算允许值得买，不属免费资源，仅作对照。'),
        ('各类「工信部 FDE 证书班」（约 ¥5800/人）与付费训练营', '#',
         '营销味重、性价比存疑，本站不推荐，请自行判断。'),
    ]),
]
v_secs = ''
for color, sec_title, items in V_SECTIONS:
    cards = ''.join(f'''<div class="about-card"><h3><a href="{u}" target="_blank" rel="noopener">{html.escape(t)}</a></h3><p>{html.escape(d)}</p></div>''' for t, u, d in items)
    v_secs += f'<h2 class="sec-h" style="--c:{color}">{sec_title}</h2><div class="about-list">{cards}</div>'
videos_core = f'''<div class="crumb"><a href="index.html">首页</a><span>/</span><span>视频资源</span></div>
<section class="path-hero slim"><div><h1>国内免费 FDE 视频/直播资源汇总</h1>
<p class="pdesc">直播、录播、播客、配套图文全收录（整理于 2026-09）。直播类活动以主办方官方渠道的报名与回放信息为准。</p></div></section>
{v_secs}
<p class="foot-note">建议路线：先看 Bob McGrew 那期建立认知（50 分钟）→ 跟 Datawhale 实战营系统学 → 通勤听范冰有声书补案例 → 动手做实战营案例原型。</p>'''
videos_out = page_head(f'视频资源 · {SITE_NAME}', '') + topbar() + \
    f'<div class="layout"><aside class="side" id="side">{sidebar("videos")}</aside><main class="main">{videos_core}</main></div><div class="mask" id="mask"></div>' + \
    '<script src="assets/hub.js"></script>\n</body></html>'
(OUT / 'videos.html').write_text(videos_out, encoding='utf-8')
print('✓ 视频资源页')

# ================================================================ 招聘雷达页（读取 fde-radar-china 快照）
if RADAR_SNAP.exists():
    RS = json.loads(RADAR_SNAP.read_text(encoding='utf-8'))
    MK_NAME = {'national': '全国', 'beijing': '北京', 'shanghai': '上海', 'shenzhen': '深圳',
               'overseas': '海外', 'hangzhou': '杭州', 'hongkong': '中国香港', 'chengdu': '成都',
               'guangzhou': '广州', 'wuhan': '武汉', 'xian': '西安'}
    MK_NOTE = {'national': '唯一岗位计数（全国口径）', 'overseas': '被追踪中国公司的海外岗位'}
    nat = RS['markets']['national']
    period = RS['period']
    RADAR_PERIOD = period

    mk_rows = ''
    for mk in RS['marketOrder']:
        m = RS['markets'][mk]
        note = f'<span class="mk-note">{MK_NOTE.get(mk, "")}</span>' if mk in MK_NOTE else ''
        mk_rows += (f'<tr><td><b>{MK_NAME.get(mk, mk)}</b>{note}</td>'
                    f'<td>{m["coreJobs"]}</td><td>{m["extendedJobs"]}</td>'
                    f'<td>{m["coreCompanies"]} / {m["extendedCompanies"]}</td><td>{m["managementRoles"]}</td></tr>')

    from collections import Counter
    comp = Counter(j['company'] for j in RS['jobs']).most_common()
    comp_html = ''.join(f'''<div class="skill-row"><span class="skill-name">{html.escape(c)}</span>
      <div class="skill-bar"><i style="width:{n / comp[0][1] * 100:.0f}%"></i></div>
      <span class="skill-n">{n} 岗</span></div>''' for c, n in comp)

    sk = sorted(RS['skills'], key=lambda s: -s['rate'])
    sk_html = ''.join(f'''<div class="skill-row"><span class="skill-name">{html.escape(s["name"])}</span>
      <div class="skill-bar"><i style="width:{s["rate"]}%"></i></div>
      <span class="skill-n">{s["rate"]}% · {s["count"]} 岗</span></div>''' for s in sk)

    sal = RS['aggregators']['salary']
    src_rows = ''.join(f'<tr><td><b>{html.escape(s["company"])}</b></td><td>{html.escape(s["system"])}</td>'
                       f'<td><a href="{s.get("careerPage", "#")}" target="_blank" rel="noopener">官网</a></td></tr>'
                       for s in RS['sources'])

    radar_core = f'''<div class="crumb"><a href="index.html">首页</a><span>/</span><span>招聘雷达</span></div>
<section class="path-hero slim"><div><h1>FDE 中国招聘雷达</h1>
<p class="snapshot-alert"><b>历史静态快照 · {period}</b>　此页不实时更新，不能代表当前岗位总量或趋势。请按页面采集周期理解数据。</p>
<p class="pdesc">聚焦中国 AI 公司 FDE 劳动力市场信号：只追踪公司官方招聘系统的公开数据，输出核验过的岗位、城市与技能信号——不估算总量，不虚构趋势。本页为 <b>{period}</b> 周度快照的静态镜像，与 fde-radar-china 项目数据契约同构。</p></div></section>

<div class="hero-stats" style="max-width:860px;margin:0 auto 8px">
  <div><b>{nat['coreJobs']}</b><span>核心 FDE 岗位</span></div>
  <div><b>{nat['extendedJobs']}</b><span>追踪岗位总数</span></div>
  <div><b>{nat['extendedCompanies']}</b><span>追踪公司</span></div>
  <div><b>{RS['coverage']['boardsMeasured']}</b><span>官方数据源</span></div>
</div>
<p class="foot-note" style="max-width:860px;margin:0 auto 26px">核心口径：forward-deployed 精确职位名 + 中文等价词（前沿部署/前线部署/客户部署工程师）；扩展口径：预定义中文部署型职位族，大厂岗需 JD 含 AI 信号。</p>

<h2 class="sec-h" style="--c:#2563eb">🗺 城市市场（岗位出现次数：多城市岗位在每个城市各计一次）</h2>
<div class="table-wrap" style="max-width:860px;margin:0 auto">
<table><thead><tr><th>市场</th><th>核心岗位</th><th>全部岗位</th><th>公司（核心/扩展）</th><th>管理岗</th></tr></thead>
<tbody>{mk_rows}</tbody></table></div>

<h2 class="sec-h" style="--c:#7c3aed">🏢 公司岗位分布（本次采集快照的样本分布，非市场总量）</h2>
<div class="skill-list" style="max-width:860px;margin:0 auto">{comp_html}</div>
<p class="foot-note" style="max-width:860px;margin:8px auto 26px">分母说明：以下比例仅描述本快照 241 岗的采集样本（其中字节跳动占约 78%，因其招聘板岗位基数最大且含大量部署型扩展口径岗位），<b>不等于中国 FDE 市场的公司分布</b>；核心 FDE 仅 {nat['coreJobs']} 岗，扩展集合口径宽于 FDE 本岗。</p>

<h2 class="sec-h" style="--c:#0d9488">🛠 技能信号（JD 提及率，样本 {nat['extendedJobs']} 岗）</h2>
<div class="skill-list" style="max-width:860px;margin:0 auto">{sk_html}</div>
<p class="foot-note" style="max-width:860px;margin:8px auto 26px">解读：「客户面向」73% 印证 FDE 的岗位本质——对业务结果负责；LLM/Agent/RAG 是技术主轴。评测（Evals）提及率 19%，只能作为岗位技术深度的线索之一——<b>JD 未提及不等于岗位不需要</b>，不宜据此判断岗位优劣。</p>

<h2 class="sec-h" style="--c:#d97706">💰 薪资参考（聚合器口径，独立于官方板统计）</h2>
<div class="hero-stats" style="max-width:860px;margin:0 auto 8px">
  <div><b>{sal['median']:,}</b><span>中位数 {sal['unit']}</span></div>
  <div><b>{sal['p25']:,}</b><span>P25</span></div>
  <div><b>{sal['p75']:,}</b><span>P75</span></div>
  <div><b>{sal['sample']}</b><span>样本量</span></div>
</div>
<p class="foot-note" style="max-width:860px;margin:0 auto 26px">来自聚合平台采样（智联招聘等，召回 {RS['aggregators']['recallTotal']} 条、发现 {len(RS['aggregators']['newEmployers'])} 家官方板之外的新雇主），未经官方核验、可能跨平台重复。样本仅 {sal['sample']} 条且职位族/城市/经验构成未知，薪资为招聘信息区间的中值统计而非实际录用薪资，<b>不可与技术章节中的海外总包或国内头部报价直接比较</b>。<b>数据铁律：覆盖不全的统计会失真——聚合器数据单独展示，绝不与官方口径合并。</b></p>

<h2 class="sec-h" style="--c:#dc2626">📡 官方数据源（8 个，直采自公司招聘系统 API）</h2>
<div class="table-wrap" style="max-width:860px;margin:0 auto">
<table><thead><tr><th>公司</th><th>招聘系统</th><th>入口</th></tr></thead>
<tbody>{src_rows}</tbody></table></div>
<p class="foot-note" style="max-width:860px;margin:8px auto 26px">已核实暂未接入：深度求索（无公开职位板）、面壁智能（未发现公开板）、科大讯飞（北森待适配）、昆仑万维（待适配）。聚合平台中：猎聘拦截自动化采集、BOSS 直聘强制登录且 ToS 禁止自动化，均不接入。</p>

<p class="foot-note" style="max-width:860px;margin:0 auto">完整动态版（周更、城市市场页、方法论 20 项指标权重）见 fde-radar-china 项目，数据快照不可变、始终可审计。<br>
<b>快照提示</b>：本页数据仅对应上述周期，不能据此推断当前岗位变化。</p>'''
    radar_out = page_head(f'招聘雷达 · {SITE_NAME}', '') + topbar() + \
        f'<div class="layout"><aside class="side" id="side">{sidebar("radar")}</aside><main class="main">{radar_core}</main></div><div class="mask" id="mask"></div>' + \
        '<script src="assets/hub.js"></script>\n</body></html>'
    (OUT / 'radar.html').write_text(radar_out, encoding='utf-8')
    print(f"✓ 招聘雷达页（周期 {period}，{nat['extendedJobs']} 岗）")
else:
    print('⚠ 未找到雷达快照，跳过 radar.html')

# ================================================================ 行业舆情页（六平台 FDE 舆情报告，来源：飞书文档）
def _yq_inline(s):
    """**粗体** → <b>，其余转义"""
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', html.escape(s))

def _yq_blocks(items):
    out, ul = [], []
    for kind, txt in items:
        if kind == 'li':
            ul.append(f'<li>{_yq_inline(txt)}</li>')
        else:
            if ul:
                out.append('<ul>' + ''.join(ul) + '</ul>'); ul = []
            out.append(f'<p>{_yq_inline(txt)}</p>')
    if ul:
        out.append('<ul>' + ''.join(ul) + '</ul>')
    return ''.join(out)

# 修正说明（原报告问题已修正，此处记录改动与核验依据）
nb = ''.join(f'<div class="yq-nb-item"><b>{html.escape(n["title"])}</b><span>{html.escape(n["detail"])}</span></div>'
             for n in YQ.EDITOR_NOTES)
yq_note = f'''<div class="yq-nb">
  <h3>✅ 本站修正说明：原报告的数据问题已逐条核实并更正</h3>
  <p class="hint">本站对原报告做了独立核验，并对其中确有问题的条目<strong>直接修正</strong>（链接更正、缺失链接补全、总条数与口径统一），修正依据与结果如下。为保证可核对，被改动的条目在明细中带「链接已更正」「本站补链」标记。</p>
  {nb}
</div>'''

# 态势与热度小节
secs_html = ''
for group, h2 in ((YQ.OVERVIEW, '📊 舆情整体态势'), (YQ.HEAT, '🌡 热度与分布特征')):
    secs_html += f'<h2 class="sec-h">{h2}</h2>'
    for s in group:
        secs_html += f'<div class="yq-sec"><h3>{html.escape(s["h"])}</h3>{_yq_blocks(s["items"])}</div>'

# 图表 1：各平台样本量
mx = max(n for _, n, _ in YQ.PLAT_SAMPLE)
ch1 = ''.join(f'''<div class="yq-bar"><span class="lb">{html.escape(cn)}</span>
  <span class="track"><i style="width:{n / mx * 100:.0f}%;background:{c}"></i></span>
  <span class="vl">{n} 条</span></div>''' for cn, n, c in YQ.PLAT_SAMPLE)

# 图表 2：B 站播放量（按原文序号）
mx2 = max(n for _, n in YQ.BILI_PLAY)
ch2 = ''.join(f'''<div class="yq-bar"><span class="lb">{i+1:02d}</span>
  <span class="track"><i style="width:{n / mx2 * 100:.0f}%;background:#7c3aed"></i></span>
  <span class="vl">{n/10000:.1f}万</span></div>''' for i, (t, n) in enumerate(YQ.BILI_PLAY))

charts = f'''<div class="yq-charts">
  <div class="yq-chart"><h4>多平台样本量</h4>
    <p class="cap">{len(YQ.PLATFORMS)} 平台共 {sum(len(p['entries']) for p in YQ.PLATFORMS)} 条可溯源内容。样本量为检索所得条目数，不代表平台真实讨论总量。</p>{ch1}</div>
  <div class="yq-chart"><h4>B站视频播放量分布</h4>
    <p class="cap">按原文条目序号（01–12）。播放量头部为培训账号的长课，深度内容播放量反而靠后。</p>{ch2}</div>
</div>'''

# 平台明细
def _badge(e):
    ten = e['ten']
    m = re.match(r'^([^（(]+)[（(](.+?)[）)]', ten)
    base, qual = (m.group(1), m.group(2)) if m else (ten, '')
    base = base.replace('偏负向', '偏负').replace('中性', '中立')
    cls = {'pos': 'pos', 'neu': 'neu', 'neg': 'neg'}[e['st']]
    b = f'<span class="yq-badge {cls}">{html.escape(base)}</span>'
    if qual:
        b += f' <span class="yq-badge gray">{html.escape(qual)}</span>'
    if e.get('lsrc') == 'added':
        b += ' <span class="yq-badge add">本站补链</span>'
    elif e.get('lsrc') == 'fixed':
        b += ' <span class="yq-badge fix">链接已更正</span>'
    return b

def _entry(e):
    t = html.escape(e['t'])
    if e['u']:
        t = f'<a href="{html.escape(e["u"])}" target="_blank" rel="noopener">{t}</a>'
    meta = [f'<span class="who">{html.escape(e["a"])}</span>']
    if e['d']: meta.append(html.escape(e['d']))
    if e['s']: meta.append(f'信源：{html.escape(e["s"])}')
    meta.append(_badge(e))
    x = f'<div class="x">{_yq_inline(e["x"])}</div>' if e['x'] else ''
    return (f'<div class="yq-entry s-{e["st"]}"><div class="t">{t}</div>'
            f'<div class="m">{"".join(meta)}</div>{x}</div>')

plats_html = '<div class="yq-plat">'
for p in YQ.PLATFORMS:
    es = p['entries']
    c = {k: sum(1 for e in es if e['st'] == k) for k in ('pos', 'neu', 'neg')}
    plats_html += f'''<div class="yq-plat-head"><span class="em">{p['emoji']}</span>
      <span class="nm">{html.escape(p['cn'])}</span><span class="ct">{len(es)} 条</span>
      <span class="nt">{html.escape(p['note'])}</span></div>
      <div class="yq-stance-sum"><span>正向 <b>{c['pos']}</b></span><span>中立 <b>{c['neu']}</b></span><span>负向 <b>{c['neg']}</b></span></div>'''
    plats_html += ''.join(_entry(e) for e in es)
plats_html += '</div>'

bd_html = '<ul>' + ''.join(f'<li>{_yq_inline(b)}</li>' for b in YQ.BOUNDARY) + '</ul>'
refs_html = '<ul>' + ''.join(
    f'<li>{html.escape(t)}：<a href="{html.escape(u)}" target="_blank" rel="noopener">{html.escape(u[:46])}{"…" if len(u) > 46 else ""}</a></li>'
    for t, u in YQ.REFS) + '</ul>'

tot = sum(len(p['entries']) for p in YQ.PLATFORMS)
cen = sum(1 for p in YQ.PLATFORMS for e in p['entries'] if e['st'] == 'neg')

yq_core = f'''<div class="crumb"><a href="index.html">首页</a><span>/</span><span>行业舆情</span></div>
<section class="path-hero slim"><div><h1>FDE 行业舆情</h1>
<p class="snapshot-alert"><b>历史静态快照 · 采集日 {html.escape(YQ.SOURCE['collected'])}</b>　样本不随时间更新，不代表当前行业舆情或全体从业者观点。</p>
<p class="pdesc">FDE 到底火不火？大家在说什么？本页是《{html.escape(YQ.SOURCE['title'])}》的全文镜像与核验——{len(YQ.PLATFORMS)} 个平台 <b>{tot} 条</b>可溯源内容的完整清单。采集日 <b>{YQ.SOURCE['collected']}</b>，为一次性快照，<b>不随周更更新</b>。</p></div></section>

<div class="hero-stats" style="max-width:860px;margin:0 auto 10px">
  <div><b>{tot}</b><span>可溯源内容</span></div>
  <div><b>{len(YQ.PLATFORMS)}</b><span>平台</span></div>
  <div><b>{cen}</b><span>负向条目</span></div>
  <div><b>{len(YQ.EDITOR_NOTES)}</b><span>本站修正项</span></div>
</div>
<p class="yq-src">原报告：<a href="{YQ.SOURCE['url']}" target="_blank" rel="noopener">{html.escape(YQ.SOURCE['title'])}</a>（飞书文档）· 采集日 {YQ.SOURCE['collected']} · 口径：{' / '.join(f"{p['cn']} {len(p['entries'])}" for p in YQ.PLATFORMS)}。<b>舆情不等同于事实</b>——样本来自各平台公开页面检索，仅代表当期公开可见的讨论。</p>

{yq_note}
{secs_html}
{charts}
<p class="foot-note" style="max-width:860px;margin:6px auto 26px">读法建议：先把上面两节（态势 + 热度）当作「市场共识与分歧的分布图」，再按平台看明细。B站看「课程化程度」，脉脉/即刻看「从业者真实观点」，小红书看「普通用户与营销帖的比例」，微博看「媒体与话题传播」，CSDN/掘金/博客园/思否等技术社区看「长文科普与外包质疑」，InfoQ/51CTO 看「行业动作与培训观察」，华为云/阿里云/腾讯云厂商社区看「官方动作、能力模型与落地方法论」。<b>负向条目不要跳过</b>——它们描述的落地困境（被当外包、一线不配合、权限不足）正是<a href="workbench.html">实战工作台</a>要提前训练的能力。</p>

<h2 class="sec-h">📋 {len(YQ.PLATFORMS)} 平台明细（原文 {tot} 条）</h2>
{plats_html}

<h2 class="sec-h">🔍 数据边界与采集说明（原文）</h2>
<div class="yq-bd">{bd_html}</div>

<h2 class="sec-h">🔗 参考来源（原文 {len(YQ.REFS)} 条）</h2>
<div class="yq-refs">{refs_html}</div>
<p class="foot-note" style="max-width:860px;margin:16px auto 0">本页为第三方舆情报告的全文镜像，观点与数据归属原报告；本站仅作结构化整理与独立核验标注，不构成职业或投资建议。相关历史资料及采集日期见知识库中的“招聘与行业历史快照”。</p>'''

yq_out = page_head(f'行业舆情 · {SITE_NAME}', f'FDE {len(YQ.PLATFORMS)} 平台舆情：{tot} 条可溯源内容的态势、热度与明细') + \
    f'<link rel="stylesheet" href="assets/sentiment.css">' + topbar() + \
    f'<div class="layout"><aside class="side" id="side">{sidebar("sentiment")}</aside><main class="main">{yq_core}</main></div><div class="mask" id="mask"></div>' + \
    '<script src="assets/hub.js"></script>\n</body></html>'
(OUT / 'sentiment.html').write_text(yq_out, encoding='utf-8')
print(f'✓ 行业舆情页（{tot} 条 / {len(YQ.PLATFORMS)} 平台 / 修正说明 {len(YQ.EDITOR_NOTES)} 项 / 补链 {sum(1 for p in YQ.PLATFORMS for e in p["entries"] if e.get("lsrc") == "added")} 更正 {sum(1 for p in YQ.PLATFORMS for e in p["entries"] if e.get("lsrc") == "fixed")}）')

# ================================================================ 实训平台（多项目引擎 + 能力档案）
WB_DIMS = [{'id': k, 'name': v['name'], 'desc': v['desc']} for k, v in WB.DIMS.items()]
WB_DATA_JS = json.dumps({
    'projects': WB.PROJECTS,
    'dims': WB_DIMS,
    'dimMap': {k: v['name'] for k, v in WB.DIMS.items()},
    'selfRate': WB.SELF_RATE,
}, ensure_ascii=False, separators=(',', ':'))

wb_core = f'''<div class="crumb"><a href="index.html">首页</a><span>/</span><span>实战工作台</span></div>
<section class="path-hero slim"><div><h1>🛠 FDE 实训平台</h1>
<p class="pdesc">建议先做企业知识助手入门项目；客服、零售、销售和央国企合规场景可作为后续迁移练习。实训提供 7 个阶段的任务说明、参考资料、关键词格式提示与本人自评，不运行代码或独立验证作品。学习记录保存在你的浏览器里。</p>
<p class="dl-lab"><a href="downloads/kb-assistant-lab.zip">⬇ 下载离线练习</a> — 虚构企业数据 + Python 脚本，需本机运行；网站不执行代码。</p></div></section>
<nav class="wb-tabs">
  <a class="wb-tab" href="#home">📚 实训库</a>
  <a class="wb-tab" href="#today">📅 今日</a>
  <a class="wb-tab" href="#diag">📋 诊断</a>
  <a class="wb-tab" href="#skills">🗺 学习记录</a>
  <a class="wb-tab" href="#data">💾 数据</a>
</nav>
<div id="wb-view"></div>
<p class="foot-note">建议先完成企业知识助手入门项目，其余四项可作为行业迁移练习。页面提供关键词格式提示与本人自评，不运行代码，也不独立验证作品；请自行检查提交内容和运行结果。</p>'''
wb_out = page_head(f'实战工作台 · {SITE_NAME}', '企业知识助手入门练习与四个可选迁移练习；包含任务说明、自评与本地学习记录') + \
    f'<link rel="stylesheet" href="assets/workbench.css">' + topbar() + \
    f'<div class="layout"><aside class="side" id="side">{sidebar("workbench")}</aside><main class="main">{wb_core}</main></div><div class="mask" id="mask"></div>' + \
    f'<script>window.WB_DATA={WB_DATA_JS};</script>\n<script src="assets/workbench.js"></script>\n<script src="assets/hub.js"></script>\n</body></html>'
(OUT / 'workbench.html').write_text(wb_out, encoding='utf-8')
print(f'✓ 实战工作台（实训库 {len(WB.PROJECTS)} 项目 / {sum(len(p["stages"]) for p in WB.PROJECTS)} 阶段 / {sum(len(p["quiz"]) for p in WB.PROJECTS)} 诊断题）')

# ---------------- 能力档案（跨项目聚合 + 导出） ----------------
profile_core = '''<div class="crumb"><a href="index.html">首页</a><span>/</span><span>学习记录</span></div>
<section class="path-hero slim"><div><h1>📊 能力档案</h1>
<p class="pdesc">汇总你在实训中的提交与自评记录，支持导出 JSON 备份或 PNG 图片分享。页面提供关键词格式提示与本人自评，不运行代码，也不独立验证作品；这些记录不是第三方认证。</p></div></section>
<div id="pf-view"></div>
<p class="foot-note">完成企业知识助手入门项目后，可继续选择客服、零售、销售或央国企合规场景作迁移练习。所有进度数据仅保存在本机浏览器。</p>'''
profile_out = page_head(f'能力档案 · {SITE_NAME}', 'FDE 实训平台能力档案：跨项目六维证据聚合，支持导出 JSON/PNG 分享') + \
    f'<link rel="stylesheet" href="assets/workbench.css"><link rel="stylesheet" href="assets/profile.css">' + topbar() + \
    f'<div class="layout"><aside class="side" id="side">{sidebar("profile")}</aside><main class="main">{profile_core}</main></div><div class="mask" id="mask"></div>' + \
    f'<script>window.PF_DATA={json.dumps({"projects": [{"id": p["id"], "title": p["title"], "tier": p["tier"], "tag": p["tag"], "stages": [{"id": s["id"], "title": s["title"], "dim": s["dim"]} for s in p["stages"]]} for p in WB.PROJECTS], "dims": WB_DIMS, "dimMap": {k: v["name"] for k, v in WB.DIMS.items()}}, ensure_ascii=False, separators=(",", ":"))};</script>\n<script src="assets/profile.js"></script>\n<script src="assets/hub.js"></script>\n</body></html>'
(OUT / 'profile.html').write_text(profile_out, encoding='utf-8')
print('✓ 能力档案页')

hub_home = page_head(f'{SITE_NAME} · 免费FDE实训平台', '免费FDE实训平台：以实战工作台为核心，6 个内容来源构成知识底座') + topbar() + \
    f'''<div class="layout"><aside class="side" id="side">{sidebar("index")}</aside><main class="main">
<section class="hero">
  <div class="hero-badge">开放学习 · 虚构数据实训 · {len(set(d['src'] for d in ALL.values()))} 个内容来源</div>
  <h1>FDE 开放联盟<span>· 免费FDE实训平台</span></h1>
  <p class="hero-sub">面向国内 FDE 学习者，建议按一条路径完成第一次练习：<b>认识岗位 → 做企业知识助手入门项目 → 自评检查并导出作品记录。</b>实训使用虚构企业和虚构数据，练习真实交付流程，不代表真实客户项目或第三方认证。</p>
  <div class="hero-stats"><div><b>{len(ALL)}</b><span>篇可搜索内容</span></div><div><b>{len(WB.PROJECTS[0]['stages'])}</b><span>入门项目阶段</span></div><div><b>{len(WB.DIMS)}</b><span>自评能力维度</span></div></div>
</section>
<h2 class="sec-h">建议学习顺序</h2>
<div class="home-steps">
  <a class="home-step" href="orientation.html"><span>01</span><div><b>先认识 FDE 岗位</b><p>几分钟了解工作内容、国内交付约束，以及它和驻场、售前的区别。</p></div><em>读岗位导读 →</em></a>
  <a class="home-step" href="workbench.html"><span>02</span><div><b>完成企业知识助手入门项目</b><p>以虚构企业数据走过业务发现、数据审计、检索、评估、交付和验收。</p></div><em>开始入门实训 →</em></a>
  <a class="home-step" href="profile.html"><span>03</span><div><b>自评检查并导出作品</b><p>查看六维证据记录，导出 JSON 或 PNG；这是学习记录，不是第三方认证。</p></div><em>查看能力档案 →</em></a>
</div>
<p class="foot-note">想换一条学习顺序？查看 <a href="paths.html">其他学习路线</a>。需要查资料时使用 <a href="library.html">知识库</a> 搜索。</p>
<p class="foot-note">内容聚合自 FDE-Wiki / 范冰《FDE 入门指南》/ FDE-Handbook / Awesome-FDE-Roadmap / Awesome-FDE / OpenFDE，版权归原作者所有，详见 <a href="about.html">来源与版权</a>。</p>
</main></div><div class="mask" id="mask"></div>
<script>window.HUB_PATHS={PATHS_JS};</script>
<script src="assets/hub.js"></script>
</body></html>'''
(OUT / 'index.html').write_text(hub_home, encoding='utf-8')

# 新手岗位导读：优先给首次访问者一个可在几分钟内读完的起点。
orientation_core = f'''<div class="crumb"><a href="index.html">首页</a><span>/</span><span>认识 FDE</span></div>
<section class="path-hero slim"><div><h1>FDE 在做什么？</h1><p class="pdesc">用几分钟了解这个岗位，再决定从哪个实训开始。</p></div></section>
<div class="orientation-body">
<section class="about-card"><h2>把业务问题带到可用的系统</h2>
<p>FDE（前沿部署工程师）在客户业务现场与工程团队之间工作。通常先理解业务流程和目标：谁遇到什么问题、现有做法哪里受阻、怎样判断改善有效。随后梳理数据、权限和系统接口，选择技术方案，做出原型并逐步走向部署、评估和使用反馈。关键产出不只是代码，还包括清楚的范围、可运行的方案、风险边界、使用方式和维护交接。FDE 需要在业务语言与工程细节之间转换；不同公司的职责边界会不同，不能只凭职位名称判断日常工作。</p></section>
<section class="about-card"><h2>国内交付需要尽早确认的条件</h2>
<p>启动时要问清楚数据能否使用、谁有权限、系统部署在哪里、哪些信息不能离开客户环境，以及安全、法务、采购和验收由谁负责。部分客户会提出私有化部署、信创适配或特定采购流程要求；具体范围应以客户实际要求和适用规则为准，不能把个别行业案例当成通用结论。将这些约束写进第一版方案和验证计划，可以减少原型完成后才发现无法接入或上线的返工。</p></section>
<section class="about-card"><h2>和驻场、售前有什么不同？</h2>
<p>驻场描述工作地点或服务安排，本身不说明要对什么结果负责；如果工作只是按单处理、长期补客户人力，未必就是 FDE 的工作方式。售前主要帮助客户理解方案并验证是否值得推进；FDE 可能参与售前，但通常还要继续面对真实数据和系统约束，跟进构建、上线、采用与反馈。区别不在于是否到现场，而在于是否参与问题定义，并持续推动方案进入实际业务使用，再把可复用经验沉淀下来。</p></section>
<p class="orientation-reading">延伸阅读：<a href="ch04.html">FDE 与相邻岗位辨析</a> · <a href="book02.html">先解决正确的问题</a> · <a href="playbook.html">客户分层与切入点方法</a></p>
<div class="path-next"><b>下一步：做企业知识助手入门项目</b><p>用虚构企业资料练习需求、数据、构建、评估和交付。完整长文可按需阅读，不影响开始实训。</p><a class="primary-btn" href="workbench.html">开始入门实训 →</a>　<a href="ch01.html">按需阅读完整岗位介绍</a></div>
</div>'''
orientation_out = page_head(f'认识 FDE · {SITE_NAME}', 'FDE 岗位导读：工作内容、国内交付约束，以及与驻场和售前的区别') + topbar() + \
    f'<div class="layout"><aside class="side" id="side">{sidebar("orientation")}</aside><main class="main">{orientation_core}</main></div><div class="mask" id="mask"></div>' + \
    '<script src="assets/hub.js"></script>\n</body></html>'
(OUT / 'orientation.html').write_text(orientation_out, encoding='utf-8')

(OUT / '404.html').write_text(page_head('页面不存在 · ' + SITE_NAME, '') + topbar() +
    '<div class="layout"><aside class="side" id="side">' + sidebar('') + '</aside><main class="main"><div class="crumb"><a href="index.html">首页</a></div><section class="path-hero slim"><div><h1>页面不存在</h1><p class="pdesc">请从左侧目录重新选择。</p></div></section></main></div><div class="mask" id="mask"></div>' +
    '<script src="assets/hub.js"></script>\n</body></html>', encoding='utf-8')

# 补充框架页进搜索索引（videos/radar/workbench/sentiment 为生成页，不走文档管线）
SEARCH += [
    {'u': 'orientation', 't': '认识 FDE', 'h': 'FDE 在做什么？',
     'x': '岗位导读：客户业务与工程之间的工作、国内项目的数据权限/部署/采购等约束，以及与驻场和售前的区别；含 ch04、book02、实战蓝皮书延伸阅读。', 'a': ''},
    {'u': 'workbench', 't': '实战工作台', 'h': '实训库：5 个项目（7 阶段任务包）',
     'x': '建议先完成企业知识助手入门练习，其余四个虚构企业场景作为可选迁移项目。每个项目提供客户简报、七阶段任务说明、基础诊断、参考资料、作品提交与本人自评；不运行代码或独立验证作品。', 'a': ''},
    {'u': 'workbench', 't': '实战工作台', 'h': '基础诊断与能力地图',
     'x': '基础诊断题覆盖六个维度（业务发现/数据与集成/AI 工程/评估安全/交付运维/客户沟通）；题目与自评仅供本人学习参考，不构成独立能力验证。', 'a': ''},
    {'u': 'profile', 't': '能力档案', 'h': '跨项目六维证据聚合与导出',
     'x': '聚合本人在实训中的提交与自评记录，可导出 JSON 备份或 PNG 图片分享。页面提供关键词格式提示与本人自评，不运行代码或独立验证作品，不是第三方认证。数据只存本机浏览器。', 'a': ''},
    {'u': 'videos', 't': '视频资源', 'h': '系统直播课（免费）',
     'x': 'Datawhale「AI+X 创造节 · FDE 实战营」系列直播，业务理解到交付运营完整链路，配套组队实战营与多城线下课；B 站录播含 Bob McGrew FDE 模式保姆级教程、Greg Isenberg 访谈；蜻蜓 FM 范冰有声版 10 集；免费文字配套与付费课程甄别。', 'a': ''},
    {'u': 'videos', 't': '视频资源', 'h': 'B 站录播（免费）',
     'x': 'FDE 模式保姆级教程：前 Palantir 研发负责人 Bob McGrew 谈 FDE 三大纪律八项注意，约 50 分钟中英字幕；揭秘年薪百万美元的 AI 工作 FDE；阿一 FDE 从入门到精通八堂课交互教程。', 'a': ''},
    {'u': 'radar', 't': '历史招聘快照', 'h': f'FDE 中国招聘样本 · {RS["period"]}',
     'x': '历史静态快照；含职位、城市、技能与来源口径。仅描述当期采集样本，不代表当前岗位总量、薪资或趋势。', 'a': ''},
    {'u': 'sentiment', 't': '历史舆情快照', 'h': f'FDE 行业讨论样本 · {YQ.SOURCE["collected"]}',
     'x': '历史静态快照；展示当期国内平台讨论与争议声音。不能代表当前行业舆情或全体从业者观点。', 'a': ''},
    {'u': 'sentiment', 't': '历史舆情快照', 'h': '负向与争议声音（落地真实困境）',
     'x': '「这不就是驻场吗」「AI 水文就别发了」「大部分时候确实是旧东西，不然就是高级外包」「需求是真的，但幻觉也是真的」「重交付重人力，很容易干成外包」「站在台下讲 AI 改造是受人尊敬的老师，进入客户现场就变成被使唤、没权限、还要担责的奴隶」「FDE 在国内没戏的，千万别干」「第一批做 FDE 的人，要转行了」「今天的 FDE，就是曾经的 TA——左手交付右手产品、信任崩塌」。', 'a': ''},
    {'u': 'sentiment', 't': '历史舆情快照', 'h': f'{len(YQ.PLATFORMS)} 平台明细与修正说明',
     'x': 'B站 12 条（课程化最彻底）、脉脉 5 条（从业者浓度最高）、即刻 3 条（生态建设者）、知乎 12 条（长文科普）、小红书 19 条（营销与噪声最多）、微博 7 条（媒体与热搜）、CSDN 10 条与掘金 12 条（技术社区最密集）、博客园 9 条（浏览量最高）、思否 7 条、InfoQ 7 条与 51CTO 7 条（技术媒体深度文）、华为云社区 4 条 / 阿里云开发者社区 6 条 / 腾讯云开发者社区 7 条（厂商官方动作、能力模型与落地方法论），合计 127 条。本站修正说明：原报告数据问题已逐条核实并更正——B站第 5 条错挂链接已更正为 BV1hJuh6AEfY、B站 7 条缺失链接已全部找回并核验补全、知乎段条数口径已统一为 12 条、原报告自述 131 条与分平台明细合计 127 条不符（已按明细校正）；厂商社区 17 条为 2026-09-22 更新版新增，与技术社区合计 69 条链接未逐条复核。补链与更正条目在明细中带标记，便于核对。', 'a': ''},
]
(OUT / 'search.json').write_text(json.dumps(SEARCH, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(f'✓ 搜索索引 {len(SEARCH)} 条')
print(f'✓ 输出 {OUT}')
