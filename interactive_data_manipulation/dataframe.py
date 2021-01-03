import pandas as pd
import numpy as np
from IPython.display import display
import ipywidgets as widgets
from matplotlib import pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

NUMPY_NUMERIC_TYPES = ["int8", "int16", "int32", "int64", "uint8", "uint16", "uint32", "uint64", "float_", "float16", "float32", "float64"]
NUMPY_DATE_TYPES = [np.datetime64]
COL_TYPE_OPTIONS = ["numeric", "categorical", "string", "date"]

class idm_dataframe():

	def __init__(self, _df):
		self._df = _df
		self.col_num_for_summary = 7
		self.ctg_unique_cnt_hard = 5
		self.ctg_unique_cnt_soft = 50
		self.qt_for_hist = 0.95
		self.top_n_for_freq = 20
		self.avg_freq_thld = 2
		self.ts_groupby_freqs = ["S", "T", "H", "D", "M", "Y"]
		self.ts_groupby_freq = {}
		self.ts_groupby_cnt_thld = 50
		self.intro_loaded = False

		# detect_type
		self.col_types = {}
		for col in self._df.columns:
			self.col_types[col] = self.detect_type(col)
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
		
		return "string"

	def _determine_groupby_period(self, column):
		for _freq_str in self.ts_groupby_freqs:
			_row_cnt = len(self._df.groupby(self._df[column].dt.to_period(_freq_str)).count())
			if _row_cnt <= self.ts_groupby_cnt_thld:
				return _freq_str
		return self.ts_groupby_freqs[-1]

	def _plot_date(self, column):
		_freq_str = self._determine_groupby_period(column)
		self.ts_groupby_freq[column] = _freq_str
		grouper = self._df.groupby(self._df[column].dt.to_period(_freq_str)).count()[column]
		date_df = pd.DataFrame(grouper).rename(columns={column: "count"}).reset_index()
		date_df["metric"] = "count"
		_ax = sns.barplot(data=date_df, x=column, y="count", hue="metric")
		plt.legend(loc="best")
		return _ax

	def _plot_numeric(self, column):
		_df = self._df
		qt_high, qt_low = _df.quantile(self.qt_for_hist)[column], _df.quantile(1 - self.qt_for_hist)[column]
		_df_qt = _df[(_df[column] <= qt_high) & (_df[column] >= qt_low)]
		_ax = sns.distplot(_df_qt[column], kde=False)
		plt.ylabel("Frequency")
		ax2 = _ax.twinx()
		sns.distplot(_df_qt[column], ax=ax2, kde=True, hist=False)
		plt.title(f"'{column}' Distribution Histogram")
		return _ax

	def _plot_ctg(self, column):
		_df = self._df
		grouper = _df.groupby(column).count()
		_col0 = grouper.columns[0]
		df_ctg = grouper.sort_values(_col0, ascending=False).rename(columns={_col0: "freq"})[:self.top_n_for_freq]
		df_ctg[column] = df_ctg.index.tolist()

		_ax = sns.barplot(x='freq', y=column, data=df_ctg, dodge=True)
		#_ax = plt.barh( df_ctg[column], df_ctg["freq"], width=0.1)
		plt.title(f"'{column}' Value Frequency")
		return _ax

	def get_col_summary(self, column, figure):
		_type = self.detect_type(column)
		if _type == "date":
			_ax = self._plot_date(column)
			figure.autofmt_xdate()
			return _ax
		elif _type == "numeric":
			return self._plot_numeric(column)
		elif _type == "categorical":
			return self._plot_ctg(column)
		return None

	def count_col_type(self, col_type):
		return len([c for c in self.col_types if self.col_types[c] == col_type])

	def get_intro_text(self):
		_substr_list = []
		for _type in COL_TYPE_OPTIONS:
			_type_cnt = self.count_col_type(_type)
			_substr_list.append(f"{_type_cnt} {_type} columns")
		_str = f"{len(self._df)} rows, {len(self._df.columns)} columns. ({', '.join(_substr_list)} detected.)"
		return _str

	def count_null(self, column):
		return self._df[column].isna().sum()

	def get_col_info_text(self, column):
		_val_unique_cnt = len(self._df[column].unique())
		_null_cnt = self.count_null(column)
		return f"Detected type: {self.detect_type(column)}, {_val_unique_cnt} different values, {_null_cnt} null values."



