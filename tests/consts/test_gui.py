from litecrypt.utils.consts import Gui


def test_gui_defaults():
    assert Gui.THEME == "vapor"
    assert Gui.TITLE == "Litecrypt"
    assert Gui.DIMENSIONS == "1500x800"
