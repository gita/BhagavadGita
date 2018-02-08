from .. import db
from ..models.verse import VerseModel
from marshmallow_sqlalchemy import ModelSchema


class VerseSchema(ModelSchema):
    class Meta:
        model = VerseModel
        fields = ('chapter_number', 'verse_number', 'text', 'transliteration', 'word_meanings', 'meaning_english')
