from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
from pymongo import MongoClient
from time import sleep
import webbrowser
from tkHyperlinkManager import HyperlinkManager
from toolTip import *
from functools import partial

class Window(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.master = master
		self.init_window()
		messagebox.showwarning("Info", "Select Database --> Select Table --> Click any Item To display tool panel :).") 

	def init_window(self):
		self.master.title('MongoDB API')
		self.master.geometry('810x500')
		# self.master.resizable(width=False, height=False)
		self._connect()

	def _connect(self):
		self.client = MongoClient('localhost', 27017)
	
		frame = Frame(self.master, width=150, height=200, bg='#aaaaff')
		frame.grid(row=0, column=0, sticky='w', padx=4, pady=4)
		frame.grid_propagate(False)

		Label(frame, text='DataBases', font=('Coureil', 13)).pack(padx=5, pady=5)
		self.dbs_list = Listbox(frame, height=9, width=20)
		self.dbs_list.pack(padx=5, pady=5)
		self.dbs_list.bind('<<ListboxSelect>>', self._tables)
		for db in self.client.list_database_names():
			self.dbs_list.insert(END, db)
		
	def _tables(self, evt):
		w = evt.widget
		index = w.curselection()
		if len(index)>0:
			value = w.get(int(index[0]))
			self.db = self.client[value]

			frame = Frame(self.master, width=150, height=200, bg='#FF5733')
			frame.grid(row=1, column=0, sticky='w', padx=4, pady=4)
			frame.grid_propagate(False)
			Label(frame, text='Collections', font=('Coureil', 13)).pack(padx=5, pady=5)
			self.cols_list = Listbox(frame, height=9, width=20)
			self.cols_list.pack(padx=5, pady=5)
			self.cols_list.bind('<<ListboxSelect>>', self._content)
			for col in self.db.list_collection_names():
				self.cols_list.insert(END, col)
			
	
	def _content(self, var):
		self.selected_col_event = var
		def selectItem(a):
			curItm = self.ctree.focus()
			win = Toplevel(width=300, height=400)
			win.wm_title("selected Item")
			win.resizable(width=False, height=False)
			textFrame = ScrolledText(win, width=100, relief="raised")
			textFrame.pack(fill='both', pady=5, padx=5)
			text = ''
			for k, it in zip(keys, self.ctree.item(curItm).get('values')):
				text += k+' : \n'+'-'*(len(list(k))+2)+'\n'+ it+'\n'+'---'*33+'\n\n'
			textFrame.insert(INSERT, text)

		wid = var.widget
		if len(wid.curselection())>0:
			col_v = wid.get(int(wid.curselection()[0]))
			self.col = self.db[col_v]
			all_items = list(self.col.find())
			frame = Frame(self.master, width=650, height=200)
			frame.grid(row=0, column=1, rowspan=2, sticky='wens', padx=4, pady=4)
			frame.grid_propagate(False)
			
			keys = tuple(k for k in self.col.find_one())

			style = ttk.Style()
			style.configure("mystyle.Treeview.Heading", font=('Calibri', 13,'bold')) # Modify the font of the headings
			self.ctree = ttk.Treeview(frame, height=17, style="mystyle.Treeview")
			self.ctree["columns"] = keys
			self.ctree.column("#0", width=40, minwidth=40, stretch=NO)
			for k in keys:
				self.ctree.column(k, width=575//len(keys), minwidth=100)
				self.ctree.heading(k, text=k)
			self.ctree.grid(row=0, column=1, padx=5, pady=5)
			self.ctree.bind('<Double-1>', selectItem)
			self.ctree.bind('<ButtonRelease-1>', self._actions)
			# Constructing vertical scrollbar 
			# with treeview 
			verscrlbar = ttk.Scrollbar(frame, orient ="vertical", command = self.ctree.yview)
			verscrlbar.grid(row=0, column=0, padx=5, pady=5, sticky=NS)

			horscrlbar = ttk.Scrollbar(frame, orient ="horizontal", command = self.ctree.xview)
			horscrlbar.grid(row=1, column=1, padx=5, pady=5, sticky=EW) 

			self.ctree.configure(yscrollcommand = verscrlbar.set, xscrollcommand = horscrlbar.set)

			for i, it in enumerate(all_items):
				bcolor = ('odd',) if i%2!=0 else ('even',)
				self.ctree.insert("", 'end', text =str(i), values=tuple(it.values()), tags=bcolor)

			self.ctree.tag_configure('odd', background='red')
			self.ctree.tag_configure('even', background='blue')
	
	def _dataFrame(self, keys, data=None):
		def _confirm():
			res = {}
			i = 0
			for k, entry in zip(keys, entrys):
				if i in txt_idx:
					res[k] = entry.get('1.0', END)
				else:
					res[k] = entry.get()
			if title=='insert':
				try:
					self.col.insert_one(res)
				except Exception as e:
					if hasattr(e, 'message'):
						msg = e.message
					else:
						msg = e
					messagebox.showerror("Error", msg)
			else:
				try:
					self.col.update_one({'_id':data[keys.index('_id')]} , {"$set":res})
				except Exception as e:
					if hasattr(e, 'message'):
						msg = e.message
					else:
						msg = e
					messagebox.showerror("Error", msg)
			sleep(0.3)
			self._content(self.selected_col_event)
			win.destroy()
			win.update()

		if data is  None:
			data = ['']*len(keys)
			title = 'insert'
		else:
			title = 'update'

		win = Toplevel()
		win.wm_title(title)
		# win.resizable(width=False, height=False)
		win.grid_propagate(False)
		win.grid_columnconfigure(0, weight=1)
		win.grid_rowconfigure(0, weight=1)
		 
		if max([len(x) for x in data])>100:
			canvas = Canvas(win, width=660, height=500)
		else:
			canvas = Canvas(win)

		win.resizable(width=False, height=True)
		scroll_y = Scrollbar(win, orient="vertical", command=canvas.yview)

		frame = Frame(canvas)
		Label(frame, text=title.upper()).grid(row=0, column=0, columnspan=2, padx=4, pady=4)
		r = 1
		entrys = []
		txt_idx = []
		for k, d in zip(keys, data):
			Label(frame, text=k, font=(13)).grid(row=r, column=0, pady=4, padx=4)
			if len(d)<100:
				entry_i = Entry(frame, width=70)
			else:
				entry_i = ScrolledText(frame, wrap=WORD, width=70)
				txt_idx.append(k-1)
			entry_i.insert(END, d)
			entry_i.grid(row=r, column=1, pady=4, padx=4, sticky=EW)
			if k=='_id' and title=='update':
				entry_i.config(state=DISABLED)
			entrys.append(entry_i)
			r+=1

		c_img = PhotoImage(file="./images/confirm.png")
		confirm_btn = Button(frame, width=140, height=70, text='CONFIRM', 
							image=c_img, command=_confirm)
		confirm_btn.image=c_img
		confirm_btn.grid(row=r, column=0, columnspan=2, padx=4, pady=4)

		# put the frame in the canvas
		canvas.create_window(0, 0, anchor='nw', window=frame)
		# make sure everything is displayed before configuring the scrollregion
		canvas.update_idletasks()
		canvas.configure(scrollregion=canvas.bbox('all'), 
		                 yscrollcommand=scroll_y.set)
		canvas.pack(fill='both', expand=True, side='left', padx=5, pady=5)
		scroll_y.pack(fill='y', side='right', padx=5, pady=5)


	def _actions(self, event):
		def _remove_item():
			curItem = self.ctree.focus()
			_id = list(self.ctree.item(curItem).get('values'))[self.ctree['column'].index('_id')]
			query = {'_id':_id}
			MsgBox = messagebox.askquestion ('Remove Item','Are you sure you want to remove this item', icon='warning')
			if MsgBox == 'yes':
				self.col.delete_one(query)
				self._content(self.selected_col_event)

		def _update_item():
			curItem = self.ctree.focus()
			self._dataFrame(self.ctree['column'], list(self.ctree.item(curItem).get('values')))

		def _insert_item():
			self._dataFrame(self.ctree['column'])

		def _find():
			messagebox.showwarning("warning", "This method will only work for BBCNews database !" ) 
			def _search():
				scrollT.delete(1.0,END)
				matches = entry.get().lower().split(' ')
				res = ''
				for item in self.col.find():
					if any(x in [t.lower() for t in item['tags']] for x in matches) or any(x in item['header'].lower() for x in matches) or any(x in item['summary'].lower() for x in matches) or any(x in item['title'].lower() for x in matches):
						res += 'id : '+str(item['_id'])+'\n'+'title : '+str(item['title'])+'\n'+'summary : '+str(item['summary'])+'\n'+'URL : '+str(item['url'])+'\n'+'---'*35+'\n'
				if res == '':
					res = "There's no result found !"
				scrollT.insert(END, res)

			win = Toplevel(width=500, height=450)
			win.wm_title('Search')
			win.grid_propagate(False)
			win.grid_columnconfigure(0, weight=1)
			win.grid_rowconfigure(0, weight=1)

			entry =  Entry(win, width=70)
			entry.grid(row=0, column=0, pady=4, padx=4, sticky=EW)

			search = Button(win, text='Search', command=_search, width=20)
			search.grid(row=0, column=1, padx=4, pady=4)

			scrollT = ScrolledText(win)
			scrollT.grid(row=1, column=0, columnspan=2, padx=4, pady=4)

		def _info():
			win = Toplevel(width=500, height=550)
			win.resizable(width=False, height=False)
			win.wm_title('Search')
			win.grid_propagate(False)
			win.grid_columnconfigure(0, weight=1)
			win.grid_rowconfigure(0, weight=1)

			text = Text(win, width=300, height=250, wrap=WORD)
			text.grid(pady=4, padx=4)
			text.insert(END, 'hello here instructions of using the app: \n\n\nSHOW ITEM : double clic on it \n\n\nDELETE ITEM : select item you want to delete then hit the delete button \n\n\nINSERT ITEM : click the Insert button entre the information and click Confirm button to insert (hit the table agin to see the updated collection) \n\n\nUPDATE ITEM : select the item you want to update then hit the update button, Confirm to send the update \n\n\n\nthanks have a good day for more information about me please check my Portfilio in ')
			hyperlink = HyperlinkManager(text)
			text.insert(INSERT, "https://www.bousseta.ml",
			            hyperlink.add(partial(webbrowser.open, "https://www.bousseta.ml/")))
			text.insert(INSERT, "\n\n And here's my LinkedIn profile : \n")
			text.insert(INSERT, "https://www.linkedin.com/in/walid-bousseta/",
			            hyperlink.add(partial(webbrowser.open, "https://www.linkedin.com/in/walid-bousseta/")))


		fframe = Frame(self.master, width=200, height=80, bg='#33FF7D')
		fframe.grid(row=2, column=0, columnspan=2, sticky='wens', padx=4, pady=4)
		fframe.grid_propagate(False)
		fframe.grid_columnconfigure(0, weight=1)
		fframe.grid_rowconfigure(0, weight=1)

		h_img = PhotoImage(file="./images/info.png")
		help_btn = Button(fframe, width=140, height=70, text='INFO',
						 image=h_img, command=_info)
		help_btn.image=h_img
		help_btn.grid(row=0, column=0, padx=4, pady=4)
		CreateToolTip(help_btn, text='Help')

		i_img = PhotoImage(file="./images/insert.png")
		insert_btn = Button(fframe, width=140, height=70, text='INSERT', 
							image=i_img, command=_insert_item)
		insert_btn.image = i_img
		insert_btn.grid(row=0, column=1, padx=4, pady=4)
		CreateToolTip(insert_btn, text='Insert new Item')

		u_img = PhotoImage(file="./images/update.png")
		update_btn = Button(fframe, width=140, height=70, text='UPDATE', 
							image=u_img, command=_update_item)
		update_btn.image=u_img
		update_btn.grid(row=0, column=2, padx=4, pady=4)
		CreateToolTip(update_btn, text='Update an Item')

		d_img = PhotoImage(file="./images/delete.png")
		delete_btn = Button(fframe, width=140, height=70, text='DELETE', 
							image=d_img, command=_remove_item)
		delete_btn.image = d_img
		delete_btn.grid(row=0, column=3, padx=4, pady=4)
		CreateToolTip(delete_btn, text='Delete a selection')

		f_img = PhotoImage(file="./images/find.png")
		find_btn = Button(fframe, width=140, height=70, text='FIND', 
						image=f_img, command=_find)
		find_btn.image=f_img
		find_btn.grid(row=0, column=4, padx=4, pady=4)
		CreateToolTip(find_btn, text='Find')	


root = Tk()
app = Window(root)
root.mainloop()
