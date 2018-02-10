from flask import render_template, jsonify, current_app
from app.models.verse import VerseModel
from app.models.chapter import ChapterModel
from . import main
from app import db


@main.route('/')
def index():
    chapters = ChapterModel.query.order_by(ChapterModel.chapter_number).all()
    return render_template('main/index.html', chapters=chapters)


@main.route('/about')
def about():
    # chapters = ChapterModel.query.all()
    # for chapter in chapters:
    #     chapter.name_english = (chapter.name_english).lstrip("u'").rstrip("'")
    #     chapter.name_english = '"' + chapter.name_english + '"'
    # db.session.commit()
    return "RadhaKrishna"
