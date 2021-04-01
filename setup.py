try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
	'name': 'BDC Simulator',
	'description': 'This Tool Creates Simulation DataFrames for BDC',
	'author': "Murtaza NASAFI",
	'e-mail': "murtaza.nasafi@fcc.gov",
	'version': '0.1dev',
	'license': 'Creative Commons Attribution-Noncommercial-Share Alike license',
	'install_requires': ['nose', 'arcpy', 'pandas', 'numpy', 'zipfile', 'shutil', 'fnmatch'],
	'packages': ['tests', 'BDCSim', 'bin',]

}

setup(**config)