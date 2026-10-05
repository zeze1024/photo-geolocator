---
name: photo-geolocator
description: 照片拍摄地点定位（看图找地点/网络迷踪）。自包含精简版：EXIF 读坐标时间焦距、查表（车牌/区号/行车方向）、太阳影子推朝向、参照物像素测距离/楼高/偏角（refmeasure.py）。★硬约束：禁止以图搜图/百度识图找位置；允许联网查参照物真实尺寸、查街景地图。Geolocate a photo with tool-verified reasoning — EXIF, lookup tables, sun/shadow math, reference-object photogrammetry. Use when the user shares a photo and asks 这是哪 / 在哪拍的 / 网络迷踪 / where was this taken.
---

# photo-geolocator

给一张照片，用**能核对**的线索推出拍摄位置。每个结论都要能指出用了哪个脚本、产出了什么。

## ★ 硬规则

1. **禁止以图搜图/百度识图找位置**。不得用反向图搜（百度识图、Yandex 识图、Google Lens 以图搜地点）来判定这是哪。
2. **允许联网**：① 查参照物真实尺寸（车长、车道宽、层高、铁路跨距、篮筐高等事实数据）；② 查街景地图（百度全景/Google Street View）做实景比对。
3. 不编核验。"在地图上量过""街景对上了"必须对应真跑过的命令；没跑就写"未核实"。
4. 精度要有出处。误差 ≤100 m 需要两条独立约束；拿不准就给区间 + 缺什么信息。
5. 元数据是假设。EXIF 坐标/时间和画面冲突时以画面为准。

## 脚本

| 脚本 | 作用 |
|---|---|
| `exif.py <照片>` | 读 GPS、拍摄时间、机型、35mm 等效焦距 |
| `geo.py` | WGS84/GCJ-02/BD-09 互转、两点方位/距离、沿方位走多远、35mm 焦距反算视角 |
| `refmeasure.py` | **参照物测量**：已知尺寸参照物占多少像素→距离；已知距离量未知楼像素→楼高；两点像素差→偏角 |
| `sun.py` | 日期/时间/经纬度→太阳方位/高度；影子方向→太阳方位→反推朝向 |
| `clues.py` | 车牌首位→省、电话国家码、靠左/靠右行驶 |

## 流程

1. **读元数据**：`exif.py photo.jpg`。有 GPS 直接给 WGS84 和 GCJ-02，但仍要用画面核对。有焦距就能算视角，不用猜倍率。
2. **提线索**：OCR 读招牌/路牌/车牌/站名；`clues.py plate 渝G` 落省；`clues.py country-code 86`、`clues.py side 日本` 判国家/行车方向。
3. **参照物测距离（核心新能力）**：
   - 先在照片里挑**明显参照物**（汽车、车道、公交、楼层、铁路桥墩跨距）。
   - 拿不准真实尺寸就**联网查**（例：标准铁路桥跨距、小汽车车长），别硬记。
   - 量它在图上的像素尺寸，算距离：`refmeasure.py range --real 4.6 --px 60 --width 3264 --hfov 62`
   - 用这个距离量旁边未知楼的像素高度→楼高（≈多少层）：`refmeasure.py height --dist 320 --px 240 --width 3264 --hfov 62`
   - 量两个参照物的水平像素差→偏角：`refmeasure.py gap --x1 1500 --x2 2000 --width 3264 --hfov 62`
4. **影子定朝向**：`sun.py position --date ... --time ... --lat ... --lon ...` 出太阳方位和影长比；`sun.py facing --shadow <影子指向>`。影子落在画面哪侧，就把画面朝向和真实方位对齐。
5. **坐标输出**：WGS84 + GCJ-02（`geo.py convert`），带误差半径和置信度。

## 输出

- 一句话：地点 + 机位 + 朝向（+ 拍摄时间，如能定）
- 坐标 WGS84 / GCJ-02 + 误差半径
- 推理链：线索 → 用了哪个脚本 → 范围
- 分档置信度（城市/片区/路/楼 各自评）
- 定不到就写：已确定到哪一级 + 还缺什么

## 运行

Python 3.10+，`uv run scripts/xxx.py`（exif 需 pillow）。坐标一律 (lat, lon)。
