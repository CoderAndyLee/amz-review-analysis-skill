# Car Phone Mount 类目备注

只对这一轮样本有效。换类目不要照抄列名，只借判断方式。

## 样本边界

- 站点：Amazon US；5 个 listing 各 8 条、共 40 条，全部 VP、无非美、无 Vine
- 5★ 32 · 4★ 8（加权 4.8），**无 1–3 星**：负面信号全部从 4–5 星的抱怨点里摘
- 未提供 BSR/选品表：覆盖率不可算，品牌/机型按公开 listing 补齐
- 形态混合：吸盘臂式（iOttie/Romuto）、出风口式（Lamicall/Blukar）、无线充自动夹（MOKPR）

## 配件旗标

本类目 5 个 listing 全是整机支架，`ACCESSORY_MODEL_RE` 未命中任何行（割草机词表对此类目天然安全）。若后续加入替换胶贴/出风口延长片等配件链接，必须重写正则。

## 分类怎么挂

- 「装不上」不开成一级：挂在「适配性差」，二级分 风口叶片 / 大屏厚壳顶键 / 仪表台材质
- 「高温脱落 / 日晒老化 / 低温迟钝」统一挂「耐候性差」：这是材质命题，不是结构命题
- 「晃动 / 异响 / 夹力松」合并为「稳定性瑕疵」：都是「底座稳了之后」的第二层问题
- 无线充相关好评单独挂「无线充电好用」，不要散进「夹持稳固」

## 07

二级仍是差评。展开才是「改进思路」和「新品方向」，每条绑 1–2 句原话。小样本（n≤3）的结论只当方向假设，不要写成类目定论。

## 复现成品

```bash
python <skill>/scripts/build_delivery.py \
  --master ".../3 Data/reviews_master.xlsx" \
  --out-dir <输出目录> \
  --category "Car Phone Mount" --marketplace US --date 2026/08/18 \
  --title "Amazon Review Analysis" \
  --excerpts-cn excerpts_cn.json \
  --cards-json cards.json \
  --direction-json direction.json
```
