import io
import json
import re
import math

ARTC = 300

ocwlis = []

tfm = []
idfm = []

ofd = {}


def load():
	fin = io.open('split_True.json', encoding='utf-8')
	ffreq = io.open('frequency.txt', encoding='utf-8')
	artj = json.load(fin)
	fout = io.open('tfidf.txt', 'w', encoding='utf-8')
	fw = io.open('words.txt', 'w', encoding='utf-8')

	reg = re.compile(r'\'(.*)\'')
	num_reg = re.compile(r'^[\d-]+$')
	#cwlis = []
	for line in ffreq:
		word = reg.search(line).group(1)
		if not num_reg.match(word): 
			#print(word)
			ocwlis.append(word)

	# key word 300
	cwlis = ocwlis[:ARTC]

	num_art = len(artj)
	idfd = dict(zip(cwlis, (0 for i in range(len(cwlis)))))
	# tf
	for art in artj:
		# init 300 word dict
		ofd = dict(zip(cwlis, (0 for i in range(len(cwlis)))))

		num = 0
		for lis in (art['text_list'], art['title_list']):
			for word in lis:
				if word in ofd:
					ofd[word] += 1
					num += 1

		
		for k in ofd.keys():
			if ofd[k] != 0:
				idfd[k] += 1
			ofd[k] /= num

		tfm.append(ofd)

		#print(ofd)
		#break

	# idf
	for k in idfd.keys():
		idfd[k] = math.log(num_art / idfd[k])

	# combine
	for d in tfm:
		for k in d.keys():
			d[k] = d[k] * idfd[k]
		fout.write(str(list(d.values())))
		fout.write('\n')
		fout.flush()

	#print(idfd)
	#print(tfm[0])
	fw.write(str(cwlis))




load()