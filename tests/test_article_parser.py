import pytest
import repackage
from newspaper.article import ArticleException

repackage.up()
from src.parsers.article_parser import filter_text, get_original_article_text

# def test_get_original_article_text_download_error():
#     url = r"gfdertghjko.com.pl"
#     headline = "Taylor Swift cheers on Travis Kelce at Kansas City Chiefs game"
#     filter_ = True
#     result = get_original_article_text(url, headline, filter_)
#     assert result[0] == headline
#     assert result[1] is None


def test_get_original_article_text_fake_url():
    url = r"gfdertghjko.com.pl"
    headline = "Taylor Swift cheers on Travis Kelce at Kansas City Chiefs game"
    filter_ = True
    with pytest.raises(ArticleException):
        get_original_article_text(url, headline, filter_)


def test_get_original_article_text_true():
    url = r"https://pl.wikipedia.org/wiki/Hr.Ms."
    headline = "Taylor Swift cheers on Travis Kelce at Kansas City Chiefs game"
    filter_ = True
    result = get_original_article_text(url, headline, filter_)
    assert result[0] == headline
    assert isinstance(result[1], str) is True


def test_filter_text_ad():
    raw_text = "A Mafia boss who spent ad nearly three decades mad."
    assert filter_text(raw_text) == "A Mafia boss who spent nearly three decades mad."


def test_filter_text_advert():
    raw_text = "A Mafia boss who spent advert nearly three decades."
    assert filter_text(raw_text) == "A Mafia boss who spent nearly three decades."


def test_filter_text_advertisment():
    raw_text = "A Mafia boss who spent advertisment nearly three decades."
    assert filter_text(raw_text) == "A Mafia boss who spent nearly three decades."


def test_filter_text_advertisement():
    raw_text = "A Mafia boss who spent advertisement nearly three decades."
    assert filter_text(raw_text) == "A Mafia boss who spent nearly three decades."


def test_filter_text_ads():
    raw_text = "A Mafia boss who spent ads nearly three decades."
    assert filter_text(raw_text) == "A Mafia boss who spent nearly three decades."


def test_filter_text_adverts():
    raw_text = "A Mafia boss who spent adverts nearly three decades."
    assert filter_text(raw_text) == "A Mafia boss who spent nearly three decades."


def test_filter_text_advertisments():
    raw_text = "A Mafia boss who spent advertisments nearly three decades."
    assert filter_text(raw_text) == "A Mafia boss who spent nearly three decades."


def test_filter_text_advertisements():
    raw_text = "A Mafia boss who spent advertisements nearly three decades."
    assert filter_text(raw_text) == "A Mafia boss who spent nearly three decades."
