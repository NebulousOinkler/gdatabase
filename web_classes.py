import sqlite3
class web_search:
	def __init__(self):
		self.conn = sqlite3.connect('gdatabase.db')
		self.c = self.conn.cursor()

	def search(self,qtype, arg):
		if qtype == 'deg_seq':
			like = "'" + arg + "%'"
			raw_entries = self.c.execute("""SELECT Refs.bib, GraphRefDetails.contrib, Graphs.vert, Graphs.edges, Graphs.name, Graphs.deg_seq FROM GraphRefDetails 
			INNER JOIN Graphs ON GraphRefDetails.gid = Graphs.gid 
			INNER JOIN Refs ON GraphRefDetails.rid = Refs.rid 
			WHERE deg_seq LIKE"""+ like).fetchall()
			
			result = self.structure(raw_entries)

		return result

	def structure(self, raw_entries):
		r = [web_entry(e) for e in raw_entries]
		return r

class web_entry:
	def __init__(self, raw_entries):
		r = raw_entries
		self.bib, self.contrib, self.vert, self.edges, self.name, self.deg_seq = raw_entries

	def display(self):
		pass
