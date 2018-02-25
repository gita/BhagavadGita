from .. import db

class ChapterModel(db.Model):

    __tablename__ = 'chapters'
    __searchable__ = ['name', 'name_transliterated', 'name_translation', 'name_meaning']


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    name_transliterated = db.Column(db.String)
    name_translation = db.Column(db.String)
    verses_count = db.Column(db.Integer)
    chapter_number = db.Column(db.Integer)
    name_meaning = db.Column(db.String)
    image_name = db.Column(db.String)
    chapter_summary = db.Column(db.String)
    verses = db.relationship('VerseModel', lazy='dynamic')

    def __init__(self, name, name_transliterated, name_translation, verses_count, chapter_number, name_meaning, image_name, chapter_summary):
        self.name = name
        self.name_transliterated = name_transliterated
        self.name_translation = name_translation
        self.verses_count = verses_count
        self.chapter_number = chapter_number
        self.name_meaning = name_meaning
        self.image_name = image_name
        self.chapter_summary = chapter_summary

    def json(self):
        return {'name': self.name, 'name_transliterated': self.name_transliterated, 'name_translation': self.name_translation, 'verses_count': self.verses_count, 'chapter_number': self.chapter_number, 'name_meaning': self.name_meaning}

    @classmethod
    def find_by_chapter_number(cls, chapter_number):
        return cls.query.filter_by(chapter_number=chapter_number).first()
