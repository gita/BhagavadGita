#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys

from flask import (abort, current_app, flash, jsonify, make_response, redirect,
                   render_template, request, url_for, send_from_directory)
from flask_rq import get_queue

from app import babel, db, es
from app.models.chapter import ChapterModel, ChapterModelHindi
from app.models.verse import VerseModel, VerseModelHindi, UserReadingPlanItems
from app.models.user import UserFavourite, User

from . import main
from ..email import send_email
from .forms import ContactForm

from flask_login import current_user, login_user
from datetime import datetime, timedelta, date
import time
from werkzeug.security import gen_salt
import atexit
import requests
import os

from collections import OrderedDict
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf8')

LANGUAGES = {'en': 'English', 'hi': 'हिंदी'}

verse_dict = {
    1: {},
    2: {
        '42': "42-43",
        '43': "42-43"
    },
    3: {},
    4: {
        '29': "29-30",
        '30': "29-30"
    },
    5: {
        '8': "8-9",
        '9': "8-9",
        '27': "27-28",
        '28': "27-28"
    },
    6: {},
    7: {},
    8: {},
    9: {},
    10: {
        '4': "4-5",
        '5': "4-5"
    },
    11: {
        '26': "26-27",
        '27': "26-27"
    },
    12: {
        '3': "3-4",
        '4': "3-4"
    },
    13: {},
    14: {},
    15: {},
    16: {
        '15': "15-16",
        '16': "15-16"
    },
    17: {},
    18: {
        '36': "36-37",
        '37': "36-37"
    },
}

@babel.localeselector
def get_locale():
    if "settings" in request.cookies:
        current_app.logger.info(request.cookies.get('settings'))
        if json.loads(request.cookies.get('settings'))["language"]:
            return json.loads(request.cookies.get('settings'))["language"]
    return request.accept_languages.best_match(LANGUAGES.keys())


@main.route('/', methods=['GET'])
def index():
    badge_list = []
    progress = {key: None for key in range(1, 19)}
    language = "en"
    if "settings" in request.cookies:
        if json.loads(request.cookies.get('settings'))["language"]:
            language = json.loads(request.cookies.get('settings'))["language"]

    if language == "en":
        chapters = ChapterModel.query.order_by(
            ChapterModel.chapter_number).all()
        
        if current_user.is_authenticated:
            sql = """
                    SELECT chapter, COUNT(verse)
                    FROM user_progress
                    WHERE user_id = %s
                    GROUP BY chapter
                """ % (current_user.get_id())
            result = db.session.execute(sql)
            user_verses = [dict(r) for r in result]

            sql = """
                    SELECT chapter_number, verses_count
                    FROM chapters
                """
            result = db.session.execute(sql)
            verses = [dict(r) for r in result]

            sql = """
                    SELECT COUNT(verse)
                    FROM user_progress
                    WHERE user_id = %s
                """ % (current_user.get_id())
            result = db.session.execute(sql)
            total_shlokas = [dict(r) for r in result][0]['count']

            for chapter in verses:
                for chapter_number in user_verses:
                    if chapter['chapter_number'] == chapter_number['chapter']:
                        progress[chapter['chapter_number']] = float(
                            "%.2f" % ((chapter_number['count']/chapter['verses_count'])*100))

        return render_template(
            'main/index.html', chapters=chapters, language=language, badge_list=badge_list, progress=progress)
    else:
        return redirect('/' + language + '/')


@main.route('/<string:language>/', methods=['GET'])
def index_radhakrishna(language):
    badge_list = []
    progress = {key: None for key in range(1, 19)}
    if language not in LANGUAGES.keys():
        abort(404)
    chapter_table = "chapters_" + language
    sql = """
        SELECT ct.name_translation, ct.name_meaning, ct.chapter_summary, c.image_name, c.chapter_number
        FROM %s ct
        JOIN
        chapters c
        ON
        c.chapter_number = ct.chapter_number
        ORDER BY c.chapter_number
    """ % (chapter_table)
    chapters = db.session.execute(sql)

    if current_user.is_authenticated:
        sql = """
                SELECT chapter, COUNT(verse)
                FROM user_progress
                WHERE user_id = %s
                GROUP BY chapter
            """ % (current_user.get_id())
        result = db.session.execute(sql)
        user_verses = [dict(r) for r in result]

        sql = """
                SELECT chapter_number, verses_count
                FROM chapters
            """
        result = db.session.execute(sql)
        verses = [dict(r) for r in result]

        sql = """
                SELECT COUNT(verse)
                FROM user_progress
                WHERE user_id = %s
            """ % (current_user.get_id())
        result = db.session.execute(sql)
        total_shlokas = [dict(r) for r in result][0]['count']

        for chapter in verses:
            for chapter_number in user_verses:
                if chapter['chapter_number'] == chapter_number['chapter']:
                    progress[chapter['chapter_number']] = float(
                        "%.2f" % ((chapter_number['count']/chapter['verses_count'])*100))

    return render_template(
        'main/index.html', chapters=chapters, language=language, badge_list=badge_list, progress=progress)


@main.route('/search', methods=['GET', 'POST'])
def search():
    badge_list = []
    query = request.args.get('query')
    res = es.search(index="*", body={
      "from": 0, "size": 1000,
      "query": {
        "multi_match": {
          "query": query,
          "fields": ["meaning", "meaning_large", "text", "transliteration", "word_meanings"]
        }
      }
    })

    verses = res['hits']['hits']

    current_app.logger.info(verses)
    return render_template(
        'main/search.html', verses=verses, query=request.args.get('query'), badge_list=badge_list)


@main.route('/krishna', methods=['GET', 'POST'])
def krishna_search():
    query = request.args.get('query')
    current_app.logger.info(query)
    res = es.search(index="verses_hi", body={
      "from": 0, "size": 10,
      "_source": ["meaning"],
      "query": {
        "multi_match": {
          "query": query,
          "fields": ["meaning"]
        }
      }
    })

    verses = res['hits']['hits']

    current_app.logger.info(verses)
    return jsonify(verses)


@main.route('/chapter-numbers', methods=['GET'])
def get_all_chapter_numbers():
    chapters = ChapterModel.query.order_by(ChapterModel.chapter_number).all()
    chapter_numbers = {}
    for chapter in chapters:
        chapter_numbers[chapter.chapter_number] = "Chapter " + str(
            chapter.chapter_number)
    return jsonify(chapter_numbers)


@main.route('/languages', methods=['GET'])
def get_all_languages():
    languages = {}
    languages['en'] = "English"
    languages['hi'] = "हिंदी"
    return jsonify(languages)


@main.route('/verse-numbers/<int:chapter_number>', methods=['GET'])
def get_all_verse_numbers(chapter_number):
    verses = VerseModel.query.order_by(
        VerseModel.verse_order).filter_by(chapter_number=chapter_number)
    verse_numbers = {}
    for verse in verses:
        verse_numbers[verse.verse_order] = "Verse " + str(verse.verse_number)
    return jsonify(verse_numbers)


@main.route('/chapter/<int:chapter_number>/', methods=['GET'])
def chapter(chapter_number):
    badge_list = []
    read_verses = []
    if chapter_number not in range(1, 19):
        abort(404)
    language = "en"
    if "settings" in request.cookies:
        if json.loads(request.cookies.get('settings'))["language"]:
            language = json.loads(request.cookies.get('settings'))["language"]

    if request.args.get('page'):
        page_number = int(request.args.get('page'))
    else:
        page_number = 1

    if language == "en":
        if current_user.is_authenticated:
            sql = """
                    SELECT verse
                    FROM user_progress
                    WHERE user_id = %s
                    AND chapter = %s
                """ % (current_user.get_id(), chapter_number)
            result = db.session.execute(sql)
            read_verses = [r['verse'] for r in result]

        chapter = ChapterModel.find_by_chapter_number(chapter_number)
        verses = VerseModel.query.filter_by(chapter_number = chapter_number).order_by(VerseModel.verse_order).paginate(per_page=6, page=page_number, error_out=True)
        return render_template(
            'main/chapter.html', chapter=chapter, verses=verses, badge_list=badge_list, read_verses=read_verses)
    else:
        return redirect(
            '/chapter/' + str(chapter_number) + '/' + language + '/')


@main.route(
    '/chapter/<int:chapter_number>/<string:language>/', methods=['GET'])
def chapter_radhakrishna(chapter_number, language):
    badge_list = []
    read_verses = []
    if chapter_number not in range(1, 19):
        abort(404)
    if language not in LANGUAGES.keys():
        abort(404)
    if request.args.get('page'):
        page_number = int(request.args.get('page'))
    else:
        page_number = 1
    if current_user.is_authenticated:
        sql = """
                SELECT verse
                FROM user_progress
                WHERE user_id = %s
                AND chapter = %s
            """ % (current_user.get_id(), chapter_number)
        result = db.session.execute(sql)
        read_verses = [r['verse'] for r in result]
    chapter = ChapterModel.query.join(ChapterModelHindi, ChapterModel.chapter_number==ChapterModelHindi.chapter_number).add_columns(ChapterModelHindi.name_translation, ChapterModelHindi.name_meaning, ChapterModelHindi.chapter_summary, ChapterModel.image_name, ChapterModel.chapter_number).filter(ChapterModel.chapter_number == chapter_number).order_by(ChapterModel.chapter_number).first()
    verses = VerseModelHindi.query.filter_by(chapter_number = chapter_number).order_by(VerseModelHindi.verse_order).paginate(per_page=6, page=page_number, error_out=True)
    return render_template('main/chapter.html', chapter=chapter, verses=verses, badge_list = badge_list, read_verses=read_verses)


@main.route(
    '/chapter/<int:chapter_number>/verse/<string:verse_number>/', defaults={'batch_id': None, 'user_reading_plan_id': None, 'batch_total': None, 'batch_no': None},
    methods=['GET'])
@main.route(
    '/chapter/<int:chapter_number>/verse/<string:verse_number>/<string:user_reading_plan_id>/batch/<int:batch_id>/batch_total/<int:batch_total>/batch_no/<int:batch_no>/',
    methods=['GET'])
def verse(chapter_number, verse_number, user_reading_plan_id, batch_id, batch_total, batch_no):
    badge = {}
    badge_list = []
    read = False
    if chapter_number not in range(1, 19):
        abort(404)
    if verse_number in verse_dict[chapter_number]:
        current_app.logger.info("RadhaKrishna")
        return redirect('/chapter/' + str(chapter_number) + '/verse/' +
                        str(verse_dict[chapter_number][verse_number]) + '/')
    else:
        language = "en"

        if "settings" in request.cookies:
            if json.loads(request.cookies.get('settings'))["language"]:
                language = json.loads(
                    request.cookies.get('settings'))["language"]

        if language == "en":
            chapter = ChapterModel.find_by_chapter_number(chapter_number)

            sql = """
                    SELECT *
                    FROM verses v
                    WHERE v.chapter_number = %s
                    AND v.verse_number = '%s'
                    ORDER BY v.verse_order
                """ % (chapter_number, verse_number)

            verse = db.session.execute(sql).first()

            if verse is None:
                abort(404)

            max_verse_number = VerseModel.query.order_by(
                VerseModel.verse_order.desc()).filter_by(
                    chapter_number=chapter_number).first().verse_number

            if verse_number == max_verse_number:
                next_verse = None
                previous_verse_order = verse.verse_order - 1
                previous_verse = VerseModel.query.filter_by(
                    chapter_number=chapter_number,
                    verse_order=previous_verse_order).first()
            else:
                next_verse_order = verse.verse_order + 1
                previous_verse_order = verse.verse_order - 1
                previous_verse = VerseModel.query.filter_by(
                    chapter_number=chapter_number,
                    verse_order=previous_verse_order).first()
                next_verse = VerseModel.query.filter_by(
                    chapter_number=chapter_number,
                    verse_order=next_verse_order).first()

            if current_user.is_authenticated:
                sql = """
                        SELECT COUNT(user_progress_id)
                        FROM user_progress
                        WHERE user_id = %s
                        AND chapter = %s
                        AND verse = '%s'
                    """ % (current_user.get_id(), chapter_number, verse_number)
                result = db.session.execute(sql)
                count = [dict(r) for r in result][0]['count']

                if count == 1: read = True

                if count < 1:
                    timestamp = datetime.now()
                    sql = """
                            INSERT INTO user_progress (user_id, chapter, verse, timestamp)
                            VALUES (%s, %s, '%s', '%s')
                        """ % (current_user.get_id(), chapter_number, verse_number, timestamp)

                    db.session.execute(sql)
                    db.session.commit()

                sql = """
                        SELECT COUNT(*) as count
                        FROM user_progress
                        WHERE user_id = %s
                    """ % (current_user.get_id())
                result = db.session.execute(sql)
                total = [dict(r) for r in result][0]['count']

                badge_id_list = []
                verse_badges = {1:1, 10:5, 100:7, 500:8, 700:9}
                if total in verse_badges.keys(): badge_id_list.append(verse_badges[total])

                sql = """
                        SELECT COUNT(*) as count
                        FROM verses
                        WHERE chapter_number = %s
                    """ % (chapter_number)
                result = db.session.execute(sql)
                total_chapter_count = [dict(r) for r in result][0]['count']

                sql = """
                        SELECT COUNT(*) as count
                        FROM user_progress
                        WHERE user_id = %s
                        AND chapter = %s
                    """ % (current_user.get_id(), chapter_number)
                result = db.session.execute(sql)
                chapter_count = [dict(r) for r in result][0]['count']

                chapter_badges = {1:1, 10:5, 100:7, 500:8, 700:9}

                if chapter_count == total_chapter_count: badge_id_list.append(chapter_number+9)

                if badge_id_list != []:
                    for badge_id in badge_id_list:
                        sql = """
                                SELECT COUNT(*) as count
                                FROM user_badges
                                WHERE user_id = %s
                                AND badge_id = %s
                            """ % (current_user.get_id(), badge_id)
                        result = db.session.execute(sql)
                        badge_count = [dict(r) for r in result][0]['count']

                        if badge_count < 1:
                            timestamp = datetime.now()
                            sql = """
                                INSERT INTO user_badges (user_id, badge_id, timestamp)
                                VALUES (%s, %s, '%s')
                            """ % (current_user.get_id(), badge_id, timestamp)
                            db.session.execute(sql)
                            db.session.commit()

                            sql = """
                                SELECT *
                                FROM badges
                                WHERE badge_id = %s
                            """ % (badge_id)
                            result = db.session.execute(sql)
                            badge = [dict(r) for r in result][0]
                            badge_list.append(badge)
                current_app.logger.info(badge_list)

            return render_template(
                'main/verse.html',
                chapter=chapter,
                verse=verse,
                next_verse=next_verse,
                previous_verse=previous_verse,
                language=language,
                user_reading_plan_id=user_reading_plan_id,
                batch_id=batch_id,
                batch_no=batch_no,
                batch_total=batch_total,
                badge_list=badge_list,
                read=read)

        else:
            return redirect('/chapter/' + str(chapter_number) + '/verse/' +
                            str(verse_number) + '/' + language + '/')


@main.route(
    '/chapter/<int:chapter_number>/verse/<string:verse_number>/<string:language>/', defaults={'batch_id': None, 'user_reading_plan_id': None, 'batch_total': None, 'batch_no': None},
    methods=['GET'])
@main.route(
    '/chapter/<int:chapter_number>/verse/<string:verse_number>/<string:language>/<string:user_reading_plan_id>/batch/<int:batch_id>/batch_total/<int:batch_total>/batch_no/<int:batch_no>/',
    methods=['GET'])
def verse_radhakrishna(chapter_number, verse_number, language, user_reading_plan_id, batch_id, batch_total, batch_no):
    badge = {}
    badge_list = []
    read = False
    if chapter_number not in range(1, 19):
        abort(404)
    chapter = ChapterModel.find_by_chapter_number(chapter_number)

    verses_table = "verses_hi"
    sql = """
            SELECT vt.meaning, vt.word_meanings, v.text, v.transliteration, v.chapter_number, v.verse_number, v.verse_order, vt.meaning_large
            FROM %s vt
            JOIN verses v
            ON
            vt.chapter_number = v.chapter_number
            AND vt.verse_number = v.verse_number
            WHERE v.chapter_number = %s
            AND v.verse_number = '%s'
            ORDER BY v.verse_order
        """ % (verses_table, chapter_number, verse_number)

    verse = db.session.execute(sql).first()

    if verse is None:
        abort(404)

    if current_user.is_authenticated:
        sql = """
                SELECT COUNT(user_progress_id)
                FROM user_progress
                WHERE user_id = %s
                AND chapter = %s
                AND verse = '%s'
            """ % (current_user.get_id(), chapter_number, verse_number)
        result = db.session.execute(sql)
        count = [dict(r) for r in result][0]['count']

        if count == 1: read = True

        if count < 1:
            timestamp = datetime.now()
            sql = """
                    INSERT INTO user_progress (user_id, chapter, verse, timestamp)
                    VALUES (%s, %s, '%s', '%s')
                """ % (current_user.get_id(), chapter_number, verse_number, timestamp)

            db.session.execute(sql)
            db.session.commit()

        sql = """
                SELECT COUNT(*) as count
                FROM user_progress
                WHERE user_id = %s
            """ % (current_user.get_id())
        result = db.session.execute(sql)
        total = [dict(r) for r in result][0]['count']

        badge_id_list = []
        verse_badges = {1: 1, 10: 5, 100: 7, 500: 8, 700: 9}
        if total in verse_badges.keys():
            badge_id_list.append(verse_badges[total])

        sql = """
                SELECT COUNT(*) as count
                FROM verses
                WHERE chapter_number = %s
            """ % (chapter_number)
        result = db.session.execute(sql)
        total_chapter_count = [dict(r) for r in result][0]['count']

        sql = """
                SELECT COUNT(*) as count
                FROM user_progress
                WHERE user_id = %s
                AND chapter = %s
            """ % (current_user.get_id(), chapter_number)
        result = db.session.execute(sql)
        chapter_count = [dict(r) for r in result][0]['count']

        chapter_badges = {1: 1, 10: 5, 100: 7, 500: 8, 700: 9}

        if chapter_count == total_chapter_count:
            badge_id_list.append(chapter_number+9)

        if badge_id_list != []:
            for badge_id in badge_id_list:
                sql = """
                        SELECT COUNT(*) as count
                        FROM user_badges
                        WHERE user_id = %s
                        AND badge_id = %s
                    """ % (current_user.get_id(), badge_id)
                result = db.session.execute(sql)
                badge_count = [dict(r) for r in result][0]['count']

                if badge_count < 1:
                    timestamp = datetime.now()
                    sql = """
                        INSERT INTO user_badges (user_id, badge_id, timestamp)
                        VALUES (%s, %s, '%s')
                    """ % (current_user.get_id(), badge_id, timestamp)
                    db.session.execute(sql)
                    db.session.commit()

                    sql = """
                        SELECT *
                        FROM badges
                        WHERE badge_id = %s
                    """ % (badge_id)
                    result = db.session.execute(sql)
                    badge = [dict(r) for r in result][0]
                    badge_list.append(badge)
        current_app.logger.info(badge_list)

    max_verse_number = VerseModel.query.order_by(
        VerseModel.verse_order.desc()).filter_by(
            chapter_number=chapter_number).first().verse_number

    if verse_number == max_verse_number:
        next_verse = None
        previous_verse_order = verse.verse_order - 1
        previous_verse = VerseModel.query.filter_by(
            chapter_number=chapter_number,
            verse_order=previous_verse_order).first()
    else:
        next_verse_order = verse.verse_order + 1
        previous_verse_order = verse.verse_order - 1
        previous_verse = VerseModel.query.filter_by(
            chapter_number=chapter_number,
            verse_order=previous_verse_order).first()
        next_verse = VerseModel.query.filter_by(
            chapter_number=chapter_number,
            verse_order=next_verse_order).first()

    return render_template(
        'main/verse.html',
        chapter=chapter,
        verse=verse,
        next_verse=next_verse,
        previous_verse=previous_verse,
        language=language,
        user_reading_plan_id=user_reading_plan_id,
        batch_id=batch_id,
        batch_no=batch_no,
        batch_total=batch_total,
        badge_list=badge_list,
        read=read)


@main.route(
    '/favourite/<int:chapter_number>/<string:verse_number>/<int:value>/',
    methods=['GET'])
def favourite(chapter_number, verse_number, value):
    current_app.logger.info("RadhaKrishna")
    badge_list = []
    if current_user.is_authenticated:
        sql = """
                SELECT COUNT(user_favourite_id)
                FROM user_favourite
                WHERE user_id = %s
                AND chapter = %s
                AND verse = '%s'
            """ % (current_user.get_id(), chapter_number, verse_number)
        result = db.session.execute(sql)
        count = [dict(r) for r in result][0]['count']

        if value == 1:
            if count < 1:
                timestamp = datetime.now()
                sql = """
                        INSERT INTO user_favourite (user_id, chapter, verse, timestamp)
                        VALUES (%s, %s, '%s', '%s')
                    """ % (current_user.get_id(), chapter_number, verse_number, timestamp)
        elif value == 0:
            sql = """
                    DELETE FROM user_favourite
                    WHERE user_id = %s
                    AND chapter = %s
                    AND verse = '%s'
                """ % (current_user.get_id(), chapter_number, verse_number)
        db.session.execute(sql)
        db.session.commit()

        sql = """
                SELECT COUNT(*) as count
                FROM user_favourite
                WHERE user_id = %s
            """ % (current_user.get_id())
        result = db.session.execute(sql)
        total = [dict(r) for r in result][0]['count']

        badge_id_list = []
        badge_favorites = {1:28, 10:29, 100:30}
        if total in badge_favorites.keys():
            badge_id_list.append(badge_favorites[total])

        if badge_id_list != []:
            for badge_id in badge_id_list:
                sql = """
                        SELECT COUNT(*) as count
                        FROM user_badges
                        WHERE user_id = %s
                        AND badge_id = %s
                    """ % (current_user.get_id(), badge_id)
                result = db.session.execute(sql)
                badge_count = [dict(r) for r in result][0]['count']

                if badge_count < 1:
                    timestamp = datetime.now()
                    sql = """
                        INSERT INTO user_badges (user_id, badge_id, timestamp)
                        VALUES (%s, %s, '%s')
                    """ % (current_user.get_id(), badge_id, timestamp)
                    db.session.execute(sql)
                    db.session.commit()

                    sql = """
                        SELECT *
                        FROM badges
                        WHERE badge_id = %s
                    """ % (badge_id)
                    result = db.session.execute(sql)
                    badge = [dict(r) for r in result][0]
                    badge_list.append(badge)
    return jsonify(badge_list)


@main.route(
    '/share',
    methods=['GET'])
def share():
    current_app.logger.info("RadhaKrishna")
    badge_list = []
    if current_user.is_authenticated:
        badge_id_list = [34]
        if badge_id_list != []:
            for badge_id in badge_id_list:
                sql = """
                        SELECT COUNT(*) as count
                        FROM user_badges
                        WHERE user_id = %s
                        AND badge_id = %s
                    """ % (current_user.get_id(), badge_id)
                result = db.session.execute(sql)
                badge_count = [dict(r) for r in result][0]['count']

                if badge_count < 1:
                    timestamp = datetime.now()
                    sql = """
                        INSERT INTO user_badges (user_id, badge_id, timestamp)
                        VALUES (%s, %s, '%s')
                    """ % (current_user.get_id(), badge_id, timestamp)
                    db.session.execute(sql)
                    db.session.commit()

                    sql = """
                        SELECT *
                        FROM badges
                        WHERE badge_id = %s
                    """ % (badge_id)
                    result = db.session.execute(sql)
                    badge = [dict(r) for r in result][0]
                    badge_list.append(badge)
    return jsonify(badge_list)


@main.route(
    '/get-favourite/<int:chapter_number>/<string:verse_number>/',
    methods=['GET'])
def get_favourite(chapter_number, verse_number):
    current_app.logger.info("RadhaKrishna")
    if current_user.is_authenticated:
        sql = """
                SELECT COUNT(user_favourite_id)
                FROM user_favourite
                WHERE user_id = %s
                AND chapter = %s
                AND verse = '%s'
            """ % (current_user.get_id(), chapter_number, verse_number)
        result = db.session.execute(sql)
        count = [dict(r) for r in result][0]['count']

        if count == 1:
            return jsonify("True")
        return jsonify("False")
    abort(401)


@main.route('/about/', methods=['GET'])
def about():
    badge_list = []
    return render_template('main/about.html', badge_list=badge_list)


@main.route('/app/', methods=['GET'])
def app():
    badge_list = []
    return render_template('main/app.html', badge_list=badge_list)


@main.route('/api/', methods=['GET'])
def api():

    return render_template('main/api.html')


@main.route('/favourite-shlokas/', methods=['GET'])
def favourite_shlokas():
    badge_list = []
    current_app.logger.info("RadhaKrishna")
    verses = None
    if current_user.is_authenticated:
        verses = UserFavourite.query.filter_by(user_id = current_user.get_id()).order_by(UserFavourite.user_favourite_id.desc()).all()

    return render_template('main/favourite.html', verses=verses, badge_list = badge_list)


@main.route('/badges/', methods=['GET'])
def badges():
    current_app.logger.info("RadhaKrishna")
    badges = None
    badge_list = []
    if current_user.is_authenticated:
        sql = """
            SELECT *
            FROM badges
            ORDER BY badges.badge_id
        """
        result = db.session.execute(sql)
        badges = [dict(d) for d in result]

        sql = """
            SELECT badge_id
            FROM user_badges
            WHERE user_id = %s
            ORDER BY badge_id
        """ % (current_user.get_id())
        result = db.session.execute(sql)
        user_badges = [d['badge_id'] for d in result]

    return render_template('main/badges.html', badges=badges, user_badges=user_badges, badge_list = badge_list)


@main.route('/reading-plans/<string:message>', methods=['GET'])
@main.route('/reading-plans/', defaults={'message': None}, methods=['GET'])
def reading_plans(message):
    current_app.logger.info("RadhaKrishna")
    plans = []
    user_plans = []
    batch_list = []
    badge_list = []
    if current_user.is_authenticated:
        sql = """
                SELECT COUNT(*) as count
                FROM user_reading_plans
                WHERE user_id = %s
                AND status = 1
            """ % (current_user.get_id())
        result = db.session.execute(sql)
        total = [dict(r) for r in result][0]['count']

        badge_id_list = []
        if total == 1:
            badge_id_list.append(32)

        if badge_id_list != []:
            for badge_id in badge_id_list:
                sql = """
                        SELECT COUNT(*) as count
                        FROM user_badges
                        WHERE user_id = %s
                        AND badge_id = %s
                    """ % (current_user.get_id(), badge_id)
                result = db.session.execute(sql)
                badge_count = [dict(r) for r in result][0]['count']

                if badge_count < 1:
                    timestamp = datetime.now()
                    sql = """
                        INSERT INTO user_badges (user_id, badge_id, timestamp)
                        VALUES (%s, %s, '%s')
                    """ % (current_user.get_id(), badge_id, timestamp)
                    db.session.execute(sql)
                    db.session.commit()

                    sql = """
                        SELECT *
                        FROM badges
                        WHERE badge_id = %s
                    """ % (badge_id)
                    result = db.session.execute(sql)
                    badge = [dict(r) for r in result][0]
                    badge_list.append(badge)

        sql = """
            SELECT *
            FROM reading_plans
        """
        result = db.session.execute(sql)
        plans = [dict(d) for d in result]

        sql = """
            SELECT reading_plan_id, user_reading_plan_id, status
            FROM user_reading_plans
            WHERE user_id = %s
        """ % (current_user.get_id())
        result = db.session.execute(sql)
        user_plans = [dict(d) for d in result]

        timestamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d')

        sql = """
            SELECT DISTINCT(batch_id), user_reading_plan_id
            FROM user_reading_plan_items
            WHERE to_char(timestamp, 'YYYY-MM-DD') = '%s'
        """ % (timestamp)
        result = db.session.execute(sql)
        batch_list = [dict(d) for d in result]

    return render_template('main/reading_plans.html', plans=plans, user_plans=user_plans, batch_list=batch_list, message=message, badge_list=badge_list)


@main.route('/create-reading-plan/<string:reading_plan_id>', methods=['GET'])
def create_reading_plan(reading_plan_id):
    current_app.logger.info("RadhaKrishna")
    if current_user.is_authenticated:
        sql = """
                SELECT COUNT(user_reading_plan_id) as count
                FROM user_reading_plans
                WHERE user_id = %s
                AND reading_plan_id = '%s'
            """ % (current_user.get_id(), reading_plan_id)
        result = db.session.execute(sql)
        count = [dict(r) for r in result][0]['count']

        if count < 1:
            sql = """
                INSERT INTO user_reading_plans
                VALUES ('%s', '%s', %s, 0)
                RETURNING user_reading_plan_id
            """ % (gen_salt(10), reading_plan_id, current_user.get_id())
            result = db.session.execute(sql)
            user_reading_plan_id = [dict(d) for d in result][0]['user_reading_plan_id']

            timestamp = datetime.now()

            sql = """
                SELECT chapter_number, verse_number
                FROM verses
                ORDER BY chapter_number asc, verse_order asc
            """
            result = db.session.execute(sql)
            verses = [OrderedDict(d) for d in result]

            count = 0
            batch_id = 1
            verse_list = []

            gita_times = {"gita_in_a_year": 365, "gita_in_a_month": 30}

            def split(a, n):
                k, m = divmod(len(a), n)
                return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

            gita_time = gita_times[reading_plan_id]

            for verse_day in list(split(verses, gita_time)):
                for verse in verse_day:
                    verse_obj = UserReadingPlanItems(user_reading_plan_id, timestamp+timedelta(days=count), verse['chapter_number'], verse['verse_number'], 0, batch_id)
                    verse_list.append(verse_obj)
                count+=1
                batch_id+=1
            db.session.bulk_save_objects(verse_list)
            db.session.commit()

            return redirect("/reading-plan/" + str(user_reading_plan_id) + '/1')
    else:
        abort(401)

@main.route('/reading-plan/<string:user_reading_plan_id>/<int:batch_id>', methods=['GET'])
def reading_plan(user_reading_plan_id, batch_id):
    current_app.logger.info("RadhaKrishna")
    plans = None
    is_done = 'False'
    badge_list = []
    if current_user.is_authenticated:
        sql = """
                SELECT COUNT(*) as count
                FROM user_reading_plans
                WHERE user_id = %s
            """ % (current_user.get_id())
        result = db.session.execute(sql)
        total = [dict(r) for r in result][0]['count']

        badge_id_list = []
        if total == 1: badge_id_list.append(31)

        if badge_id_list != []:
            for badge_id in badge_id_list:
                sql = """
                        SELECT COUNT(*) as count
                        FROM user_badges
                        WHERE user_id = %s
                        AND badge_id = %s
                    """ % (current_user.get_id(), badge_id)
                result = db.session.execute(sql)
                badge_count = [dict(r) for r in result][0]['count']

                if badge_count < 1:
                    timestamp = datetime.now()
                    sql = """
                        INSERT INTO user_badges (user_id, badge_id, timestamp)
                        VALUES (%s, %s, '%s')
                    """ % (current_user.get_id(), badge_id, timestamp)
                    db.session.execute(sql)
                    db.session.commit()

                    sql = """
                        SELECT *
                        FROM badges
                        WHERE badge_id = %s
                    """ % (badge_id)
                    result = db.session.execute(sql)
                    badge = [dict(r) for r in result][0]
                    badge_list.append(badge)

        sql = """
            SELECT urpi.user_reading_plan_item_id, urpi.chapter_number, urpi.verse_number, to_char(timestamp, 'DD MONTH YYYY') as day, urpi.batch_id, urpi.status
            FROM user_reading_plan_items urpi
            JOIN user_reading_plans urp
            ON urpi.user_reading_plan_id = urp.user_reading_plan_id
            WHERE urp.user_id = %s
            AND urp.user_reading_plan_id = '%s'
            AND urpi.batch_id = '%s'
            ORDER BY urpi.user_reading_plan_item_id asc
        """ % (current_user.get_id(), user_reading_plan_id, batch_id)
        result = db.session.execute(sql)
        plans = [dict(d) for d in result]

        sql = """
            SELECT COUNT(DISTINCT batch_id) as count
            FROM user_reading_plan_items
            WHERE user_reading_plan_id = '%s'
        """ % (user_reading_plan_id)
        result = db.session.execute(sql)
        total_batches = [dict(d) for d in result][0]['count']

        sql = """
            SELECT COUNT(*) as count
            FROM user_reading_plan_items
            WHERE user_reading_plan_id = '%s'
            AND batch_id = %s
            AND status = 1
        """ % (user_reading_plan_id, batch_id)
        result = db.session.execute(sql)
        is_done = [dict(d) for d in result][0]['count']

        sql = """
            SELECT COUNT(*) as count
            FROM user_reading_plan_items
            WHERE user_reading_plan_id = '%s'
            AND batch_id = %s
        """ % (user_reading_plan_id, batch_id)
        result = db.session.execute(sql)
        total_batch_verses = [dict(d) for d in result][0]['count']
        if is_done == total_batch_verses:
            is_done = 'True'

        sql = """
            SELECT status
            FROM user_reading_plans
            WHERE user_reading_plan_id = '%s'
        """ % (user_reading_plan_id)
        result = db.session.execute(sql)
        status = [dict(r) for r in result][0]['status']

        sql = """
            SELECT rp.*
            FROM reading_plans rp
            JOIN user_reading_plans urp
            ON rp.reading_plan_id = urp.reading_plan_id
            WHERE user_reading_plan_id = '%s'
        """ % (user_reading_plan_id)
        result = db.session.execute(sql)
        reading_plan = [dict(r) for r in result][0]

        sql = """
            SELECT chapter_number, verse_number
            FROM user_reading_plan_items
            WHERE user_reading_plan_id = '%s'
            AND batch_id = %s
            AND status = 0
        """ % (user_reading_plan_id, batch_id)
        next_batch_verse = db.session.execute(sql).first()

        if status == 1: return redirect(url_for('main.reading_plans'))

        return render_template('main/reading_plan.html', plans=plans, batch_id=plans[0]['batch_id'], user_reading_plan_id=user_reading_plan_id, is_done=is_done, total_batches=total_batches, badge_list=badge_list, reading_plan=reading_plan, next_batch_verse=next_batch_verse)
    else:
        abort(401)


@main.route('/get-next-verse/<string:user_reading_plan_id>/<int:batch_id>/<int:chapter_number>/<string:verse_number>/', methods=['GET'])
def get_next_verse(user_reading_plan_id, batch_id, verse_number, chapter_number):
    current_app.logger.info("RadhaKrishna")
    if current_user.is_authenticated:
        sql = """
            UPDATE user_reading_plan_items
            SET status = 1
            WHERE user_reading_plan_id = '%s'
            AND batch_id = %s
            AND chapter_number = %s
            AND verse_number = '%s'
        """ % (user_reading_plan_id, batch_id, chapter_number, verse_number)
        db.session.execute(sql)
        db.session.commit()

        sql = """
            SELECT COUNT(*) as total
            FROM user_reading_plan_items
            WHERE user_reading_plan_id = '%s'
        """ % (user_reading_plan_id)
        result = db.session.execute(sql)
        total_verses = [dict(r) for r in result][0]['total']

        sql = """
            SELECT COUNT(*) as done
            FROM user_reading_plan_items
            WHERE user_reading_plan_id = '%s'
            AND status = 1
        """ % (user_reading_plan_id)
        result = db.session.execute(sql)
        done_verses = [dict(r) for r in result][0]['done']

        if total_verses == done_verses:
            sql = """
                UPDATE user_reading_plans
                SET status = 1
                WHERE user_reading_plan_id = '%s'
            """ % (user_reading_plan_id)
            db.session.execute(sql)
            db.session.commit()

        sql = """
            SELECT chapter_number, verse_number
            FROM user_reading_plan_items
            WHERE user_reading_plan_id = '%s'
            AND batch_id = %s
            AND status = 0
            ORDER BY user_reading_plan_item_id
        """ % (user_reading_plan_id, batch_id)
        result = db.session.execute(sql)
        next_verse = [dict(r) for r in result]
        if next_verse != []:
            return jsonify(next_verse[0])
        else:
            return jsonify("None")
    else:
        abort(401)


@main.route('/get-previous-verse/<string:user_reading_plan_id>/<int:batch_id>/<int:chapter_number>/<string:verse_number>/', methods=['GET'])
def get_previous_verse(user_reading_plan_id, batch_id, verse_number, chapter_number):
    current_app.logger.info("RadhaKrishna")
    if current_user.is_authenticated:
        sql = """
            SELECT chapter_number, verse_number
            FROM user_reading_plan_items
            WHERE user_reading_plan_id = '%s'
            AND batch_id = %s
            AND status = 1
            ORDER BY user_reading_plan_item_id
        """ % (user_reading_plan_id, batch_id)
        result = db.session.execute(sql)
        previous_verse = [dict(r) for r in result]
        current_app.logger.info(previous_verse)
        if previous_verse != []:
            return jsonify(previous_verse[0])
        else:
            return jsonify("None")
    else:
        abort(401)


@main.route('/delete-plan/<string:user_reading_plan_id>/', methods=['GET'])
def delete_plan(user_reading_plan_id):
    current_app.logger.info("RadhaKrishna")
    if current_user.is_authenticated:
        sql = """
            DELETE FROM user_reading_plan_items
            WHERE user_reading_plan_id = '%s'
        """ % (user_reading_plan_id)
        db.session.execute(sql)

        sql = """
            DELETE FROM user_reading_plans
            WHERE user_reading_plan_id = '%s'
        """ % (user_reading_plan_id)
        db.session.execute(sql)
        db.session.commit()

        return "RadhaKrishna"
    else:
        abort(401)


@main.route('/update-verse-status/<string:user_reading_plan_id>/<int:batch_id>/<int:user_reading_plan_item_id>/<int:status>/', methods=['GET'])
def update_verse_status(user_reading_plan_id, batch_id, user_reading_plan_item_id, status):
    current_app.logger.info("RadhaKrishna")
    if current_user.is_authenticated:
        sql = """
            UPDATE user_reading_plan_items
            SET status = %s
            WHERE user_reading_plan_id = '%s'
            AND batch_id = %s
            AND user_reading_plan_item_id = %s
        """ % (status, user_reading_plan_id, batch_id, user_reading_plan_item_id)
        db.session.execute(sql)
        db.session.commit()

        sql = """
            SELECT COUNT(*) as total
            FROM user_reading_plan_items
            WHERE user_reading_plan_id = '%s'
        """ % (user_reading_plan_id)
        result = db.session.execute(sql)
        total_verses = [dict(r) for r in result][0]['total']
        current_app.logger.info(total_verses)

        sql = """
            SELECT COUNT(*) as done
            FROM user_reading_plan_items
            WHERE user_reading_plan_id = '%s'
            AND status = 1
        """ % (user_reading_plan_id)
        result = db.session.execute(sql)
        done_verses = [dict(r) for r in result][0]['done']
        current_app.logger.info(done_verses)

        if total_verses == done_verses:
            sql = """
                UPDATE user_reading_plans
                SET status = 1
                WHERE user_reading_plan_id = '%s'
            """ % (user_reading_plan_id)
            db.session.execute(sql)
            db.session.commit()

        return jsonify("RadhaKrishna")
    else:
        abort(401)


@main.route('/progress/', methods=['GET'])
def progress():
    current_app.logger.info("RadhaKrishna")
    progress = {}
    gita = None
    total_shlokas = 0
    badge_list = []
    thegita = []
    progress = {key:None for key in range(1, 19)}

    if current_user.is_authenticated:
        sql = """
                SELECT radhakrishna.date, count(up.user_progress_id) FROM (
                    select to_char(date_trunc('day', (current_date - offs)), 'YYYY-MM-DD')
                    AS date
                    FROM generate_series(0, 6, 1)
                    AS offs
                    ) radhakrishna
                LEFT OUTER JOIN (
                    SELECT * FROM user_progress
                    WHERE user_id=%s
                ) up
                ON (radhakrishna.date=to_char(date_trunc('day', up.timestamp), 'YYYY-MM-DD'))
                GROUP BY radhakrishna.date
                ORDER BY radhakrishna.date desc
            """ % (current_user.get_id())
        result = db.session.execute(sql)
        for r in result:
            d = {}
            d['x'] = time.mktime(datetime.strptime(r['date'], "%Y-%m-%d").timetuple())
            d['y'] = r['count']
            thegita.append(d)

        sql = """
                SELECT chapter, COUNT(verse)
                FROM user_progress
                WHERE user_id = %s
                GROUP BY chapter
            """ % (current_user.get_id())
        result = db.session.execute(sql)
        user_verses = [dict(r) for r in result]

        sql = """
                SELECT chapter_number, verses_count
                FROM chapters
            """
        result = db.session.execute(sql)
        verses = [dict(r) for r in result]

        sql = """
                SELECT COUNT(verse)
                FROM user_progress
                WHERE user_id = %s
            """ % (current_user.get_id())
        result = db.session.execute(sql)
        total_shlokas = [dict(r) for r in result][0]['count']

        for chapter in verses:
            for chapter_number in user_verses:
                if chapter['chapter_number'] == chapter_number['chapter']:
                    progress[chapter['chapter_number']] = float("%.2f" % ((chapter_number['count']/chapter['verses_count'])*100))

        if total_shlokas:
            gita = float("%.2f" % (total_shlokas/692))
    return render_template('main/progress.html', progress=progress, gita=gita, thegita=json.dumps(thegita), badge_list = badge_list)


@main.route('/thegita/', methods=['GET'])
def thegita():
    current_app.logger.info("RadhaKrishna")

    sql = """
            SELECT EXTRACT(EPOCH FROM timestamp), count(*)
            FROM user_progress
            WHERE user_id = %s
            AND date_part('year', timestamp) = '2018'
            GROUP BY EXTRACT(EPOCH FROM timestamp)
        """ % (current_user.get_id())
    result = db.session.execute(sql)
    thegita = {r['date_part']:r['count'] for r in result}

    return jsonify(thegita)


def shloka_of_the_day_radhakrishna():
    ts = time.time()
    today = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    sql = """
        SELECT *
        FROM verse_of_day
        WHERE timestamp::date = date '%s'
    """ % (today)
    verse = db.session.execute(sql).first()

    if verse is None:
        sql = """
                INSERT INTO verse_of_day (chapter_number, verse_number)
                SELECT chapter_number, verses.verse_number
                FROM verses ORDER BY random() LIMIT 1
        """
        db.session.execute(sql)
        db.session.commit()


def shloka_of_the_day():
    ts = time.time()
    today = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    sql = """
            SELECT v.*
            FROM verses v
            JOIN verse_of_day vod
            ON v.chapter_number = vod.chapter_number
            AND v.verse_number = vod.verse_number
            WHERE vod.timestamp::date = date '%s'
            LIMIT 1
        """ % (today)
    verse = db.session.execute(sql).first()

    if verse is None:
        yesterday = date.today() - timedelta(1)
        yesterday = yesterday.strftime('%Y-%m-%d')
        current_app.logger.info(yesterday)
        sql = """
            SELECT v.*
            FROM verses v
            JOIN verse_of_day vod
            ON v.chapter_number = vod.chapter_number
            AND v.verse_number = vod.verse_number
            WHERE vod.timestamp::date = date '%s'
            LIMIT 1
        """ % (yesterday)
        verse = db.session.execute(sql).first()
    return verse

@main.route('/verse-of-the-day/', methods=['GET'])
def verse_of_the_day():
    current_app.logger.info("RadhaKrishna")
    badge_list = []
    verse = shloka_of_the_day()
    return render_template('main/verse_of_the_day.html', verse=verse, badge_list = badge_list)


def verse_of_the_day_notification():
    verse = shloka_of_the_day()
    auth = "Basic " + os.environ.get('ONESIGNAL') or 'Onesignal'
    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": auth}

    payload = {"app_id": "2713183b-9bcc-418c-a4a6-79f84fc40f2c",
               "template_id": "565cdba0-c3b3-4510-aac7-4e3571e18ea1",
               "included_segments": ["Test"],
               "contents": {"en": verse.text}}

    req = requests.post("https://onesignal.com/api/v1/notifications",
                        headers=header, data=json.dumps(payload))


def radhakrishna():
    print("RadhaKrishnaHanuman")

radhakrishna()

scheduler.add_job(shloka_of_the_day_radhakrishna, 'cron', hour=7, minute=57)
scheduler.add_job(verse_of_the_day_notification, 'cron', hour=7, minute=57)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

@main.route('/privacy-policy/', methods=['GET'])
def privacy_policy():
    badge_list = []
    return render_template('main/privacy-policy.html', badge_list=badge_list)


@main.route('/bhagavad-gita-quotes/', methods=['GET'])
def bhagavad_gita_quotes():
    badge_list = []
    quotes = [
        "Whenever dharma declines and the purpose of life is forgotten, I manifest myself on earth. I am born in every age to protect the good, to destroy evil, and to reestablish dharma.",
        "As they approach me, so I receive them. All paths, Arjuna, lead to me.",
        "I am the beginning, middle, and end of creation.",
        "Among animals I am the lion; among birds, the eagle Garuda. I am Prahlada, born among the demons, and of all that measures, I am time.",
        "I am death, which overcomes all, and the source of all beings still to be born.",
        "Just remember that I am, and that I support the entire cosmos with only a fragment of my being.",
        "Behold, Arjuna, a million divine forms, with an infinite variety of color and shape. Behold the gods of the natural world, and many more wonders never revealed before. Behold the entire cosmos turning within my body, and the other things you desire to see.",
        "I am time, the destroyer of all; I have come to consume the world.",
        "That one is dear to me who runs not after the pleasant or away from the painful, grieves not, lusts not, but lets things come and go as they happen.",
        "Just as a reservoir is of little use when the whole countryside is flooded, scriptures are of little use to the illumined man or woman, who sees the Lord everywhere.",
        "They alone see truly who see the Lord the same in every creature, who see the deathless in the hearts of all that die. Seeing the same Lord everywhere, they do not harm themselves or others. Thus they attain the supreme goal.",
        "With a drop of my energy I enter the earth and support all creatures. Through the moon, the vessel of life-giving fluid, I nourish all plants. I enter breathing creatures and dwell within as the life-giving breath. I am the fire in the stomach which digests all food.",
        "There are three gates to this self-destructive hell: lust, anger, and greed. Renounce these three.",
        "Pleasure from the senses seems like nectar at first, but it is bitter as poison in the end.",
        "That which seems like poison at first, but tastes like nectar in the end - this is the joy of sattva, born of a mind at peace with itself.",
        "The Lord dwells in the hearts of all creatures and whirls them round upon the wheel of maya. Run to him for refuge with all your strength, and peace profound will be yours through his grace.",
        "Whatever you do, make it an offering to me - the food you eat, the sacrifices you make, the help you give, even your suffering.",
        "I am heat; I give and withhold the rain. I am immortality and I am death; I am what is and what is not.",
        "Those who worship other gods with faith and devotion also worship me, Arjuna, even if they do not observe the usual forms. I am the object of all worship, its enjoyer and Lord.",
        "Those who remember me at the time of death will come to me. Do not doubt this. Whatever occupies the mind at the time of death determines the destination of the dying; always they will tend toward that state of being.",
        "When meditation is mastered, the mind is unwavering like the flame of a lamp in a windless place.",
        "They are forever free who renounce all selfish desires and break away from the egocage of 'I', 'me', and 'mine' to be united with the Lord. This is the supreme state. Attain to this, and pass from death to immortality.",
        "They live in wisdom who see themselves in all and all in them, who have renounced every selfish desire and sense-craving tormenting the heart.",
        "The meaning of Karma is in the intention. The intention behind action is what matters. Those who are motivated only by desire for the fruits of action are miserable, for they are constantly anxious about the results of what they do.",
        "You have the right to work, but never to the fruit of work. You should never engage in action for the sake of reward, nor should you long for inaction.",
        "Perform work in this world, Arjuna, as a man established within himself - without selfish attachments, and alike in success and defeat. For yoga is perfect evenness of mind.",
        "At the beginning of time I declared two paths for the pure heart: jnana yoga, the contemplative path of spiritual wisdom, and karma yoga, the active path of selfless service. There are the fundamental different types of yoga.",
        "Do your work with the welfare of others always in mind. It was by such work that Janaka attained perfection; others too have followed this path.",
        "There is nothing in the three worlds for me to gain, Arjuna, nor is there anything I do not have; I continue to act, but I am not driven by any need of my own.",
        "The ignorant work for their own profit, Arjuna; the wise work for the welfare of the world, without thought for themselves.",
        "It is better to strive in one's own dharma than to succeed in the dharma of another. Nothing is ever lost in following one's own dharma, but competition in another's dharma breeds fear and insecurity.",
        "The senses are higher than the body, the mind higher than the senses; above the mind is the intellect, and above the intellect is the Atman. Thus, knowing that which is supreme, let the Atman rule the ego. Use your mighty arms to slay the fierce enemy that is selfish desire.",
        "You and I have passed through many births, Arjuna. You have forgotten, but I remember them all.",
        "My true being is unborn and changeless. I am the Lord who dwells in every creature. Through the power of my own maya, I manifest myself in a finite form.",
        "Those who know me as their own divine Self break through the belief that they are the body and are not reborn as separate creatures. Such a one, Arjuna, is united with me.",
        "Delivered from selfish attachment, fear, and anger, filled with me, surrendering themselves to me, purified in the fire of my being, many have reached the state of unity in me.",
        "Actions do not cling to me because I am not attached to their results. Those who understand this and practice it live in freedom.",
        "The wise see that there is action in the midst of inaction and inaction in the midst of action. Their consciousness is unified, and every act is done with complete awareness.",
        "The process of offering is Brahman; that which is offered is Brahman. Brahman offers the sacrifice in the fire of Brahman. Brahman is attained by those who see Brahman in every action.",
        "The offering of wisdom is better than any material offering, Arjuna; for the goal of all work is spiritual wisdom.",
        "Approach those who have realized the purpose of life and question them with reverence and devotion; they will instruct you in this wisdom.",
        "Even if you were the most sinful of sinners, Arjuna, you could cross beyond all sin by the raft of spiritual wisdom.",
        "Krishna delivers the Gita to Arjuna.",
        "As the heat of a fire reduces wood to ashes, the fire of knowledge burns to ashes all karma.",
        "Those who surrender to Brahman all selfish attachments are like the leaf of a lotus floating clean and dry in water. Sin cannot touch them.",
        "Those who renounce attachment in all their deeds live content in the 'city of nine gates', the body, as its master. They are not driven to act, nor do they involve others in action.",
        "Those who possess this wisdom have equal regard for all. They see the same Self in a spiritual aspirant and an outcaste, in an elephant, a cow, and a dog.",
        "Pleasures conceived in the world of the senses have a beginning and an end and give birth to misery, Arjuna. The wise do not look for happiness in them. But those who overcome the impulses of lust and anger which arise in the body are made whole and live in joy. They find their joy, their rest, and their light completely within themselves. United with the Lord, they attain nirvana in Brahman.",
        "Free from anger and selfish desire, unified in mind, those who follow the path of yoga and realize the Self are established forever in that supreme state.",
        "Knowing me as the friend of all creatures, the Lord of the universe, the end of all offerings and all spiritual disciplines, they attain eternal peace.",
        "It is not those who lack energy or refrain from action, but those who work without expectation of reward who attain the goal of meditation.",
        "Those who cannot renounce attachment to the results of their work are far from the path.",
        "Reshape yourself through the power of your will; never let yourself be degraded by self-will. The will is the only friend of the Self, and the will is the only enemy of the Self.",
        "To those who have conquered themselves, the will is a friend. But it is the enemy of those who have not found the Self within them.",
        "The supreme Reality stands revealed in the consciousness of those who have conquered themselves. They live in peace, alike in cold and heat, pleasure and pain, praise and blame.",
        "With all fears dissolved in the peace of the Self and all actions dedicated to Brahman, controlling the mind and fixing it on me, sit in meditation with me as your only goal.",
        "Arjuna, those who eat too much or eat too little, who sleep too much or sleep too little, will not succeed in meditation. But those who are temperate in eating and sleeping, work and recreation, will come to the end of sorrow through meditation.",
        "In the still mind, in the depths of meditation, the Self reveals itself. Beholding the Self by means of the Self, an aspirant knows the joy and peace of complete fulfillment.",
        "Wherever the mind wanders, restless and diffuse in its search for satisfaction without, lead it within; train it to rest in the Self.",
        "I am ever present to those who have realized me in every creature. Seeing all life as my manifestation, they are never separated from me.",
        "When a person responds to the joys and sorrows of others as if they were his own, he has attained the highest state of spiritual union.",
        "No one who does good work will ever come to a bad end, either here or in the world to come.",
        "Through constant effort over many lifetimes, a person becomes purified of all selfish desires and attains the supreme goal of life.",
        "Meditation is superior to severe asceticism and the path of knowledge. It is also superior to selfless service. May you attain the goal of meditation, Arjuna!",
        "Even among those who meditate, that man or woman who worships me with perfect faith, completely absorbed in me, is the most firmly established in yoga.",
        "With your mind intent on me, Arjuna, discipline yourself with the practice of yoga. Depend on me completely. Listen, and I will dispel all your doubts; you will come to know me fully and be united with me.",
        "The birth and dissolution of the cosmos itself take place in me. There is nothing that exists separate from me, Arjuna. The entire universe is suspended from me as my necklace of jewels.",
        "Arjuna, I am the taste of pure water and the radiance of the sun and moon. I am the sacred word and the sound heard in air, and the courage of human beings. I am the sweet fragrance in the earth and the radiance of fire; I am the life in every creature and the striving of the spiritual aspirant.",
        "My eternal seed, Arjuna, is to be found in every creature. I am the power of discrimination in those who are intelligent, and the glory of the noble. In those who are strong, I am strength, free from passion and selfish attachment. I am desire itself, if that desire is in harmony with the purpose of life.",
        "The states of sattva, rajas, and tamas come from me, but I am not in them.",
        "The three gunas make up my divine maya, difficult to overcome. But they cross over this maya who take refuge in me.",
        "Some come to the spiritual life because of suffering, some in order to understand life; some come through a desire to achieve life's purpose, and some come who are men and women of wisdom. Unwavering in devotion, always united with me, the man or woman of wisdom surpasses all the others.",
        "After many births the wise seek refuge in me, seeing me everywhere and in everything. Such great souls are very rare.",
        "The world, deluded, does not know that I am without birth and changeless. I know everything about the past, the present, and the future, Arjuna; but there is no one who knows me completely.",
        "Delusion arises from the duality of attraction and aversion, Arjuna; every creature is deluded by these from birth.",
        "Those who see me ruling the cosmos, who see me in the adhibhuta, the adhidaiva, and the adhiyajna, are conscious of me even at the time of death.",
        "The Lord is the supreme poet, the first cause, the sovereign ruler, subtler than the tiniest particle, the support of all, inconceivable, bright as the sun, beyond darkness.",
        "Remembering me at the time of death, close down the doors of the senses and place the mind in the heart. Then, while absorbed in meditation, focus all energy upwards to the head. Repeating in this state the divine name, the syllable Om that represents the changeless Brahman, you will go forth from the body and attain the supreme goal.",
        "I am easily attained by the person who always remembers me and is attached to nothing else. Such a person is a true yogi, Arjuna.",
        "Every creature in the universe is subject to rebirth, Arjuna, except the one who is united with me.",
        "The six months of the northern path of the sun, the path of light, of fire, of day, of the bright fortnight, leads knowers of Brahman to the supreme goal. The six months of the southern path of the sun, the path of smoke, of night, of the dark fortnight, leads other souls to the light of the moon and to rebirth.",
        "Under my watchful eye the laws of nature take their course. Thus is the world set in motion; thus the animate and the inanimate are created.",
        "I am the ritual and the sacrifice; I am true medicine and the mantram. I am the offering and the fire which consumes it, and the one to whom it is offered.",
        "I am the father and mother of this universe, and its grandfather too; I am its entire support. I am the sum of all knowledge, the purifier, the syllable Om; I am the sacred scriptures, the Rig, Yajur, and Sama Vedas.",
        "I am the goal of life, the Lord and support of all, the inner witness, the abode of all. I am the only refuge, the one true friend; I am the beginning, the staying, and the end of creation; I am the womb and the eternal seed.",
        "Those who follow the rituals given in the Vedas, who offer sacrifices and take soma, free themselves from evil and attain the vast heaven of the gods, where they enjoy celestial pleasures. When they have enjoyed these fully, their merit is exhausted and they return to this land of death. Thus observing Vedic rituals but caught in an endless chain of desires, they come and go.",
        "Those who worship me and meditate on me constantly, without any other thought - I will provide for all their needs.",
        "Those who worship the devas will go to the realm of the devas; those who worship their ancestors will be united with them after death. Those who worship phantoms will become phantoms; but my devotees will come to me. Those who worship the devas will go to the realm of the devas; those who worship their ancestors will be united with them after death. Those who worship phantoms will become phantoms; but my devotees will come to me.",
        "Fill your mind with me; love me; serve me; worship me always. Seeking me in your heart, you will at last be united with me.",
        "All the scriptures lead to me; I am their author and their wisdom.",
        "Bhishma, Drona, Jayadratha, Karna, and many others are already slain. Kill those whom I have killed. Do not hesitate. Fight in this battle and you will conquer your enemies.",
        "Not by knowledge of the Vedas, nor sacrifice, nor charity, nor rituals, nor even by severe asceticism has any other mortal seen what you have seen, O heroic Arjuna.",
        "Better indeed is knowledge than mechanical practice. Better than knowledge is meditation. But better still is surrender of attachment to results, because there follows immediate peace.",
        "Some realize the Self within them through the practice of meditation, some by the path of wisdom, and others by selfless service. Others may not know these paths; but hearing and following the instructions of an illumined teacher, they too go beyond death.",
        "The brightness of the sun, which lights up the world, the brightness of the moon and of fire - these are my glory.",
        "Calmness, gentleness, silence, self-restraint, and purity: these are the disciplines of the mind.",
        "To refrain from selfish acts is one kind of renunciation, called sannyasa; to renounce the fruit of action is another, called tyaga.",
        "By serving me with steadfast love, a man or woman goes beyond the gunas. Such a one is fit for union with Brahman.",
        "When they see the variety of creation rooted in that unity and growing out of it, they attain fulfillment in Brahman.",
        "I have shared this profound truth with you, Arjuna. Those who understand it will attain wisdom; they will have done that which has to be done.",
        "I give you these precious words of wisdom; reflect on them and then do as you choose."
    ]
    return render_template('main/bhagavad-gita-quotes.html', quotes=quotes, badge_list = badge_list)


@main.route('/terms-of-service/', methods=['GET'])
def terms_of_service():
    badge_list = []
    return render_template('main/terms-of-service.html', badge_list = badge_list)


@main.route('/contact/', methods=['GET', 'POST'])
def contact():
    badge_list = []
    form = ContactForm()
    if form.validate_on_submit():
        args_dict = {}
        args_dict['name'] = form.name.data
        args_dict['email'] = form.email.data
        args_dict['subject'] = form.subject.data
        args_dict['message'] = form.message.data

        get_queue().enqueue(
            send_email,
            recipient="contact@bhagavadgita.io",
            subject=str(args_dict['subject']),
            template='main/email/contact',
            email_subject=args_dict['subject'],
            name=args_dict['name'],
            email=args_dict['email'],
            message=args_dict['message'])
        flash(
            'Thank you for your message. We will try to reply as soon as possible.'
        )
        return redirect(url_for('main.index'))
    return render_template('main/contact.html', form=form, badge_list=badge_list)


@main.route('/setcookie', methods=['GET'])
def set_cookie():
    if "settings" not in request.cookies:
        settings = {}
        settings['language'] = 'en'
        settings['font_size'] = '10'
        response = make_response("RadhaKrishna")
        response.set_cookie('settings', json.dumps(settings))

    return response


@main.route('/getcookie', methods=['GET'])
def get_cookie():
    radha = request.cookies.get('settings')
    return radha


@main.route('/robots.txt')
@main.route('/sitemap.xml')
@main.route('/android-chrome-192x192.png')
@main.route('/android-chrome-512x512.png')
@main.route('/apple-touch-icon.png')
@main.route('/browserconfig.xml')
@main.route('/favicon-16x16.png')
@main.route('/favicon-32x32.png')
@main.route('/favicon.ico')
@main.route('/mstile-150x150.png')
@main.route('/safari-pinned-tab.svg')
@main.route('/manifest.json')
@main.route('/OneSignalSDKWorker.js')
@main.route('/OneSignalSDKUpdaterWorker.js')
@main.route('/radhakrishna.js')
@main.route('/pwabuilder-sw.js')
def static_from_root():
    return send_from_directory(current_app.static_folder, request.path[1:])
