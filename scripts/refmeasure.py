#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""参照物测量：认出照片里明显参照物 -> 查真实尺寸 -> 量像素反推距离/楼高/偏角。

  refmeasure.py range  --real 4.6 --px 60 --width 3264 --hfov 62
  refmeasure.py height --dist 320 --px 240 --width 3264 --hfov 62
  refmeasure.py gap    --x1 1500 --x2 2000 --width 3264 --hfov 62
  refmeasure.py info
没给 --hfov 时用 --equiv-focal 35 反算视角。
"""
from __future__ import annotations
import argparse, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import geo  # noqa: E402

REFERENCES = {
    "car": 4.6, "car_width": 1.8, "bus": 12.0, "truck": 16.0,
    "lane": 3.5, "storey": 3.0, "bball_hoop": 3.05, "train_span": 32.0,
    "wheelbase_car": 2.7, "person": 1.7, "door": 2.05, "street_light": 8.0,
}

def _hfov(args):
    if args.equiv_focal:
        lo, _ = geo.fov_from_equiv_focal(args.equiv_focal); return lo
    return float(args.hfov)

def main():
    ap = argparse.ArgumentParser(description="参照物测距离/楼高/偏角")
    sub = ap.add_subparsers(dest="cmd", required=True)
    def common(p):
        p.add_argument("--width", type=int, required=True)
        g = p.add_mutually_exclusive_group(required=True)
        g.add_argument("--hfov", type=float); g.add_argument("--equiv-focal", type=float)
    r = sub.add_parser("range"); common(r)
    r.add_argument("--real", type=float, required=True); r.add_argument("--px", type=float, required=True)
    h = sub.add_parser("height"); common(h)
    h.add_argument("--dist", type=float, required=True); h.add_argument("--px", type=float, required=True)
    gp = sub.add_parser("gap"); common(gp)
    gp.add_argument("--x1", type=float, required=True); gp.add_argument("--x2", type=float, required=True)
    sub.add_parser("info")
    args = ap.parse_args()
    if args.cmd == "info":
        print("参照物真实尺寸参考(米), 拿不准请联网查:")
        for k, v in REFERENCES.items(): print(f"  {k:16s} = {v}")
        return
    hf = _hfov(args); f = geo.focal_px(args.width, hf)
    if args.cmd == "range":
        dist = args.real*f/args.px
        print(f"视角={hf:.1f}deg  焦距={f:.0f}px  -> 距离 ≈ {dist:.0f} m")
    elif args.cmd == "height":
        real = args.px*args.dist/f
        print(f"视角={hf:.1f}deg  -> 真实高度 ≈ {real:.1f} m  (≈{real/REFERENCES['storey']:.0f}层)")
    elif args.cmd == "gap":
        ang = math.degrees(math.atan(abs(args.x2-args.x1)/f))
        center = args.width/2
        a1 = geo.px_to_angle(args.x1, center, args.width, hf)
        a2 = geo.px_to_angle(args.x2, center, args.width, hf)
        print(f"两点水平偏角差 ≈ {ang:.2f} deg  (相对中心: {a1:+.1f}deg / {a2:+.1f}deg)")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8"); main()
