#!/usr/bin/python
# -*- coding: utf-8 -*-

from flasgger import SwaggerView
from flask import jsonify

from ... import csrf, oauth
from ...models.chapter import ChapterModel
from ...schemas.chapter import ChapterSchema

chapter_schema = ChapterSchema()
chapters_schema = ChapterSchema(many=True)


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
              - chapter_number: 1
                name: u'अर्जुनविषादयोग'
                name_english: u'Arjuna Dilemma'
                name_transliterated: u'Arjun Viṣhād Yog'
                name_transliterated_simple: u'Arjuna Visada Yoga'
                verses_count: 47

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

        chapter = ChapterModel.find_by_chapter_number(chapter_number)
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
              - chapter_number: 1
                name: u'अर्जुनविषादयोग'
                name_english: u'Arjuna Dilemma'
                name_transliterated: u'Arjun Viṣhād Yog'
                name_transliterated_simple: u'Arjuna Visada Yoga'
                verses_count: 47
              - chapter_number: 2
                name: u'सांख्ययोग'
                name_english: u'Transcendental Knowledge'
                name_transliterated: u'Sānkhya Yog'
                name_transliterated_simple: u'Sankhya Yoga'
                verses_count: 72
          400:
            description: 'Bad Request: The request was unacceptable due to wrong parameter(s).'
          401:
            description: 'Unauthorized: Invalid access_token used.'
          402:
            description: 'Request Failed.'
          500:
            description: 'Server Error: Something went wrong on our end.'
        """

        chapters = ChapterModel.query.all()
        result = chapters_schema.dump(chapters)
        return jsonify(result.data)
