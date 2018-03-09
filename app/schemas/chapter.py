from marshmallow_sqlalchemy import ModelSchema

from .. import db
from ..models.chapter import ChapterModel


class ChapterSchema(ModelSchema):
    class Meta:
        model = ChapterModel
        fields = ('chapter_number', 'name', 'name_transliterated',
                  'name_translation', 'verses_count', 'name_meaning', 'chapter_summary')
