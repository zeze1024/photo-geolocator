#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""小查表：车牌省份、电话国家码、行车方向。内置精简表。

  clues.py plate 渝G / clues.py country-code 86 / clues.py side 日本
"""
from __future__ import annotations
import sys

PLATE_PROVINCE = {
    "京":"北京","津":"天津","沪":"上海","渝":"重庆",
    "冀":"河北","晋":"山西","辽":"辽宁","吉":"吉林","黑":"黑龙江",
    "苏":"江苏","浙":"浙江","皖":"安徽","闽":"福建","赣":"江西","鲁":"山东",
    "豫":"河南","鄂":"湖北","湘":"湖南","粤":"广东","琼":"海南",
    "川":"四川","黔":"贵州","滇":"云南","陕":"陕西","甘":"甘肃","青":"青海",
    "蒙":"内蒙古","桂":"广西","宁":"宁夏","新":"新疆","藏":"西藏",
}
COUNTRY_CODE = {
    "86":"中国","852":"香港","853":"澳门","886":"台湾",
    "1":"美国/加拿大","44":"英国","81":"日本","82":"韩国",
    "65":"新加坡","61":"澳大利亚","49":"德国","33":"法国","7":"俄罗斯",
}
LEFT_TRAFFIC = {
    "英国","日本","泰国","澳大利亚","印度","印度尼西亚","巴基斯坦",
    "香港","澳门","新加坡","马来西亚","新西兰","南非","爱尔兰",
}

def main():
    if len(sys.argv) < 3: sys.exit(__doc__)
    kind, val = sys.argv[1], sys.argv[2]
    if kind == "plate": print(f"{val} -> {PLATE_PROVINCE.get(val.strip()[:1], '未知')}")
    elif kind == "country-code": print(f"+{val} -> {COUNTRY_CODE.get(val, '未知')}")
    elif kind == "side": print(f"{val} -> {'靠左行驶' if val in LEFT_TRAFFIC else '靠右行驶'}")
    else: sys.exit(__doc__)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8"); main()
