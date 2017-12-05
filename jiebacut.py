import jieba
import json
import re
import io

elems = []
stop_words = []
frequency = {}

def read_stop_words():
	# text = io.open('stop_words.txt', 'r', encoding='utf-8')
	with io.open('stop_words.txt', 'r', encoding='utf-8') as file:
		for line in file:
			stop_words.append(line[:-1])
	#print(stop_words[:20])

def require_check_stop_words():
	print('choose whether removing stop words, type \'y/n\'')
	ch = input()
	if ch == 'y':
		return True
	else:
		return False


def load():
	check_stop_words = require_check_stop_words()
	f = io.open('xq_yanbao.json', encoding='utf-8')
	content = json.load(f)
	file = io.open('split_%s.json' % (check_stop_words), 'w', encoding='utf-8')
	ffreq = io.open('frequency.txt', 'w', encoding='utf-8')

	if check_stop_words:
		read_stop_words()

	company_regex = re.compile(r'［(.*)：(.*)］(.*)')
	note_regex = re.compile(r'[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?：●【】“”！，。？、~@#￥%……&*（）]+')

	for sj in content:
		# to select paper in 2017
		if len(sj['time']) >= 15:
			continue
		m_title = company_regex.match(sj['title'])
		elem = {}
		elem['company'] = m_title.group(1)
		elem['atitude'] = m_title.group(2)
		elem['title_list'] = list(jieba.cut(re.sub(note_regex, '', m_title.group(3))))
		elem['text_list'] = list(jieba.cut(re.sub(note_regex, '', sj['text'])))
		if check_stop_words:
			for word in elem['title_list']:
				if word in stop_words:
					elem['title_list'].remove(word)
			for word in elem['text_list']:
				if word in stop_words:
					elem['text_list'].remove(word)
		elems.append(elem)

		# count frequency
		for word in elem['title_list']:
			if word in frequency:
				frequency[word] += 1
			else:
				frequency[word] = 1
		for word in elem['text_list']:
			if word in frequency:
				frequency[word] += 1
			else:
				frequency[word] = 1

	file.write((json.dumps(elems, ensure_ascii=False, sort_keys=True)))
	file.flush()
	file.close()

	sorted_list = sorted(frequency.items(),key = lambda x:x[1], reverse=True)

	#print(sorted_list[:100])
	for i in range(350):
		ffreq.write('%d.  ' % i)
		ffreq.write('%s\n' % str(sorted_list[i]))
		ffreq.flush()
	#ffreq.write(str(sorted_list[:250]))

	
	ffreq.close()

load()