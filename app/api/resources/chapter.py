from flask_restful import Resource
from ...models.chapter import ChapterModel
from ... import oauth


class Chapter(Resource):
    @oauth.require_oauth()
    def get(self, chapter_number):
        chapter = ChapterModel.find_by_chapter_number(chapter_number)
        if chapter:
            return chapter.json()
        return {'message': 'Chapter not found'}, 404


class ChapterList(Resource):
    @oauth.require_oauth()
    def get(self):
        return {'chapters': [chapter.json() for chapter in ChapterModel.query.all()]}
