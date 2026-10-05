#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""坐标系换算 + 方位/距离 + 相机几何。纯数学，无外部数据。经纬度一律 (lat, lon)。"""
from __future__ import annotations
import math, sys

_A = 6378245.0
_EE = 0.00669342162296594323

def _out_of_china(lat, lon):
    return not (73.66 < lon < 135.05 and 3.86 < lat < 53.55)

def _t_lat(x, y):
    r = -100 + 2*x + 3*y + 0.2*y*y + 0.1*x*y + 0.2*math.sqrt(abs(x))
    r += (20*math.sin(6*x*math.pi)+20*math.sin(2*x*math.pi))*2/3
    r += (20*math.sin(y*math.pi)+40*math.sin(y/3*math.pi))*2/3
    r += (160*math.sin(y/12*math.pi)+320*math.sin(y/30*math.pi))*2/3
    return r

def _t_lon(x, y):
    r = 300 + x + 2*y + 0.1*x*x + 0.1*x*y + 0.1*math.sqrt(abs(x))
    r += (20*math.sin(6*x*math.pi)+20*math.sin(2*x*math.pi))*2/3
    r += (20*math.sin(x*math.pi)+40*math.sin(x/3*math.pi))*2/3
    r += (150*math.sin(x/12*math.pi)+300*math.sin(x/30*math.pi))*2/3
    return r

def _gcj_delta(lat, lon):
    dlat = _t_lat(lon-105, lat-35); dlon = _t_lon(lon-105, lat-35)
    rad = lat/180*math.pi; m = 1-_EE*math.sin(rad)**2; sm = math.sqrt(m)
    dlat = dlat*180/((_A*(1-_EE))/(m*sm)*math.pi)
    dlon = dlon*180/(_A/sm*math.cos(rad)*math.pi)
    return dlat, dlon

def wgs2gcj(lat, lon):
    if _out_of_china(lat, lon): return lat, lon
    dlat, dlon = _gcj_delta(lat, lon); return lat+dlat, lon+dlon

def gcj2wgs(lat, lon):
    if _out_of_china(lat, lon): return lat, lon
    wlat, wlon = lat, lon
    for _ in range(8):
        glat, glon = wgs2gcj(wlat, wlon); wlat += lat-glat; wlon += lon-glon
    return wlat, wlon

_XPI = math.pi*3000/180

def gcj2bd(lat, lon):
    z = math.hypot(lon, lat)+0.00002*math.sin(lat*_XPI)
    th = math.atan2(lat, lon)+0.000003*math.cos(lon*_XPI)
    return z*math.sin(th)+0.006, z*math.cos(th)+0.0065

def bd2gcj(lat, lon):
    x, y = lon-0.0065, lat-0.006
    z = math.hypot(x, y)-0.00002*math.sin(y*_XPI)
    th = math.atan2(y, x)-0.000003*math.cos(x*_XPI)
    return z*math.sin(th), z*math.cos(th)

def convert(lat, lon, src, dst):
    if src == dst: return lat, lon
    if src == "wgs": wlat, wlon = lat, lon
    elif src == "gcj": wlat, wlon = gcj2wgs(lat, lon)
    elif src == "bd": wlat, wlon = gcj2wgs(*bd2gcj(lat, lon))
    else: raise ValueError(src)
    if dst == "wgs": return wlat, wlon
    g = wgs2gcj(wlat, wlon)
    if dst == "gcj": return g
    if dst == "bd": return gcj2bd(*g)
    raise ValueError(dst)

_R = 6371008.8

def distance(p, q):
    la1,lo1,la2,lo2 = map(math.radians, (*p, *q))
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*_R*math.asin(math.sqrt(h))

def bearing(p, q):
    la1,lo1,la2,lo2 = map(math.radians, (*p, *q))
    y = math.sin(lo2-lo1)*math.cos(la2)
    x = math.cos(la1)*math.sin(la2)-math.sin(la1)*math.cos(la2)*math.cos(lo2-lo1)
    return (math.degrees(math.atan2(y, x))+360) % 360

def dest(p, brg, dist_m):
    la1, lo1 = map(math.radians, p); b = math.radians(brg); d = dist_m/_R
    la2 = math.asin(math.sin(la1)*math.cos(d)+math.cos(la1)*math.sin(d)*math.cos(b))
    lo2 = lo1+math.atan2(math.sin(b)*math.sin(d)*math.cos(la1), math.cos(d)-math.sin(la1)*math.sin(la2))
    return math.degrees(la2), math.degrees(lo2)

def focal_px(image_w_px, hfov_deg):
    return (image_w_px/2)/math.tan(math.radians(hfov_deg)/2)

def fov_from_equiv_focal(focal_mm, aspect=(4, 3)):
    diag = 43.2666; w, h = aspect; k = diag/math.hypot(w, h)
    ls, ss = w*k, h*k
    return math.degrees(2*math.atan(ls/2/focal_mm)), math.degrees(2*math.atan(ss/2/focal_mm))

def range_from_size(real_m, size_px, image_w_px, hfov_deg):
    return real_m*focal_px(image_w_px, hfov_deg)/size_px

def px_to_angle(px, center_px, image_w_px, hfov_deg):
    return math.degrees(math.atan((px-center_px)/focal_px(image_w_px, hfov_deg)))

def _pair(s):
    a, b = s.split(","); return float(a), float(b)

def main():
    import argparse
    ap = argparse.ArgumentParser(description="坐标换算/方位/距离/相机几何")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("convert")
    c.add_argument("--from", dest="src", required=True, choices=["wgs","gcj","bd"])
    c.add_argument("--to", dest="dst", required=True, choices=["wgs","gcj","bd"])
    c.add_argument("a", type=float); c.add_argument("b", type=float)
    b = sub.add_parser("bearing"); b.add_argument("p", type=_pair); b.add_argument("q", type=_pair)
    d = sub.add_parser("dest"); d.add_argument("p", type=_pair)
    d.add_argument("--bearing", type=float, required=True); d.add_argument("--dist", type=float, required=True)
    f = sub.add_parser("fov"); f.add_argument("focal", type=float)
    args = ap.parse_args()
    if args.cmd == "convert":
        x, y = convert(args.a, args.b, args.src, args.dst); print(f"{x:.7f},{y:.7f}")
    elif args.cmd == "bearing":
        print(f"bearing={bearing(args.p,args.q):.1f}deg  distance={distance(args.p,args.q):.0f}m")
    elif args.cmd == "dest":
        la, lo = dest(args.p, args.bearing, args.dist); print(f"{la:.7f},{lo:.7f}")
    elif args.cmd == "fov":
        lo, so = fov_from_equiv_focal(args.focal); print(f"长边视角={lo:.1f}deg  短边视角={so:.1f}deg")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8"); main()
