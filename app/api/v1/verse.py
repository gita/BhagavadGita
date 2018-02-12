#!/usr/bin/python
# -*- coding: utf-8 -*-

from ...models.verse import VerseModel
from app.models.chapter import ChapterModel
from ... import oauth, csrf
from ...schemas.chapter import ChapterSchema
from ...schemas.verse import VerseSchema
from flask import jsonify
from flasgger import Schema, Swagger, SwaggerView, fields


verse_schema = VerseSchema()
verses_schema = VerseSchema(many=True)


class VerseList(SwaggerView):

    decorators = [csrf.exempt, oauth.require_oauth('verse')]
    definitions = {'VerseSchema': VerseSchema}

    def get(self):
        """
        Get all the Verses.
        Get a list of all Verses.
        ---
        tags:
        - verse
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
              $ref: '#/definitions/VerseSchema'
            examples:
              - chapter_number: 1
                meaning_english: "Dhritarashtra said: O Sanjay, after gathering on the holy field of Kurukshetra, and desiring to fight, what did my sons and the sons of Pandu do?"
                text: "धृतराष्ट्र उवाच | धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः | मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय |||1||"
                transliteration: "dhṛitarāśhtra uvācha dharma-kṣhetre kuru-kṣhetre samavetā yuyutsavaḥ māmakāḥ pāṇḍavāśhchaiva kimakurvata sañjaya"
                verse_number: 1
                word_meanings: "dhṛitarāśhtraḥ uvācha—Dhritarashtra said; dharma-kṣhetre—the land of dharma; kuru-kṣhetre—at Kurukshetra; samavetāḥ—having gathered; yuyutsavaḥ—desiring to fight; māmakāḥ—my sons; pāṇḍavāḥ—the sons of Pandu; cha—and; eva—certainly; kim—what; akurvata—did they do; sañjaya—Sanjay"
              - chapter_number: 1
                meaning_english: 'Sanjay said: On observing the Pandava army standing in military formation, King Duryodhan approached his teacher Dronacharya, and said the following words.'
                text: "सञ्जय उवाच | दृष्ट्वा तु पाण्डवानीकं व्यूढं दुर्योधनस्तदा | आचार्यमुपसङ्गम्य राजा वचनमब्रवीत् | ||2||"
                transliteration: "sañjaya uvācha dṛiṣhṭvā tu pāṇḍavānīkaṁ vyūḍhaṁ duryodhanastadā āchāryamupasaṅgamya rājā vachanamabravīt"
                verse_number: 2
                word_meanings: "sanjayaḥ uvācha—Sanjay said; dṛiṣhṭvā—on observing; tu—but; pāṇḍava-anīkam—the Pandava army; vyūḍham—standing in a military formation; duryodhanaḥ—King Duryodhan; tadā—then; āchāryam—teacher; upasaṅgamya—approached; rājā—the king; vachanam—words; abravīt—spoke"

          400:
            description: 'Bad Request: The request was unacceptable due to wrong parameter(s).'
          401:
            description: 'Unauthorized: Inavlid access_token used.'
          402:
            description: 'Request Failed.'
          500:
            description: 'Server Error: Something went wrong on our end.'
        """

        verses = VerseModel.query.all()
        result = verses_schema.dump(verses)
        return jsonify(result.data)


class VerseListByChapter(SwaggerView):

    decorators = [csrf.exempt, oauth.require_oauth('verse')]
    definitions = {'VerseSchema': VerseSchema}

    def get(self, chapter_number):
        """
        Get all the Verses from a Chapter.
        Get a list of all Verses from a particular Chapter.
        ---
        tags:
        - verse
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
              $ref: '#/definitions/VerseSchema'
            examples:
            - chapter_number: 1
              meaning_english: "Dhritarashtra said: O Sanjay, after gathering on the holy field of Kurukshetra, and desiring to fight, what did my sons and the sons of Pandu do?"
              text: "धृतराष्ट्र उवाच | धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः | मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय |||1||"
              transliteration: "dhṛitarāśhtra uvācha dharma-kṣhetre kuru-kṣhetre samavetā yuyutsavaḥ māmakāḥ pāṇḍavāśhchaiva kimakurvata sañjaya"
              verse_number: 1
              word_meanings: "dhṛitarāśhtraḥ uvācha—Dhritarashtra said; dharma-kṣhetre—the land of dharma; kuru-kṣhetre—at Kurukshetra; samavetāḥ—having gathered; yuyutsavaḥ—desiring to fight; māmakāḥ—my sons; pāṇḍavāḥ—the sons of Pandu; cha—and; eva—certainly; kim—what; akurvata—did they do; sañjaya—Sanjay"
            - chapter_number: 1
              meaning_english: 'Sanjay said: On observing the Pandava army standing in military formation, King Duryodhan approached his teacher Dronacharya, and said the following words.'
              text: "सञ्जय उवाच | दृष्ट्वा तु पाण्डवानीकं व्यूढं दुर्योधनस्तदा | आचार्यमुपसङ्गम्य राजा वचनमब्रवीत् | ||2||"
              transliteration: "sañjaya uvācha dṛiṣhṭvā tu pāṇḍavānīkaṁ vyūḍhaṁ duryodhanastadā āchāryamupasaṅgamya rājā vachanamabravīt"
              verse_number: 2
              word_meanings: "sanjayaḥ uvācha—Sanjay said; dṛiṣhṭvā—on observing; tu—but; pāṇḍava-anīkam—the Pandava army; vyūḍham—standing in a military formation; duryodhanaḥ—King Duryodhan; tadā—then; āchāryam—teacher; upasaṅgamya—approached; rājā—the king; vachanam—words; abravīt—spoke"
          400:
            description: 'Bad Request: The request was unacceptable due to wrong parameter(s).'
          401:
            description: 'Unauthorized: Invalid access_token used.'
          404:
            description: 'Not Found: The chapter number you are looking for could not be found.'
          402:
            description: 'Request Failed.'
          500:
            description: 'Server Error: Something went wrong on our end.'
        """

        chapter = ChapterModel.find_by_chapter_number(chapter_number)
        if chapter:
            verses = VerseModel.query.filter_by(chapter_number=chapter_number)
            result = verses_schema.dump(verses)
            return jsonify(result.data)
        return (jsonify({'message': 'Chapter not found.'}), 404)


class VerseByChapter(SwaggerView):

    decorators = [csrf.exempt, oauth.require_oauth('verse')]
    definitions = {'VerseSchema': VerseSchema}

    def get(self, chapter_number, verse_number):
        """
        Get a particular verse from a chapter.
        Get a specific verse from a specific chapter.
        ---
        tags:
        - verse
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
        - name: verse_number
          in: path
          type: string
          enum:
          - 1
          - 2
          - 3
          required: 'true'
          default: 1
          description: Which Verse Number to filter?
        consumes:
        - application/json
        produces:
        - application/json
        responses:
          200:
            description: 'Success: Everything worked as expected.'
            schema:
              $ref: '#/definitions/VerseSchema'
            examples:
            - chapter_number: 1
              meaning_english: "Dhritarashtra said: O Sanjay, after gathering on the holy field of Kurukshetra, and desiring to fight, what did my sons and the sons of Pandu do?"
              text: "धृतराष्ट्र उवाच | धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः | मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय |||1||"
              transliteration: "dhṛitarāśhtra uvācha dharma-kṣhetre kuru-kṣhetre samavetā yuyutsavaḥ māmakāḥ pāṇḍavāśhchaiva kimakurvata sañjaya"
              verse_number: 1
              word_meanings: "dhṛitarāśhtraḥ uvācha—Dhritarashtra said; dharma-kṣhetre—the land of dharma; kuru-kṣhetre—at Kurukshetra; samavetāḥ—having gathered; yuyutsavaḥ—desiring to fight; māmakāḥ—my sons; pāṇḍavāḥ—the sons of Pandu; cha—and; eva—certainly; kim—what; akurvata—did they do; sañjaya—Sanjay"
          400:
            description: 'Bad Request: The request was unacceptable due to wrong parameter(s).'
          401:
            description: 'Unauthorized: Invalid access_token used.'
          402:
            description: 'Request Failed.'
          404:
            description: 'Not Found: The chapter/verse number you are looking for could not be found.'
          500:
            description: 'Server Error: Something went wrong on our end.'
        """

        chapter = ChapterModel.find_by_chapter_number(chapter_number)
        if chapter:
            verse = VerseModel.find_by_chapter_number_verse_number(chapter_number, verse_number)
            if verse:
                result = verse_schema.dump(verse)
                return jsonify(result.data)
            return (jsonify({'message': 'Verse not found.'}), 404)
        return (jsonify({'message': 'Chapter not found.'}), 404)
