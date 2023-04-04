import sqlite3
import coins
from datetime import datetime


def get(pair, start, end):
	rows = db.execute('SELECT * FROM %s%s WHERE `time` >= ? AND `time` < ?' % pair, (start, end))
	return [dict(row) for row in rows]

def at(pair, date):
	row = db.execute('SELECT * FROM %s%s WHERE `time` >= ?' % pair, (date,)).fetchone()

	if not row:
		print('[history] missing history for %s%s' % pair)
		#exit()
		return db.execute('SELECT * FROM %s%s ORDER BY `time` DESC LIMIT 1' % pair).fetchone()


	delay = row['time'] - date

	if delay > 60 * 2:
		print('[history] too long delay for %s (%is) wanted %s but have %s' % (
			'%s%s' % pair, 
			delay,
			datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M'),
			datetime.utcfromtimestamp(row['time']).strftime('%Y-%m-%d %H:%M')
		))
	#	exit()

	return row

def get_value(asset, base, date):
	value = 1

	if asset == base:
		return value

	for swap in coins.swap(asset, base):
		quote = at(swap['pair'], date)['open']

		if not quote:
			print('[history] missing quote for %s%s' % swap['pair'])
			exit()

		value = value / quote if swap['inv'] else value * quote

	return value