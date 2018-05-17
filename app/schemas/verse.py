from marshmallow_sqlalchemy import ModelSchema
from ..models.verse import VerseModel


class VerseSchema(ModelSchema):
    class Meta:
        model = VerseModel
        fields = ('chapter_number', 'verse_number', 'text', 'transliteration',
                  'word_meanings', 'meaning', 'meaning_large')
