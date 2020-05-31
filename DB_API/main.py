from tkinter import *
from tkinter import ttk
from pymongo import MongoClient

class Window(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.master = master
		self.init_window()

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
		wid = var.widget
		if len(wid.curselection())>0:
			col_v = wid.get(int(wid.curselection()[0]))
			self.col = self.db[col_v]
			all_items = list(self.col.find())
			frame = Frame(self.master, width=650, height=200)
			frame.grid(row=0, column=1, rowspan=2, sticky='wens', padx=4, pady=4)
			frame.grid_propagate(False)
			
			keys = tuple(k for k in self.col.find_one())
			tree = ttk.Treeview(frame, style="Foo2.Treeview", height=17)
			tree["columns"] = keys
			tree.column("#0", width=20, minwidth=20, stretch=NO)
			for k in keys:
				tree.column(k, width=700//len(keys), minwidth=100)
				tree.heading(k, text=k)
			tree.grid(row=0, column=1, padx=5, pady=5)

			# Constructing vertical scrollbar 
			# with treeview 
			verscrlbar = ttk.Scrollbar(frame, orient ="vertical", command = tree.yview)
			verscrlbar.grid(row=0, column=0, padx=5, pady=5, sticky=NS)

			horscrlbar = ttk.Scrollbar(frame, orient ="horizontal", command = tree.xview)
			horscrlbar.grid(row=1, column=1, padx=5, pady=5, sticky=EW) 

			tree.configure(yscrollcommand = verscrlbar.set, xscrollcommand = horscrlbar.set)

			for i, it in enumerate(all_items):
				tree.insert("", 'end', text ="L"+str(i), values=tuple(it.values())) 
			
			


root = Tk()
app = Window(root)
root.mainloop()
