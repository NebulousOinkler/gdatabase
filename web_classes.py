import sqlite3

class web_search:
	def __init__(self):
		self.conn = sqlite3.connect('gdatabase.db')
		self.c = conn.cursor()

	def search(qtype, arg):
		if qtype == 'deg_seq':
			raw_entries = self.c.execute("""SELECT Refs.bib, GraphRefDetails.contrib, Graphs.vert, Graphs.edges, Graphs.name FROM GraphRefDetails 
			INNER JOIN Graphs ON GraphRefDetails.gid = Graphs.gid 
			INNER JOIN Refs ON GraphRefDetails.rid = Refs.rid 
			WHERE deg_seq LIKE (?)%""",(arg,)).fetchall()

			result = self.structure(raw_entries)

			return result

	def structure(self, raw_entries):
		return web_entry(raw_entries)

class web_entry:
	def __init__(self, raw_entries):
		r = raw_entries
		self.bib, self.contrib, self.vert, self.edges, self.name = raw_entries