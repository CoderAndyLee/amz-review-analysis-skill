---
name: amz-review-analysis
description: >
  Amazon 评论分析：合并卖家精灵 review、按一级/二级/三级动态长出分类列、
  把好评差评原文摘录写入对应列，再按指南输出类目/品牌/ASIN 报告和 HTML 看板。
  Use when the user asks for Amazon review 分析、评论标注、好评差评分类、
  卖家精灵 review 合并、类目 review 把脉, or runs /amz-review-analysis
  or /amazon-review-analysis.
---

# Amazon Review 分析

按 `references/guide.md` 做，不另起框架。分类列在分析中长出；层级必须是一级 / 二级 / 三级。

协议与报告结构只写在：

- `references/taxonomy-protocol.md`
- `references/report-framework.md`

产品化背景、数据合同、看板约定见 `references/product-dev-spec.md`。后续对话先读该文档，不要另起分类法或看板信息架构。

类目特例（配件词、地形怎么挂）写在 `examples/`，不要写回主流程。

## 输入

一个类目目录，至少：

- `1 Products/`：BSR 或选品表（含 ASIN、品牌、标题、评分数）
- `2 Reviews/`：卖家精灵按 ASIN 导出的 xlsx

空目录骨架：`templates/category-folder/`。

先盘点：有多少 ASIN、下载条数 vs 站点评分数、是否混入配件、是否跨站点。样本缺口写进报告抬头。

## 流程

`<skill>` = 本仓库根目录。

### 1. 合并总表

```bash
python <skill>/scripts/merge_reviews.py \
  --reviews-dir "<cat>/2 Reviews" \
  --products-xlsx "<cat>/1 Products/<bsr>.xlsx" \
  --out "<cat>/3 Data/reviews_master.xlsx"
```

保留 `source_file`。不要删行；配件型号、非美、VP、Vine 用 flag。

空 ASIN 用文件名里的 listing ASIN 回填，并保留 review 上的子 ASIN。配件旗标必须写窄，禁止用泛化词把整机场景打成配件。

### 2. 抽样开列（第 1 波）

```bash
python <skill>/scripts/sample_reviews.py \
  --master "<cat>/3 Data/reviews_master.xlsx" \
  --n 80 --out "<cat>/5 Work/wave1_reviews.json"
```

从空 taxonomy 开始标这批。目标是一级挂稳、二级开始长，不是锁死分类。

### 3. 逐条标注

精读每条的 `标题` + `内容`。输出 JSONL，一条 review 一个对象：

```json
{
  "row_id": 12,
  "review_key": "https://...",
  "sentiment_mix": "混合",
  "assignments": [
    {
      "polarity": "好评",
      "l1": "功能表现很好",
      "l2": "贴边修剪干净",
      "l3": "",
      "excerpt": "edge cutting is excellent along the driveway",
      "new_column": true
    }
  ]
}
```

规则见 `references/taxonomy-protocol.md`。默认落到二级；三级少开。辩证评论两边都摘。

```bash
python <skill>/scripts/apply_annotations.py \
  --master "<cat>/3 Data/reviews_master.xlsx" \
  --annotations "<cat>/5 Work/wave1_annotations.jsonl" \
  --batch wave1
```

### 4. 后续波次

```bash
python <skill>/scripts/export_pending.py \
  --master "<cat>/3 Data/reviews_master.xlsx" \
  --out "<cat>/5 Work/pending.json"
```

带着当前 taxonomy 继续标。对得上就复用列，对不上再加一级/二级/三级。

并行只允许发生在同一版词典之内。波次边界做近义对齐：

```bash
python <skill>/scripts/merge_columns.py \
  --master "<cat>/3 Data/reviews_master.xlsx" \
  --map "<cat>/5 Work/merge_map.json"
```

不要改成扁平标签，也不要第一波之后禁止加列。

### 5. 报告与看板

```bash
python <skill>/scripts/build_delivery.py \
  --master "<cat>/3 Data/reviews_master.xlsx" \
  --out-dir "<cat>/4 Reports" \
  --html-template "<skill>/templates/review-analysis.html" \
  --category "Robotic Lawn Mower" \
  --marketplace US \
  --date 2026/08/13
```

卡片约 200 字，由 Agent 写入看板文案和 `DIRECTION_DATA`（07 每条行动必须绑 1–2 条原声）。脚本会写出统计层、层级透视、`SOURCE_DATA` 和 01–06 的树。

看板标题不要写死类目名。`board-data.js` 里的 `PAGE_META` 只改 `category` / `marketplace` / `date`。

Demo：`examples/robotic-lawn-mower/review-analysis.html`。

### 6. 收尾

核对：混合评论是否双边进列、摘录是否原文、taxonomy 的 first_row_id 是否可回溯、报告数字能否从总表透视。本轮新学到的类目特例写进 `examples/<category>/`，不另起平行规则。

## 标注时的硬约束

- 单元格 = 原文摘录，不是模型复述
- 列名 = `极性|一级|二级` 或 `极性|一级|二级|三级`
- 一级少而稳，二级是分析颗粒，三级只在二级不够聚类时加
- 星级不替代文本：5 星里的差评点、1 星里的好评点都要摘
- 不把抽样 ASIN 写成全类目结论，除非覆盖已经声明为全量
