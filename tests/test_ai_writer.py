import re

import pytest
import repackage

repackage.up()
from src.ai.ai_writer import AI_Writer, Filter


@pytest.fixture(scope="module", name="string_empty")
def fixture_string_empty():
    yield ""


@pytest.fixture(scope="module", name="string_full")
def fixture_string_full():
    yield "Armenia PM takes swipe at Russia as first civilians leave breakaway Nagorno-Karabakh"


def test_rewrite_article_test_type(string_full):
    ai_writer = AI_Writer(string_full, string_full)
    assert isinstance(ai_writer.rewrite_article(), str) is True


def test_rewrite_article_test_non_equality(string_full):
    ai_writer = AI_Writer(string_full, string_full)
    assert ai_writer.rewrite_article() != string_full


def test_rewrite_headline_test_type(string_full):
    ai_writer = AI_Writer(string_full, string_full)
    assert isinstance(ai_writer.rewrite_headline(), str) is True


def test_rewrite_headline_test_non_equality(string_full):
    ai_writer = AI_Writer(string_full, string_full)
    assert ai_writer.rewrite_headline() != string_full


def test_detect_topic_named_entities_none(string_empty):
    article = "What is the most beautiful color?"
    ai_writer = AI_Writer(string_empty, article)
    classes = ["business", "politics", "lifestyle"]
    result = ai_writer.detect_topic(candidate_labels=classes)
    assert result == "lifestyle"


def test_detect_topic_per_named_entities_none(string_full):
    ai_writer = AI_Writer(string_full, string_full)
    classes = ["business", "politics", "lifestyle"]
    result = ai_writer.detect_topic(candidate_labels=classes)
    assert result == "politics"


def test_detect_topic_no_image():
    headline = ""
    article = "Ebighar Rajjashwili is the most famous Armenian politician."
    ai_writer = AI_Writer(headline, article)
    classes = ["economy", "lifestyle"]
    result = ai_writer.detect_topic(candidate_labels=classes)
    assert result == "economy"


def test_detect_topic_true():
    headline = ""
    article = "Donald Trump takes swipe at Russia as first civilians leave breakaway Nagorno-Karabakh"
    ai_writer = AI_Writer(headline, article)
    assert ai_writer.detect_topic() in [
        "images/donald_trump_0.jpg",
        "images/donald_trump_1.jpg",
        "images/donald_trump_2.jpg",
        "images/donald_trump_3.jpg",
    ]


def test_get_named_entities(string_full):
    ai_writer = AI_Writer(string_full, string_full)
    assert ai_writer.get_named_entities()[1]["word"] == "Russia"


def test_get_named_entities_person_true():
    headline = ""
    article = ""
    ai_writer = AI_Writer(headline, article)
    list_of_named_entities = [
        {
            "entity_group": "LOC",
            "score": 0.9723994,
            "word": "Russia",
            "start": 25,
            "end": 32,
        },
        {
            "entity_group": "PER",
            "score": 0.99805874,
            "word": "John Smith",
            "start": 67,
            "end": 84,
        },
    ]
    result = ["John Smith"]
    assert ai_writer.get_named_entities_person(list_of_named_entities) == result


def test_get_named_entities_person_false(string_empty):
    ai_writer = AI_Writer(string_empty, string_empty)
    list_of_named_entities = [
        {
            "entity_group": "LOC",
            "score": 0.9723994,
            "word": "Russia",
            "start": 25,
            "end": 32,
        },
        {
            "entity_group": "LOC",
            "score": 0.9723994,
            "word": "New York",
            "start": 55,
            "end": 62,
        },
    ]
    assert ai_writer.get_named_entities_person(list_of_named_entities) is None


def test_get_random_image_of_person_true(string_empty):
    ai_writer = AI_Writer(string_empty, string_empty)
    list_of_persons = ["Donald Trump"]
    result = ai_writer.get_random_image_of_person(list_of_persons)
    assert result in [
        "donald_trump_0.jpg",
        "donald_trump_1.jpg",
        "donald_trump_2.jpg",
        "donald_trump_3.jpg",
    ]


def test_get_random_image_of_person_false(string_empty):
    ai_writer = AI_Writer(string_empty, string_empty)
    list_of_persons = ["Ebighar Rajjashwili"]
    assert ai_writer.get_random_image_of_person(list_of_persons) is None


def test_classify_article_to_topic(string_empty, string_full):
    ai_writer = AI_Writer(string_empty, string_full)
    assert ai_writer.classify_article_to_topic(string_full) == "politics"


def test_rewrite_text_test_type(string_empty, string_full):
    ai_writer = AI_Writer(string_empty, string_empty)
    assert isinstance(ai_writer.rewrite_text(string_full, 1, 1), str) is True


def test_rewrite_text_test_non_equality(string_empty, string_full):
    ai_writer = AI_Writer(string_empty, string_empty)
    assert ai_writer.rewrite_text(string_full, 1, 1) != string_full


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
