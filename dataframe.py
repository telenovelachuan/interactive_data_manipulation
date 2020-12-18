import pandas as pd
import numpy as np
from IPython.display import display
import ipywidgets as widgets
from matplotlib import pyplot as plt
import seaborn as sns

NUMPY_NUMERIC_TYPES = ["int8", "int16", "int32", "int64", "uint8", "uint16", "uint32", "uint64", "float_", "float16", "float32", "float64"]
NUMPY_DATE_TYPES = [np.datetime64]

class idm_dataframe():

	def __init__(self, _df):
		self._df = _df
		self.col_num_for_summary = 7
		self.ctg_unique_cnt_hard = 5
		self.ctg_unique_cnt_soft = 20
		self.qt_for_hist = 0.95
		self.top_n_for_freq = 20
		self.avg_freq_thld = 2
		sns.set()

	def to_pd_df(self):
		return self._df

	def detect_type(self, column):
		
		
		pd_type = self._df.dtypes[column]
		if np.issubdtype(pd_type, np.datetime64):
			return "date"
		unique_cnt = len(self._df[column].unique())
		if unique_cnt <= self.ctg_unique_cnt_hard:
			return "categorical"
		if pd_type in [np.dtype(t) for t in NUMPY_NUMERIC_TYPES]:
			return "numeric"
		avg_freq = self._df[column].value_counts().mean()
		if unique_cnt <= self.ctg_unique_cnt_soft and avg_freq >= self.avg_freq_thld:
			return "categorical"
		
		return "other"

	def _plot_date(self, column):
		grouper = self._df.groupby(self._df[column].dt.to_period("Y")).count()[column]
		date_df = pd.DataFrame(grouper).rename(columns={column: "count"}).reset_index()
		date_df["metric"] = "count"
		_ax = sns.barplot(data=date_df, x=column, y="count", hue="metric")
		plt.legend(loc="best")
		return _ax

	def _plot_numeric(self, column):
		_df = self._df
		qt_high, qt_low = _df.quantile(self.qt_for_hist)[column], _df.quantile(1 - self.qt_for_hist)[column]
		_df_qt = _df[(_df[column] <= qt_high) & (_df[column] >= qt_low)]
		_ax = plt.hist(_df_qt[column])
		plt.title(f"'{column}' Distribution Histogram")
		return _ax

	def _plot_ctg(self, column):
		_df = self._df
		grouper = _df.groupby(column).count()
		_col0 = grouper.columns[0]
		df_ctg = grouper.sort_values(_col0, ascending=False).rename(columns={_col0: "freq"})[:self.top_n_for_freq]
		df_ctg[column] = df_ctg.index.tolist()

		_ax = sns.barplot(x='freq', y=column, data=df_ctg)
		plt.title(f"'{column}' Value Frequency")
		return _ax

	def get_col_summary(self, column):
		_type = self.detect_type(column)
		if _type == "date":
			return self._plot_date(column)
		elif _type == "numeric":
			return self._plot_numeric(column)
		elif _type == "categorical":
			return self._plot_ctg(column)
		return None




