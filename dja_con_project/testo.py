import os
def run():
	SETTINGS_DIR = os.path.dirname(__file__)
	PROJECT_PATH = os.path.join(SETTINGS_DIR, os.pardir)
	PROJECT_PATH = os.path.abspath(PROJECT_PATH)
	TEMPLATE_PATH = os.path.join(PROJECT_PATH, 'templates')
	print TEMPLATE_PATH, PROJECT_PATH

run()