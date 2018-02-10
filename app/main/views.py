from flask import render_template, jsonify, current_app
from app.models.verse import VerseModel
from app.models.chapter import ChapterModel
from . import main
from app import db


@main.route('/')
def index():
    chapters = ChapterModel.query.order_by(ChapterModel.chapter_number).all()
    return render_template('main/index.html', chapters=chapters)


@main.route('/chapter/<int:chapter_number>')
def chapter(chapter_number):
    chapter = ChapterModel.find_by_chapter_number(chapter_number)
    verses = VerseModel.query.order_by(VerseModel.verse_number).filter_by(chapter_number=chapter_number)
    return render_template('main/chapter.html', chapter=chapter, verses=verses)


@main.route('/about')
def about():
    # verses = VerseModel.query.all()
    # for verse in verses:
    #     verse.transliteration = (verse.transliteration).lstrip("u'").rstrip("'")
    #     verse.transliteration = '"' + verse.transliteration + '"'
    # db.session.commit()
    return "RadhaKrishna"
