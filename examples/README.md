# examples

类目特例和 Demo 放这里，不要写回 `SKILL.md` 主流程。

## robotic-lawn-mower

第一次跑通的参考实现。

- `review-analysis.html` + `board-data.js`：可直接用浏览器打开
- `cards.json` + `direction.json`：本轮 Agent 精编文案。与 `reviews_master.xlsx` 一起喂给 `scripts/build_delivery.py` 可复现成品（board-data.js 逐字节一致，交付簿 14 个 sheet）
- `NOTES.md`：配件旗标、卡住如何挂树、样本边界

数字口径：10 个已下载整机 ASIN，963 条标注，主分析排除 7 条配件行 → 956。不是全美割草机普查。
