from main import Price, Order, OrderBook, Side


def test_prices():
    p1 = Price(12345, 2)
    p2 = Price(12346, 2)
    p3 = Price(12346, 3)
    p4 = Price(12345, 2)
    assert p1 < p2
    assert p3 < p1
    assert p1 == p4

def test_match_basic():
    ob = OrderBook()
    ob.submit_order(Order(Side.BUY, Price(1000, 2), 10))
    assert ob.get_order_count() == 1
    ob.submit_order(Order(Side.SELL, Price(1100, 2), 10))
    assert ob.get_order_count() == 0
