from pyvsystems_rewards.format import format_as_vsys


def test_format_as_vsys():
    assert format_as_vsys(100000000) == '1.00000000'
    assert format_as_vsys(703) == '0.00000703'
    assert format_as_vsys(4747) == '0.00004747'
    assert format_as_vsys(123456789) == '1.23456789'
    assert format_as_vsys(-123456789) == '-1.23456789'
