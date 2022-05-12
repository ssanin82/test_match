from math import isclose
from main import Price, Order, OrderBook, Side, Trade


def test_prices():
    p1 = Price(12345, 2)
    p2 = Price(12346, 2)
    p3 = Price(12346, 3)
    p4 = Price(12345, 2)
    assert p1 < p2
    assert p3 < p1
    assert p1 == p4


def test_no_match_basic():
    ob = OrderBook()
    ob.submit_order(Order(Side.BUY, Price(980, 2), 10))
    assert ob.get_order_count() == 1
    ob.submit_order(Order(Side.SELL, Price(990, 2), 10))
    assert ob.get_order_count() == 2


def test_match_opposite_all():
    ob = OrderBook()
    o1 = Order(Side.SELL, Price(1000, 2), 10)
    o2 = Order(Side.BUY, Price(1100, 2), 10)

    ob.submit_order(o1)
    assert ob.get_order_count() == 1
    trades = ob.submit_order(o2)
    assert ob.get_order_count() == 0
    assert len(trades) == 2
    assert trades[0] == Trade(o2.id, o2.qty, True)
    assert trades[1] == Trade(o1.id, o1.qty, True)


def test_match_opposite_incoming_full():
    ob = OrderBook()
    o1 = Order(Side.SELL, Price(1000, 2), 12)
    o2 = Order(Side.BUY, Price(1100, 2), 10)

    ob.submit_order(o1)
    assert ob.get_order_count() == 1
    trades = ob.submit_order(o2)
    assert ob.get_order_count() == 1
    assert len(trades) == 2
    assert trades[0] == Trade(o2.id, o2.qty, True)
    assert trades[1] == Trade(o1.id, o2.qty, False)
    assert ob.asks[o1.price][0].qty == 2


def test_match_opposite_existing_full():
    ob = OrderBook()
    o1 = Order(Side.SELL, Price(1000, 2), 10)
    o2 = Order(Side.BUY, Price(1100, 2), 13)

    ob.submit_order(o1)
    assert ob.get_order_count() == 1
    trades = ob.submit_order(o2)
    assert ob.get_order_count() == 1
    assert len(trades) == 2
    assert trades[0] == Trade(o2.id, o1.qty, False)
    assert trades[1] == Trade(o1.id, o1.qty, True)
    assert ob.bids[o2.price][0].qty == 3


def test_multi_match_buy():
    ob = OrderBook()
    o1 = Order(Side.SELL, Price(1001, 2), 2)
    o2 = Order(Side.SELL, Price(1002, 2), 3)
    o3 = Order(Side.SELL, Price(1003, 2), 2)
    o4 = Order(Side.BUY, Price(1100, 2), 4)
    o5 = Order(Side.BUY, Price(990, 2), 4)

    ob.submit_order(o1)
    ob.submit_order(o2)
    ob.submit_order(o3)
    assert ob.get_order_count() == 3
    trades = ob.submit_order(o4)
    trades += ob.submit_order(o5)
    assert ob.get_order_count() == 3
    assert len(trades) == 4
    assert trades[0] == Trade(o4.id, 2, False)
    assert trades[1] == Trade(o1.id, 2, True)
    assert trades[2] == Trade(o4.id, 2, True)
    assert trades[3] == Trade(o2.id, 2, False)
    assert o1.price not in ob.asks
    assert ob.asks[o2.price][0].qty == 1
    assert isclose(0.12, ob.get_spread())


def test_multi_match_sell():
    ob = OrderBook()
    o1 = Order(Side.BUY, Price(991, 2), 2)
    o2 = Order(Side.BUY, Price(992, 2), 3)
    o3 = Order(Side.BUY, Price(993, 2), 2)
    o4 = Order(Side.SELL, Price(990, 2), 4)
    o5 = Order(Side.SELL, Price(994, 2), 4)

    ob.submit_order(o1)
    ob.submit_order(o2)
    ob.submit_order(o3)
    assert ob.get_order_count() == 3
    trades = ob.submit_order(o4)
    trades += ob.submit_order(o5)
    assert ob.get_order_count() == 3
    assert len(trades) == 4
    assert trades[0] == Trade(o4.id, 2, False)
    assert trades[1] == Trade(o3.id, 2, True)
    assert trades[2] == Trade(o4.id, 2, True)
    assert trades[3] == Trade(o2.id, 2, False)
    assert o3.price not in ob.bids
    assert ob.bids[o2.price][0].qty == 1
    assert isclose(0.02, ob.get_spread())


def test_buys_in_order():
    ob = OrderBook()
    ob.submit_order(Order(Side.BUY, Price(1000, 2), 10))
    ob.submit_order(Order(Side.BUY, Price(999, 2), 10))
    kk = list(ob.bids.keys())
    assert kk[0] < kk[1]


def test_sells_in_order():
    ob = OrderBook()
    ob.submit_order(Order(Side.SELL, Price(1000, 2), 10))
    ob.submit_order(Order(Side.SELL, Price(999, 2), 10))
    kk = list(ob.asks.keys())
    assert kk[0] < kk[1]


def test_ask_levels():
    ob = OrderBook()
    ob.submit_order(Order(Side.SELL, Price(1000, 2), 10))
    ob.submit_order(Order(Side.SELL, Price(990, 2), 11))
    ob.submit_order(Order(Side.SELL, Price(1100, 2), 12))
    ob.submit_order(Order(Side.SELL, Price(1000, 2), 13))
    ask_levels = ob.get_ask_levels()
    assert len(ask_levels) == 3
    assert ask_levels[0] == (Price(990, 2), 11)
    assert ask_levels[1] == (Price(1000, 2), 23)
    assert ask_levels[2] == (Price(1100, 2), 12)


def test_bid_levels():
    ob = OrderBook()
    ob.submit_order(Order(Side.BUY, Price(1000, 2), 10))
    ob.submit_order(Order(Side.BUY, Price(990, 2), 11))
    ob.submit_order(Order(Side.BUY, Price(1100, 2), 12))
    ob.submit_order(Order(Side.BUY, Price(1000, 2), 13))
    bid_levels = ob.get_bid_levels()
    assert len(bid_levels) == 3
    assert bid_levels[2] == (Price(990, 2), 11)
    assert bid_levels[1] == (Price(1000, 2), 23)
    assert bid_levels[0] == (Price(1100, 2), 12)


def test_spread():
    ob = OrderBook()
    ob.submit_order(Order(Side.BUY, Price(1000, 2), 10))
    ob.submit_order(Order(Side.BUY, Price(1050, 2), 10))
    ob.submit_order(Order(Side.SELL, Price(1100, 2), 10))
    assert isclose(0.5, ob.get_spread())


def test_cancel_order():
    ob = OrderBook()
    o1 = Order(Side.SELL, Price(1000, 2), 10)
    o2 = Order(Side.SELL, Price(990, 2), 11)
    o3 = Order(Side.SELL, Price(1100, 2), 12)
    o4 = Order(Side.SELL, Price(1000, 2), 13)
    o5 = Order(Side.BUY, Price(900, 2), 10)
    o6 = Order(Side.BUY, Price(890, 2), 11)
    o7 = Order(Side.BUY, Price(910, 2), 12)
    o8 = Order(Side.BUY, Price(912, 2), 13)
    ob.submit_orders([o1, o2, o3, o4, o5, o6, o7, o8])

    ask_levels = ob.get_ask_levels()
    assert len(ask_levels) == 3
    assert ask_levels[0] == (Price(990, 2), 11)
    assert ask_levels[1] == (Price(1000, 2), 23)
    assert ask_levels[2] == (Price(1100, 2), 12)
    bid_levels = ob.get_bid_levels()
    assert len(bid_levels) == 4
    assert bid_levels[0] == (Price(912, 2), 13)
    assert bid_levels[1] == (Price(910, 2), 12)
    assert bid_levels[2] == (Price(900, 2), 10)
    assert bid_levels[3] == (Price(890, 2), 11)

    assert isclose(9.9 - 9.12, ob.get_spread())
    assert ob.get_order_count() == 8
    ob.cancel_order(o2.id)
    assert isclose(10 - 9.12, ob.get_spread())
    assert ob.get_order_count() == 7
    ob.cancel_order(o8.id)
    assert isclose(10 - 9.1, ob.get_spread())
    assert ob.get_order_count() == 6

    ob.cancel_order(o4.id)
    ask_levels = ob.get_ask_levels()
    assert len(ask_levels) == 2
    assert ask_levels[0] == (Price(1000, 2), 10)
    assert ask_levels[1] == (Price(1100, 2), 12)
    assert isclose(10 - 9.1, ob.get_spread())


# TODO ts sorted
