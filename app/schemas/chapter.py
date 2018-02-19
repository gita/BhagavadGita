from .. import db
from ..models.chapter import ChapterModel
from marshmallow_sqlalchemy import ModelSchema


class ChapterSchema(ModelSchema):
    class Meta:
        model = ChapterModel
        fields = ('chapter_number', 'name', 'name_transliterated', 'name_transliterated_simple', 'verses_count', 'chapter_number', 'name_english', 'chapter_summary')
