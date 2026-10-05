# photo-geolocator

给一张照片，用**能核对**的线索推出拍摄位置。不依赖大数据库，纯脚本 + 联网查事实。

## 能力

- `exif.py` — 读 GPS / 拍摄时间 / 35mm 等效焦距
- `geo.py` — WGS84/GCJ-02/BD-09 互转、两点方位与距离、沿方位定位、焦距→视角
- `refmeasure.py` — **参照物测量**：已知尺寸的参照物占多少像素 → 距离；已知距离量未知楼像素 → 楼高；两点像素差 → 偏角
- `sun.py` — 日期/时间/经纬度 → 太阳方位/高度；影子方向反推朝向
- `clues.py` — 车牌→省、电话国家码、靠左/靠右行驶

## 硬规则

- ❌ **禁止以图搜图/百度识图找位置**（不反向搜这是哪）
- ✅ 允许联网查参照物真实尺寸（车长、车道宽、层高、铁路跨距…）
- ✅ 允许联网查街景地图做实景比对

## 快速上手

```bash
uv run scripts/exif.py photo.jpg
uv run scripts/refmeasure.py range --real 4.6 --px 60 --width 3264 --hfov 62
uv run scripts/sun.py position --date 2026-10-04 --time 14:30 --lat 45.7 --lon 126.6
```

详见 `SKILL.md`。Python 3.10+。
