

class idm_tabs():

	def __init__(self, _df):
		self._df = _df
		self.titles = []
		self.outputs = {}

	def get_output(self, col):
		return self.outputs[col]

	def set_output(self, col, output):
		self.outputs[col] = output