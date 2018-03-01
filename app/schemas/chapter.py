from marshmallow_sqlalchemy import ModelSchema
from ..models.chapter import ChapterModel


class ChapterSchema(ModelSchema):
    class Meta:
        model = ChapterModel
        fields = ('chapter_number', 'name', 'name_transliterated',
                  'name_translation', 'verses_count', 'chapter_number',
                  'name_meaning', 'chapter_summary')
