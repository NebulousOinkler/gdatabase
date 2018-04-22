import sqlite3
import json
class web_search:
	def __init__(self):
		self.conn = sqlite3.connect('gdatabase.db')
		self.c = self.conn.cursor()

	def search(self,qtype, arg):
		result = []
		select = """SELECT Graphs.gid, GROUP_CONCAT(Refs.bib,'||') AS bib_data, GROUP_CONCAT(GraphRefDetails.contrib, '||') AS contrib_data, Graphs.vert, Graphs.edges, Graphs.name, Graphs.deg_seq, GROUP_CONCAT(GraphRefDetails.pages, '||'), GROUP_CONCAT(GraphRefDetails.image, '||'), GROUP_CONCAT(GraphRefDetails.comments, '||') FROM GraphRefDetails 
			INNER JOIN Graphs ON GraphRefDetails.gid = Graphs.gid 
			INNER JOIN Refs ON GraphRefDetails.rid = Refs.rid """

		if qtype == 'deg_seq':
			like = "'" + arg + "%' "
			raw_entries = self.c.execute( select + """WHERE Graphs.deg_seq LIKE"""+ like + """GROUP BY Graphs.gid""")
			result = self.structure(raw_entries)
			
		if qtype == 'graph':
			gid = "'" + str(int(arg[1:])) + "' "
			raw_entries = self.c.execute( select + """WHERE GraphRefDetails.gid="""+ gid + """GROUP BY Graphs.gid""")
			result = self.structure(raw_entries)
		
		if qtype == 'ref':
			#Not Yet Implemented
			#raw_entries = self.c.execute( select + """WHERE Refs.bib LIKE"""+ arg + """GROUP BY Graphs.gid""")
			#result = self.structure(raw_entries)
			pass

		return result

	def structure(self, raw_entries):
		r = [web_entry(e) for e in raw_entries]
		return r

class web_entry:
	def __init__(self, raw_entries):
		self.gid, bib_data, contrib_data, self.vert, self.edges, self.name, self.deg_seq, pages_data, image_data, comment_data = raw_entries
		
		bib = bib_data.split('||')
		self.pages = pages_data.split('||')
		self.contrib = ', '.join(set(contrib_data.split('||')))
		
		if image_data:
			self.images = image_data.split('||')
		else:
			self.images = ['']
		
		if comment_data:
			self.comments = comment_data.split('||')
		else:
			self.comments = ['']
		
		self.refs = zip(map(json.loads,bib),self.pages)

	def display(self):
		h = html()
		labeled_gid = 'G' + '0'*(6-len(str(self.gid))) + str(self.gid)
		gid = h.b("ID:")+ "               " + labeled_gid + "\n"
		name = h.b("Name:") + "             " + str(self.name)+ "\n"
		verts = h.b("Vertices:")+ "         " + str(self.vert)+ "\n"
		degseq = h.b("Degree Sequence:") + "  " + str(self.deg_seq)+ "\n"
		edges = h.b("Edge List:")+ "        " + str(self.edges)+ "\n"
		references = self._refparse(self.refs)
		contrib = h.b("Contributors:") + "     " + self.contrib + "\n"
			
		txt = gid + name + verts + degseq + edges + references + contrib
		return txt
		
	def full_display(self):
	#Has Comments, large generated image, and Each Reference should have it's own image
		h = html()
		labeled_gid = 'G' + '0'*(6-len(str(self.gid))) + str(self.gid)
		gid = h.b("ID:")+ "               " + labeled_gid + "\n"
		name = h.b("Name:") + "             " + str(self.name)+ "\n"
		verts = h.b("Vertices:")+ "         " + str(self.vert)+ "\n"
		degseq = h.b("Degree Sequence:") + "  " + str(self.deg_seq)+ "\n"
		edges = h.b("Edge List:")+ "        " + str(self.edges)+ "\n"
		references = self._refparse(self.refs)
		comments = self._commentparse(self.comments)
		contrib = h.b("Contributors:") + "     " + self.contrib + "\n"
			
		txt = gid + name + verts + degseq + edges + references + comments + contrib
		return txt

	def _commentparse(self, commentlist):
		h = html()
		strlist = []
		for c in commentlist:
			strlist.append(' '*18 + c)
		commentstr = '\n'.join(strlist)
		comments = h.b("Comments:") + commentstr[9:] + "\n"
		return comments
		
	def _refparse(self,reflist):
		h = html()
		strlist = []
		for b, page in reflist:
			strlist.append(' '*18 + b['author'] + ', ' + b['title'] + ', ' + b['journal'] + ' (' + str(b['year']) + ')' + ', p.'+page)
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