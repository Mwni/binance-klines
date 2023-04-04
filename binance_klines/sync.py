import time
import sqlite3
from datetime import datetime, timezone
from argparse import ArgumentParser
from dateutil.parser import parse as parsedate
from binance.client import Client
from .config import read_config


def pretty_duration(s):
	if s < 60:
		return str(s) + 's'
	elif s < 60 * 60:
		return '%im' % (s//60)
	elif s < 60 * 60 * 24:
		return '%ih' % (s//(60*60))
	else:
		return '%id' % (s//(60*60*24))

def timestamp2datestr(t):
	return datetime.utcfromtimestamp(t).strftime('%Y-%m-%d %H:%M')



def ensure_table(symbol):
	db.execute(
		'''
		CREATE TABLE IF NOT EXISTS %s (
			"time"	INTEGER NOT NULL UNIQUE,
			"open"	NUMERIC NOT NULL,
			"high"	NUMERIC NOT NULL,
			"low"	NUMERIC NOT NULL,
			"close"	NUMERIC NOT NULL,
			"volume"	NUMERIC NOT NULL,
			"buyquote"	NUMERIC NOT NULL,
			"buybase"	NUMERIC NOT NULL,
			"trades"	INTEGER NOT NULL,
			PRIMARY KEY("time")
		);
		''' % (symbol)
	)


def sync(symbol, start_time):
	if db.execute('SELECT `time` FROM %s' % symbol).fetchone():
		tspan_start, tspan_end = db.execute('SELECT MIN(`time`), MAX(`time`) FROM %s' % symbol).fetchone()
	else:
		tspan_start = tspan_end = 0


	now = datetime.now(tz=timezone.utc).timestamp()
	latest = max(start_time, tspan_end)
	behind = now - latest

	if behind < 60 * 10:
		return True

	try:
		klines = client.get_historical_klines(
			symbol, 
			interval, 
			datetime.utcfromtimestamp(latest+1).isoformat(), 
			None, 
			10000
		)
	except Exception as e:
		print('failed at symbol %s:' % symbol, e)
		return

	for kline in klines:
		db.execute('INSERT INTO %s (`time`,open,high,low,close,volume,buyquote,buybase,trades) VALUES (?,?,?,?,?,?,?,?,?)' % symbol, (
			int(kline[0]//1000),#time
			float(kline[1]), 	#open
			float(kline[2]), 	#high
			float(kline[3]),	#low
			float(kline[4]),	#close
			float(kline[5]),	#volume
			float(kline[10]),	#taker buy quote
			float(kline[9]),	#taker buy base
			int(kline[8])		#trades
		))

	db.commit()

	print('%s: added %s - %s (%s behind)      ' % (
		symbol, 
		str(datetime.utcfromtimestamp(int(klines[0][0]//1000))), 
		str(datetime.utcfromtimestamp(int(klines[-1][0]//1000))), 
		pretty_duration(behind)
	), end='\r')



def main():
	global client, db, interval

	parser = ArgumentParser()
	parser.add_argument('config')
	args = parser.parse_args()

	db_path, config = read_config(args.config)
	credentials = config['credentials']
	pairs = config['pairs']

	client = Client(credentials['key'], credentials['secret'])


	db = sqlite3.connect(db_path)
	start_date = parsedate(config['start_date'])
	interval = config['interval']

	print('kline interval is %s' % interval)
	print('syncing following pairs into database "%s" starting from %s:' % (db_path, str(start_date)))
	print('> %s' % (' '.join(pairs)))
	print('')

	for pair in pairs:
		ensure_table(pair)


	while True:
		all_idle = True

		for pair in pairs:
			idle = sync(pair, start_date.timestamp())
			all_idle = idle and all_idle

		if all_idle:
			print('nothing to sync - waiting 10s       ', end='\r')
			time.sleep(10)



if __name__ == '__main__':
	main()