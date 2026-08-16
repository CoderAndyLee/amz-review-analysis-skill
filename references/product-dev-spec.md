# Amazon Review Analysis — 产品开发执行文档

> 给后续对话 / 其他模型用的单一背景包。读完应能独立理解：业务要解决什么、数据长什么样、分类协议、交付物长什么样、哪些已跑通、下一步做什么。
>
> 版本：2026-08-13  
> 业务发起人：Andy  
> 方法论来源：《Amazon Review 分析完全指南 - 20260952》  
> 参考实现：US Robotic Lawn Mower，10 ASIN / 963 条评论

---

## 1. 一句话

客户提供 **产品表 + Review 表 + LLM（自带 Key 或订阅额度）**，系统按固定框架产出：

1. 带一级 / 二级 / 三级分类列、单元格为**买家原文摘录**的标注总表  
2. 可下钻的层级透视（极性 → 一级 → 二级 → 三级 → 原声）  
3. 可交互 HTML 看板（口碑速读、评论总结六卡、详细分析 01–07、整体分析图表）

类目名、站点、日期只写在配置里，不写死在 HTML。

这不是「用 AI 写一篇评测」，而是 **可复用的评论标注 + 分析生成器**。割草机只是第一次跑通的类目。

---

## 2. 业务背景与目标用户

### 2.1 为什么做

选品 / 产品 / 运营看 Amazon 评论时，常见做法是抽几条差评或看星级分布。信息密度不够：

- 一条 4 星评论经常好坏都有，星级不能当标签  
- 同类问题散落在几百条英文长评里，无法聚类、无法 retro 到原话  
- 卖点、售后 FAQ、新品方向需要对着「足够多的原声案例」，不是模型复述

指南的核心手段：**分类列在分析过程中长出来**；每条评论的好评点 / 差评点，把**原文摘录**放进对应列。列攒厚了，某一类问题的客户原话就齐了。

### 2.2 谁用

- 内部：类目研究、竞品拆解、卖点 / 痛点、售后话术  
- 对外（产品化）：客户丢两张表，几天内拿到同一套看板 + Excel

### 2.3 明确不做

- 不把 10 个 ASIN 的样本写成「整个 Amazon 类目普查」（除非覆盖声明为全量）  
- 不先锁死一份「官方分类表」再往里塞  
- 不把整段 review 塞进一个列，不把同义措辞开成新列  
- 07 不是再讲一遍差评，是行动指引

---

## 3. 参考实现（必须知道的样本边界）

路径：参考实现的原始工作区不进本仓库。看板 Demo 在 `examples/robotic-lawn-mower/`。

| 项 | 值 |
|---|---|
| 类目 | US Robotic Lawn Mowers |
| 产品池 | BSR Top100，约 78 整机 + 配件噪声 |
| 本轮范围 | 已下载的 10 个整机 ASIN，**不补** Greenworks C30Z、WORX 头部机 |
| 评论 | 963 条全部标注；主分析排除 7 条配件行 → **956** |
| 综合分 | 3.9 / 5（1–5 星加权） |
| 星级 | 5★ 500 · 4★ 210 · 3★ 68 · 2★ 46 · 1★ 132 |
| sentiment_mix | 混合 459 · 好评 352 · 差评 138 · 信息不足 7 |
| VP / Vine | 764 / 82 |
| 非美 | 108（DE/FR 等，主要来自 ANTHBOT M5 导出混入） |
| 时间 | 2024-04 ~ 2026-08，2026 年 3 月后放量 |

**必须写进抬头的缺口：**

- 销量第一 Greenworks C30Z（月销约 1277 / 610 条评）不在池  
- BSR #2 WORX WR320s 不在池  
- NAVIMOW i110N 下载约 278/499，ANTHBOT M5 约 193/389  

结论口径：这 10 个已下载 ASIN 的买家声音，不是全美割草机普查。

---

## 4. 方法论（来自指南，产品必须遵守）

完整原文：`references/guide.md`。实现协议：`references/taxonomy-protocol.md`、`references/report-framework.md`。

### 4.1 分类是长出来的，不是先锁死

处理一条 review：

1. 只精读 **标题 + 内容**。星级只参考。  
2. 拆好评点 / 差评点。辩证评论必须两边都进。  
3. 对得上已有列 → 把**原文短摘录**写入该列。  
4. 对不上 → **新建**一级和/或二级（三级少开），再建完立刻写入摘录。  
5. 无有效信息 → `sentiment_mix=信息不足`，不加列。

单元格 = 买家原话，不改写、不翻译进总表（翻译只出现在看板里，点「翻译」才显示）。同一格多条用 ` | ` 连接。

### 4.2 层级

列名：

```
极性|一级|二级
极性|一级|二级|三级
```

例：`差评|贴边修剪差|贴边留边，仍需人工补刀`  
例：`差评|导航定位差|复杂地形易卡顿|小坑不平地反复卡住`

| 层 | 作用 | 增长 |
|---|---|---|
| 一级 | 聚类大桶，带极性，少而稳 | 很慢 |
| 二级 | **默认落点**，主分析颗粒 | 中等 |
| 三级 | 二级内要分开聚类的子情况 | 持续分析才频繁加 |

不要用一级列当落点。不要把「复杂地形易卡顿」再开成一级——它挂在「导航定位差」下，坑/坡/湿草进三级。

新列标准是**新语义**，不是新措辞。`battery dies` 和 `needs frequent recharge` 同一二级。

### 4.3 波次与近义合并

- 第 1 波：抽样约 80 条，让一级挂稳、二级开始长  
- 之后带着**同一版活词典**分批标，允许加列  
- 并行只允许发生在同一版词典之内  
- 波次边界做近义对齐：同义二级合并到先出现的列，摘录搬走，taxonomy 标 `merged`

### 4.4 分析框架（看板结构）

**评论总结（六张卡，各约 200 字，写判断）：**  
好评亮点 / 差评痛点 / 买家期待 / 人群画像 / 使用场景 / 购买理由  

卡片底部固定左下角跳转文案，必须指向详细分析对应节，不要写「查看一级/二级与原声」。

对应关系：

| 卡片 | 跳到 |
|---|---|
| 好评亮点 | 01 买家最喜欢什么 |
| 差评痛点 | 02 差评主要抱怨什么 |
| 买家期待 | 03 买家希望哪里更好 |
| 人群画像 | 04 哪些人群/场景更适合 |
| 使用场景 | 05 哪些情况不适合 |
| 购买理由 | 06 值不值这个价 |

**详细分析（手风琴）：**

- 点 01–07 展开/折叠  
- 点一级分类（绿点好评 / 红点差评）再展开二级  
- 二级描述附原声；默认只显示英文，点「翻译」才出中文  
- 每层展开后按**频次降序**

07 特殊（不是再讲差评）：

```
07 改进思路 & 新品方向     角标：x 个方向切入
  └ 二级 = 差评切入（贴边、卡住、装机…）
       ├ 改进思路
       │    ├ 一条改进
       │    │    └ 1–2 条对应原声
       │    └ …
       └ 新品方向
            ├ 一条新品命题
            │    └ 1–2 条对应原声
            └ …
```

**整体分析（ECharts，不是源表字段堆砌）：**  
KPI + 按月×星级堆叠趋势 + 星级/情感环图 + 类型/品牌/国家/ASIN 柱状。数字必须能从总表透视回去。

页头：`Amazon Review Analysis`，小字 `{类目} · {站点}`，日期胶囊 `YYYY/MM/DD`。全部来自 `PAGE_META`，禁止写死类目名。

---

## 5. 数据合同

### 5.1 产品表（卖家精灵 BSR 类导出）

常见 sheet：`US`。关键列：

`ASIN, 品牌, 商品标题, 父ASIN, 价格($), 小类BSR, 月销量, 月销售额($), 评分, 评分数, #, 上架时间`

读 xlsx 必须 `read_only=True`（部分导出含非法 drawing XML，普通 openpyxl 会挂）。

### 5.2 Review 表（按 ASIN 一个 xlsx）

关键列：

`ASIN, 标题, 标题(翻译), 内容, 内容(翻译), VP评论, Vine Voice评论, 型号, 星级, 赞同数, 图片数量, 图片地址, 是否有视频, 视频地址, 评论链接, 评论人, 所属国家, 评论时间`

注意：

- 文件名里的 ASIN 是 listing；表内 `ASIN` 可能是变体，也可能为空（空则回填 listing）  
- `标题(翻译)` / `内容(翻译)` 经常全空，不能依赖  
- 型号里可能混刀片 / 车库等配件行  

### 5.3 合并后总表 `reviews_master`

源字段 + 产品回挂 + 旗标 + 标注字段 + **动态分类列**。

旗标（不删行）：

| 字段 | 含义 |
|---|---|
| `source_file` | 来自哪份导出 |
| `listing_asin` | 文件名 ASIN |
| `flag_non_us` | 国家不是 US |
| `flag_accessory_model` | 型号像配件（刀片套装等）。禁止用泛化 `garage` 把「整机+车库」打成配件 |
| `flag_vp` / `flag_vine` | VP / Vine |
| `flag_has_image` / `flag_has_video` | 有图 / 有视频 |
| `sentiment_mix` | 好评 / 差评 / 混合 / 信息不足 |
| `annotate_status` | pending / done |
| `annotate_batch` | 波次名 |

分类列顺序（交付簿）：**先全部好评，再全部差评**；同极性内按一级 / 二级频次降序。从左往右不能好坏交错。

主分析默认：`flag_accessory_model` 为空。

### 5.4 单条标注 JSONL（LLM 输出合同）

```json
{
  "row_id": 12,
  "review_key": "https://...",
  "sentiment_mix": "混合",
  "assignments": [
    {
      "polarity": "好评",
      "l1": "功能表现很好",
      "l2": "真正切到的地方效果不错",
      "l3": "",
      "excerpt": "What it does decide to cut is nice.",
      "new_column": false
    }
  ]
}
```

`new_column=true` 仅当 `极性|一级|二级(|三级)` 不在当前活词典。一批 50 条里新列通常应很少。

### 5.5 看板数据 `board-data.js`

```js
window.PAGE_META = {
  title: "Amazon Review Analysis",
  category: "Robotic Lawn Mower",   // 换类目改这里
  marketplace: "US",
  date: "2026/08/13"
};
window.BOARD_DATA = [ /* 01–06 节：l1[] → l2[] → excerpts[{en,cn}] */ ];
window.DIRECTION_DATA = {
  pains: [
    {
      name: "贴边留边，仍需人工补刀",
      n: 106,
      polarity: "差评",
      improve: [{ text: "…", excerpts: [{en, cn}] }],
      product: [{ text: "…", excerpts: [{en, cn}] }]
    }
  ]
};
window.SOURCE_DATA = { /* n, rating, stars, mix, vp, vine, time[], brands, asins, countries */ };
```

`improve[]` / `product[]`：**每一条行动必须自带对应原声**，不能整节末尾堆 5 条共用摘录。

---

## 6. 流水线（已实现的脚本）

Skill 根目录：本仓库根目录。

| 步骤 | 脚本 | 作用 |
|---|---|---|
| 合并 | `scripts/merge_reviews.py` | 多 ASIN review 合并，挂产品，listing 回填，写旗标 |
| 抽样 | `scripts/sample_reviews.py` | 按品牌×星级抽第 1 波 |
| 回写 | `scripts/apply_annotations.py` | JSONL → 总表加列 + 摘录，重建 taxonomy |
| 导出待标 | `scripts/export_pending.py` | 未标注行 |
| 近义合并 | `scripts/merge_columns.py` | 旧列摘录并入保留列，删空列 |
| 统计 | `scripts/taxonomy_stats.py` | L1/L2 频次、品牌/ASIN 切片 JSON |
| 交付簿 | `scripts/build_delivery.py` | 生成交付 xlsx + 整包写出 `board-data.js` + 拷贝 HTML |

建议目录：

```
<类目>/
  1 Products/     BSR 或选品表
  2 Reviews/      每 ASIN 一份 xlsx
  3 Data/         reviews_master.xlsx（工作底稿，交付后不要当唯一成品）
  4 Reports/      HTML + board-data.js + 交付 xlsx
  5 Work/         波次 JSONL、摘录翻译缓存
```

本轮交付物：

| 文件 | 说明 |
|---|---|
| `examples/robotic-lawn-mower/review-analysis.html` | 看板 Demo（ECharts 走 CDN） |
| `examples/robotic-lawn-mower/board-data.js` | 页头 + 01–07 + 整体分析数据 |
| 原始 `reviews_master.xlsx` | 不上库（含评论人与全文） |

---

## 7. 看板交互约定（实现时不要走回头路）

已和业务方对齐过的交互，后续改 UI 不得无故推翻：

1. 评论总结和详细分析在**同一页上下排列**，不要拆成两个 Tab。  
2. 默认摘录**只显示英文**；点「翻译」才显示中文；再点「原文」收回。不要默认中英双语、不要 EN/CN 分段器当默认。  
3. 绿点 = 好评，红点 = 差评。  
4. 展开后每一层频次降序。  
5. 卡片跳转文案钉在卡片**底部靠左**，文案是目标节名。  
6. 07 角标：**x 个方向切入**（不是「差评切入」）。  
7. 整体分析用 **ECharts**，不要手写 SVG 表。  
8. 页头类目 / 站点 / 日期来自 `PAGE_META`。

---

## 8. 产品化形态

### 8.1 最小输入

```
产品表路径 + Review 目录 + PAGE_META + LLM endpoint/key
```

可选：客户自带 Key，或平台订阅额度。

### 8.2 建议模块

| 模块 | 职责 |
|---|---|
| Ingest | 读卖家精灵 xlsx，listing 回填，配件/非美打标，去重 |
| Labeler | 带活词典逐条/分批调 LLM，写 JSONL，回写宽表 |
| Taxonomy | 新列登记、近义合并、first_row 追溯 |
| Synthesizer | 六张卡、01–06 结构、07 行动（每条绑原声）、摘录翻译 |
| Analytics | 星级、时间×星、品牌/ASIN/VP/Vine/图视频 |
| Publisher | 写 `board-data.js`、套 HTML 模板、出交付 xlsx |

### 8.3 必须人审的门禁（第一版不要省）

- 第 1 波结束后扫一眼一级是否爆炸、是否有同义两列  
- 07 每条 improve/product 是否真有对应原声（禁止空绑、禁止张冠李戴）  
- 样本边界是否写进页头（缺哪些头部品牌/ASIN、覆盖率）  
- 配件规则换类目是否误伤整机  

### 8.4 商业包装

- 单次：两张表 → HTML + Excel  
- 订阅：类目月更，只标增量，分类列接着长  
- 嵌入：API 收表，回传 `board-data.js` + xlsx  

---

## 9. 质量红线（写进测试用例）

- 摘录是原文，不是 paraphrase  
- 5 星里的差评点、1 星里的好评点都要摘  
- 混合评论两边进列  
- 数字能从总表非空单元格数对回去（注意：列命中次数 ≠ 去重评论数；看板一级 n 用**去重评论数**）  
- 不把 VP/Vine 开箱好评单独当成质量结论  
- 不把配件行主分析进整机结论  

---

## 10. 本轮已验证的工程坑

1. 卖家精灵 xlsx 含非法 drawing，`openpyxl` 非 `read_only` 会报错。  
2. 同一 listing 导出里大量行 `ASIN` 为空，必须用文件名 listing 回填，否则丢行（本轮曾丢 141 条）。  
3. `型号` 含 `Garage` 不等于配件（「High Version+Garage」是整机套装）。  
4. 变体 ASIN 不在 BSR 表里，品牌要用 listing 回挂，否则品牌变空。  
5. ANTHBOT M5 会混入 DE/FR 评论和刀片/车库型号，要靠旗标而不是删除。  
6. ECharts 看板依赖 CDN；离线交付需打包本地 `echarts.min.js`。  
7. `build_delivery.py` 必须整包写回 `PAGE_META` / `BOARD_DATA` / `DIRECTION_DATA` / `SOURCE_DATA`，禁止只改其中一块。  

---

## 11. 给下一任实现者的优先级

**P0 — 变成产品入口（缺这个就还是手工编排）**

一个命令或一个 API：

```
--products --reviews --category --marketplace --date --llm
→ 3 Data/reviews_master.xlsx
→ 4 Reports/review-analysis.html + board-data.js
→ 4 Reports/*-Review-Analysis.xlsx
```

**P1 — Labeler 产品化**

- 活词典作为请求上下文传入 LLM  
- 批大小、新列配额、近义合并自动化  
- 翻译缓存（本轮已有 `5 Work/excerpts_cn.json`）  

**P1 — 07 生成器**

输入：高频差评二级 + 该列全部摘录  
输出：`improve[]` / `product[]`，每条 1–2 条**语义对齐**的原声  
校验：无摘录的行动项不得进看板  

**P2 — 增量与多站点**

只标新 `review_key`；taxonomy 跨月继承。  

**P2 — 离线包**

ECharts 与字体打进交付目录。  

---

## 12. 其他对话应先读的文件

按这个顺序喂给下一个模型：

1. **本文**（业务 + 产品 + 已做 + 坑）  
2. `Amazon Review 分析完全指南 - 20260952.md`（原始方法论，含截图路径）  
3. 仓库根目录 `SKILL.md` + `references/taxonomy-protocol.md` + `references/report-framework.md`  
4. 看板实物：`examples/robotic-lawn-mower/review-analysis.html`（用浏览器打开，不要只读源码）  
5. 分类树协议：`references/taxonomy-protocol.md`；类目特例见 `examples/robotic-lawn-mower/NOTES.md`  

不要从零发明另一套分类法或另一套看板信息架构。有争议先对照第 4、7 节「已对齐的交互」，再改。

---

## 13. 术语表

| 用语 | 含义 |
|---|---|
| 活词典 / taxonomy | 分析中长出的一级/二级/三级列清单 |
| 分类列 | 总表右侧 `极性\|一级\|二级` 列，格内是摘录 |
| 波次 | 一批标注；波次边界才合并近义列 |
| VP | Amazon Vine 以外的 Verified Purchase 一类标记（源表「VP评论」） |
| Vine | Vine Voice 评论 |
| listing_asin | 导出文件名所代表的父/当前 listing |
| 主分析 | 排除配件型号行后的统计口径 |
| 方向切入 | 07 里作为二级的差评主题，展开后是行动不是再骂一次 |
| PAGE_META | 看板类目 / 站点 / 日期配置 |
