from dataclasses import dataclass, field
from enum import Enum
from sortedcontainers import SortedDict
from math import isclose
from datetime import datetime


_id = 0


def get_unique_id():
    global _id
    _id += 1
    return _id


class Side(Enum):
    BUY = 0
    SELL = 1


@dataclass
class Price:
    # XXX for simplicity assuming digits(qty) >= decimals
    qty: int
    decimals: int

    def to_float(self):
        return self.qty / 10**self.decimals

    def __lt__(self, other: "Price"):
        return self.to_float() < other.to_float()

    def __hash__(self):
        return hash((self.qty, self.decimals))


@dataclass
class Order:
    side: Side
    price: Price
    qty: float
    id: int = field(default_factory=get_unique_id)
    ts: float = field(default_factory=datetime.now)


@dataclass
class Trade:
    oid: int
    qty: float
    is_full: bool = False

    def __repr__(self) -> str:
        return f"oid={self.oid}, qty={self.qty}, full={self.is_full}"


class OrderBook:
    def __init__(self) -> None:
        self.bids = SortedDict()  # can only get reverse iterator later
        self.asks = SortedDict()
        self.oid_to_order = dict()

    def get_bids(self):
        # TODO list (price, qty)
        # rev
        return self.bids.values()

    def get_asks(self):
        # TODO (price, qty)
        return self.asks.values()
    
    def get_order_count(self):
        return len(self.oid_to_order)

    def get_spread(self):
        if self.bids and self.asks:
            return self.asks[0].price - self.bids[0].price
        else:
            return None

    def _match(self, o: Order, orders, orders_opposite, from_sell=True):
        trades = list()
        to_remove = list()
        filled = False
        for k in orders_opposite.__reversed__() if not from_sell else orders_opposite:
            for _o in orders_opposite[k]:
                if (
                    (not from_sell and o.price > _o.price)
                    or (from_sell and o.price < _o.price)
                ):
                    if o.qty > _o.qty:
                        trades.append(Trade(o.id, _o.qty))
                        trades.append(Trade(_o.id, _o.qty, True))
                        to_remove.append((_o.id, _o.price, _o.ts))
                        o.qty -= _o.qty
                    elif isclose(o.qty, _o.qty):
                        trades.append(Trade(o.id, _o.qty, True))
                        trades.append(Trade(_o.id, _o.qty, True))
                        to_remove.append((_o.id, _o.price, _o.ts))
                        filled = True
                    else:
                        trades.append(Trade(o.id, o.qty, True))
                        trades.append(Trade(_o.id, o.qty))
                        self.oid_to_order[_o.id].qty -= o.qty
                        filled = True
        for _id, p, ts in to_remove:
            del self.oid_to_order[_id]
            for i, oo in enumerate(orders_opposite[p]):
                if oo.ts == ts:
                    del orders_opposite[p][i]
                    if not orders_opposite[p]:
                        del orders_opposite[p]

        if not filled:
            if o.price not in orders:
                orders[o.price] = list()
            orders[o.price].append(o)
            orders[o.price].sort(key=lambda o: o.ts)
            self.oid_to_order[o.id] = o

        return trades

    def submit_order(self, o: Order):
        trades = None
        if Side.BUY == o.side:
            trades = self._match(o, self.bids, self.asks, False)
        else:
            trades = self._match(o, self.asks, self.bids)
        for t in trades:
            print(t)
        return trades

    def cancel_order(self, oid: int):
        o = self.id_to_order[oid]
        if Side.BUY == o.side:
            k = (o.price, o.ts)
            if k in self.bids[k]:
                del self.bids[k] 
        else:
            k = (o.price, o.ts)
            if k in self.asks[k]:
                del self.asks[k] 


def main():
    o1 = Order(Side.BUY, Price(10023, 2), 10)
    o2 = Order(Side.SELL, Price(10034, 2), 20)
    o3 = Order(Side.BUY, Price(10543, 3), 30)
    print(o1, o2, o3)


if "__main__" == __name__:
    main()
