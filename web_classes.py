import sqlite3
import json
class web_search:
	def __init__(self):
		self.conn = sqlite3.connect('gdatabase.db')
		self.c = self.conn.cursor()

	def search(self,qtype, arg):
		if qtype == 'deg_seq':
			like = "'" + arg + "%'"
			raw_entries = self.c.execute("""SELECT Graphs.gid, GROUP_CONCAT(Refs.bib,'||') AS bib_data, GROUP_CONCAT(GraphRefDetails.contrib, '||') AS contrib_data, Graphs.vert, Graphs.edges, Graphs.name, Graphs.deg_seq FROM GraphRefDetails 
			INNER JOIN Graphs ON GraphRefDetails.gid = Graphs.gid 
			INNER JOIN Refs ON GraphRefDetails.rid = Refs.rid 
			WHERE deg_seq LIKE"""+ like + """GROUP BY Graphs.gid""").fetchall()
			
			result = self.structure(raw_entries)

		return result

	def structure(self, raw_entries):
		r = [web_entry(e) for e in raw_entries]
		return r

class web_entry:
	def __init__(self, raw_entries):
		self.gid, bib_data, contrib_data, self.vert, self.edges, self.name, self.deg_seq = raw_entries
		
		bib = bib_data.split('||')
		self.contrib = ', '.join(set(contrib_data.split('||')))
		self.refs = map(json.loads,bib)

	def display(self):
		h = html()
		gid = h.b("ID:")+ "               " + str(self.gid) + "\n"
		name = h.b("Name:") + "             " + str(self.name)+ "\n"
		verts = h.b("Vertices:")+ "         " + str(self.vert)+ "\n"
		degseq = h.b("Degree Sequence:") + "  " + str(self.deg_seq)+ "\n"
		edges = h.b("Edge List:")+ "        " + str(self.edges)+ "\n"
		references = self._refparse(self.refs)
		contrib = h.b("Contributors:") + "     " + self.contrib + "\n"
			
		txt = gid + name + verts + degseq + edges + references + contrib
		return txt
	
	def _refparse(self,reflist):
		h = html()
		strlist = []
		for b in reflist:
			strlist.append(' '*18 + b['author'] + ', ' + b['title'] + ', ' + b['journal'] + ' (' + str(b['year']) + ')')
		strlist.sort()
		refstring = '\n'.join(strlist)
		references = h.b("References:") + refstring[11:] + "\n"
		return references

class html:
	def __init__(self):
		pass

	def h1(self, arg):
		return "<h1>"+str(arg)+"</h1>"

	def p(self, arg):
		return "<p>"+str(arg)+"</p>"

	def h2(self, arg):
		return "<h2>"+str(arg)+"</h2>"
	
	def h3(self,arg):
		return "<h3>"+str(arg)+"</h3>"
		
	def b(self,arg):
		return "<b>"+str(arg)+"</b>"