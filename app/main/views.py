#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, jsonify, current_app, request, make_response, redirect
from app.models.verse import VerseModel, RadhaKrishnaModel
from app.models.chapter import ChapterModel
from . import main
from app import db
import json
from app import babel
from flask_babel import gettext


import sys
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf8')


LANGUAGES = {
    'en': 'English',
    'hi': 'हिंदी'
}


verse_dict = {
  1:{
    4:"4-6",
    5:"4-6",
    6:"4-6",
    16:"16-18",
    17:"16-18",
    18:"16-18",
    21:"21-22",
    22:"21-22",
    29:"29-31",
    30:"29-31",
    31:"29-31",
    32:"32-33",
    33:"32-33",
    34:"34-35",
    35:"34-35",
    36:"36-37",
    37:"36-37",
    38:"38-39",
    39:"38-39",
    45:"45-46",
    46:"45-46",
  },
  2:{
    42:"42-43",
    43:"42-43",
  },
  3:{
    1:"1-2",
    2:"1-2",
    20:"20-21",
    21:"20-21",
  },
  4:{
    29:"29-30",
    30:"29-30",
  },
  5:{
    8:"8-9",
    9:"8-9",
    27:"27-28",
    28:"27-28",
  },
  6:{
    12:"12-13",
    13:"12-13",
    24:"24-25",
    25:"24-25",
    41:"41-42",
    42:"41-42",
  },
  7: {},
  8:{
    1:"1-2",
    2:"1-2",
    9:"9-10",
    10:"9-10",
    23:"23-26",
    24:"23-26",
    25:"23-26",
    26:"23-26",
  },
  9:{
    7:"7-8",
    8:"7-8",
    16:"16-17",
    17:"16-17",
  },
  10:{
    4:"4-5",
    5:"4-5",
    12:"12-13",
    13:"12-13",
    16:"16-17",
    17:"16-17",
  },
  11:{
    10:"10-11",
    11:"10-11",
    26:"26-27",
    27:"26-27",
    28:"28-29",
    29:"28-29",
    41:"41-42",
    42:"41-42",
    52:"52-53",
    53:"52-53",
  },
  12:{
    3:"3-4",
    4:"3-4",
    6:"6-7",
    7:"6-7",
    13:"13-14",
    14:"13-14",
    18:"18-19",
    19:"18-19",
  },
  13:{
    8:"8-12",
    9:"8-12",
    10:"8-12",
    11:"8-12",
    12:"8-12",
  },
  14:{
    3:"3-4",
    4:"3-4",
    11:"11-13",
    12:"11-13",
    13:"11-13",
    14:"14-15",
    15:"14-15",
    22:"22-23",
    23:"22-23",
    24:"24-25",
    25:"24-25",
  },
  15:{
    3:"3-4",
    4:"3-4",
  },
  16:{
    1:"1-3",
    2:"1-3",
    3:"1-3",
    13:"13-15",
    14:"13-15",
    15:"13-15",
    19:"19-20",
    20:"19-20",
  },
  17:{
    5:"5-6",
    6:"5-6",
    26:"26-27",
    27:"26-27",
  },
  18:{
    15:"15-16",
    16:"15-16",
    51:"51-53",
    52:"51-53",
    53:"51-53",
  },
}

@babel.localeselector
def get_locale():
    if "settings" in request.cookies:
        if json.loads(request.cookies.get('settings'))["language"]:
            return json.loads(request.cookies.get('settings'))["language"]
    return request.accept_languages.best_match(LANGUAGES.keys())


@main.route('/')
def index():
    language = "en"
    if "settings" in request.cookies:
        if json.loads(request.cookies.get('settings'))["language"]:
            language = json.loads(request.cookies.get('settings'))["language"]

    if language == "en":
        chapters = ChapterModel.query.order_by(ChapterModel.chapter_number).all()
        return render_template('main/index.html', chapters=chapters, language=language)
    else:
        return redirect('/' + language + '/')


@main.route('/<string:language>/')
def index_radhakrishna(language):
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

    return render_template('main/index.html', chapters=chapters, language=language)



@main.route('/search')
def search():
    verses = VerseModel.query.whoosh_search(request.args.get('query')).all()
    return render_template('main/search.html', verses=verses, query=request.args.get('query'))


@main.route('/chapter-numbers')
def get_all_chapter_numbers():
    chapters = ChapterModel.query.order_by(ChapterModel.chapter_number).all()
    chapter_numbers = {}
    for chapter in chapters:
        chapter_numbers[chapter.chapter_number] = "Chapter " + str(chapter.chapter_number)
    return jsonify(chapter_numbers)


@main.route('/languages')
def get_all_languages():
    languages = {}
    languages['en'] = "English"
    languages['hi'] = "हिंदी"
    return jsonify(languages)


@main.route('/verse-numbers/<int:chapter_number>')
def get_all_verse_numbers(chapter_number):
    verses = VerseModel.query.order_by(VerseModel.verse_order).filter_by(chapter_number=chapter_number)
    verse_numbers = {}
    for verse in verses:
        verse_numbers[verse.verse_order] = "Verse " + str(verse.verse_number)
    return jsonify(verse_numbers)


@main.route('/chapter/<int:chapter_number>/')
def chapter(chapter_number):
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
        return render_template('main/chapter.html', chapter=chapter, verses=verses)
    else:
        return redirect('/chapter/' + str(chapter_number) + '/' + language + '/')


@main.route('/chapter/<int:chapter_number>/<string:language>/')
def chapter_radhakrishna(chapter_number, language):
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


@main.route('/chapter/<int:chapter_number>/verse/<string:verse_number>/')
def verse(chapter_number, verse_number):
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
                AND v.verse_number = '%s'
                ORDER BY v.verse_order
            """ % (chapter_number, verse_number)

        verse = db.session.execute(sql).first()

        max_verse_number = VerseModel.query.order_by(VerseModel.verse_order.desc()).filter_by(chapter_number=chapter_number).first().verse_number

        if verse_number==max_verse_number:
            next_verse = None
            previous_verse_order = verse.verse_order - 1
            previous_verse = VerseModel.query.filter_by(chapter_number=chapter_number, verse_order=previous_verse_order).first()
        else:
            next_verse_order = verse.verse_order + 1
            previous_verse_order = verse.verse_order - 1
            previous_verse = VerseModel.query.filter_by(chapter_number=chapter_number, verse_order=previous_verse_order).first()
            next_verse = VerseModel.query.filter_by(chapter_number=chapter_number, verse_order=next_verse_order).first()

        return render_template('main/verse.html', chapter=chapter, verse=verse, next_verse=next_verse, previous_verse=previous_verse, language=language)

    else:
        return redirect('/chapter/' + str(chapter_number) + '/verse/' + str(verse_number) + '/' + language + '/')


@main.route('/chapter/<int:chapter_number>/verse/<string:verse_number>/<string:language>/')
def verse_radhakrishna(chapter_number, verse_number, language):
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

    max_verse_number = VerseModel.query.order_by(VerseModel.verse_order.desc()).filter_by(chapter_number=chapter_number).first().verse_number

    if verse_number==max_verse_number:
        next_verse = None
        previous_verse_order = verse.verse_order - 1
        previous_verse = VerseModel.query.filter_by(chapter_number=chapter_number, verse_order=previous_verse_order).first()
    else:
        next_verse_order = verse.verse_order + 1
        previous_verse_order = verse.verse_order - 1
        previous_verse = VerseModel.query.filter_by(chapter_number=chapter_number, verse_order=previous_verse_order).first()
        next_verse = VerseModel.query.filter_by(chapter_number=chapter_number, verse_order=next_verse_order).first()

    return render_template('main/verse.html', chapter=chapter, verse=verse, next_verse=next_verse, previous_verse=previous_verse, language=language)


@main.route('/about')
def about():

    return gettext('BHAGAVAD GITA')


@main.route('/setcookie')
def set_cookie():
    if "settings" not in request.cookies:
        settings = {}
        settings['language'] = 'en'
        settings['font_size'] = '10'
        response = make_response("RadhaKrishna")
        response.set_cookie('settings', json.dumps(settings))

    return response


@main.route('/getcookie')
def get_cookie():
    radha = request.cookies.get('settings')
    return radha
