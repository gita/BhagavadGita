#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys

from flask import (abort, current_app, flash, jsonify, make_response, redirect,
                   render_template, request, url_for, send_from_directory)
from flask_rq import get_queue

from app import babel, db, es
from app.models.chapter import ChapterModel
from app.models.verse import VerseModel

from . import main
from ..email import send_email
from .forms import ContactForm


if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf8')

LANGUAGES = {'en': 'English', 'hi': 'हिंदी'}

verse_dict = {
    1: {
        '16': "16-18",
        '17': "16-18",
        '18': "16-18",
        '21': "21-22",
        '22': "21-22",
        '32': "32-35",
        '33': "32-35",
        '34': "32-35",
        '35': "32-35",
        '37': "37-38",
        '38': "37-38",
    },
    2: {
        '42': "42-43",
        '43': "42-43",
    },
    3: {},
    4: {},
    5: {
        '8': "8-9",
        '9': "8-9",
        '27': "27-28",
        '28': "27-28",
    },
    6: {
        '11': "11-12",
        '12': "11-12",
        '13': "13-14",
        '14': "13-14",
        '20': "20-23",
        '21': "20-23",
        '22': "20-23",
        '23': "20-23",
    },
    7: {},
    8: {},
    9: {},
    10: {
        '4': "4-5",
        '5': "4-5",
        '12': "12-13",
        '13': "12-13",
    },
    11: {
        '10': "10-11",
        '11': "10-11",
        '26': "26-27",
        '27': "26-27",
        '41': "41-42",
        '42': "41-42",
    },
    12: {
        '3': "3-4",
        '4': "3-4",
        '6': "6-7",
        '7': "6-7",
        '13': "13-14",
        '14': "13-14",
        '18': "18-19",
        '19': "18-19",
    },
    13: {
        '1': "1-2",
        '2': "1-2",
        '6': "6-7",
        '7': "6-7",
        '8': "8-12",
        '9': "8-12",
        '10': "8-12",
        '11': "8-12",
        '12': "8-12",
    },
    14: {
        '22': "22-25",
        '23': "22-25",
        '24': "22-25",
        '25': "22-25",
    },
    15: {
        '3': "3-4",
        '4': "3-4",
    },
    16: {
        '1': "1-3",
        '2': "1-3",
        '3': "1-3",
        '11': "11-12",
        '12': "11-12",
        '13': "13-15",
        '14': "13-15",
        '15': "13-15",
    },
    17: {
        '5': "5-6",
        '6': "5-6",
        '26': "26-27",
        '27': "26-27",
    },
    18: {
        '51': "51-53",
        '52': "51-53",
        '53': "51-53",
    },
}


@babel.localeselector
def get_locale():
    if "settings" in request.cookies:
        if json.loads(request.cookies.get('settings'))["language"]:
            return json.loads(request.cookies.get('settings'))["language"]
    return request.accept_languages.best_match(LANGUAGES.keys())


@main.route('/', methods=['GET'])
def index():
    language = "en"
    if "settings" in request.cookies:
        if json.loads(request.cookies.get('settings'))["language"]:
            language = json.loads(request.cookies.get('settings'))["language"]

    if language == "en":
        chapters = ChapterModel.query.order_by(
            ChapterModel.chapter_number).all()
        return render_template(
            'main/index.html', chapters=chapters, language=language)
    else:
        return redirect('/' + language + '/')


@main.route('/<string:language>/', methods=['GET'])
def index_radhakrishna(language):
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

    return render_template(
        'main/index.html', chapters=chapters, language=language)


@main.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query')
    res = es.search(index="verses", body={
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
        'main/search.html', verses=verses, query=request.args.get('query'))


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
    if chapter_number not in range(1, 19):
        abort(404)
    language = "en"
    if "settings" in request.cookies:
        if json.loads(request.cookies.get('settings'))["language"]:
            language = json.loads(request.cookies.get('settings'))["language"]

    if language == "en":
        chapter = ChapterModel.find_by_chapter_number(chapter_number)
        sql = """
                SELECT *
                FROM verses v
                WHERE v.chapter_number = %s
                ORDER BY v.verse_order
            """ % (chapter_number)

        verses = db.session.execute(sql)
        return render_template(
            'main/chapter.html', chapter=chapter, verses=verses)
    else:
        return redirect(
            '/chapter/' + str(chapter_number) + '/' + language + '/')


@main.route(
    '/chapter/<int:chapter_number>/<string:language>/', methods=['GET'])
def chapter_radhakrishna(chapter_number, language):
    if chapter_number not in range(1, 19):
        abort(404)
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
        WHERE c.chapter_number = %s
        ORDER BY c.chapter_number
    """ % (chapter_table, chapter_number)
    chapter = db.session.execute(sql).first()

    verses_table = "verses_" + language
    sql = """
            SELECT verse_number, meaning, chapter_number
            FROM %s
            WHERE chapter_number = %s
            ORDER BY verse_order
        """ % (verses_table, chapter_number)

    verses = db.session.execute(sql)
    return render_template('main/chapter.html', chapter=chapter, verses=verses)


@main.route(
    '/chapter/<int:chapter_number>/verse/<string:verse_number>/',
    methods=['GET'])
def verse(chapter_number, verse_number):
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

            return render_template(
                'main/verse.html',
                chapter=chapter,
                verse=verse,
                next_verse=next_verse,
                previous_verse=previous_verse,
                language=language)

        else:
            return redirect('/chapter/' + str(chapter_number) + '/verse/' +
                            str(verse_number) + '/' + language + '/')


@main.route(
    '/chapter/<int:chapter_number>/verse/<string:verse_number>/<string:language>/',
    methods=['GET'])
def verse_radhakrishna(chapter_number, verse_number, language):
    if chapter_number not in range(1, 19):
        abort(404)
    chapter = ChapterModel.find_by_chapter_number(chapter_number)

    verses_table = "verses_" + language
    sql = """
            SELECT vt.meaning, vt.word_meanings, v.text, v.transliteration, v.chapter_number, v.verse_number, v.verse_order
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
        language=language)


@main.route('/about/', methods=['GET'])
def about():

    return render_template('main/about.html')


@main.route('/api/', methods=['GET'])
def api():

    return render_template('main/api.html')


@main.route('/privacy-policy/', methods=['GET'])
def privacy_policy():

    return render_template('main/privacy-policy.html')


@main.route('/terms-of-service/', methods=['GET'])
def terms_of_service():

    return render_template('main/terms-of-service.html')


@main.route('/contact/', methods=['GET', 'POST'])
def contact():
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
    return render_template('main/contact.html', form=form)


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
@main.route('/upup.min.js')
@main.route('/bhagavadgita.min.js')
@main.route('/bhagavadgitachapter.min.js')
@main.route('/bhagavadgitaverse.min.js')
@main.route('/OneSignalSDKWorker.js')
@main.route('/OneSignalSDKUpdaterWorker.js')
def static_from_root():
    return send_from_directory(current_app.static_folder, request.path[1:])
