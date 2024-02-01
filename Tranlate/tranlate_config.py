from UzTransliterator import UzTransliterator

from Tranlate.translate_language import latin, russian
from utils import vil

obj = UzTransliterator.UzTransliterator()


def translate(lang: str, text: str):
    if lang.__eq__('lat'):
        return str(latin.get(text))
    elif lang.__eq__("ru"):
        return str(russian.get(text))
    elif lang.__eq__("cyr"):
        text = str(latin.get(text))
        return obj.transliterate(text, from_="lat", to="cyr")


def translate_cyrillic_or_latin(text: str, lang: str):
    if lang.__eq__("lat"):
        return obj.transliterate(text, from_="cyr", to="lat")
    if lang.__eq__("cyr") or lang.__eq__("ru"):
        return obj.transliterate(text, from_="lat", to="cyr")
