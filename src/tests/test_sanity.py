import pytest


def test_one_equals_one():
    assert 1 == 1


@pytest.mark.asyncio
async def test_two_equals_two():
    assert 2 == 2
