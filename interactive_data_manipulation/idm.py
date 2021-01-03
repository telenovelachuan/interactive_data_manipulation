from IPython import get_ipython
import pandas as pd
from ipywidgets import interact, interactive, fixed, interact_manual, Layout
import ipywidgets as widgets
from matplotlib import pyplot as plt
from IPython.display import display, clear_output
from .dataframe import idm_dataframe
from .summary import idm_tabs

local_vars = []
local_dfs = {}
#main_out = widgets.Output(layout=Layout(border='solid 1px black'))
main_out = widgets.Output()
menu_out = widgets.Output()
pre_canvas_out = widgets.Output()
df_intro_out = widgets.Output()
tabs_out = widgets.Output()
canvas_out = widgets.Output()
post_canvas_out = widgets.Output()
backward_paging_text = "...previous"
forward_paging_text = "...next"
_configs = {
	"menu_unfolded": False,
	"chosen_df": None,
	"menus": ["Summary", "Drop NA", "Filter", "Dedup", "Join", "Transpose"],
	"col_num_for_summary": 7,
	"df": None,
	"tab_paging_start": 0,
	"tab_paging_end": -1,
	"idm_tabs": None,
	"tabs_children": [],
	"_tab": None
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

def _render_single_tab(_df, col_name, out):
	
	out.clear_output(wait=True)
	_pd_df = _df.to_pd_df()
	with out:
		_fig, _axes = plt.subplots(figsize=(16, 7))
		_axes = _df.get_col_summary(col_name, _fig)
		_label = widgets.Label(value=_df.get_col_info_text(col_name))
		display(_label)
		if _axes is not None:
			
			plt.show(_fig)
		else:
			plt.close()
			display(widgets.Label(value=f"Example Values:"))
			print(_pd_df[[col_name]].head(5))

def _click_paging_tab(direction="forward"):
	if direction == "forward":
		_configs["tab_paging_start"] += _configs["col_num_for_summary"]
		_configs["tab_paging_end"] = min(_configs["tab_paging_start"] + _configs["col_num_for_summary"], len(_configs["df"].to_pd_df().columns) - 1)
		tabs_out.clear_output()
		_render_summary()
		_configs["_tab"].selected_index = 1
	else:
		_configs["tab_paging_start"] -= _configs["col_num_for_summary"]
		_configs["tab_paging_end"] = _configs["tab_paging_start"] + _configs["col_num_for_summary"]
		tabs_out.clear_output()
		_render_summary()
		if _configs["tab_paging_start"] != 0:
			_configs["_tab"].selected_index = 1

def _summary_tab_changed(widget):
	tab_idx = widget['new']
	tab_title = widget["owner"]._titles[str(tab_idx)]
	_df = _configs["df"]
	_pd_df = _df.to_pd_df()
	if tab_title == backward_paging_text:
		_click_paging_tab("backward")
		return
	elif tab_title == forward_paging_text:
		_click_paging_tab("forward")
		return
		
	_render_single_tab(_df, tab_title, out=_configs["tabs_children"][tab_idx])


def _render_summary():
	_df = _configs["df"]
	total_col_cnt = len(_df.to_pd_df().columns)
	_backward_paging, _forward_paging = False, False
	tabs = idm_tabs(_df)
	_configs["idm_tabs"] = tabs
	if _configs["tab_paging_end"] == -1:
		_configs["tab_paging_end"] = min(_configs["tab_paging_start"] + _configs["col_num_for_summary"], total_col_cnt - 1)
	head_cols = list(_df.to_pd_df().columns[_configs["tab_paging_start"]: _configs["tab_paging_end"]])

	if _df.intro_loaded is False:

		with df_intro_out:
			intro_str = _df.get_intro_text()
			display(widgets.Label(value=intro_str))
		_df.intro_loaded = True

	# generate backward paging tab if valid
	if _configs["tab_paging_start"] != 0:
		_backward_paging = True
		children = [widgets.Output()]
	else:
		children = []

	for idx, _col in enumerate(head_cols):
		_out = widgets.Output()
		_child = widgets.Label(value=f"Column '{_col}'")

		if idx == 0:
			_render_single_tab(_df, _col, _out)

		_configs["idm_tabs"].set_output(_col, _out)
		children.append(_configs["idm_tabs"].get_output(_col))

	if _configs["tab_paging_end"] != total_col_cnt - 1:
		_forward_paging = True
		children.append(widgets.Output())
		head_cols.append(forward_paging_text)

	tab = widgets.Tab()
	tab.children = children
	_configs["tabs_children"] = children
	tab.observe(_summary_tab_changed, names='selected_index')
	if _backward_paging is True:
		head_cols = [backward_paging_text] + head_cols
	[tab.set_title(num, name) for num, name in enumerate(head_cols)]
	_configs["_tab"] = tab
	with tabs_out:
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
		)
		_btn.on_click(_gnrt_btn_click(_menu))
		btns.append(_btn)
	display(widgets.HBox(btns))

def init_outputs():
	with main_out:
		render_essentials()
		display(menu_out)
		display(pre_canvas_out)
		with pre_canvas_out:
			display(df_intro_out)
			display(tabs_out)
		display(canvas_out)
		display(post_canvas_out)
	display(main_out)

def load_local_vars():
    from IPython.core.getipython import get_ipython
    shell = get_ipython()
    #n = shell.set_next_input(contents, replace=False)
    shell.run_cell("interactive_data_manipulation.local_vars = list(vars().items())")

def df_dpd_change(change):
    if change['type'] == 'change' and change['name'] == 'value':
        _df = idm_dataframe(local_dfs[change['new']])
        _configs["df"] = _df
        canvas_out.clear_output()
        tabs_out.clear_output()
        df_intro_out.clear_output()

        with canvas_out:
        	display(widgets.Label(value="Data Preview:"))
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


