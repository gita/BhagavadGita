# coding=utf8
import bs4, requests
import simplejson
import time

bhagavad_gita = []

for chapter in range(18, 19):
	for verse in range(1, 79):
		try:
			url = requests.get('http://www.holy-bhagavad-gita.org/chapter/' + str(chapter) + '/verse/' + str(verse) + '/')
			url.raise_for_status()
		except Exception:
			continue

		data = url.text
		soup = bs4.BeautifulSoup(data, "html.parser")

		verse = {}

		# Get the verse_no
		verse_id = soup.select('#translation > p > span > u')
		verse_no = verse_id[0].getText()
		verse_no = verse_no.lstrip('BG ' + str(chapter))
		verse_no = verse_no.lstrip('.')
		verse['chapter'] = chapter
		verse['verse_no'] = verse_no

		# Get the verse in Sanskrit
		sanskrit_verse_selector = soup.select('#originalVerse > p')
		sanskrit_verses = ""
		for i in range(len(sanskrit_verse_selector)):
			sanskrit_verse = sanskrit_verse_selector[i].getText()
			sanskrit_verses += sanskrit_verse
		sanskrit = []
		krishna = sanskrit_verses[-2:]
		if krishna == '||':
			for s in sanskrit_verses.split(' |'):
				if s[-2:]!= '||':
					sanskrit.append(s + ' |')
				else:
					sanskrit.append('|' + s)
		else:
			radha = '।'.decode('utf-8')
			for s in sanskrit_verses.split(' '+radha):
				if s[-2:]!= ''+radha+radha:
					sanskrit.append(s + ' '+radha)
				else:
					sanskrit.append(''+ radha + s)
		verse['sanskrit'] = sanskrit

		for br in soup.find_all("br"):
			br.replace_with("\n")
		transliteration_verse_selector = soup.select('#transliteration > p')
		transliteration_verses = ""
		for i in range(len(transliteration_verse_selector)):
			transliteration_verse = transliteration_verse_selector[i].getText()
			transliteration_verses += transliteration_verse
		transliteration = []
		for t in transliteration_verses.splitlines():
			transliteration.append(t)
		# sanskrit_verse = sanskrit_verse.lstrip('BG ' + str(chapter) + '.' + str(verse) + ': \n')
		verse['transliteration'] = transliteration

		word_verse_selector = soup.select('#wordMeanings')
		word_verse = word_verse_selector[0].getText()
		# sanskrit_verse = sanskrit_verse.lstrip('BG ' + str(chapter) + '.' + str(verse) + ': \n')
		verse['word'] = word_verse

		bhagavad_gita.append(verse)

		time.sleep(1)

radhakrishna = open('bhagavad_gita_sanskrit_18.txt', 'w')
simplejson.dump(bhagavad_gita, radhakrishna)
radhakrishna.close()

print "RadhaKrishna"
