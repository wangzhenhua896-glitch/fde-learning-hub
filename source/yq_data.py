# -*- coding: utf-8 -*-
"""FDE 多平台舆情报告数据（来源：飞书文档 revision 64，采集日 2026-09-22，15 平台 127 条）

字段说明：t 标题 / u 链接 / a 作者 / d 日期 / x 描述 / s 信源 / ten 原报告的倾向标注
        st 归一化态度（pos 正向 / neu 中性 / neg 负向）/ lsrc 链接来源（orig 原报告 / added 本站补链 / fixed 本站更正）
前 12 平台沿用 2026-09-22 上一版（含本站对 B站 8 条链接的补全与更正）；末 3 个厂商社区（华为云/阿里云/腾讯云）为 2026-09-22 更新版新增。
total 以分平台明细逐条相加为准（127），原报告自述 131 条与其分平台明细合计不符，见 EDITOR_NOTES。
"""

SOURCE = {
    'url': "https://feishu.doubao.com/docx/X2YFdYdQdocDwex6bqNcjEn0nsb",
    'title': "FDE 多平台热度分析：B站/脉脉/即刻/知乎/小红书/微博/CSDN/掘金/博客园",
    'collected': "2026-09-22",
    'total': 127,
}

# 修正说明：原报告的数据问题，本站已核实并直接修正（链接更正/补全、条数口径统一）
EDITOR_NOTES = [
    {
        'title': "B站第 5 条原链接错挂，已更正为正确视频",
        'detail': "原报告第 5 条（马士兵学堂）误用了第 1 条的视频号 BV1HpNt6fE3q，同一链接下出现两套不同的标题、作者与播放量（2026-09-22 更新版报告仍未更正此问题）。经 B站官方接口核验，该条实际为 BV1hJuh6AEfY「2026年AI前沿部署工程师（FDE）入门到就业完整版教程：核心技能+实战指南+面试题解析」（马士兵学堂，时长 5 小时 19 分，播放 4.4 万）——与报告记载的UP主、播放量、时长三项吻合，本站沿用该更正。",
    },
    {
        'title': "B站 7 条缺失链接已全部找回并核验",
        'detail': "原报告 B站第 6–12 条仅有文字描述、未附原始链接（含播放 5.7 万的头部课程，2026-09-22 更新版仍未附）。本站逐一通过 B站官方检索定位，以「UP 主 + 标题 + 播放量」三重吻合为准补全全部 7 条链接。补齐后，原报告「数据边界与采集说明」中「条目均为一手信源（原帖/原视频/原专栏/原微博链接）」的声明成立。补全与更正的条目在明细中以「本站补链」「链接已更正」标记区分。",
    },
    {
        'title': "知乎段自述条数已按实际口径统一",
        'detail': "原报告知乎段落开头自述「共采集 17 条专栏/回答」（2026-09-22 更新版仍保留该句），但正文实际列出 12 条，报告自身的「样本口径」与「数据边界」也均记为 12 条。本页统一按实际列出的 12 条呈现。",
    },
    {
        'title': "原报告自述总条数与分平台明细合计不符，本站按明细校正",
        'detail': "原报告正文引言与「数据边界」两处均自述「共获取 131 条」，但按其自己列出的分平台条数逐项相加只有 127 条：B站 12 + 脉脉 5 + 即刻 3 + 知乎 12 + 小红书 19 + 微博 7 + CSDN 10 + 掘金 12 + 博客园 9 + SegmentFault 7 + InfoQ 7 + 51CTO 7 + 华为云社区 4 + 阿里云开发者社区 6 + 腾讯云开发者社区 7 = 127。差额 4 条在原报告中无从对应。本页以可逐条核对的明细为准，统一按 127 条呈现（明细条数与各平台标注完全一致）。",
    },
    {
        'title': "技术社区与厂商社区共 69 条链接未逐条复核",
        'detail': "本次更新累计新增 CSDN 10 条、掘金 12 条、博客园 9 条、SegmentFault 7 条、InfoQ 7 条、51CTO 7 条、华为云社区 4 条、阿里云开发者社区 6 条、腾讯云开发者社区 7 条，共 69 条，链接均为原报告直接给出；与 B站补链同口径的「官方接口三重吻合」核验仅覆盖此前 B站 8 条，这 69 条本站未逐条复核，如遇失效链接以原平台检索为准。另：华为云、阿里云、腾讯云三个厂商社区的原报告条目未给出作者署名，本页 author 字段统一记为「佚名」，不代表原文作者实名信息缺失之外的处置。",
    },
    {
        'title': "数据时点说明",
        'detail': "本页条目内容为原报告 2026-09-22 采集时点（revision 64，此前为 revision 57）的快照；B站、脉脉、即刻、知乎、小红书、微博、CSDN、掘金、博客园、SegmentFault、InfoQ、51CTO 十二个平台条目与上一版逐条一致，本次更新仅新增华为云/阿里云/腾讯云三个厂商社区共 17 条，并更新「热度与分布特征」下的平台分层结论。播放量、评论数等指标会随时间自然变化，本站核验读数与报告采集值可能存在小幅出入，属正常增长。",
    },
]

# 舆情整体态势与归类总结（原文三节）
OVERVIEW = [
    {
        'h': "正向与中性舆情占主流：科普、转型、行业分析三类构成主体",
        'items': [
            ('li', "**科普讲透类（约 9 条）**：集中在 B站与即刻。B站以\"入门到就业完整版教程\"\"实战规划课\"等长视频课程为主，播放量 654–5.7 万；即刻有范冰_XDash 的二十万字开源书（fde4.ai，3 周近 4k star）、High寧 的中美 FDE 对谈播客（E09）等高质量内容。"),
            ('li', "**转型机遇类（约 5 条）**：集中在脉脉与 B站。脉脉有\"38 岁 Java 后端转 FDE 月薪 2 万涨到 5 万+期权\"\"FDE 是国内 CSM 理想转型方向\"等真实案例与职业分析；B站有\"程序员&PM 转行 FDE 年薪 65W+\"等课程向内容。"),
            ('li', "**行业宏观分析类（约 4 条）**：脉脉\"有个趋势想分享出来\"梳理了微软 Frontier Company 25 亿美元招 6000 人、字节 FDE 最高 105 万年薪等数据；\"FDE 是伪命题吗\"从创始人视角谈需求真伪与生意模式。"),
        ],
    },
    {
        'h': "负向与争议舆情集中在质疑与警惕：约两成，多存于评论区",
        'items': [
            ('li', "**\"换皮驻场/旧瓶装新酒\"质疑（3 处）**：脉脉 Bright Wang 帖下评论\"这不就是驻场吗？每次 ai 都新出名次\"；赵嘉盟帖下评论\"AI 水文就别发了\"；佟桐帖正文直言\"大部分时候确实是旧东西……不然就是高级外包\"。"),
            ('li', "**培训收割警惕（2 处）**：B站\"终于 FDE 也要烂大街了\"（ToB老人家，1.5 万播放）与\"WorkBuddy 力推 FDE，暴露企业 AI 最难的一关\"（3 万播放）均带批判视角；抖音平台亦有同类视频（本报告不含）。"),
            ('li', "**落地困境陈述（1 处）**：佟桐\"需求是真的，但'幻觉'也是真的\"——老板对 AI 认知两极，市场教育仍在早期。"),
        ],
    },
    {
        'h': "整体判断：热度真实、以正向营销与科普为主，质疑已萌芽",
        'items': [
            ('p', "多平台 FDE 热度与岗位需求（领英 42 倍增长、脉脉职位发布同比涨 21 倍）相互印证，属于**真实产业热度而非纯概念炒作**。B站课程生态已成熟（多个 1 万+ 播放课程）、即刻有深度开源内容、脉脉有真实从业者讨论，构成\"课程化—生态化—职业化\"三层次热度结构。负向声音集中在\"是否换皮外包\"与\"培训割韭菜\"两点，说明市场处于早期教育阶段，争议未成规模。"),
        ],
    },
]

# 热度与分布特征（原文三节）
HEAT = [
    {
        'h': "平台热度分层：B站与小红书最高，技术社区（CSDN/掘金/博客园/SegmentFault/InfoQ/51CTO）和厂商社区（华为云/阿里云/腾讯云）长文最密集，微博话题传播广，知乎/脉脉/即刻居中",
        'items': [
            ('p', "<html5-block alt=\"多平台FDE热度分布对比：B站/脉脉/即刻/知乎/小红书/微博/CSDN/掘金的样本量与信息可得性矩阵\" data-ref=\"html5_1\"></html5-block>"),
        ],
    },
    {
        'h': "B站：课程化最彻底，播放量头部为培训账号",
        'items': [
            ('p', "<html5-block alt=\"B站FDE相关视频播放量分布：头部课程号与科普号并存，播放量从数百到5.7万不等\" data-ref=\"html5_2\"></html5-block>"),
            ('p', "B站 FDE 内容呈现明显的**培训课程化**特征：头部播放视频（5.7 万、4.1 万、3 万）均为\"全 526 集/748 集入门到精通\"类标题，账号多带\"码士集团\"\"马士兵学堂\"等培训品牌，评论区常见\"配套资料评论区置顶自取\"的引流话术。真正偏内容深度的是 Easonlee《OpenAI 团队：FDE 工程师的未来》（1385 播放）与 ToB老人家批判视角视频，播放量反而靠后——**流量向培训倾斜、深度内容叫好不叫座**是 B站 FDE 生态的显著特征。"),
        ],
    },
    {
        'h': "脉脉、即刻与小红书：从业者浓度高、观点更真实",
        'items': [
            ('p', "脉脉 5 条帖子全部来自一线从业者（房产中介视角的行业观察、被优化后转岗的 38 岁 Java 后端、创始人兼 CEO、客户成功区域经理、资深猎头），讨论围绕\"值不值得转、是不是伪命题、CSM 转型路径\"展开，评论区有真实质疑。即刻则以**生态建设者**为核心：范冰_XDash 开源书+官网+付费社群形成完整内容生态，High寧 播客打通中美视野。小红书 19 条笔记以**个人转型经历分享+入门引流**为主，点赞头部达 2748（清华姜学长），但证书/面试题营销帖占比明显（\"腾讯云 1200 块值得考吗\"\"高频面试题 63 道\"），且出现\"国内没戏千万别干\"等劝退帖——普通用户浓度高，但营销与噪声也最多。三个平台阅读/点赞绝对值不高或分化明显，但信息质量与从业者真实度高于 B站课程化内容。"),
        ],
    },
]

# 12 平台条目（明细）。前 6 平台 = 2026-09-21 版（含本站修正）；后 6 平台 = 2026-09-22 新增
PLATFORMS = [
    {
        'key': "bilibili", 'cn': "B站", 'emoji': "📺", 'color': "#7c3aed",
        'note': "课程化最彻底，播放量头部为培训账号",
        'entries': [
            {'t': "FDE(前沿部署工程师)入门到就业完整版教程", 'u': "https://www.bilibili.com/video/BV1HpNt6fE3q/", 'a': "码士教育-小森", 'd': "2026-07-14", 'x': "42 集系列课，覆盖概念→智能体框架→Milvus 实操→面试；简介带\"1对1职业规划、免费资料\"引流。播放 2.3 万、评论 147、收藏 615", 's': "一手", 'ten': "中性（课程引流）", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "【2026最新版】全网最详尽FDE实战规划课", 'u': "https://www.bilibili.com/video/BV1WmMM6QErx/", 'a': "码儿要吃草", 'd': "2026-07-05", 'x': "20 集，含\"私教服务与市场展望\"节；播放 654、评论 26、收藏 120", 's': "一手", 'ten': "中性（课程引流）", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "OpenAI团队：FDE工程师的未来", 'u': "https://www.bilibili.com/video/BV1tV7Q6TEcf/", 'a': "Easonlee的AI笔记", 'd': "2026-06-07", 'x': "OpenAI/Ramp/Nominal/Dataland 工程领袖圆桌，FDE 角色演变、收入意识、激进所有权模式；播放 1385、评论 32、收藏 113", 's': "一手", 'ten': "正向（深度）", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "【FDE】B站最全FDE落地实战与面试指南", 'u': "https://www.bilibili.com/video/BV1a5Tj6pEdF/", 'a': "码士集团_马小帆", 'd': "2026-07-02", 'x': "20 集；播放 1.2 万、评论 135、收藏 1306、点赞 594", 's': "一手", 'ten': "中性（课程引流）", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "2026年AI前沿部署工程师（FDE）入门到就业完整版教程", 'u': "https://www.bilibili.com/video/BV1hJuh6AEfY/", 'a': "马士兵学堂", 'd': "2026", 'x': "播放 4.1 万、评论 137，5:19:27 长课，B站推荐位可见", 's': "一手", 'ten': "中性（课程引流）", 'st': "neu", 'lsrc': "fixed", 'nolink': False, 'dup': False},
            {'t': "【全526集】AI FDE入门到精通程", 'u': "https://www.bilibili.com/video/BV178Ev6LEm9/", 'a': "AI产品经理小蓝", 'd': "2026", 'x': "播放 5.7 万、评论 130，标题强调\"零基础小白到 40k\"", 's': "一手（推荐位）", 'ten': "中性（课程引流）", 'st': "neu", 'lsrc': "added", 'nolink': False, 'dup': False},
            {'t': "为什么FDE在AI时代这么火？因为差距不在模型，在业务细节", 'u': "https://www.bilibili.com/video/BV1tXKi6NE4b/", 'a': "课代表立正", 'd': "2026", 'x': "播放 1.8 万、评论 9", 's': "一手（推荐位）", 'ten': "正向", 'st': "pos", 'lsrc': "added", 'nolink': False, 'dup': False},
            {'t': "3分钟了解FDE，20年前的概念最近火了？", 'u': "https://www.bilibili.com/video/BV13yun6KEEy/", 'a': "极海Channel", 'd': "2026", 'x': "播放 1.9 万、评论 31", 's': "一手（推荐位）", 'ten': "中性", 'st': "neu", 'lsrc': "added", 'nolink': False, 'dup': False},
            {'t': "WorkBuddy 力推 FDE，暴露企业 AI 最难的一关", 'u': "https://www.bilibili.com/video/BV1Wvbr6aELE/", 'a': "公众号-ToB老人家", 'd': "2026", 'x': "播放 3 万、评论 2，批判视角", 's': "一手（推荐位）", 'ten': "负向（警惕）", 'st': "neg", 'lsrc': "added", 'nolink': False, 'dup': False},
            {'t': "终于，FDE也要烂大街了！", 'u': "https://www.bilibili.com/video/BV14zTp68Ey5/", 'a': "公众号-ToB老人家", 'd': "2026", 'x': "播放 1.5 万、评论 1，批判视角", 's': "一手（推荐位）", 'ten': "负向（警惕）", 'st': "neg", 'lsrc': "added", 'nolink': False, 'dup': False},
            {'t': "程序员&PM转行FDE，年薪65W+", 'u': "https://www.bilibili.com/video/BV1xSKp6fErV/", 'a': "唐宇迪AI入门课", 'd': "2026", 'x': "播放 4246、评论 73", 's': "一手（推荐位）", 'ten': "正向（课程向）", 'st': "pos", 'lsrc': "added", 'nolink': False, 'dup': False},
            {'t': "未来硅世界第19期：FDE项目和AI Coding作品大赏", 'u': "https://www.bilibili.com/video/BV16vKb6YEqt/", 'a': "通往AGI之路", 'd': "2026", 'x': "播放 3669、评论 3，社区内容", 's': "一手（推荐位）", 'ten': "正向", 'st': "pos", 'lsrc': "added", 'nolink': False, 'dup': False},
        ],
    },
    {
        'key': "maimai", 'cn': "脉脉", 'emoji': "💼", 'color': "#2563eb",
        'note': "从业者浓度最高，观点更真实、争议更多",
        'entries': [
            {'t': "有个趋势想分享出来跟大家讨论", 'u': "https://maimai.cn/article/detail?efid=yqcQbIcP9aMeE4f9q5vGFQ&fid=1919446545", 'a': "不到九点", 'd': "2026-07-05", 'x': "微软 Frontier Company 25 亿美元招 6000 人；字节 FDE 月薪 3.5–7 万、年薪最高 105 万；阿里云 2–5 万×16 薪；全球 FDE 岗位三年增长 42 倍", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "从写代码到AI交付师，35岁程序员第二春", 'u': "https://maimai.cn/article/detail?efid=2o-tLrwXr0lcGUiB2AmjIQ&fid=1923704409", 'a': "赵嘉盟", 'd': "2026-08-10", 'x': "38 岁 Java 后端被优化后转 FDE，月薪 2 万涨到 5 万+期权；FDE 四步工作流（需求翻译→任务拆解→调优编排→交付运维）；评论区出现\"AI 水文就别发了\"质疑", 's': "一手", 'ten': "正向（有质疑评论）", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "FDE是伪命题吗？聊聊大实话", 'u': "https://maimai.cn/article/detail?efid=f8_Pv-o6ZBq6mKeybghm-w&fid=1924194448", 'a': "佟桐", 'd': "2026-08-14", 'x': "创始人视角：需求是真的但\"幻觉\"也是真的；新旧不重要关键看价值；\"重交付重人力，很容易干成外包\"", 's': "一手", 'ten': "中性偏负向（反思）", 'st': "neg", 'nolink': False, 'dup': False},
            {'t': "FDE是国内CSM的理想转型方向?", 'u': "https://maimai.cn/article/detail?efid=WDgLhlL10s7hCy_1KOSKmA&fid=1915897482", 'a': "赵云锋", 'd': "2026-09-20", 'x': "岗位标准化加速、70% 企业有 AI 采购需求但落地不足 20%、垂直细分为金融/工业智造/政务/医疗四大赛道", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "2026大火的岗位——FDE", 'u': "https://maimai.cn/article/detail?efid=-bReXzmOsKClWI3Hwd57wQ&fid=1923096164", 'a': "Bright Wang", 'd': "2026-08-05", 'x': "资深猎头解读：FDE=深入客户现场的工程师；评论区出现\"这不就是驻场吗\"质疑", 's': "一手", 'ten': "中性（有质疑评论）", 'st': "neu", 'nolink': False, 'dup': False},
        ],
    },
    {
        'key': "jike", 'cn': "即刻", 'emoji': "🌱", 'color': "#0d9488",
        'note': "生态建设者为核心：开源书、播客、圆桌",
        'entries': [
            {'t': "FDE 二十万字资料开源书 + fde4.ai 官网 + 付费社群", 'u': "https://m.okjike.com/originalPosts/6a7e6aa4846af03db5c88682", 'a': "范冰_XDash", 'd': "2026-08-13", 'x': "开源书 3 周近 4k star；官网含案例库（160+ 案例）、生态地图、名录；8 月 26 日直播并沉淀课程（199 元→299 元）。热度 10916、评论 65", 's': "一手", 'ten': "正向（生态建设+商业变现）", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "E09.横跨中美，聊透FDE真相", 'u': "https://m.okjike.com/users/143B8259-AD62-4C1B-A96F-4C7323623206", 'a': "High寧/Linkloud Talk", 'd': "2026-08 下旬", 'x': "对谈 Cresta FDE 负责人 Jove 与 OpenFDE 创始人 Lyon，覆盖真相、争议与未来；音视频同步小宇宙、小红书、视频号。热度 125", 's': "一手", 'ten': "正向（深度）", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "FDE 圆桌讨论召集帖", 'u': "https://m.okjike.com/users/78c07949-236d-4de8-b859-244bf79ace42", 'a': "徐邦睿", 'd': "2026-09-13", 'x': "参与者含研发、售前、咨询、HR 及 To B 从业者，围绕\"企业如何落地 AI\"讨论两个多小时", 's': "一手（个人主页）", 'ten': "中性（讨论向）", 'st': "neu", 'nolink': False, 'dup': False},
        ],
    },
    {
        'key': "zhihu", 'cn': "知乎", 'emoji': "📝", 'color': "#0891b2",
        'note': "长文科普与转型指南为主，营销文混杂",
        'entries': [
            {'t': "什么是FDE驻场部署工程师：一个被Palantir逼出来、又被AI重新点燃的岗位", 'u': "https://zhuanlan.zhihu.com/p/2054970755759204335", 'a': "王朋友", 'd': "2026-06-29", 'x': "Palantir 起源、Delta 代号、与普通工程师区分，科普向代表作", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "那些被管理层请进公司，却不被一线员工接受的FDE们", 'u': "https://zhuanlan.zhihu.com/p/2077698871891969825", 'a': "知乎专栏", 'd': "2026", 'x': "**负向代表作**：FDE 落地时与一线员工的冲突、被架空的真实困境", 's': "一手", 'ten': "负向", 'st': "neg", 'nolink': False, 'dup': False},
            {'t': "2026 年技术人转型，FDE（前沿部署工程师）到底是不是一个真机会？", 'u': "https://zhuanlan.zhihu.com/p/2072330048007313318", 'a': "陽清AI一人企业", 'd': "2026-08-17", 'x': "10 年全栈后端视角，\"真机会但不是给所有人\"", 's': "一手", 'ten': "正向（理性）", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "WorkBuddy都开始招FDE了！程序员转型AI前沿部署工程师指南（建议收藏）", 'u': "https://zhuanlan.zhihu.com/p/2075345316648428850", 'a': "刀哥聊AI", 'd': "2026", 'x': "从地铁广告到真实需求，转型指南向", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "第一批做FDE的人，要转行了", 'u': "https://www.zhihu.com/question/2054821899465660091/answer/2064046329530262118", 'a': "运营研究社/钟楚笛", 'd': "2026-08-08", 'x': "7 赞同 3 评论，转载自 AI 故事计划，\"单人接单月入十万\"\"零基础转行年薪百万\"的社交平台叙事拆解", 's': "一手", 'ten': "中性偏负向（行业反思）", 'st': "neg", 'nolink': False, 'dup': False},
            {'t': "AI公司都在抢，FDE前沿部署工程师到底是什么！", 'u': "https://zhuanlan.zhihu.com/p/2078539047023256308", 'a': "强比软件开发", 'd': "2026-09-02", 'x': "\"月薪开到十万都要抢\"，大厂抢人叙事", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "FDE（前线部署工程师）是什么？薪资多少？2026 年普通人怎么入行", 'u': "https://zhuanlan.zhihu.com/p/2084449693841544003", 'a': "知乎专栏", 'd': "2026", 'x': "薪资与入行指南向", 's': "一手", 'ten': "中性", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "2026年江浙沪FDE制造业前沿部署工程师培训机构选择逻辑拆解", 'u': "https://zhuanlan.zhihu.com/p/2085408207032280272", 'a': "知乎专栏", 'd': "2026", 'x': "**培训机构营销文**", 's': "一手", 'ten': "中性（营销）", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "FDE前沿部署工程师是什么？为什么企业AI落地离不开织信这样的智能开发平台", 'u': "https://zhuanlan.zhihu.com/p/2068712304355578479", 'a': "知乎专栏", 'd': "2026", 'x': "**软件厂商营销文**", 's': "一手", 'ten': "中性（营销）", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "FDE前沿部署工程师的两种范式：技术纵深型vs场景应用型", 'u': "https://zhuanlan.zhihu.com/p/2068379755150414870", 'a': "知乎专栏", 'd': "2026", 'x': "岗位细分分析", 's': "一手", 'ten': "中性", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "FDE前沿部署工程师与Agent Engineer智能体工程师岗位深度分析", 'u': "https://zhuanlan.zhihu.com/p/2054187330936778845", 'a': "知乎专栏", 'd': "2026", 'x': "岗位对比分析", 's': "一手", 'ten': "中性", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "洞见人才新范式｜从FDE前沿部署工程师，看企业自动化落地的底层逻辑", 'u': "https://zhuanlan.zhihu.com/p/2081752702195865239", 'a': "知乎专栏", 'd': "2026", 'x': "企业视角", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
        ],
    },
    {
        'key': "xhs", 'cn': "小红书", 'emoji': "📕", 'color': "#dc2626",
        'note': "普通用户浓度高，营销与噪声也最多",
        'entries': [
            {'t': "FDE——AI带来的新岗位，正在悄悄爆火", 'u': "https://www.xiaohongshu.com/explore/6a184b49000000003502a492", 'a': "清华姜学长", 'd': "2026-05-28", 'x': "2748 赞，科普向头部爆款", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "老头们的快乐生活（FDE 相关视频）", 'u': "https://www.xiaohongshu.com/explore/6aab551d000000000d0255cf", 'a': "老头们的快乐生活", 'd': "4 天前", 'x': "2274 赞，视频笔记", 's': "一手", 'ten': "中性", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "突然爆火的 FDE 是什么？一张图讲透新风口！", 'u': "https://www.xiaohongshu.com/explore/6a0e85a40000000006036cc6", 'a': "Cestlavia", 'd': "2026-05-21", 'x': "934 赞，图文讲透", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "这或许AI时代最不愁工作的岗位", 'u': "https://www.xiaohongshu.com/explore/6a6ff25c0000000006005c73", 'a': "干饭打工人", 'd': "2026-08-10", 'x': "917 赞，职业前景向", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "程序员转型FDE，不用卷也能高薪", 'u': "https://www.xiaohongshu.com/explore/69fee887000000003601d14b", 'a': "观界", 'd': "2026-05-21", 'x': "386 赞，转型故事", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "做完20个agent项目，悟到FDE必备的5个能力", 'u': "https://www.xiaohongshu.com/explore/6a4e5e10000000000803cbf2", 'a': "斯年的AI创业", 'd': "2026-07-09", 'x': "297 赞，实战经验", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "国家部委正名！FDE=前线部署工程师", 'u': "https://www.xiaohongshu.com/explore/6a962e36000000002601f7c4", 'a': "AI-FDE知行社", 'd': "2026-09-01", 'x': "208 赞，政策信号向", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "腾讯云这个 FDE 认证，1200 块值得考吗🤔", 'u': "https://www.xiaohongshu.com/explore/6aa25caa000000002803595f", 'a': "一颗番茄", 'd': "2026-09-10", 'x': "108 赞，证书讨论", 's': "一手", 'ten': "中性（证书营销）", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "突然爆火的 FDE，普通人怎么入门？", 'u': "https://www.xiaohongshu.com/explore/6a5eeefd0000000001033d22", 'a': "Ai果果姐", 'd': "2026-07-21", 'x': "94 赞，入门科普", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "FDE在国内没戏的，千万别干", 'u': "https://www.xiaohongshu.com/explore/6a79cf4d000000000503002c", 'a': "Archer", 'd': "2026-08-10", 'x': "67 赞，负向代表作", 's': "一手", 'ten': "负向", 'st': "neg", 'nolink': False, 'dup': False},
            {'t': "FDE 工程师全是先进去再说的", 'u': "https://www.xiaohongshu.com/explore/6aa227e9000000000b00fd60", 'a': "Lily 的Ai学习日记", 'd': "2026-09-10", 'x': "50 赞，吐槽式", 's': "一手", 'ten': "负向/中性", 'st': "neg", 'nolink': False, 'dup': False},
            {'t': "坦白说，我劝你先别学Agent了😮‍💨", 'u': "https://www.xiaohongshu.com/explore/6a996cee000000002a005ee3", 'a': "知乎AGI", 'd': "2026-09-04", 'x': "17 赞，理性劝退", 's': "一手", 'ten': "中性", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "什么人适合做FDE", 'u': "https://www.xiaohongshu.com/explore/6a71f3510000000025017871", 'a': "职场马伊琍", 'd': "2026-08-04", 'x': "21 赞，画像向", 's': "一手", 'ten': "中性", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "宝子们！FDE前沿部署工程师来啦！", 'u': "https://www.xiaohongshu.com/explore/6a151f590000000006031c73", 'a': "张镇涛｜AI部署师创始人", 'd': "2026-05-26", 'x': "22 赞，从业者引流", 's': "一手", 'ten': "中性", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "真心建议考个FDE前沿部署工程师的n个理由！", 'u': "https://www.xiaohongshu.com/explore/6aabd2eb0000000011036221", 'a': "极客职场AI", 'd': "4 天前", 'x': "4 赞，证书营销", 's': "一手", 'ten': "中性（培训营销）", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "FDE前沿部署工程师高频面试题63道汇总", 'u': "https://www.xiaohongshu.com/explore/6a8521ea00000000220123bd", 'a': "巧儿老师", 'd': "2026-08-19", 'x': "3 赞，面试资料引流", 's': "一手", 'ten': "中性（培训营销）", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "海外AI博士团队招人啦！FDE招聘！", 'u': "https://www.xiaohongshu.com/explore/6a6223f70000000008009c01", 'a': "微澜科技", 'd': "2026-07-23", 'x': "6 赞，招聘帖", 's': "一手", 'ten': "中性", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "企业AI转型为什么需要FDE", 'u': "https://www.xiaohongshu.com/explore/6ab12390000000003303427c", 'a': "AI果哥笔记", 'd': "1 小时前", 'x': "企业视角", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "AI 落地 95% 失败，硅谷把宝押在这个岗位上", 'u': "https://www.xiaohongshu.com/explore/6ab119b8000000003703fb90", 'a': "自然成长笔记", 'd': "2 小时前", 'x': "硅谷视角", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
        ],
    },
    {
        'key': "weibo", 'cn': "微博", 'emoji': "📢", 'color': "#d97706",
        'note': "媒体报道与话题传播，已上热搜",
        'entries': [
            {'t': "站在台上讲企业AI改造时是受人尊敬的老师，但真正进入客户现场后FDE就会变成乙方和供应商，甚至是被使唤、没权限、还要担责的奴隶", 'u': "https://weibo.com/5700099573/RfUtDDnhC", 'a': "数字生命卡兹克", 'd': "2026-08-31", 'x': "22 转发 8 评论 48 赞，**负向代表作**，一线落地真实困境", 's': "一手", 'ten': "负向", 'st': "neg", 'nolink': False, 'dup': False},
            {'t': "【杭州有企业开出96万年薪招FDE】【AI岗位FDE最高年薪128万美元】", 'u': "https://weibo.com/1847582585/RiIp15PFi", 'a': "都市快报", 'd': "2026-09-18", 'x': "1 转发 3 评论，媒体报道，硅谷 128 万美元 vs 国内 40.8 万平均年薪", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "腾讯研究院发布《FDE模式行业观察与实践》", 'u': "https://weibo.com/1900197770/RiS8xaQen", 'a': "程贵锋gui", 'd': "2026-09-19", 'x': "3 评论，行业报告转发", 's': "一手", 'ten': "中性", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "【月之暗面启动\"登月计划\"】以FDE模型与行业系统集成商共建前置部署工程师队伍", 'u': "https://weibo.com/1737694250/RhscFfnB4", 'a': "CNMO科技", 'd': "2026-09-10", 'x': "1 转发 2 评论，国内首家采用 FDE 模型的大模型公司", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "AI新词FDE！要信早信——2025年4月至2026年4月岗位从643个飙至5330个，同比增729%", 'u': "https://weibo.com/1885016273/RcHUiwqse", 'a': "股市包工头", 'd': "2026-08-10", 'x': "4 评论 19 赞，投资视角", 's': "一手", 'ten': "正向", 'st': "pos", 'nolink': False, 'dup': False},
            {'t': "青岛线下AI职业实训（含FDE前沿部署工程师方向）", 'u': "https://weibo.com/5228372196/RiEjIcDlW", 'a': "李雅Jy", 'd': "2026-09-18", 'x': "3 评论，**培训机构营销**", 's': "一手", 'ten': "中性（营销）", 'st': "neu", 'nolink': False, 'dup': False},
            {'t': "这个\"一眼看不懂工作内容\"的新职业，能\"火\"吗？", 'u': "https://weibo.com/1726918143/RgfKHBtww", 'a': "中国青年报", 'd': "2026-09-02", 'x': "2 评论 3 赞，官媒视角", 's': "一手", 'ten': "中性", 'st': "neu", 'nolink': False, 'dup': False},
        ],
    },
    {'key': "csdn", 'cn': "CSDN", 'emoji': "💻", 'color': "#fc5531",
     'note': "技术社区内容最密集（约 1337 个结果）：长文科普、认证解读、入行指南",
     'entries': [
            {'t': "前沿部署工程师（FDE）：AI时代最炙手可热的新岗位", 'u': "https://blog.csdn.net/2401_83600008/article/details/163641611", 'a': "林间码客", 'd': "2026-08-10", 'x': "829 阅读 19 评论，Palantir 起源、六阶段工作流、OpenAI×John Deere 案例", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE是什么-AI时代最炙手可热的前沿部署工程师完全指南", 'u': "https://blog.csdn.net/fullbug/article/details/162720229", 'a': "xiejava1018", 'd': "2026-07-09", 'x': "774 阅读 7 评论，军事术语起源、Palantir/CIA 第一个客户", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "腾讯云FDE认证：行业首个前沿部署工程师认证深度解读", 'u': "https://blog.csdn.net/weixin_33391446/article/details/165905243", 'a': "张瑞", 'd': "2026-09-19", 'x': "262 阅读 2 评论，认证方向拆解", 's': "一手", 'ten': "中性（认证解读）", 'st': "neu", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE到底在做什么——前沿部署工程师的真实一天", 'u': "https://blog.csdn.net/dandelion____z/article/details/163696607", 'a': "Dandelion____z", 'd': "2026-08-12", 'x': "231 阅读 7 评论，数据基建、RAG、系统联调四大环节", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "《FDE前沿部署工程师的自我修养》全书导读", 'u': "https://blog.csdn.net/2601_94865727/article/details/163977647", 'a': "AI-FDE知行社", 'd': "2026-08-17", 'x': "七篇十四章系统讲清 FDE 角色", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE（前沿部署工程师）：国内百万年薪风口岗深度解析", 'u': "https://blog.csdn.net/enjoyedu/article/details/164115033", 'a': "enjoyedu", 'd': "2026", 'x': "城市分布、薪资区间深度解析", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE 怎么入行：从工程师到前沿部署的 4 项核心历练", 'u': "https://blog.csdn.net/ltqvibe/article/details/163753865", 'a': "ltqvibe", 'd': "2026", 'x': "入行路径指南", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE和普通程序员到底差在哪——前沿部署工程师为什么企业抢着要", 'u': "https://blog.csdn.net/aigs001/article/details/163751811", 'a': "aigs001", 'd': "2026", 'x': "岗位对比", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "腾讯云FDE认证深度解读：前沿部署工程师如何持证上岗", 'u': "https://blog.csdn.net/tencent cloud/article/details/165905158", 'a': "腾讯云官方", 'd': "2026", 'x': "厂商官方认证专题", 's': "一手", 'ten': "中性（厂商营销）", 'st': "neu", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "《FDE前沿部署工程师实战教程》01 - FDE是什么：AI时代正在崛起的新型工程师", 'u': "https://blog.csdn.net/it_oracle/article/details/164095205", 'a': "it_oracle", 'd': "2026", 'x': "系列教程开篇", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
        ],
    },
    {'key': "juejin", 'cn': "掘金", 'emoji': "⛏️", 'color': "#1e80ff",
     'note': "互动量中等：转型视角、实操与概念辨析并存",
     'entries': [
            {'t': "前端没有死，只是换了个姿势年薪百万", 'u': "https://juejin.cn/post/7657809077683257387", 'a': "涛涛ing", 'd': "2026-07", 'x': "56 赞 25 评论，领英 42 倍增长数据，前端转型视角", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "告别单纯的\"跑分\"时代：FDE崛起与AI的业务落地深水区", 'u': "https://juejin.cn/post/7644099022207647780", 'a': "阿黎梨梨", 'd': "2026-06", 'x': "19 赞，Indeed 数据、业务落地深水区分析", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "硅谷爆火的FDE是AI新风口，还是高级外包？", 'u': "https://juejin.cn/post/7685224015707979826", 'a': "狼爷", 'd': "2026-09", 'x': "4 赞 7 评论，**负向代表作**，\"换皮交付、高级外包\"质疑", 's': "一手", 'ten': "负向", 'st': "neg", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "最近火爆出圈的，FDE到底是个什么岗位？", 'u': "https://juejin.cn/post/7684795356343336998", 'a': "狂师", 'd': "2026-09", 'x': "13 赞 2 评论，\"智能厨房设备\"比喻讲清 FDE", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "第1章 FDE的崛起", 'u': "https://juejin.cn/post/7679458659610738738", 'a': "怕浪猫", 'd': "2026-08", 'x': "9 赞 6 评论，系统教程章节", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE：一个缩写，两种命运", 'u': "https://juejin.cn/post/7686806089748693007", 'a': "码事漫谈", 'd': "2026-09", 'x': "5 赞，概念辨析：安全圈 FDE=全盘加密 vs AI 圈 FDE=前沿部署工程师", 's': "一手", 'ten': "中性", 'st': "neu", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE前沿部署工程师：AI时代最火的新岗位，以及用Coze零代码搭建AI应用", 'u': "https://juejin.cn/post/7644010555012169763", 'a': "Darling噜啦啦", 'd': "2026-06", 'x': "10 赞 1 评论，Coze 实操向", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE：从系统落地工程师，演变为企业AI能力的知识架构师", 'u': "https://juejin.cn/post/7682069529204768811", 'a': "吴佳浩Alben", 'd': "2026-08", 'x': "3 赞 1 评论，2026 年 FDE 新定位", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE爆火背后：AI落地最后一公里的工程化拆解（附真实案例与四步方法论）", 'u': "https://juejin.cn/post/7682499191227547667", 'a': "小虎AI生活", 'd': "2026-08", 'x': "1 赞 3 评论，Indeed 643→5330 数据", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE前沿部署工程师学习笔记", 'u': "https://juejin.cn/post/7645830893320978459", 'a': "用户2417140141860", 'd': "2026-06", 'x': "12 赞，岗位梳理学习笔记", 's': "一手", 'ten': "中性", 'st': "neu", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "AI部署师正在崛起：FDE或将成为AI时代最重要的新职业", 'u': "https://juejin.cn/post/7642682099159253033", 'a': "AI部署师", 'd': "2026-05", 'x': "从业者视角", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "前沿部署工程师（FDE）——AI项目落地的关键角色怎么练", 'u': "https://juejin.cn/post/7657374956293095475", 'a': "溯朢", 'd': "2026-07", 'x': "Palantir 起源、能力模型", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
        ],
    },
    {'key': "cnblogs", 'cn': "博客园", 'emoji': "🌿", 'color': "#0078e7",
     'note': "技术社区浏览量最高（头部 5698）：深度长文、模式解读、路线图",
     'entries': [
            {'t': "前沿部署工程师（FDE）是什么？一文说透这个2026年最火的AI岗", 'u': "https://www.cnblogs.com/lincats/articles/20677208", 'a': "AI钉子铺", 'd': "2026-06-21", 'x': "5698 浏览，\"会写代码的超级技术顾问\"定位，谷歌云/OpenAI/Anthropic布局", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "Forward Deployed Engineer（FDE）前沿部署工程师模式", 'u': "https://www.cnblogs.com/suntroop/articles/19516199", 'a': "suntroop", 'd': "2026-01-22", 'x': "2977 浏览，Palantir起源、Echo-Delta经典模式、驻场工程师+业务专家协同", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "年薪百万、需求暴涨42倍：AI时代最火岗位FDE到底是干嘛的？", 'u': "https://www.cnblogs.com/itech/p/20509065", 'a': "iTech", 'd': "2026-06-13", 'x': "推荐1次 779 浏览，\"碎石路vs高速公路\"方法论、全球收入盘点", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE工程师路线图", 'u': "https://www.cnblogs.com/wintersun/p/23053486", 'a': "PetterLiu", 'd': "2026-09-20", 'x': "职位能力路线图，\"FDE不是初级岗位，通常需要从全栈工程师转型\"", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE到底在做什么——前沿部署工程师的真实一天", 'u': "https://www.cnblogs.com/xiangliangz/p/22420035", 'a': "婆婆丁Dandelion", 'd': "2026-08-12", 'x': "38 浏览，行业工作侧重点分析", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "AI商业化加速，谁来搞定\"安装\"？揭秘前沿部署工程师（FDE）的崛起之路", 'u': "https://www.cnblogs.com/longxiapro/articles/21347057", 'a': "龙虾PRO", 'd': "2026-07-10", 'x': "31 浏览，\"人肉接口\"定位、模糊业务痛点 vs 确定性需求", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "2026年FDE前沿部署工程师培训机构推荐：岗位能力与实训就业闭环选型指南", 'u': "https://www.cnblogs.com/pinpai/p/22705254", 'a': "品牌测评鉴赏家", 'd': "2026-08-26", 'x': "27 浏览，**培训机构推荐榜**", 's': "一手", 'ten': "中性（营销）", 'st': "neu", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "年薪百万的\"AI工头\"：FDE如何成为硅谷最抢手的岗位？", 'u': "https://www.cnblogs.com/hay-lee/articles/21222954", 'a': "hay_lee", 'd': "2026-07-07", 'x': "17 浏览，\"一个人就是一支军队\"、年薪30-50万美元深层矛盾", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "2026 AI-FDE赋能制造业大会成功启动，大任智库发布2026 AI人才培育项目", 'u': "https://www.cnblogs.com/georank/p/22827954", 'a': "GEORANK", 'd': "2026-09-03", 'x': "15 浏览，制造业FDE大会、首批A-FDE联合工厂创始成员", 's': "一手", 'ten': "中性（行业动态）", 'st': "neu", 'lsrc': "orig", 'nolink': False, 'dup': False},
        ],
    },
    {'key': "segmentfault", 'cn': "SegmentFault 思否", 'emoji': "🧩", 'color': "#009a61",
     'note': "问答社区密度最高（约 10000 条结果），含尖锐外包质疑",
     'entries': [
            {'t': "AI圈最火的新岗位，到了国内可能又变成外包了", 'u': "https://segmentfault.com/a/1190000048276984", 'a': "佚名", 'd': "2026-09-06", 'x': "**负向代表作**，\"驻场开发加救火队长\"、\"名片换了但活还是外包的活\"", 's': "一手", 'ten': "负向", 'st': "neg", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "月薪8万的FDE，大厂为什么抢着把工程师送进客户现场？", 'u': "https://segmentfault.com/a/1190000048153208", 'a': "佚名", 'd': "2026-08-12", 'x': "FDE、Agent工程师、AI解决方案工程师岗位名称辨析", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "年薪$60万赶超ML研究员？拆解Palantir\"FDE+Echo\"双引擎如何跨越AI落地死亡谷", 'u': "https://segmentfault.com/a/1190000048034607", 'a': "佚名", 'd': "2026-07-16", 'x': "MIT研究95%企业AI试点失败、Demo只占20%工程难度", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "什么是FDE工程师？打通AI应用落地的最后一公里", 'u': "https://segmentfault.com/a/1190000048111827", 'a': "佚名", 'd': "2026-08-03", 'x': "2026年全球AI总投入2.52万亿美元、规模化落地瓶颈", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "技术专栏｜FDE是什么？为什么AI越强，越需要这群人？", 'u': "https://segmentfault.com/a/1190000048071997", 'a': "佚名", 'd': "2026-07-24", 'x': "OpenAI/Anthropic/Google布局、现场硬骨头", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "行业观察：面向在职程序员的中高端IT与AI技术培训——以咕泡科技为例", 'u': "https://segmentfault.com/a/1190000048297190", 'a': "佚名", 'd': "2026-09-15", 'x': "培训机构行业观察", 's': "一手", 'ten': "中性", 'st': "neu", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE企业项目实战训练营网盘资料", 'u': "https://segmentfault.com/a/1190000048309088", 'a': "佚名", 'd': "2026-09-21", 'x': "实战笔记、踩坑记录", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
        ],
    },
    {'key': "infoq", 'cn': "InfoQ", 'emoji': "📰", 'color': "#b91c1c",
     'note': "技术媒体：行业大会报道、深度分析与白皮书",
     'entries': [
            {'t': "9月20日杭州，FDE现场解码:企业AI真正卡在技术，还是组织?", 'u': "https://www.infoq.cn/article/QIIYxNtMINFNh4sCM3vu", 'a': "佚名", 'd': "2026-09-09", 'x': "行业大会深度讨论", 's': "一手", 'ten': "中性", 'st': "neu", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "全面解读FDE前沿部署工程师", 'u': "https://xie.infoq.cn/article/9bc18dfc27586d549783cfc9f", 'a': "AIWeker", 'd': "2026-06-19", 'x': "\"AI特种兵\"\"技术翻译官\"定位、大模型从\"斗兽棋\"到\"巷战\"", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE前沿部署工程师的两种范式:技术纵深型vs场景应用型", 'u': "https://xie.infoq.cn/article/d2abeeaa9b1249f9fae258e98", 'a': "咕泡ai", 'd': "2026-08-10", 'x': "两种职业范式对比分析", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "2026·AICon上海站，收获的第一个关键词--FDE", 'u': "https://xie.infoq.cn/article/f0631285937203ebbf90a62d9", 'a': "Tango_IT蜗壳", 'd': "2026-06-30", 'x': "中位数年薪17-20万美元、Indeed岗位一年暴增729%", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "从\"地图\"到\"导航\":中国制造业AI落地白皮书", 'u': "https://xie.infoq.cn/article/cef593918f49501e3ec85e4ff", 'a': "一线数智", 'd': "2026-07-26", 'x': "FDE+FDR双轮协同体系、模型迭代周期从3个月缩短至1-2周", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "AI前线部署工程师FDE实战特训|持证落地AI项目", 'u': "https://xie.infoq.cn/article/87c92cdca9cf45719b9e4ea93", 'a': "雅菲奥朗", 'd': "2026-06-21", 'x': "工信部教考中心人工智能工程师（高级）证书培训", 's': "一手", 'ten': "中性（培训营销）", 'st': "neu", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "制造业AI落地的\"东莞样本\"有了哪些新进展?", 'u': "https://xie.infoq.cn/article/07ddca34234ad60d514a56a7a", 'a': "一线数智", 'd': "2026-07-29", 'x': "SLP方法论、八大场景量化案例", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
        ],
    },
    {'key': "51cto", 'cn': "51CTO", 'emoji': "🏢", 'color': "#2b80ff",
     'note': "深度评论、JD 拆解与培训观察，负向代表作集中",
     'entries': [
            {'t': "FDE突然火了，但90%的公司根本不该做FDE", 'u': "https://www.51cto.com/article/855590.html", 'a': "佚名", 'd': "2026-09-11", 'x': "**负向代表作**，\"翻译层缺失\"判断、真正瓶颈不在模型而在落地", 's': "一手", 'ten': "负向", 'st': "neg", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "Anthropic工程师谈FDE前沿部署工程:把平台卖成结果，Palantir 400万美元客单价背后的秘密", 'u': "https://www.51cto.com/article/856527.html", 'a': "佚名", 'd': "2026-09-21", 'x': "Kevin Bai（Palantir/Rippling/Anthropic）一线经验", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE培训:只教本体和Agent够吗", 'u': "https://www.51cto.com/article/856542.html", 'a': "佚名", 'd': "2026-09-21", 'x': "**尖锐质疑**，\"最好教的不是最重要的\"、课纲同质化", 's': "一手", 'ten': "负向", 'st': "neg", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE究竟每天在做什么?34份北上广深真实JD给出答案", 'u': "https://blog.51cto.com/u_15944283/14938758", 'a': "佚名", 'd': "2026-09-16", 'x': "BOSS直聘60个招聘链接逐个拆解", 's': "一手", 'ten': "中性", 'st': "neu", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "数据治理工程师如何一步步转型成为FDE", 'u': "https://blog.51cto.com/u_16213592/14937307", 'a': "佚名", 'd': "2026-09-16", 'x': "转型路径分析、Palantir起源、OpenAI/Databricks/Salesforce大规模复制", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "AI落地为什么需要FDE:从\"实验室玩具\"到\"生产力引擎\"的破壁者", 'u': "https://www.51cto.com/article/845772.html", 'a': "佚名", 'd': "2026-06-09", 'x': "\"落地总包方\"定位、深入客户一线的\"特种兵\"", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "北森官宣全面转型AI应用公司，发布一站式AI HR专家平台Mavens", 'u': "https://www.51cto.com/article/847365.html", 'a': "佚名", 'd': "2026-06-24", 'x': "北森投资组建300+人FDE团队", 's': "一手", 'ten': "中性（行业动态）", 'st': "neu", 'lsrc': "orig", 'nolink': False, 'dup': False},
        ],
    },
    {'key': "huaweicloud", 'cn': "华为云社区", 'emoji': "☁️", 'color': "#c7000b",
     'note': "厂商社区：官方视角的定位、边界与真实落地反差",
     'entries': [
            {'t': "前沿部署工程师(FDE)到底是干嘛的?为什么最近突然火了", 'u': "https://bbs.huaweicloud.com/blogs/486706", 'a': "佚名", 'd': "2026-08-26", 'x': "\"把最前沿的大模型真正塞进客户业务里，并让它稳定跑起来\"", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE:一个缩写，两种命运", 'u': "https://bbs.huaweicloud.com/blogs/ceaab53ef7a8475fae3f40d88331ba36", 'a': "佚名", 'd': "2026-09-19", 'x': "\"塞进去、跑起来、真正\"三个关键词、标准产品覆盖不到的地方用手写代码补上", 's': "一手", 'ten': "中性", 'st': "neu", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE 的起源、形态与真实边界", 'u': "https://bbs.huaweicloud.com/blogs/0e9aa7444559499197db46d0f46df569", 'a': "佚名", 'd': "2026-09-15", 'x': "PoC 阶段热血上头、进生产环境\"一拳打在棉花上\"", 's': "一手", 'ten': "中性", 'st': "neu", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "硅谷爆火的高薪岗位FDE到底是什么?", 'u': "https://bbs.huaweicloud.com/blogs/489518", 'a': "佚名", 'd': "2026-09-09", 'x': "复合型岗位、AI时代新型技术岗", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
        ],
    },
    {'key': "aliyun", 'cn': "阿里云开发者社区", 'emoji': "🟠", 'color': "#ff6a00",
     'note': "厂商社区：岗位招聘量、能力模型与落地方法论",
     'entries': [
            {'t': "FDE火了，但老金告你，这件事远没你想的那么简单", 'u': "https://developer.aliyun.com/article/1761406", 'a': "佚名", 'd': "2026-09-07", 'x': "2026年1-8月同名岗位招聘量同比增长超10倍、OpenAI官网19个岗位", 's': "一手", 'ten': "中性", 'st': "neu", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "最近火爆出圈的，FDE到底是个什么岗位?", 'u': "https://developer.aliyun.com/article/1763041", 'a': "佚名", 'd': "2026-09-14", 'x': "驻客户现场、贯通技术与业务、端到端落地", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "从YC2026看企业AI落地:Agent标配化之后，真正缺的是部署力", 'u': "https://developer.aliyun.com/article/1756065", 'a': "佚名", 'd': "2026-08-16", 'x': "44%项目挤进Agent-as-a-Service、FDE从\"加分项\"变\"基础设施\"", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "年薪$60万赶超ML研究员?拆解Palantir\"FDE+Echo\"双引擎", 'u': "https://developer.aliyun.com/article/1748300", 'a': "佚名", 'd': "2026-07-16", 'x': "Delta三角洲部队、T型能力全栈工程师、本体模型", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "从百炼到FDE:六大门派里，工程师该选哪一段?", 'u': "https://developer.aliyun.com/article/1755591", 'a': "佚名", 'd': "2026-08-13", 'x': "95家玩家切成6类、技能栈地图", 's': "一手", 'ten': "中性", 'st': "neu", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "从模型能力到业务结果:这本书讲透了FDE", 'u': "https://developer.aliyun.com/article/1757598", 'a': "佚名", 'd': "2026-08-22", 'x': "\"不等于外包，也不等于售前\"", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
        ],
    },
    {'key': "tencentcloud", 'cn': "腾讯云开发者社区", 'emoji': "🔵", 'color': "#0052d9",
     'note': "厂商社区：认证体系发布、大厂抢人与信任崩塌警示并存",
     'entries': [
            {'t': "腾讯云推出行业首个FDE工程师认证，同时启动FDE合作伙伴招募", 'u': "https://cloud.tencent.com/developer/article/2742722", 'a': "佚名", 'd': "2026-09-14", 'x': "**官方动作**，9月10日发布《腾讯云ADP前沿部署工程师（FDE）》认证体系", 's': "一手", 'ten': "中性（官方动态）", 'st': "neu", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "今天的FDE，就是曾经的TA(全栈要求·核心岗位·薪资暴涨·信任崩塌)", 'u': "https://cloud.tencent.com/developer/article/2745893", 'a': "佚名", 'd': "2026-09-17", 'x': "**负向代表作**，\"二元性\"左手交付右手产品、信任崩塌风险", 's': "一手", 'ten': "负向", 'st': "neg", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "Anthropic百万年薪抢的人，不是程序员，是\"带AI上战场\"的人", 'u': "https://cloud.tencent.com/developer/article/2740386", 'a': "佚名", 'd': "2026-09-09", 'x': "面试指南、年薪百万美元级别", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE:AI时代最抢手的四不像岗位，大厂开百万年薪抢人", 'u': "https://cloud.tencent.com/developer/article/2732877", 'a': "佚名", 'd': "2026-08-27", 'x': "Palantir 2011年Delta三角洲部队、把工程师派到客户现场", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE不再只是一个岗位:前向部署工程师、架构师、AI工程师的崛起", 'u': "https://developer.cloud.tencent.com/article/2730331?policyId=1004", 'a': "佚名", 'd': "2026-08-22", 'x': "Forward Deployed Software Engineer/Engineer/AI Engineer分类指南", 's': "一手", 'ten': "中性", 'st': "neu", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE", 'u': "https://cloud.tencent.com/developer/article/2671223", 'a': "佚名", 'd': "2026-05-20", 'x': "三大AI公司同时押注FDE、根本矛盾：AI落地比想象中难得多", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
            {'t': "FDE到底是什么?", 'u': "https://cloud.tencent.com/developer/news/4287193", 'a': "佚名", 'd': "2026-07-20", 'x': "四种能力：懂业务现场、能把方案落地、会用数据持续校准、能把经验沉淀", 's': "一手", 'ten': "正向", 'st': "pos", 'lsrc': "orig", 'nolink': False, 'dup': False},
        ],
    },
]

# 数据边界与采集说明（原文）
BOUNDARY = [
    "**样本口径**：本报告样本通过通用搜索与各平台公开页面采集（2026 年 9 月 22 日执行），覆盖 B站 12 条、脉脉 5 条、即刻 3 条、小红书 19 条、知乎 12 条、微博 7 条、CSDN 10 篇、掘金 12 篇、博客园 9 篇、SegmentFault 7 篇、InfoQ 7 篇、51CTO 7 篇、华为云社区 4 篇、阿里云开发者社区 6 篇、腾讯云开发者社区 7 篇，共 127 条（原报告此处记为 131 条，与其分平台明细合计不符，本站按明细校正，见修正说明）。",
    "**互动数据可得性**：B站、即刻、小红书可获取播放/热度/点赞/评论/收藏；脉脉仅显示阅读数（1–2），无点赞评论数据。",
    "**一手/二手区分**：B站、脉脉、即刻、小红书、知乎、微博、CSDN、掘金、博客园、SegmentFault、InfoQ、51CTO、华为云社区、阿里云开发者社区、腾讯云开发者社区条目均为一手信源（原帖/原视频/原专栏/原微博/原文章链接）。",
    "**局限性**：B站部分条目来自视频页推荐位；即刻徐邦睿条目链接为其个人主页而非单帖；知乎互动量普遍偏低（1–7 赞同）；微博以媒体转发为主；CSDN 阅读量为平台口径（数百级）；掘金互动量中等（1–56 赞）；博客园头部文章浏览量最高（5698）；SegmentFault 约10000条结果但精选文章互动量未逐一统计；InfoQ 与 51CTO 为技术媒体，以深度文章为主；华为云/阿里云/腾讯云社区为厂商开发者社区，以官方动作和深度分析为主。",
    "本报告仅供舆情观察与市场研究参考，不构成职业或投资建议。",
]

# 参考来源（原文 13 条）
REFS = [
    ("B站 FDE 教程合集", "https://www.bilibili.com/video/BV1HpNt6fE3q/"),
    ("B站 FDE 实战规划课", "https://www.bilibili.com/video/BV1WmMM6QErx"),
    ("B站 OpenAI FDE 圆桌", "https://www.bilibili.com/video/BV1tV7Q6TEcf/"),
    ("脉脉趋势讨论帖", "https://maimai.cn/article/detail?efid=yqcQbIcP9aMeE4f9q5vGFQ&fid=1919446545"),
    ("脉脉 35 岁程序员转 FDE 帖", "https://maimai.cn/article/detail?efid=2o-tLrwXr0lcGUiB2AmjIQ&fid=1923704409"),
    ("脉脉 FDE 伪命题帖", "https://maimai.cn/article/detail?efid=f8_Pv-o6ZBq6mKeybghm-w&fid=1924194448"),
    ("脉脉 CSM 转型方向帖", "https://maimai.cn/article/detail?efid=WDgLhlL10s7hCy_1KOSKmA&fid=1915897482"),
    ("脉脉猎头解读帖", "https://maimai.cn/article/detail?efid=-bReXzmOsKClWI3Hwd57wQ&fid=1923096164"),
    ("即刻范冰开源书动态", "https://m.okjike.com/originalPosts/6a7e6aa4846af03db5c88682"),
    ("即刻 High寧 主页", "https://m.okjike.com/users/143B8259-AD62-4C1B-A96F-4C7323623206"),
    ("即刻徐邦睿主页", "https://m.okjike.com/users/78c07949-236d-4de8-b859-244bf79ace42"),
    ("腾讯云开发者社区 FDE 解读（知乎转载形态）", "https://cloud.tencent.com/developer/article/2724165"),
    ("新浪财经（小红书 FDE 内容佐证）", "https://finance.sina.com.cn/wm/2026-08-31/doc-iniqfeam7887222.shtml.md"),
]

BILI_PLAY = [
    ("FDE(前沿部署工程师)入门到就业完整版教程", 23000),
    ("【2026最新版】全网最详尽FDE实战规划课", 654),
    ("OpenAI团队：FDE工程师的未来", 1385),
    ("【FDE】B站最全FDE落地实战与面试指南", 12000),
    ("2026年AI前沿部署工程师（FDE）入门到就业完整", 41000),
    ("【全526集】AI FDE入门到精通程", 57000),
    ("为什么FDE在AI时代这么火？因为差距不在模型，在业", 18000),
    ("3分钟了解FDE，20年前的概念最近火了？", 19000),
    ("WorkBuddy 力推 FDE，暴露企业 AI 最", 30000),
    ("终于，FDE也要烂大街了！", 15000),
    ("程序员&PM转行FDE，年薪65W+", 4246),
    ("未来硅世界第19期：FDE项目和AI Coding作", 3669),
]

# 各平台样本量（用于图表）
PLAT_SAMPLE = [
    ("B站", 12, "#7c3aed"),
    ("脉脉", 5, "#2563eb"),
    ("即刻", 3, "#0d9488"),
    ("知乎", 12, "#0891b2"),
    ("小红书", 19, "#dc2626"),
    ("微博", 7, "#d97706"),
    ("CSDN", 10, "#fc5531"),
    ("掘金", 12, "#1e80ff"),
    ("博客园", 9, "#0078e7"),
    ("SegmentFault", 7, "#009a61"),
    ("InfoQ", 7, "#b91c1c"),
    ("51CTO", 7, "#2b80ff"),
    ("华为云社区", 4, "#c7000b"),
    ("阿里云开发者社区", 6, "#ff6a00"),
    ("腾讯云开发者社区", 7, "#0052d9"),
]

