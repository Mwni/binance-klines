import os
import json


def read_config(path):
	with open(path) as f:
		config = json.load(f)

	db_path = os.path.join(os.path.dirname(path), config['db_file'])

	return db_path, config