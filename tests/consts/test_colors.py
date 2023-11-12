from litecrypt.utils.consts import Colors


def test_colors():
    assert Colors.RED == "\033[91m"
    assert Colors.GREEN == "\033[92m"
    assert Colors.YELLOW == "\033[93m"
    assert Colors.BLUE == "\033[94m"
    assert Colors.MAGENTA == "\033[95m"
    assert Colors.CYAN == "\033[96m"
    assert Colors.BROWN == "\033[33;1m"
    assert Colors.RESET == "\033[0m"
