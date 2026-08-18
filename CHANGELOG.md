# Changelog

## v1.1.1 - 2026-08-18

- 看板模板去类目化：「买家口碑速读」（一句话/chips/评分盒）和「评论总结」六张卡不再写死在 HTML，改由 `CARDS_DATA`（cards.json + direction.json 的 `hero` 键）与 `SOURCE_DATA` 渲染；未提供时自动用一级频次与分区 lead 兜底
- 「整体分析」区同步去类目化：品牌图「仅本批 N 个 ASIN」、国家图副标题（按 countries 数据生成）、KPI「主分析评论」均改为动态
- 修复星级分布条全显示 0% 的问题（`SOURCE_DATA.stars` 为对象数组，模板按 `{star,n,pct}` 解析）
- `build_delivery.py` 的 `board-data.js` 输出新增 `CARDS_DATA` 段
- 修复：换类目重跑后看板速读/总结区仍显示上一类目内容的问题
- 割草机 demo 的 `board-data.js` 补入 `CARDS_DATA`，与新模板配对仍正常渲染

## v1.1.0 - 2026-08-18

- `build_delivery.py` 新增 `--cards-json`：写入 `09_评论总结` 六张卡
- `--direction-json` 扩展为 Agent 精编层：`board`（精编 BOARD_DATA）/ `highlights` / `pains`（DIRECTION_DATA）/ `rows`（写入 `11_产品方向`）/ `source`（品牌与 ASIN note 等）/ `brand_notes`（06 读法列）/ `asin_meta`（07 机型、一句话列）/ `readme_extra`（00 补充行）
- sheet 编号自动连续：未提供 Agent 文案时跳过 09/11 并重排前缀，不再出现编号空洞
- `00_说明` 增加加权评分公式、星级占比、VP/Vine 行和全 sheet 索引；`05_星级分布` 加权均分保留两位小数并附公式
- `board-data.js` 输出与既有成品逐字节兼容（PAGE_META 紧凑、其余段保持原分隔符）
- Demo 可复现：`examples/robotic-lawn-mower/` 新增 `cards.json`、`direction.json`，带 json 重跑可得到与 8/13 交付一致的 board-data.js 与 14 个 sheet

## v1.0.0 - 2026-08-16

首个公开版本。

- 全流程脚本：合并卖家精灵 review、抽样开列、JSONL 标注回写、近义列合并、频次统计、交付 Excel + HTML 看板
- 分类协议与报告框架（`references/`）
- 看板模板（口碑速读 / 六张总结卡 / 详细分析 01–07 / 月度趋势），ECharts 主 CDN 失败时自动切备用 CDN
- Demo：美区 Robotic Lawn Mower，10 个整机 ASIN / 主分析 956 条（`examples/`）
- 类目工作目录空骨架（`templates/category-folder/`）
