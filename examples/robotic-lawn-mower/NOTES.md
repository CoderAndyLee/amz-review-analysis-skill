# Robotic Lawn Mower 类目备注

只对这一轮样本有效。换类目不要照抄列名，只借判断方式。

## 样本边界

- 站点：Amazon US
- 已下载 10 个整机 ASIN，963 条全部标注
- 主分析排除 `flag_accessory_model=Y` 的 7 行 → 956
- 缺销量第一 Greenworks C30Z、缺 BSR #2 WORX WR320s
- NAVIMOW i110N、ANTHBOT M5 下载覆盖不全
- 非美 108 条主要来自 ANTHBOT M5 导出混入
- VP / Vine 偏多，开箱观感类好评要打折

## 配件旗标

不要用泛化的 `garage` / `wheel` 去匹配。

会误伤：「High Version+Garage」是整机套装；评论里写把机器停在车库不是配件。

本轮收窄后的型号规则见 `scripts/merge_reviews.py` 的 `ACCESSORY_MODEL_RE`。换类目必须重写这则正则。

## 分类怎么挂

「卡住」不要开成一级。

- 一级：导航定位差
- 二级：复杂地形易卡顿
- 三级：小坑 / 上坡 / 湿草 / 覆盖物

贴边留边是全表最高频差评二级，仍挂在「贴边修剪差」下，不要升成一级。

## 07

二级仍是差评（贴边、卡住、装机…）。展开才是「改进思路」和「新品方向」，每条绑 1–2 句原话。

## 复现成品

`cards.json` / `direction.json` 是本轮 Agent 精编文案（六张卡、看板分区与 desc、产品方向行、品牌/ASIN 点评）。配合项目 `3 Data/reviews_master.xlsx` 重跑：

```bash
python <skill>/scripts/build_delivery.py \
  --master ".../3 Data/reviews_master.xlsx" \
  --out-dir <输出目录> \
  --category "Robotic Lawn Mower" --marketplace US --date 2026/08/13 \
  --title "Amazon Review Analysis" \
  --excerpts-cn ".../5 Work/excerpts_cn.json" \
  --cards-json cards.json \
  --direction-json direction.json
```

得到的 `board-data.js` 与 2026/08/13 交付版逐字节一致；交付簿 14 个 sheet 中 12 个内容一致（`10_详细分析` 为脚本自动树版本、`06_品牌切片` 列更全，属通用模板与精编版的预期差异）。
