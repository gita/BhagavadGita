from .. import db

class ChapterModel(db.Model):

    __tablename__ = 'chapters'
    __searchable__ = ['name', 'name_transliterated', 'name_transliterated_simple', 'name_english']


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    name_transliterated = db.Column(db.String)
    name_transliterated_simple = db.Column(db.String)
    verses_count = db.Column(db.Integer)
    chapter_number = db.Column(db.Integer)
    name_english = db.Column(db.String)
    image_name = db.Column(db.String)
    chapter_summary = db.Column(db.String)
    verses = db.relationship('VerseModel', lazy='dynamic')

    def __init__(self, name, name_transliterated, name_transliterated_simple, verses_count, chapter_number, name_english, image_name, chapter_summary):
        self.name = name
        self.name_transliterated = name_transliterated
        self.name_transliterated_simple = name_transliterated_simple
        self.verses_count = verses_count
        self.chapter_number = chapter_number
        self.name_english = name_english
        self.image_name = image_name
        self.chapter_summary = chapter_summary

    def json(self):
        return {'name': self.name, 'name_transliterated': self.name_transliterated, 'name_transliterated_simple': self.name_transliterated_simple, 'verses_count': self.verses_count, 'chapter_number': self.chapter_number, 'name_english': self.name_english}

    @classmethod
    def find_by_chapter_number(cls, chapter_number):
        return cls.query.filter_by(chapter_number=chapter_number).first()
