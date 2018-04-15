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


@main.route('/bhagavad-gita-quotes/', methods=['GET'])
def bhagavad_gita_quotes():
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
        "That which seems like poison at first, but tastes like nectar in the end â€“ this is the joy of sattva, born of a mind at peace with itself.",
        "The Lord dwells in the hearts of all creatures and whirls them round upon the wheel of maya. Run to him for refuge with all your strength, and peace profound will be yours through his grace.",
        "Whatever you do, make it an offering to me â€“ the food you eat, the sacrifices you make, the help you give, even your suffering.",
        "I am heat; I give and withhold the rain. I am immortality and I am death; I am what is and what is not.",
        "Those who worship other gods with faith and devotion also worship me, Arjuna, even if they do not observe the usual forms. I am the object of all worship, its enjoyer and Lord.",
        "Those who remember me at the time of death will come to me. Do not doubt this. Whatever occupies the mind at the time of death determines the destination of the dying; always they will tend toward that state of being.",
        "When meditation is mastered, the mind is unwavering like the flame of a lamp in a windless place.",
        "They are forever free who renounce all selfish desires and break away from the egocage of â€œI,â€ â€œme,â€ and â€œmineâ€ to be united with the Lord. This is the supreme state. Attain to this, and pass from death to immortality.",
        "They live in wisdom who see themselves in all and all in them, who have renounced every selfish desire and sense-craving tormenting the heart.",
        "The meaning of Karma is in the intention. The intention behind action is what matters. Those who are motivated only by desire for the fruits of action are miserable, for they are constantly anxious about the results of what they do.",
        "You have the right to work, but never to the fruit of work. You should never engage in action for the sake of reward, nor should you long for inaction.",
        "Perform work in this world, Arjuna, as a man established within himself â€“ without selfish attachments, and alike in success and defeat. For yoga is perfect evenness of mind.",
        "At the beginning of time I declared two paths for the pure heart: jnana yoga, the contemplative path of spiritual wisdom, and karma yoga, the active path of selfless service. There are the fundamental different types of yoga.",
        "Do your work with the welfare of others always in mind. It was by such work that Janaka attained perfection; others too have followed this path.",
        "There is nothing in the three worlds for me to gain, Arjuna, nor is there anything I do not have; I continue to act, but I am not driven by any need of my own.",
        "The ignorant work for their own profit, Arjuna; the wise work for the welfare of the world, without thought for themselves.",
        "It is better to strive in oneâ€™s own dharma than to succeed in the dharma of another. Nothing is ever lost in following oneâ€™s own dharma, but competition in anotherâ€™s dharma breeds fear and insecurity.",
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
        "Those who renounce attachment in all their deeds live content in the â€œcity of nine gates,â€ the body, as its master. They are not driven to act, nor do they involve others in action.",
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
        "Some come to the spiritual life because of suffering, some in order to understand life; some come through a desire to achieve lifeâ€™s purpose, and some come who are men and women of wisdom. Unwavering in devotion, always united with me, the man or woman of wisdom surpasses all the others.",
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
        "Those who worship me and meditate on me constantly, without any other thought â€“ I will provide for all their needs.",
        "Those who worship the devas will go to the realm of the devas; those who worship their ancestors will be united with them after death. Those who worship phantoms will become phantoms; but my devotees will come to me. Those who worship the devas will go to the realm of the devas; those who worship their ancestors will be united with them after death. Those who worship phantoms will become phantoms; but my devotees will come to me.",
        "Fill your mind with me; love me; serve me; worship me always. Seeking me in your heart, you will at last be united with me.",
        "All the scriptures lead to me; I am their author and their wisdom.",
        "Bhishma, Drona, Jayadratha, Karna, and many others are already slain. Kill those whom I have killed. Do not hesitate. Fight in this battle and you will conquer your enemies.",
        "Not by knowledge of the Vedas, nor sacrifice, nor charity, nor rituals, nor even by severe asceticism has any other mortal seen what you have seen, O heroic Arjuna.",
        "Better indeed is knowledge than mechanical practice. Better than knowledge is meditation. But better still is surrender of attachment to results, because there follows immediate peace.",
        "Some realize the Self within them through the practice of meditation, some by the path of wisdom, and others by selfless service. Others may not know these paths; but hearing and following the instructions of an illumined teacher, they too go beyond death.",
        "The brightness of the sun, which lights up the world, the brightness of the moon and of fire â€“ these are my glory.",
        "Calmness, gentleness, silence, self-restraint, and purity: these are the disciplines of the mind.",
        "To refrain from selfish acts is one kind of renunciation, called sannyasa; to renounce the fruit of action is another, called tyaga.",
        "By serving me with steadfast love, a man or woman goes beyond the gunas. Such a one is fit for union with Brahman.",
        "When they see the variety of creation rooted in that unity and growing out of it, they attain fulfillment in Brahman.",
        "I have shared this profound truth with you, Arjuna. Those who understand it will attain wisdom; they will have done that which has to be done.",
        "I give you these precious words of wisdom; reflect on them and then do as you choose."
    ]
    return render_template('main/bhagavad-gita-quotes.html', quotes=quotes)


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
@main.route('/OneSignalSDKWorker.js')
@main.route('/OneSignalSDKUpdaterWorker.js')
@main.route('/radhakrishna.js')
def static_from_root():
    return send_from_directory(current_app.static_folder, request.path[1:])
