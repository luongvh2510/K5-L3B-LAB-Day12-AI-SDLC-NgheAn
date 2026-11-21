"""P3-04 Quán itemized stock, freshness and freshness-priced cooking rules."""

import copy
import unittest

from chonoi.contract import load_contract
from chonoi.freshness import UNITS_PER_POINT
from chonoi.ids import IdAllocator
from chonoi.inputs import InputPlayer
from chonoi.rng import Streams
from chonoi.sim.quan import QuanSim


TUNING = load_contract()["tuning"]
FRESH = TUNING["freshness"]
Q = TUNING["quan"]
HZ = TUNING["tick_hz"]
FIRST = Q["first_customer_tick"]


def item(ident, kind="ca_loc", fresh=100):
    return {"id": ident, "kind": kind, "fresh": fresh}


def customer(ident, table, item_ids, order_tick=0):
    return {"id": ident, "table_id": table, "dish_id": "ca_loc_nuong_trui",
            "order_tick": order_tick, "reserved": item_ids}


def sim(scenario=None, stock=(), tuning=None):
    return QuanSim(tuning or TUNING, scenario or {}, Streams(4), IdAllocator(), inventory=list(stock))


def step_many(s, count):
    inputs = InputPlayer([])
    events = []
    for _ in range(count):
        events.extend(s.step(inputs.advance(s.sim_tick)))
    return events


class FreshnessAndReservation(unittest.TestCase):
    def test_count_adapter_and_locked_freshness_price_for_tip(self):
        adapted = QuanSim(TUNING, {}, Streams(4), IdAllocator(), inventory={"ca_loc": 1},
                          contract_version="1.2")
        self.assertEqual(adapted.stock[0]["kind"], "ca_loc")
        self.assertEqual(adapted.stock[0]["fresh"], FRESH["initial"] * UNITS_PER_POINT)

        scenario = {"random_customers": False, "player": {"pos": [9, 1.8]},
                    "hand": {"order_id": "K1", "dish_id": "ca_loc_nuong_trui", "base_price": 13},
                    "customers": [{"id": "K1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                                   "order_status": "assigned", "reserved": []}]}
        s = sim(scenario, [item("I1")])
        player = InputPlayer([{"tick": 0, "interact": True}])
        rows = s.step(player.advance(0))
        served = next(data for name, data in rows if name == "served")
        self.assertEqual((served["base_price"], served["tip"]), (13, 2))

    def test_quan_decay_includes_reserved_stock_and_spoil_event_is_id_sorted(self):
        stocks = [item("I10", fresh=30.004), item("I2", fresh=30.004)]
        scenario = {"random_customers": False,
                    "customers": [customer("K1", "T1", ["I10"]), customer("K2", "T2", ["I2"])]}
        t = copy.deepcopy(TUNING)
        t["quan"]["tables"] += [{"id": "T2", "pos": [13, 2]}]
        s = sim(scenario, stocks, t)
        self.assertEqual(s.stock[0]["fresh"], round(30.004 * UNITS_PER_POINT))
        events = step_many(s, 2)
        spoiled = [data["item_id"] for name, data in events if name == "spoiled"]
        self.assertEqual(spoiled, ["I2", "I10"])
        self.assertEqual(s.stock[0]["fresh"], round(30.004 * UNITS_PER_POINT) - 2)

    def test_spoiled_event_fires_once_across_later_ticks(self):
        s = sim(stock=[item("I1", fresh=30.004)])
        events = step_many(s, 8)
        spoiled = [(name, data) for name, data in events if name == "spoiled"]
        self.assertEqual(spoiled, [("spoiled", {"item_id": "I1", "kind": "ca_loc", "location": "stock"})])

    def test_spoiled_orders_release_then_re_reserve_once_in_order(self):
        stocks = [item("I1", fresh=30.004), item("I2", fresh=30.004), item("I3", fresh=31)]
        scenario = {"random_customers": False,
                    "customers": [customer("K2", "T2", ["I2"], order_tick=2),
                                  customer("K1", "T1", ["I1"], order_tick=1)]}
        t = copy.deepcopy(TUNING)
        t["quan"]["tables"] += [{"id": "T2", "pos": [13, 2]}]
        s = sim(scenario, stocks, t)
        step_many(s, 2)
        customers = {c["id"]: c for c in s.customers}
        self.assertEqual((customers["K1"]["order_status"], customers["K1"]["reserved"]),
                         ("reserved", ["I3"]))
        self.assertEqual((customers["K2"]["order_status"], customers["K2"]["reserved"]),
                         ("unfulfillable", []))

    def test_reservation_uses_freshest_then_id_order(self):
        s = sim(stock=[item("I10", fresh=80), item("I2", fresh=80)])
        events = step_many(s, FIRST)
        self.assertTrue(any(name == "customer_arrived" for name, _ in events))
        self.assertEqual(s.customers[0]["reserved"], ["I2"])
        self.assertEqual(s.snapshot()["customers"][0]["reserved"], ["I2"])

    def test_reservation_prefers_fresher_item_over_older_id(self):
        s = sim(stock=[item("I1", fresh=60), item("I2", fresh=80)])
        step_many(s, FIRST)
        self.assertEqual(s.customers[0]["reserved"], ["I2"])

    def test_spoiled_items_are_excluded_at_arrival_and_re_reservation(self):
        only_spoiled = sim(stock=[item("I1", fresh=29)])
        events = step_many(only_spoiled, FIRST)
        self.assertIn(("no_dish", {}), events)
        self.assertEqual(only_spoiled.customers, [])

        mixed = sim(stock=[item("I1", fresh=20), item("I2", fresh=80)])
        step_many(mixed, FIRST)
        self.assertEqual(mixed.customers[0]["reserved"], ["I2"])

        scenario = {"random_customers": False, "player": {"pos": [2, 8]},
                    "customers": [customer("K1", "T1", ["I3"])]}
        re_reserve = sim(scenario, [item("I1", fresh=20), item("I3", fresh=30.004)])
        step_many(re_reserve, 2)
        order = re_reserve.customers[0]
        self.assertEqual((order["order_status"], order["reserved"]), ("unfulfillable", []))
        press = InputPlayer([{"tick": re_reserve.sim_tick, "interact": True}])
        events = re_reserve.step(press.advance(re_reserve.sim_tick))
        self.assertFalse(any(name == "cook_started" for name, _ in events))
        self.assertEqual(re_reserve.stoves[0]["state"], "idle")

    def test_scenario_orders_without_reserved_are_served_by_order_tick_then_table(self):
        """Ticket-03: bỏ `reserved` cho đơn reserved thì cấp theo order_tick rồi id bàn, lấy tươi nhất rồi id nhỏ."""
        t = copy.deepcopy(TUNING)
        t["quan"]["tables"] += [{"id": "T2", "pos": [13, 2]}]
        stock = [item("I1", fresh=90), item("I2", fresh=70)]
        late_first_in_list = {"id": "K2", "table_id": "T2", "dish_id": "ca_loc_nuong_trui", "order_tick": 1}
        early = {"id": "K1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "order_tick": 5}
        s = sim({"random_customers": False, "customers": [early, late_first_in_list]}, [item("I1", fresh=90), item("I3", fresh=70)], t)
        by_id = {c["id"]: c["reserved"] for c in s.customers}
        self.assertEqual((by_id["K2"], by_id["K1"]), (["I1"], ["I3"]))  # order_tick nhỏ hơn (K2, đứng sau trong danh sách) giữ cá thể tươi nhất
        same_tick = [dict(early, order_tick=0), dict(late_first_in_list, order_tick=0)]
        s = sim({"random_customers": False, "customers": same_tick}, stock + [item("I9", fresh=60)], t)
        by_id = {c["id"]: c["reserved"] for c in s.customers}
        self.assertEqual((by_id["K1"], by_id["K2"]), (["I1"], ["I2"]))  # hòa order_tick thì theo id bàn T1 rồi T2

    def test_reservation_prefers_the_fresher_item_even_with_a_larger_id(self):
        """Bổ sung theo phá thử của D: giữ chỗ chọn cũ nhất thay vì tươi nhất không bị test cũ (hai cá thể cùng độ tươi) bắt."""
        s = sim(stock=[item("I1", fresh=50), item("I9", fresh=90)])
        step_many(s, FIRST)
        self.assertEqual(s.customers[0]["reserved"], ["I9"])

    def test_spoiled_event_is_emitted_once_when_crossing_not_every_tick(self):
        """Bổ sung theo phá thử của D: `spoiled` chỉ phát khi qua ngưỡng, không phát lại mỗi tick khi hàng đã ươn."""
        s = sim({"random_customers": False}, [item("I1", fresh=30.004)])
        events = step_many(s, 10)
        self.assertEqual([data["item_id"] for name, data in events if name == "spoiled"], ["I1"])
        self.assertTrue(TUNING["freshness"]["spoiled_below"] * UNITS_PER_POINT > s.stock[0]["fresh"])

    def test_spoiled_reserved_item_is_never_cooked(self):
        """Bổ sung theo phá thử của D: hàng đã ươn không được nấu dù còn trong phần giữ chỗ của khách."""
        s = sim({"random_customers": False, "player": {"pos": [2, 8]},
                 "customers": [customer("K1", "T1", ["I1"])]}, [item("I1", fresh=10)])
        rows = s.step(InputPlayer([{"tick": 0, "interact": True}]).advance(0))
        self.assertFalse(any(name == "cook_started" for name, _ in rows))
        self.assertEqual([x["id"] for x in s.stock], ["I1"])
        self.assertEqual(s.snapshot()["stoves"][0]["state"], "idle")

    def test_freshness_price_and_itemized_cook_payload(self):
        stocks = [item("I10", "ca_loc", 80), item("I2", "bong_dien_dien", 60)]
        s = sim({"random_customers": False, "player": {"pos": [2, 8]},
                 "customers": [{"id": "K1", "table_id": "T1", "dish_id": "canh_chua_ca_loc",
                                "reserved": ["I10", "I2"]}]}, stocks)
        inputs = InputPlayer([{"tick": 0, "interact": True}])
        rows = s.step(inputs.advance(0))
        event = next(data for name, data in rows if name == "cook_started")
        decay = round(FRESH["quan_decay_per_s"] * UNITS_PER_POINT / HZ)
        fresh_units = sum(round(x["fresh"] * UNITS_PER_POINT) - decay for x in stocks)
        expected = TUNING["menu"]["canh_chua_ca_loc"]["price"] * fresh_units // (
            100 * UNITS_PER_POINT * len(stocks))
        self.assertEqual(event["base_price"], expected)
        self.assertEqual([(x["kind"], x["id"]) for x in event["items"]],
                         [("bong_dien_dien", "I2"), ("ca_loc", "I10")])
        self.assertEqual(set(event["items"][0]), {"id", "kind", "fresh"})


if __name__ == "__main__":
    unittest.main()
