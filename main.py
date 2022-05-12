from dataclasses import dataclass
from enum import Enum
from sortedcontainers import SortedDict
from math import isclose


_id = 0

# assume ts unique


def get_unique_id():
    _id += 1
    return _id


class Side(Enum):
    BUY = 0
    SELL = 1


class Price:
    qty: int
    decimals: int


@dataclass
class Order:
    id: int
    ts: float
    price: Price
    qty: float
    side: Side


@dataclass
class Level:
    price: float
    qty: float


class OrderBook:
    def __init__(self) -> None:
        self.bids = SortedDict(reversed=True)
        self.asks = SortedDict()
        self.oid_to_order = dict()

    def get_bids(self):
        # TODO list (price, qty)
        return self.bids.values()

    def get_asks(self):
        # TODO (price, qty)
        return self.asks.values()

    def get_spread(self):
        if self.bids and self.asks:
            return self.asks[0].price - self.bids[0].price
        else:
            return None

    def _prepare(self, o: Order, ctr):
        if o.price not in self.bids:
            self.bids[o.price] = list()
        self.bids[o.price].append(o)
        self.bids[o.price].sort(key=lambda o: o.ts)
        to_remove = list()
        for k, _o in self.asks.items():
            price, _ = k
            q = o.qty
            if o.price > price:
                q -= _o.qty
                if q > 0:
                    print(f"TRADE oid={o.id}, qty={o._qty}")
                    print(f"TRADE oid={_o.id}, qty={_o.qty} full")
                    to_remove.append((_o.id, _o.price, _o.ts))
                elif isclose(q, 0):
                    print(f"TRADE oid={o.id}, qty={o._qty} full")
                    print(f"TRADE oid={_o.id}, qty={_o.qty} full")
                    to_remove.append((o.id, o.price, o.ts))
                    to_remove.append((_o.id, _o.price, _o.ts))
                else:
                    print(f"TRADE oid={o.id}, qty={o._qty} full")
                    print(f"TRADE oid={_o.id}, qty={_o.qty}")
                    to_remove.append((o.id, o.price, o.ts))
        for _id, p, q in to_remove:
            del self.id_to_order[o.oid]
            del self.asks[(p, q)]

    def submit_order(self, o: Order):
        self.id_to_order[o.oid] = o

        # prepare
        if Side.BUY == o.side:
            # price -> list sorted by ts
            if o.price not in self.bids():
                self.bids[o.price] = list()
            self.bids[o.price].append(o)
            self.bids[o.price].sort(key=lambda o: o.ts)
            to_remove = list()
            for k, _o in self.asks.items():
                price, _ = k
                q = o.qty
                if o.price > price:
                    q -= _o.qty
                    if q > 0:
                        print(f"TRADE oid={o.id}, qty={o._qty}")
                        print(f"TRADE oid={_o.id}, qty={_o.qty} full")
                        to_remove.append((_o.id, _o.price, _o.ts))
                    elif isclose(q, 0):
                        print(f"TRADE oid={o.id}, qty={o._qty} full")
                        print(f"TRADE oid={_o.id}, qty={_o.qty} full")
                        to_remove.append((o.id, o.price, o.ts))
                        to_remove.append((_o.id, _o.price, _o.ts))
                    else:
                        print(f"TRADE oid={o.id}, qty={o._qty} full")
                        print(f"TRADE oid={_o.id}, qty={_o.qty}")
                        to_remove.append((o.id, o.price, o.ts))
            for _id, p, q in to_remove:
                del self.id_to_order[o.oid]
                del self.asks[(p, q)]
        else:
            if o.price not in self.asks():
                self.asks[o.price] = list()
            self.asks[o.price].append(o)
            self.asks[o.price].sort(key=lambda o: o.ts)
            #match
            # TODO


    def cancel_order(self, oid: int):
        o = self.id_to_order[o.oid]
        if Side.BUY == o.side:
            k = (o.price, o.ts)
            if k in self.bids[k]:
                del self.bids[k] 
        else:
            k = (o.price, o.ts)
            if k in self.asks[k]:
                del self.asks[k] 


def main():
    pass
