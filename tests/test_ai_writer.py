import re

import repackage

repackage.up()
from src.ai.ai_writer import Filter


def test_contains_pattern1():
    text = "Speaking at the United Nations General Assembly in New York"
    pattern = r"[Nn]ew"
    flags = None
    assert Filter.contains_pattern(pattern, text, flags) is True


def test_contains_pattern2():
    text = "Speaking at the United Nations General Assembly in New York"
    pattern = r"[Nn]ew"
    flags = re.I
    assert Filter.contains_pattern(pattern, text, flags) is True


def test_contains_pattern3():
    text = "Speaking at the United Nations General Assembly in New York"
    pattern = r"[Nn]ew"
    flags = re.NOFLAG
    assert Filter.contains_pattern(pattern, text, flags) is True


def test_contains_pattern4():
    text = "Speaking at the United Nations General Assembly in New York"
    pattern = r"new"
    flags = re.NOFLAG
    assert Filter.contains_pattern(pattern, text, flags) is False


def test_contains_video_yes1():
    text = "Speaking at the United Nations Video General Assembly in New York, Yoon"
    assert Filter.contains_video(text) is True


def test_contains_video_yes2():
    text = "Speaking at the United Nations VIDEO General Assembly in New York, Yoon"
    assert Filter.contains_video(text) is True


def test_contains_video_yes3():
    text = "Speaking at the United Nations video General Assembly in New York, Yoon"
    assert Filter.contains_video(text) is True


def test_contains_video_no():
    text = "Speaking at the United Nations General Assembly in New York, Yoon"
    assert Filter.contains_video(text) is False


def test_is_too_short_text_short():
    short_text = """Speaking at the United Nations General Assembly in New York, Yoon
    declared: “While military strength may vary among countries, by uniting in unwavering
    solidarity and steadfastly adhering to our principles, we can deter any unlawful
    provocation.” He also called to reform the UN Security Council - of which Russia
    is a member - saying such a move “would receive a broad support” if Moscow did supply
    Pyongyang with information in exchange for weapons. “It is paradoxical that
    a permanent member of the UN Security Council, entrusted as the ultimate guardian
    of world peace, would wage war by invading another sovereign nation and receive
    arms and ammunition from a regime that blatantly violates UN Security Council
    resolutions,” Yoon said."""
    assert Filter.is_too_short_text(short_text) is True


def test_is_too_short_text_long():
    long_text = """Speaking at the United Nations General Assembly in New York, Yoon
    declared: “While military strength may vary among countries, by uniting in unwavering
    solidarity and steadfastly adhering to our principles, we can deter any unlawful
    provocation.” He also called to reform the UN Security Council - of which Russia
    is a member - saying such a move “would receive a broad support” if Moscow did supply
    Pyongyang with information in exchange for weapons. “It is paradoxical that
    a permanent member of the UN Security Council, entrusted as the ultimate guardian
    of world peace, would wage war by invading another sovereign nation and receive
    arms and ammunition from a regime that blatantly violates UN Security Council
    resolutions,” Yoon said. Speaking at the United Nations General Assembly in New York,
    Yoon
    declared: “While military strength may vary among countries, by uniting in unwavering
    solidarity and steadfastly adhering to our principles, we can deter any unlawful
    provocation.” He also called to reform the UN Security Council - of which Russia
    is a member - saying such a move “would receive a broad support” if Moscow did supply
    Pyongyang with information in exchange for weapons. “It is paradoxical that
    a permanent member of the UN Security Council, entrusted as the ultimate guardian
    of world peace, would wage war by invading another sovereign nation and receive
    arms and ammunition from a regime that blatantly violates UN Security Council
    resolutions,” Yoon said."""
    assert Filter.is_too_short_text(long_text) is False


def test_replace_unwanted_keywords1():
    string = "Speaking at the United Nations General Assembly in New Yorks"
    keywords = {"United": "Unified"}
    assert (
        Filter.replace_unwanted_keywords(string, keywords)
        == "Speaking at the Unified Nations General Assembly in New Yorks"
    )


def test_replace_unwanted_keywords2():
    string = "Speaking at the CNN United Nations General Assembly in New Yorks"
    keywords = None
    assert (
        Filter.replace_unwanted_keywords(string, keywords)
        == "Speaking at the media United Nations General Assembly in New Yorks"
    )


def test_replace_unwanted_keywords3():
    string = "Speaking at the United Nations General Assembly in New Yorks"
    keywords = {"Lookup": "None"}
    assert (
        Filter.replace_unwanted_keywords(string, keywords)
        == "Speaking at the United Nations General Assembly in New Yorks"
    )
