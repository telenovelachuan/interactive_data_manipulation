from IPython import get_ipython
import pandas as pd
from ipywidgets import interact, interactive, fixed, interact_manual, Layout
import ipywidgets as widgets
from matplotlib import pyplot as plt
from IPython.display import display, clear_output
from dataframe import idm_dataframe

local_vars = []
local_dfs = {}
main_out = widgets.Output(layout=Layout(border='solid 1px black'))
menu_out = widgets.Output(layout=Layout(border='solid 1px black'))
pre_canvas_out = widgets.Output(layout=Layout(border='solid 1px red'))
canvas_out = widgets.Output(layout=Layout(border='solid 1px orange'))
post_canvas_out = widgets.Output(layout=Layout(border='solid 1px yellow'))
_configs = {
	"menu_unfolded": False,
	"chosen_df": None,
	"menus": ["Summary", "Drop NA", "Dedup", "Join", "Transpose"],
	"col_num_for_summary": 7,
	"df": None,
	"summary_tab_outputs": {}
}

def render_essentials():
	df_dpd_label = widgets.Label('Choose a dataframe: ', layout=Layout(width='150px'))
	df_dropdown = widgets.Dropdown(
	    options=list(local_dfs.keys()),
	    value=None,
	    description='',
	    disabled=False,
	)
	df_dropdown.observe(df_dpd_change)
	display(widgets.HBox([df_dpd_label, df_dropdown]))

def _summary_tab_changed(widget):
	tab_idx = widget['new']
	_df = _configs["df"]
	_pd_df = _df.to_pd_df()
	# lazy load the selected tab
	col_name = _pd_df.columns[tab_idx]
	_out = _configs["summary_tab_outputs"][col_name]
	_out.clear_output(wait=True)
	with _out:
		_fig, _axes = plt.subplots(figsize=(16, 7))
		_axes = _df.get_col_summary(col_name)
		_val_unique_cnt = len(_pd_df[col_name].unique())
		_label = widgets.Label(value=f"potential type: {_df.detect_type(col_name)}, {_val_unique_cnt} different values.")
		display(_label)
		if _axes is not None:
			plt.show(_fig)
		else:
			plt.close()
			display(widgets.Label(value=f"Example Values:"))
			print(_pd_df[[col_name]].head(5))
			_fig, _axes = None, None

	

def _render_summary():
	_df = _configs["df"]
	head_cols = _df.to_pd_df().columns[:_configs["col_num_for_summary"]]
	children = []
	for idx, _col in enumerate(head_cols):
		_out = widgets.Output()
		#_type = _df.detect_type(_col)
		_child = widgets.Label(value=f"Column '{_col}'")

		with _out:
			# only render the first one
			if idx == 0:				
				_fig, _axes = plt.subplots(figsize=(16, 7))
				_axes = _df.get_col_summary(_col)
				_val_unique_cnt = len(_df.to_pd_df()[_col].unique())
				_label = widgets.Label(value=f"potential type: {_df.detect_type(_col)}, {_val_unique_cnt} different values.")
				display(_label)
				if _axes is not None:
					plt.show(_fig)
				else:
					plt.close()
					display(widgets.Label(value=f"Example Values:"))
					print(_df.to_pd_df()[[_col]].head(5))
					_fig, _axes = None, None

		children.append(_out)
		_configs["summary_tab_outputs"][_col] = _out

	tab = widgets.Tab()
	tab.children = children
	tab.observe(_summary_tab_changed, names='selected_index')
	[tab.set_title(num, name) for num, name in enumerate(head_cols)]
	with pre_canvas_out:
		display(tab)

def _gnrt_btn_click(menu_name):
	def _btn_click(b):
		render_func = globals().get(f"_render_{menu_name.lower()}")
		render_func()

	return _btn_click

def render_menu():
	btns = []
	for _menu in _configs["menus"]:
		_btn = widgets.Button(
		    description=_menu,
		    disabled=False,
		    button_style='', # 'success', 'info', 'warning', 'danger' or ''
		)
		_btn.on_click(_gnrt_btn_click(_menu))
		btns.append(_btn)
	display(widgets.HBox(btns))

def init_outputs():
	with main_out:
		render_essentials()
		display(menu_out)
		display(pre_canvas_out)
		display(canvas_out)
		display(post_canvas_out)
	display(main_out)

def load_local_vars():
    from IPython.core.getipython import get_ipython
    shell = get_ipython()
    #n = shell.set_next_input(contents, replace=False)
    shell.run_cell("idm.local_vars = list(vars().items())")

def df_dpd_change(change):
    if change['type'] == 'change' and change['name'] == 'value':
        _df = idm_dataframe(local_dfs[change['new']])
        _configs["df"] = _df
        canvas_out.clear_output()
        with canvas_out:
        	display(_df.to_pd_df())

        if _configs["menu_unfolded"] is False:
        	with menu_out:
        		render_menu()
        		_configs["menu_unfolded"] = True

def load():
	load_local_vars()
	for item in [i for i in local_vars if not hasattr(i, '__call__')]:
		name, value = item
		if type(value) == pd.core.frame.DataFrame:
			local_dfs[name] = value

	

	init_outputs()
	# with main_out:
	# 	display(widgets.HBox([df_dpd_label, df_dropdown]))

print(locals()["_render_summary"])
