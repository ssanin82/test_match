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
    assert ob.asks[o2.price][0].qty == 2

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

def test_partial_fill():
    pass
    # ob = OrderBook()
    # ob.submit_order(Order(Side.BUY, Price(1000, 2), 10))
    # ob.submit_order(Order(Side.BUY, Price(999, 2), 10))
    # kk = list(ob.bids.keys())
    # assert kk[0] < kk[1]


# TODO levels
# TODO cancel order
# TODO ts sorted
