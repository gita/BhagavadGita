from flask_restful import Resource
from ...models.chapter import ChapterModel
from ... import oauth
from ...schemas.chapter import ChapterSchema
from flask import jsonify


chapter_schema = ChapterSchema()
chapters_schema = ChapterSchema(many=True)


class Chapter(Resource):
    @oauth.require_oauth()
    def get(self, chapter_number):
        chapter = ChapterModel.find_by_chapter_number(chapter_number)
        if chapter:
            result = chapter_schema.dump(chapter)
            return jsonify(result.data)
        return {'message': 'Chapter not found'}, 404


class ChapterList(Resource):
    @oauth.require_oauth()
    def get(self):
        chapters = ChapterModel.query.all()
        result = chapters_schema.dump(chapters)
        return jsonify(result.data)
