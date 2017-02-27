#!/usr/bin/env python
#coding: utf-8

import json, pprint, clipboard, os, console

import ui, textwrap, editor, os, bz2, base64, clipboard

'''
2016.2.26 full support subview like v['subview']['subview']['subview']...
'''

def to_abs_path(*value):
	import os
	abs_path = os.path.join(os.path.expanduser('~'),'Documents')
	for _value in value:
		abs_path = os.path.join(abs_path,_value)
	return abs_path



def get_attrib(node):
	global subclass_name_list, gui_helper
	for attrib in node:
		#print attrib
		class_name = attrib['class']
		
		name = attrib['attributes']['name']
		class_name = attrib['class']
			
		print 'name {}'.format(name)
		print 'class name {}'.format(class_name)

		if subclass_name_list:
			print subclass_name_list
			_subclass_name_list = map(lambda x:"['"+x+"']", subclass_name_list)
			object_str = "{}['{}']".format(''.join(_subclass_name_list), name)
			object_str = 'self.{title} = self.{view_title}{subclass_str}'.format(title=name, view_title=gui_helper.view_title, subclass_str=object_str)
		else:
			
			object_str = "self.{title} = self.{view_title}['{title}']".format(title=name, view_title=gui_helper.view_title)
		
		print object_str
			
			
		#gui_helper
		
		
		if class_name == 'View':
			gui_helper.insert_View(name, object_str)
			
		elif class_name == 'insert_Label':
			gui_helper.insert_Label(name, object_str)
			
		elif class_name == 'TextField':
			gui_helper.insert_TextField(name, object_str)
			
		elif class_name == 'TextView':
			gui_helper.insert_TextView(name, object_str)
			
		elif class_name == 'Button':
			gui_helper.insert_Button(name, object_str)
			
		elif class_name == 'Slider':
			gui_helper.insert_Slider(name, object_str)
		
		elif class_name == 'Switch':
			gui_helper.insert_Switch(name, object_str)
			
		elif class_name == 'SegmentedControl':
			gui_helper.insert_SegmentedControl(name, object_str)
			
		elif class_name == 'TableView':
			gui_helper.insert_TableView(name, object_str)
			
		elif class_name == 'TextView':
			gui_helper.insert_TextView(name, object_str)
		
	
		
		#find all subview
		if attrib['nodes']:
			subclass_name_list.append(name)
			get_attrib(attrib['nodes'])
	if subclass_name_list:
		del subclass_name_list[-1]

def get_attrib_main(pyui_path, extra_func_mode, remove_title_bar, remove_status_bar, class_name, main_view_name):
	global subclass_name_list, gui_helper
	with open(pyui_path) as in_file:
		r = json.load(in_file)
		#pprint.pprint(r)
		attrib = r[0]
		
		title = attrib.get('name', 'Untitled')
		custom_class = attrib.get('custom_class', None)
		print 'title {}'.format(title)
		print 'custom_class {}'.format(custom_class)
		print '----------'
		subclass_name_list = []
	
		gui_helper = GUI_Helper(view_title=title, pyui_path=pyui_path, extra_func_mode=extra_func_mode, remove_title_bar=remove_title_bar, remove_status_bar=remove_status_bar, class_name=class_name, main_view_name=main_view_name)
		
		get_attrib(attrib['nodes'])


class GUI_Helper(object):
	def __init__(self, view_title, pyui_path, extra_func_mode=False, remove_title_bar=False, remove_status_bar=False, class_name=False, main_view_name=False):
		self.extra_func_mode=extra_func_mode
		self.remove_title_bar=remove_title_bar
		self.remove_status_bar=remove_status_bar
		self.pyui_path = pyui_path
		
		name = os.path.splitext(os.path.basename(pyui_path))[0]
		if class_name:
			class_title = self.class_title = class_name
		else:
			class_title = self.class_title = console.input_alert('Class Title','',name)
		
		if main_view_name:
			self.view_title = main_view_name
		else:	
			self.view_title = 'Untitled' if view_title == '' else view_title
			
		self.relpath = os.path.relpath(pyui_path, to_abs_path())
		
		imp_obj = ''
		if remove_status_bar or remove_title_bar:
			imp_obj += 'import objc_util'
			remove_bar_def = '''def find_nav_bar(v):
	sv=v.superview()
	if sv:
		for c in sv.subviews():
			if c._get_objc_classname()==b'UINavigationBar':
				return c
		return find_nav_bar(sv)

@objc_util.on_main_thread
def remove_title_bar(v):
	navbar=find_nav_bar(objc_util.ObjCInstance(v))
	if navbar:
		navbar.hidden=True
		v.frame =(0,0,ui.get_screen_size()[0],ui.get_screen_size()[1])
	
def hide_status_bar():
	objc_util.UIApplication.sharedApplication().statusBar().hidden = True
				'''
		
		else:
			remove_bar_def = ''
			
		self.init_text = '''#!/usr/bin/env python
#coding: utf-8

import ui
import speech
{imp_obj}

def to_abs_path(*value):
	import os
	abs_path = os.path.join(os.path.expanduser('~'),'Documents')
	for _value in value:
		abs_path = os.path.join(abs_path,_value)
	return abs_path

{remove_bar_def}
'''.format(class_title=class_title, view_title=self.view_title, relpath=self.relpath, imp_obj=imp_obj, remove_bar_def=remove_bar_def)


		if extra_func_mode:
			self.init_text += '''
class {class_title}(ui.View):
	def __init__(self, view):
		self.{view_title} = view'''.format(class_title=class_title, view_title=self.view_title)
		
		else:		
			self.init_text += '''
class {class_title}(object):
	def __init__(self):
		self.{view_title} = ui.load_view(to_abs_path('{relpath}'))'''.format(class_title=class_title, view_title=self.view_title, relpath=self.relpath)
		

		self.def_text = ''
		#self.view_from_dict(view_dict) #making text
			
		
	
	def get_text(self):
		extra_func_text = '''
class _{class_title}({class_title}):
	def __init__(self):
		pass
	
	def did_load(self):
		self.main_view = {class_title}(self)
		
	def will_close(self):
		speech.say('close', 'en-US')
		
	def touch_began(self, touch):
		# Called when a touch begins.
		pass

	def touch_moved(self, touch):
		# Called when a touch moves.
		pass

	def touch_ended(self, touch):
		# Called when a touch ends.
		pass

v = ui.load_view(to_abs_path('{relpath}'))
v.present()
'''.format(class_title=self.class_title, relpath=self.relpath)
			
		self.text = self.init_text
		self.text += '''
		self.{view_title}.present()'''.format(view_title=self.view_title) if not self.extra_func_mode else ''
		if not self.extra_func_mode:
			if self.remove_status_bar:
				self.text += '''
		hide_status_bar()'''
			if self.remove_title_bar:
				self.text += '''
		remove_title_bar(self.{view_title})'''.format(view_title=self.view_title)
		
		
		self.text += '''
{def_text}
	'''.format(init_text=self.init_text, def_text=self.def_text, view_title=self.view_title,class_title=self.class_title)
			
		if self.extra_func_mode:
			add_custom_class(self.pyui_path, '_'+self.class_title)
			self.text += extra_func_text
			if self.remove_status_bar:
				self.text += '''
hide_status_bar()'''
			if self.remove_title_bar:
				self.text += '''
remove_title_bar(v)'''
				
		else:
			add_custom_class(self.pyui_path, 'ui.View')
			self.text += '''
{class_title}()'''.format(class_title=self.class_title)
		return self.text
	
	
	
	
	
	def insert_View(self, title, object_str):
			self.init_text += '''
		{}'''.format(object_str)
	
	def insert_Label(self, title, object_str):
		print('Label')
		
	def insert_TextField(self, title, object_str):
		print 'TextField'
		self.init_text += '''
		{object_str}
		self.{title}.delegate = self.{title}_Delegate
		self.{title}.delegate.textfield_did_change = self.{title}_did_change
		self.{title}.autocorrection_type = False
		self.{title}.spellchecking_type =False
		self.{title}.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
		'''.format(title=title, object_str=object_str)
		self.def_text += '''
	class {title}_Delegate():
		pass
	
	def {title}_did_change(self, textfield):
		speech.say('{title}', 'en-US')
		pass		
			'''.format(title=title)
		
	def insert_TextView(self, title, object_str):
		print 'TextView'
		
	def insert_Button(self, title, object_str):
		print 'Button'
		self.init_text += '''
		{object_str}
		self.{title}.action = self.{title}_action
		'''.format(title=title, object_str=object_str)
		self.def_text += '''
	def {title}_action(self, sender):
		speech.say('{title}', 'en-US')
		pass
			'''.format(title=title)
	
							
	def insert_Slider(self, title, object_str):
		print 'Slider'
		self.init_text += '''
		{object_str}
		self.{title}.continuous = False
		self.{title}.action = self.{title}_action
		'''.format(title=title, object_str=object_str)
		self.def_text += '''
	def {title}_action(self, sender):
		speech.say('{title}', 'en-US')
		pass
			'''.format(title=title)
		
	def insert_Switch(self, title, object_str):
		print 'Switch'
		self.init_text += '''
		{object_str}
		self.{title}.action = self.{title}_action
		'''.format(title=title, object_str=object_str)
		self.def_text += '''
	def {title}_action(self, sender):
		speech.say('{title}', 'en-US')
		pass
			'''.format(title=title)
	
	def insert_SegmentedControl(self, title, object_str):
		print 'SegmentedControl'
		self.init_text += '''
		{object_str}
		self.{title}.action = self.{title}_action
		'''.format(title=title, object_str=object_str)
		self.def_text += '''
	def {title}_action(self, sender):
		speech.say('{title}', 'en-US')
		pass
			'''.format(title=title)
		
	def insert_WebView(self, title, object_str):
		print 'WebView'
	
	def insert_TableView(self, title, object_str):
		print 'TableView'
			
		self.init_text += '''
		{object_str}
		self.{title}.data_source.items = ['Item1', 'Item2', 'Item3']
		self.{title}.data_source.tableview_cell_for_row = self.{title}_cell_for_row
		self.{title}.data_source.tableview_delete = self.{title}_delete
		self.{title}.delegate.tableview_did_select = self.{title}_did_select
		self.{title}.delegate.tableview_accessory_button_tapped = self.{title}_info_btn
		 
		'''.format(title=title, object_str=object_str)
		
		
		self.def_text += '''
	def {title}_cell_for_row(self, tableview, section, row):
		lst = tableview.data_source
		cell = ui.TableViewCell('subtitle')
		cell.detail_text_label.text_color = '#757575'
		cell.detail_text_label.text = 'Detail text here'
		selected_item = lst.items[row]
		cell.text_label.text = selected_item
		cell.accessory_type = 'detail_button'
		cell.image_view.image = ui.Image.named('emj:Cat_Face_Grinning')
		
		return cell
	
	def {title}_did_select(self, tableview, section, row):
		lst = tableview.data_source
		selected_item = lst.items[row]
		lst.selected_row = row
		if lst.action:
			lst.action(lst)
		speech.say(selected_item, 'en-US')
		
	def {title}_delete(self, tableview, section, row):
		lst = tableview.data_source
		selected_item = lst.items[row]
		del lst.items[row]
		speech.say(selected_item+' was deleted', 'en-US')
		
	def {title}_info_btn(self, tableview, section, row):
		import console
		lst = tableview.data_source
		selected_item = lst.items[row]
		console.hud_alert(selected_item)
		
			'''.format(title=title)
		
	def insert_DatePicker(self, title, object_str):
		print 'DatePicker'
	
	def insert_ScrollView(self, title, object_str):
		print 'ScrollView'
	
	def insert_TextView(self, title, object_str):
		print 'TextView'
	
	def insert_ImageView(self, title, object_str):
		print 'ImageView'	
	
######file picker#####
#quoted from https://gist.github.com/omz/e3433ebba20c92b63111
def file_picker(title=None, root_dir=None, multiple=False,
	select_dirs=False, file_pattern=None, show_size=True):
	#files = file_picker('Pick files', multiple=True, select_dirs=True, file_pattern=r'^.+$')
	import ui
	from objc_util import ObjCInstance, ObjCClass
	from operator import attrgetter
	import functools
	import ftplib,re
		
	class TreeNode (object):
		def __init__(self):
			self.expanded = False
			self.children = None
			self.leaf = True
			self.title = ''
			self.subtitle = ''
			self.icon_name = None
			self.level = 0
			self.enabled = True
			
		def expand_children(self):
			self.expanded = True
			self.children = []
			
		def collapse_children(self):
			self.expanded = False
			
		def __repr__(self):
			return '<TreeNode: "%s"%s>' % (self.title, ' (expanded)' if self.expanded else '')
			
	class FileTreeNode (TreeNode):
		def __init__(self, path, show_size=True, select_dirs=True,
		file_pattern=None):
			TreeNode.__init__(self)
			self.path = path
			self.title = os.path.split(path)[1]
			self.select_dirs = select_dirs
			self.file_pattern = file_pattern
			is_dir = os.path.isdir(path)
			self.leaf = not is_dir
			ext = os.path.splitext(path)[1].lower()
			if is_dir:
				self.icon_name = 'Folder'
			elif ext == '.py':
				self.icon_name = 'FilePY'
			elif ext == '.pyui':
				self.icon_name = 'FileUI'
			elif ext in ('.png', '.jpg', '.jpeg', '.gif'):
				self.icon_name = 'FileImage'
			else:
				self.icon_name = 'FileOther'
			self.show_size = show_size
			if not is_dir and show_size:
				self.subtitle = human_size((os.stat(self.path).st_size))
			if is_dir and not select_dirs:
				self.enabled = False
			elif not is_dir:
				filename = os.path.split(path)[1]
				self.enabled = not file_pattern or re.match(file_pattern, filename)
				
		@property
		def cmp_title(self):
			return self.title.lower()
			
		def expand_children(self):
			if self.children is not None:
				self.expanded = True
				return
			files = os.listdir(self.path)
			children = []
			for i,filename in enumerate(files):
				if filename.startswith('.'):
					continue
					
				full_path = os.path.join(self.path, filename)
				node = FileTreeNode(full_path, self.show_size, self.select_dirs, self.file_pattern)
				node.level = self.level + 1
				children.append(node)
				
			self.expanded = True
			self.children = sorted(children, key=attrgetter('leaf', 'cmp_title'))
			
	class TreeDialogController (object):
		def __init__(self, root_node, allow_multi=False, async_mode=False):
			self.async_mode = async_mode
			self.allow_multi = allow_multi
			self.selected_entries = None
			self.table_view = ui.TableView()
			self.table_view.frame = (0, 0, 500, 500)
			self.table_view.data_source = self
			self.table_view.delegate = self
			self.table_view.flex = 'WH'
			self.table_view.allows_multiple_selection = True
			self.table_view.tint_color = 'gray'
			self.view = ui.View(frame=self.table_view.frame)
			self.view.add_subview(self.table_view)
			self.view.name = root_node.title
			self.busy_view = ui.View(frame=self.view.bounds, flex='WH', background_color=(0, 0, 0, 0.35))
			hud = ui.View(frame=(self.view.center.x - 50, self.view.center.y - 50, 100, 100))
			hud.background_color = (0, 0, 0, 0.7)
			hud.corner_radius = 8.0
			hud.flex = 'TLRB'
			spinner = ui.ActivityIndicator()
			spinner.style = ui.ACTIVITY_INDICATOR_STYLE_WHITE_LARGE
			spinner.center = (50, 50)
			spinner.start_animating()
			hud.add_subview(spinner)
			self.busy_view.add_subview(hud)
			self.busy_view.alpha = 0.0
			self.view.add_subview(self.busy_view)
			self.done_btn = ui.ButtonItem(title='Done', action=self.done_action)
			self.root_btn = ui.ButtonItem(title='Root', action=self.root_btn_action)
			self.mobile_btn = ui.ButtonItem(title='Mobile', action=self.mobile_btn_action)
			self.view.right_button_items = [self.mobile_btn, self.root_btn]
			if self.allow_multi:
				self.view.right_button_items = [self.done_btn, self.mobile_btn, self.root_btn]
			self.done_btn.enabled = False
			self.root_node = root_node
			self.entries = []
			self.flat_entries = []
			if self.async_mode:
				self.set_busy(True)
				t = threading.Thread(target=self.expand_root)
				t.start()
			else:
				self.expand_root()
				
		def expand_root(self):
			self.root_node.expand_children()
			self.set_busy(False)
			self.entries = self.root_node.children
			self.flat_entries = self.entries
			self.table_view.reload()
			
		def flatten_entries(self, entries, dest=None):
			if dest is None:
				dest = []
			for entry in entries:
				dest.append(entry)
				if not entry.leaf and entry.expanded:
					self.flatten_entries(entry.children, dest)
			return dest
			
		def rebuild_flat_entries(self):
			self.flat_entries = self.flatten_entries(self.entries)
			
		def tableview_number_of_rows(self, tv, section):
			return len(self.flat_entries)
			
		def tableview_cell_for_row(self, tv, section, row):
			cell = ui.TableViewCell()
			entry = self.flat_entries[row]
			level = entry.level - 1
			image_view = ui.ImageView(frame=(44 + 20*level, 5, 34, 34))
			label_x = 44+34+8+20*level
			label_w = cell.content_view.bounds.w - label_x - 8
			if entry.subtitle:
				label_frame = (label_x, 0, label_w, 26)
				sub_label = ui.Label(frame=(label_x, 26, label_w, 14))
				sub_label.font = ('<System>', 12)
				sub_label.text = entry.subtitle
				sub_label.text_color = '#999'
				cell.content_view.add_subview(sub_label)
			else:
				label_frame = (label_x, 0, label_w, 44)
			label = ui.Label(frame=label_frame)
			if entry.subtitle:
				label.font = ('<System>', 15)
			else:
				label.font = ('<System>', 18)
			label.text = entry.title
			label.flex = 'W'
			cell.content_view.add_subview(label)
			if entry.leaf and not entry.enabled:
				label.text_color = '#999'
			cell.content_view.add_subview(image_view)
			if not entry.leaf:
				has_children = entry.expanded
				btn = ui.Button(image=ui.Image.named('CollapseFolder' if has_children else 'ExpandFolder'))
				btn.frame = (20*level, 0, 44, 44)
				btn.action = self.expand_dir_action
				cell.content_view.add_subview(btn)
			if entry.icon_name:
				image_view.image = ui.Image.named(entry.icon_name)
			else:
				image_view.image = None
			cell.selectable = entry.enabled
			return cell
			
		def row_for_view(self, sender):
			'''Helper to find the row index for an 'expand' button'''
			cell = ObjCInstance(sender)
			while not cell.isKindOfClass_(ObjCClass('UITableViewCell')):
				cell = cell.superview()
			return ObjCInstance(self.table_view).indexPathForCell_(cell).row()
			
		def expand_dir_action(self, sender):
			'''Invoked by 'expand' button'''
			row = self.row_for_view(sender)
			entry = self.flat_entries[row]
			if entry.expanded:
				sender.image = ui.Image.named('ExpandFolder')
			else:
				sender.image = ui.Image.named('CollapseFolder')
			self.toggle_dir(row)
			self.update_done_btn()
			
		def toggle_dir(self, row):
			'''Expand or collapse a folder node'''
			entry = self.flat_entries[row]
			if entry.expanded:
				entry.collapse_children()
				old_len = len(self.flat_entries)
				self.rebuild_flat_entries()
				num_deleted = old_len - len(self.flat_entries)
				deleted_rows = range(row + 1, row + num_deleted + 1)
				self.table_view.delete_rows(deleted_rows)
			else:
				if self.async_mode:
					self.set_busy(True)
					expand = functools.partial(self.do_expand, entry, row)
					t = threading.Thread(target=expand)
					t.start()
				else:
					self.do_expand(entry, row)
					
		def do_expand(self, entry, row):
			'''Actual folder expansion (called on background thread if async_mode is enabled)'''
			entry.expand_children()
			self.set_busy(False)
			old_len = len(self.flat_entries)
			self.rebuild_flat_entries()
			num_inserted = len(self.flat_entries) - old_len
			inserted_rows = range(row + 1, row + num_inserted + 1)
			self.table_view.insert_rows(inserted_rows)
			
		def tableview_did_select(self, tv, section, row):
			self.update_done_btn()
			
		def tableview_did_deselect(self, tv, section, row):
			self.update_done_btn()
			
		def update_done_btn(self):
			'''Deactivate the done button when nothing is selected'''
			selected = [self.flat_entries[i[1]] for i in self.table_view.selected_rows if self.flat_entries[i[1]].enabled]
			if selected and not self.allow_multi:
				self.done_action(None)
			else:
				self.done_btn.enabled = len(selected) > 0
				
		def set_busy(self, flag):
			'''Show/hide spinner overlay'''
			def anim():
				self.busy_view.alpha = 1.0 if flag else 0.0
			ui.animate(anim)
			
		def done_action(self, sender):
			self.selected_entries = [self.flat_entries[i[1]] for i in self.table_view.selected_rows if self.flat_entries[i[1]].enabled]
			self.view.close()
		
		def root_btn_action(self, sender):
			root_node = FileTreeNode('/', True, True, r'^.+$')
			self.root_node = root_node
			self.expand_root()
		
		def mobile_btn_action(self, sender):
			root_node = FileTreeNode('/var/mobile', True, True, r'^.+$')
			self.root_node = root_node
			self.expand_root()
			
		
	
	
	if root_dir is None:
		root_dir = os.path.expanduser('~/Documents')
	if title is None:
		title = os.path.split(root_dir)[1]
	root_node = FileTreeNode(root_dir, show_size, select_dirs, file_pattern)
	root_node.title = title or ''
	picker = TreeDialogController(root_node, allow_multi=multiple)
	
	picker.view.present('sheet')
	picker.view.wait_modal()
	if picker.selected_entries is None:
		return None
	paths = [e.path for e in picker.selected_entries]
	if multiple:
		return paths
	else:
		return paths[0]

######file picker#####

def human_size(size_bytes, no_suffixs=False):
	'''Helper function for formatting human-readable file sizes'''
	if size_bytes == 1:
		return "1 byte"
	suffixes_table = [('bytes',0),('KB',0),('MB',1),('GB',2),('TB',2), ('PB',2)]
	num = float(size_bytes)
	for suffix, precision in suffixes_table:
		if num < 1024.0:
			break
		num /= 1024.0
	if precision == 0:
		formatted_size = "%d" % num
	else:
		formatted_size = str(round(num, ndigits=precision))
	if not no_suffixs:
		return "%s %s" % (formatted_size, suffix)
	else:
		return formatted_size


def to_abs_path(*value):
	import os
	abs_path = os.path.join(os.path.expanduser('~'),'Documents')
	for _value in value:
		abs_path = os.path.join(abs_path,_value)
	return abs_path

def add_custom_class(pyui_path, class_name):
	with open(pyui_path, 'r') as f:
		root_list = json.loads(f.read())
		root_view_dict = root_list[0]
		#print root_view_dict
		root_view_dict['attributes']['custom_class'] = class_name
		root_view_str = '[' + json.dumps(root_view_dict) + ']'
		
	with open(pyui_path, 'w') as f:
		f.write(root_view_str)
	

def main(pyui_path, extra_func_mode=False, remove_title_bar=False, remove_status_bar=False, class_name=False, main_view_name=False):
	global gui_helper
	
	if not pyui_path:
		exit()
	if os.path.exists(pyui_path):
		get_attrib_main(pyui_path, extra_func_mode, remove_title_bar, remove_status_bar, class_name, main_view_name) #making text
		to_path = os.path.dirname(pyui_path)+'/'+os.path.basename(pyui_path).replace('.pyui','')+'_GUI_Helper.py'
		
		with open(to_path,'w') as f:
			f.write(gui_helper.get_text())
		editor.open_file(to_path, True)
		console.hide_output()
	else:
		console.hud_alert('pyui not found')


def make_action(sender):
	global pyui_path
	if not pyui_path:
		pyui_path = file_picker('Select pyui file', multiple=False, select_dirs=False, file_pattern=r'^.+.pyui$')
		
	extra_func_mode = v['sw_extra'].value
	remove_title_bar = v['sw_remove_title_bar'].value
	remove_status_bar = v['sw_remove_status_bar'].value
	class_name = v['tf_class_name'].text
	main_view_name = v['tf_main_view_name'].text
	main(pyui_path, extra_func_mode, remove_title_bar, remove_status_bar, class_name, main_view_name)
	sender.superview.close()

data = '''\
QlpoOTFBWSZTWYit4gkABmtfgHUQcGd/9T+GHQq/79/6UAU+5rbDrOjmmwAHAkiTTSM00E
FGQPUNpGg8pppkGagA1NT0ZCaaZT0oAAAAaAAAAiSaiptJ4KaA0AA00DEaMmIAHNMTARpg
RhGAAAAJhGAikJpom1MjJKD1NABoaAAaHlNpqVTeDrC7IwiKelTUPb56zCcCUgopAKYU1q
ZKYExFCLEIxAMsjNBBDNEB8CgPVm1CDCQWREkDcREHBdfhyeAk3zj2V/v9Vkjk84ArUkPD
xy3mvc6i2ubf5sXJZsIwSt4KUrKIRCJVUAHThHBSbBIG52v8RxKU1N/CxAZsiScj7NLXke
kg+fR5d+yN9qL0xQ0T4dXVEKzA5vtUjaJI6UvX0pFHAQsxUSJGMIXLsIUri2iRCLYNKXhS
7JSlmGJC6ogsAdQTDtnP4ezBm6JhTCmFIib0SmKbTfC+6WAHl9+cyne38Jkxud8cMIBo0U
ZZ6VTUuOHLBx5xYQdnIRwXXYbcaRCIQxpc9TegaGnsUvQlAcCIQI/eI6fhDZnchqpOvovP
ZjXrz+PDJIbiNsF08UJqPojlGZnxr8k99YsTXngBjqoVPpGsfZBKJF6jBhw5pKAQFqhZfc
2o0ioz9d1lZDSntIGNuRlHHYgKT5QpLacyKVzxNc5RbmLrnhteWfKWA6QjYS2wns1wz2Yz
fTblTCWWjUM1dcB8WdwnC4gz4DUaMY34RWjVbDJnAxaeDZZTxRcEqnZKhmK2dZTK+u6VwE
tto8qllfGy+zWUtJ3k1ejdnKlmN8xhqtEWxlK5WSa8xkQnZqELE6djbGT5Qhog6QI6ETHo
GX2thmkQGQW4YSRLXzUnTwCG3HC69+ZH2mwOOtRScRBSp0REOS+K9OLBvzvrGt3diWpOXG
BlhLjQrbrn1jTBO4BLoFkgqIB5VxNGOddTE3tfMJkDWiNqcxIylUPUX5iUTxV60IVgCidF
rM41qUUVo4gPEBrAw+iTI5/EC9XPvSOzo4ebw3e+jcOMagHlFyAFh7jkNgfyJmk/Cmj644
W4vk4qFVSAxCwjUHQxCTweJ+gBMJ/gDliNiuxiA2WPYTFlhZSaMgtQNGoNsa+zjUk7LSPI
IEDzA8HGYRKCIUwxPWSB0Oiko94JL2VuFgdCq4htouR0hHAGyZ8TTyDtImL2DNUIWWRZd6
/8BrvqDCnf6g7HtI6AU905HJ8aDJ40Arzg5vRXPqkxGRrQMmAfcqvfZeM6neHLAXMIaLSv
dEUFTuXALVNIJTqvIGxIyO6p8K1BxWdlcjMHQJNC6uoauDLz+C/eEw3N7hDzC/W6pg5GxQ
wBp0gkdc0GMgGJRTmLYHfICRoIzndccHr3HCw7LmEgnxCtyo8AyXIHJe0ULyvi5YluhygG
xQ1FsG3N3NKqUqG0srxXnzBxPUUFxC8r7htEFX/hsHo0hhdQGR1KRTpkIsYQYxJIsSG6qY
9anBf4VLE5jo4kqpRy0QOfHLV4+z9es0JH/i7kinChIRFbxBI=
'''
import ui
import bz2
from base64 import b64decode
pyui = bz2.decompress(b64decode(data))
v = ui.load_view_str(pyui.decode('utf-8'))

v['bt_make'].action = make_action
v.present('sheet')

pyui_path = file_picker('Select pyui file', multiple=False, select_dirs=False, file_pattern=r'^.+.pyui$')
if pyui_path:
	class_name = os.path.splitext(os.path.basename(pyui_path))[0]
	with open(pyui_path) as in_file:
		r = json.load(in_file)
		attrib = r[0]
		main_view_name = attrib['attributes'].get('name', 'view')
	v['tf_class_name'].text = class_name
	v['tf_main_view_name'].text = main_view_name
