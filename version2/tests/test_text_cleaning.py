from core.utils.text_cleaning import clean_text


def test_clean_text_basic():
    text = "  Hello WORLD!!  "
    cleaned = clean_text(text)
    assert cleaned == "hello world"
