from dynamodb_counter import Counter


def test_counter():
    counter = Counter(
        table='test',
        PK='users',
        SK='count'
    )

    assert counter.reset() == 0
    assert counter.next() == 1
    assert counter.next(increment=5) == 6
    assert counter.set(12) == 12
    assert counter.next() == 13
    assert counter.reset() == 0