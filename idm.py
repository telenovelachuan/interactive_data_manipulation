from IPython import get_ipython
import pandas as pd

local_dfs = []

def print_dfs():
	for item in [i for i in local_dfs if not hasattr(i, '__call__')]:
		if type(item[1]) == pd.core.frame.DataFrame:
			print(item)

# def add_cell():
# 	get_ipython().run_cell_magic(u'HTML', u'', u'<font color=red>heffffo</font>')


def load_dataframes():
    from IPython.core.getipython import get_ipython
    shell = get_ipython()
    #n = shell.set_next_input(contents, replace=False)
    shell.run_cell("idm.local_dfs = list(vars().items())")