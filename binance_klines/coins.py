import json


def exists(symbol):
	return symbol in repo


def lookup(symbol):
	if '-' in symbol:
		parts = symbol.split('-')
	elif '/' in symbol:
		parts = symbol.split('/')
	else:
		parts = None

	if parts:
		parts = ['USDT' if part == 'USD' else part for part in parts]

		for part in parts:
			if not exists(part):
				#print('%s of %s not found' % (part, symbol))
				return None

		return parts

	if exists(symbol):
		return [symbol, None]

	pairs = []

	for k in repo.keys():
		if symbol.startswith(k):
			other = symbol[len(k):]

			if exists(other):
				pairs.append((k, other))

	if len(pairs) == 0:
		#print('no pairs found for', symbol)
		return None

	if len(pairs) > 1:
		#print('found more than 1 possible pair for %s: %s' % (symbol, str(pairs)))

		for pair in pairs:
			if 'BTC' in pair or 'ETH' in pair or 'USDT' in pair:
				#print('choosing pair: %s' % str(pair))
				return pair

	return pairs[0]



def swap(fro, to):
	m = match([fro, to])

	if m:
		return [m]

	fro_pairs = get_pairs_having(fro)
	to_pairs = get_pairs_having(to)
	matches = []

	for fp in fro_pairs:
		for tp in to_pairs:
			if fp[0] in tp or fp[1] in tp:
				matches.append((
					{'pair': fp, 'inv': fro == fp[1]},
					{'pair': tp, 'inv': to == tp[0]}
				))

	if len(matches) == 0:
		return None

	matches = sorted(matches, 
		reverse=True,
		key=lambda swap: get_base_rank(
			swap[0]['pair'][0] if swap[0]['pair'][0] in swap[1]['pair'] else swap[0]['pair'][1]))

	return matches[0]


def match(target):
	for pair in pairs:
		if pair[0] == target[0] and pair[1] == target[1]:
			return {'pair': pair, 'inv': False}
		elif pair[0] == target[1] and pair[1] == target[0]:
			return {'pair': pair, 'inv': True}

def get_pairs_having(symbol):
	return [pair for pair in pairs if symbol in pair]

def get_base_rank(pair):
	for i, b in enumerate(reversed(bases)):
		if b in pair:
			return i+1

	return 0

def select_optimal(symbols):
	target = symbols[0][0]
	pairs = get_pairs_having(target)

	if len(pairs) == 0:
		return None

	return sorted(pairs, key=lambda pair: get_base_rank(pair), reverse=True)



bases = ['BTC', 'USDT', 'EUR']

with open('coins.json') as f:
	repo = json.load(f)['Data']
	repo['IOTA'] = repo['MIOTA']

with open('data/pairs.txt') as f:
	pairs = [lookup(symbol.replace('\n', '')) for symbol in f.readlines()]
	pairs = [pair for pair in pairs if pair]
