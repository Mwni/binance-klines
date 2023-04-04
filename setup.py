from setuptools import setup

setup(
	name='binance-klines',
	version='0.1',
	packages=[
		'binance_klines'
	],
	install_requires=[
		'python-binance'
	],
	entry_points ={
		'console_scripts': [
			'binance_klines = binance_klines.sync:main'
		]
	}
)