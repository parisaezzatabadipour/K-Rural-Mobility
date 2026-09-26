"""
modules/av_simulator.py
-----------------------
K-Rural-Mobility — شبیه‌ساز وضعیت لحظه‌ای کپسول‌های خودران.

مدل هر خودرو:
  • باتری ۰ تا ۱۰۰ درصد (مصرف ~۰٫۵٪ به‌ازای هر کیلومتر)
  • ظرفیت مسافر ۰ تا ۲ نفر
  • موقعیت جغرافیایی که به‌مرور زمان روی مسیر تخصیص‌یافته حرکت می‌کند
"""

import copy
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

KM_PER_TICK = 1.2          # سرعت شبیه‌سازی: کیلومتر در هر تیک
BATTERY_PER_KM = 0.5       # درصد مصرف باتری در هر کیلومتر
CAPACITY = 2


@dataclass
class AV:
    """وضعیت یک کپسول خودران ۲ نفره."""
    id: str
    lat: float
    lng: float
    battery: float = 100.0
    passengers: int = 0
    stops: List[Dict] = field(default_factory=list)   # توقف‌های باقی‌مانده
    status: str = "idle"                              # idle | moving | charging
    distance_done: float = 0.0                        # کیلومتر طی‌شده در سفر جاری
    wait_start: Optional[float] = None

    @property
    def available(self) -> bool:
        return self.status in ("idle", "moving") and self.battery > 10.0

    def assign_route(self, stops: List[Dict], passengers: int) -> None:
        """تخصیص مسیر جدید (خروجی routing_engine)."""
        self.stops = copy.deepcopy(stops)
        self.passengers = passengers
        self.status = "moving"
        self.distance_done = 0.0
        self.wait_start = time.time()

    def board(self, n: int) -> None:
        """سوار شدن مسافر (با رعایت ظرفیت)."""
        self.passengers = min(CAPACITY, self.passengers + n)

    def alight(self, n: int) -> None:
        """پیاده شدن مسافر."""
        self.passengers = max(0, self.passengers - n)


class FleetSimulator:
    """مدیریت کل ناوگان و آمار عملیات."""

    def __init__(self, fleet_defs: List[Dict]):
        self.vehicles: Dict[str, AV] = {
            f["id"]: AV(id=f["id"], lat=f["lat"], lng=f["lng"],
                        battery=f.get("battery", 100.0))
            for f in fleet_defs
        }
        self.completed_trips = 0
        self.total_wait_seconds = 0.0   # مجموع زمان انتظار سفرهای تکمیل‌شده
        self.total_distance_km = 0.0    # مجموع مسافت طی‌شده
        self.last_tick = time.time()

    # ---------- به‌روزرسانی فیزیکی ----------
    def _move_toward(self, av: AV, target_lat: float, target_lng: float,
                     km: float) -> float:
        """حرکت av به‌سوی نقطه هدف به اندازه km کیلومتر.
        خروجی: مسافت باقی‌مانده تا هدف (۰ یعنی رسید)."""
        from modules.routing_engine import haversine
        d = haversine(av.lat, av.lng, target_lat, target_lng)
        if d <= km or d == 0:
            av.lat, av.lng = target_lat, target_lng
            return 0.0
        ratio = km / d
        av.lat += (target_lat - av.lat) * ratio
        av.lng += (target_lng - av.lng) * ratio
        return d - km

    def tick(self, coords: Dict[str, tuple]) -> None:
        """
        یک تیک زمانی از شبیه‌سازی.
        coords: دیکشنری station_id -> (lat, lng) از RoutingEngine.
        """
        now = time.time()
        dt = max(now - self.last_tick, 0.05)
        self.last_tick = now

        for av in self.vehicles.values():
            if av.status == "moving" and av.stops:
                target_id = av.stops[0]["station_id"]
                tlat, tlng = coords[target_id]
                moved = KM_PER_TICK
                remaining = self._move_toward(av, tlat, tlng, moved)
                self.total_distance_km += moved - max(remaining, 0.0)
                av.battery = max(0.0, av.battery - BATTERY_PER_KM * (moved - max(remaining, 0.0)))

                if remaining <= 0.0:  # رسیدن به توقف
                    stop = av.stops.pop(0)
                    if stop["activity"] == "pickup":
                        av.board(stop["passengers"])
                    else:
                        av.alight(stop["passengers"])
                        self.completed_trips += 1
                        if av.wait_start is not None:
                            self.total_wait_seconds += (now - av.wait_start)
                    if not av.stops:
                        av.status = "idle"
                        av.passengers = 0

            # منطق شارژ: باتری پایین → رفتن به حالت شارژ تا ۸۰٪
            if av.battery <= 10.0 and av.status != "charging":
                av.status = "charging"
            elif av.status == "charging":
                av.battery = min(100.0, av.battery + 1.0)  # شارژ سریع شبیه‌سازی
                if av.battery >= 80.0:
                    av.status = "idle"

    # ---------- آمار KPI ----------
    def kpis(self) -> Dict:
        waits = self.total_wait_seconds
        avg_wait = (waits / self.completed_trips) if self.completed_trips else 0.0
        low_battery = sum(1 for v in self.vehicles.values() if v.battery < 20.0)
        return {
            "completed_trips": self.completed_trips,
            "avg_wait_seconds": round(avg_wait, 1),
            "total_distance_km": round(self.total_distance_km, 2),
            "fleet_size": len(self.vehicles),
            "fleet_active": sum(1 for v in self.vehicles.values() if v.status == "moving"),
            "fleet_idle": sum(1 for v in self.vehicles.values() if v.status == "idle"),
            "fleet_charging": sum(1 for v in self.vehicles.values() if v.status == "charging"),
            "low_battery_count": low_battery,
        }

    def snapshot(self) -> Dict[str, Dict]:
        """تصویر لحظه‌ای وضعیت برای داشبورد."""
        return {
            vid: {
                "lat": v.lat, "lng": v.lng,
                "battery": round(v.battery, 1),
                "passengers": v.passengers,
                "status": v.status,
                "next_stop": v.stops[0]["station_id"] if v.stops else None,
            }
            for vid, v in self.vehicles.items()
        }


if __name__ == "__main__":
    import json, os
    path = os.path.join(os.path.dirname(__file__), "..", "data", "rural_nodes.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    sim = FleetSimulator(data["fleet"])
    print(sim.snapshot())
    print(sim.kpis())
