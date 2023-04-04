import sqlite3
from datetime import datetime
from .config import read_config


class Reader:
	def __init__(self, config_path):
		db_path, config = read_config(config_path)
		self.db = sqlite3.connect(db_path)
		self.pairs = config['pairs']

	def get_kline(self, pair, time):
		if isinstance(time, datetime):
			time = datetime.timestamp()

		print('SELECT * FROM %s WHERE `time` <= ? ORDER BY `time` DEC LIMIT 1' % pair, (time,))
		print('SELECT * FROM %s WHERE `time` <= ? ORDER BY `time` DEC LIMIT 1' % pair, (time,))
		print('SELECT * FROM %s WHERE `time` <= ? ORDER BY `time` DEC LIMIT 1' % pair, (time,))

		row = self.db.execute('SELECT * FROM %s WHERE `time` <= ? ORDER BY `time` DEC LIMIT 1' % pair, (time,)).fetchone()

		if not row:
			raise Exception('no kline for %s at timestamp %i' % (pair, time))

		return row