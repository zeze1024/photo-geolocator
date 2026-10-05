#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""太阳位置：日期/时间/经纬度 -> 太阳方位角和高度角。影子朝哪=太阳在相反方位。

  sun.py position --date 2026-10-04 --time 14:30 --lat 45.7 --lon 126.6
  sun.py facing  --shadow 240
"""
from __future__ import annotations
import argparse, math, sys
from datetime import datetime

def solar_position(dt_local, tz, lat, lon):
    """返回 (方位角deg 0=北顺时针, 高度角deg)。"""
    N = dt_local.timetuple().tm_yday
    B = math.radians((N-1)*360/365)
    eot = 9.87*math.sin(2*B)-7.53*math.cos(B)-1.5*math.sin(B)
    tc = 4*(lon-tz*15)+eot
    solar_min = dt_local.hour*60+dt_local.minute+tc
    H = math.radians(15*(solar_min/60-12))
    dec = math.radians(23.45*math.sin(math.radians(360/365*(284+N))))
    la = math.radians(lat)
    sin_a = math.sin(la)*math.sin(dec)+math.cos(la)*math.cos(dec)*math.cos(H)
    alpha = math.asin(max(-1, min(1, sin_a)))
    cos_A = (math.sin(dec)-math.sin(alpha)*math.sin(la))/(math.cos(alpha)*math.cos(la))
    cos_A = max(-1, min(1, cos_A))
    A = math.acos(cos_A)
    az = (360-math.degrees(A)) if math.sin(H) > 0 else math.degrees(A)
    return az % 360, math.degrees(alpha)

def main():
    ap = argparse.ArgumentParser(description="太阳位置/影子推朝向")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("position")
    p.add_argument("--date", required=True); p.add_argument("--time", default="12:00")
    p.add_argument("--tz", type=float, default=8)
    p.add_argument("--lat", type=float, required=True); p.add_argument("--lon", type=float, required=True)
    f = sub.add_parser("facing"); f.add_argument("--shadow", type=float, required=True)
    args = ap.parse_args()
    if args.cmd == "position":
        dt = datetime.strptime(args.date+" "+args.time, "%Y-%m-%d %H:%M")
        az, h = solar_position(dt, args.tz, args.lat, args.lon)
        print(f"太阳方位角={az:.1f}deg(0=北,顺时针)  高度角={h:.1f}deg")
        ratio = 1/math.tan(math.radians(max(h,1))) if h > 0 else float("nan")
        print(f"影子朝向={(az+180)%360:.1f}deg  影长比≈{ratio:.2f}(物高倍数, 仅h>0)")
    elif args.cmd == "facing":
        sun = (args.shadow+180) % 360
        print(f"影子朝 {args.shadow:.0f}deg -> 太阳在 {sun:.0f}deg")
        print("影子落在画面左/右/正前方时，据此把画面朝向和真实方位对齐。")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8"); main()
