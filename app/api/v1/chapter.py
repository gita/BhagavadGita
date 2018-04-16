#!/usr/bin/python
# -*- coding: utf-8 -*-

from flasgger import SwaggerView
from flask import jsonify, request
from ... import csrf, oauth, db
from ...models.chapter import ChapterModel
from ...schemas.chapter import ChapterSchema

chapter_schema = ChapterSchema()
chapters_schema = ChapterSchema(many=True)

LANGUAGES = {'en': 'English', 'hi': 'हिंदी'}


class Chapter(SwaggerView):

    decorators = [csrf.exempt, oauth.require_oauth('chapter')]
    definitions = {'ChapterSchema': ChapterSchema}

    def get(self, chapter_number):
        """
        Get a specific chapter from the Bhagavad Gita.
        Get information about a specific chapter from the Bhagavad Gita.
        ---
        tags:
        - chapter
        parameters:
        - name: access_token
          in: query
          required: 'True'
          type: 'string'
          description: "Your app's access token."
        - name: chapter_number
          in: path
          type: int
          enum:
          - 1
          - 2
          - 3
          required: 'true'
          default: 1
          description: Which Chapter Number to filter?
        - name: language
          in: query
          type: 'string'
          description: "Language to query. Leave blank for english."
          enum: ['hi']
        consumes:
        - application/json
        produces:
        - application/json
        responses:
          200:
            description: 'Success: Everything worked as expected.'
            schema:
              $ref: '#/definitions/ChapterSchema'
            examples:
              application/json: |-
                {
                  "chapter_number": 1, 
                  "name": "u'\u0905\u0930\u094d\u091c\u0941\u0928\u0935\u093f\u0937\u093e\u0926\u092f\u094b\u0917'", 
                  "name_english": "u'Arjuna Dilemma'", 
                  "name_transliterated": "u'Arjun Vi\u1e63h\u0101d Yog'", 
                  "name_transliterated_simple": "u'Arjuna Visada Yoga'", 
                  "verses_count": 47
                }
          400:
            description: 'Bad Request: The request was unacceptable due to wrong parameter(s).'
          401:
            description: 'Unauthorized: Invalid access_token used.'
          402:
            description: 'Request Failed.'
          404:
            description: 'Not Found: The chapter number you are looking for could not be found.'
          500:
            description: 'Server Error: Something went wrong on our end.'
        """

        language = request.args.get('language')

        if chapter_number not in range(1, 19):
            return (jsonify({'message': 'Invalid Chapter.'}), 404)

        if language is None:
            chapter = ChapterModel.find_by_chapter_number(chapter_number)
        else:
            if language not in LANGUAGES.keys():
                return (jsonify({'message': 'Invalid Language.'}), 404)
                
            chapter_table = "chapters_" + language
            sql = """
                SELECT ct.name_translation, ct.name_meaning, ct.chapter_summary, c.chapter_number, c.verses_count, c.name
                FROM %s ct
                JOIN
                chapters c
                ON
                c.chapter_number = ct.chapter_number
                WHERE c.chapter_number = %s
                ORDER BY c.chapter_number
            """ % (chapter_table, chapter_number)
            chapter = db.session.execute(sql).first()

        if chapter:
            result = chapter_schema.dump(chapter)
            return jsonify(result.data)
        return (jsonify({'message': 'Chapter not found.'}), 404)


class ChapterList(SwaggerView):

    decorators = [csrf.exempt, oauth.require_oauth('chapter')]
    definitions = {'ChapterSchema': ChapterSchema}

    def get(self):
        """
        Get all the 18 Chapters of the Bhagavad Gita.
        Get a list of all the 18 Chapters of the Bhagavad Gita.
        ---
        tags:
        - chapter
        parameters:
        - name: access_token
          in: query
          required: 'True'
          type: 'string'
          description: "Your app's access token."
        - name: language
          in: query
          type: 'string'
          description: "Language to query. Leave blank for english."
          enum: ['hi']
        consumes:
        - application/json
        produces:
        - application/json
        responses:
          200:
            description: 'Success: Everything worked as expected.'
            schema:
              $ref: '#/definitions/ChapterSchema'
            examples:
              application/json: |-
                {
                  "chapters": [
                    {
                      "chapter_number": 1, 
                      "name": "u'\u0905\u0930\u094d\u091c\u0941\u0928\u0935\u093f\u0937\u093e\u0926\u092f\u094b\u0917'", 
                      "name_english": "u'Arjuna Dilemma'", 
                      "name_transliterated": "u'Arjun Vi\u1e63h\u0101d Yog'", 
                      "name_transliterated_simple": "u'Arjuna Visada Yoga'", 
                      "verses_count": 47
                    }, 
                    {
                      "chapter_number": 2, 
                      "name": "u'\u0938\u093e\u0902\u0916\u094d\u092f\u092f\u094b\u0917'", 
                      "name_english": "u'Transcendental Knowledge'", 
                      "name_transliterated": "u'S\u0101nkhya Yog'", 
                      "name_transliterated_simple": "u'Sankhya Yoga'", 
                      "verses_count": 72
                    }
                  ]
                }
          400:
            description: 'Bad Request: The request was unacceptable due to wrong parameter(s).'
          401:
            description: 'Unauthorized: Invalid access_token used.'
          402:
            description: 'Request Failed.'
          500:
            description: 'Server Error: Something went wrong on our end.'
        """

        language = request.args.get('language')

        if language is None:
            chapters = ChapterModel.query.order_by(
                ChapterModel.chapter_number).all()
        else:
            if language not in LANGUAGES.keys():
                return (jsonify({'message': 'Invalid Language.'}), 404)

            chapter_table = "chapters_" + language
            sql = """
                SELECT ct.name_translation, ct.name_meaning, ct.chapter_summary, c.chapter_number, c.verses_count, c.name
                FROM %s ct
                JOIN
                chapters c
                ON
                c.chapter_number = ct.chapter_number
                ORDER BY c.chapter_number
            """ % (chapter_table)
            chapters = db.session.execute(sql)

        result = chapters_schema.dump(chapters)
        return jsonify(result.data)
