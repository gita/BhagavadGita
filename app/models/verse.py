from .. import db


class VerseModel(db.Model):

    __tablename__ = 'verses'
    __searchable__ = ['text', 'meaning_english', 'transliteration', 'word_meanings']


    id = db.Column(db.Integer, primary_key=True)
    verse_number = db.Column(db.String)
    text = db.Column(db.String)
    transliteration = db.Column(db.String)
    word_meanings = db.Column(db.String)
    meaning_english = db.Column(db.String)
    verse_order = db.Column(db.Integer)

    chapter_number = db.Column(db.Integer, db.ForeignKey('chapters.chapter_number'))
    chapters = db.relationship('ChapterModel')

    def __init__(self, chapter_number, verse_number, text, transliteration, word_meanings, meaning_english, verse_order):
        self.chapter_number = chapter_number
        self.verse_number = verse_number
        self.text = text
        self.transliteration = transliteration
        self.word_meanings = word_meanings
        self.meaning_english = meaning_english
        self.verse_order = verse_order

    def json(self):
        return {'chapter_number': self.chapter_number, 'verse_number': self.verse_number, 'text': self.text, 'transliteration': self.transliteration, 'word_meanings': self.word_meanings, 'meaning_english': self.meaning_english}

    @classmethod
    def find_by_verse_number(cls, verse_number):
        return cls.query.filter_by(verse_number=verse_number).first()

    @classmethod
    def find_by_chapter_number_verse_number(cls, chapter_number, verse_number):
        return cls.query.filter_by(chapter_number=chapter_number, verse_number=verse_number).first()
