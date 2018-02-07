from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from ...models.verse import VerseModel
from ...models.chapter import ChapterModel
from ... import oauth

# class Verse(Resource):
#     parser = reqparse.RequestParser()
#     parser.add_argument('chapter_number',
#         type=int,
#         required=True,
#         help="This field cannot be left blank."
#     )
#     parser.add_argument('verse_number',
#         type=int,
#         required=True,
#         help="Every verse needs a store id."
#     )
#     parser.add_argument('text',
#         type=str,
#         required=True,
#         help="This field cannot be left blank."
#     )
#     parser.add_argument('transliteration',
#         type=str,
#         help="Every verse needs a store id."
#     )

#     parser.add_argument('word_meanings',
#         type=str,
#         help="This field cannot be left blank."
#     )
#     parser.add_argument('meaning_english',
#         type=str,
#         help="Every verse needs a store id."
#     )

    # @jwt_required()
    # def get(self, verse_number):
    #     verse = VerseModel.find_by_verse_number(verse_number)
    #     if verse:
    #         return verse.json()
    #     return {'message': 'Verse not found'}, 404


class VerseList(Resource):
    @oauth.require_oauth()
    def get(self):
        return {'verses': [verse.json() for verse in VerseModel.query.all()]}


class VerseListByChapter(Resource):
    @oauth.require_oauth()
    def get(self, chapter_number):
        chapter = ChapterModel.find_by_chapter_number(chapter_number)
        if chapter:
            return {'verses': [verse.json() for verse in VerseModel.query.filter_by(chapter_number=chapter_number)]}
        return {'message': 'Chapter not found'}, 404


class VerseByChapter(Resource):
    @oauth.require_oauth()
    def get(self, chapter_number, verse_number):
        chapter = ChapterModel.find_by_chapter_number(chapter_number)
        if chapter:
            verse = VerseModel.find_by_chapter_number_verse_number(chapter_number, verse_number)
            if verse:
                return verse.json()
            return {'message': 'Verse not found'}, 404
        return {'message': 'Chapter not found'}, 404
