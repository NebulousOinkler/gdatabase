import networkx as nx
from networkx.classes.graph import Graph
import matplotlib.pyplot as plt
import bibtexparser as btx
from bibtexparser.bparser import BibTexParser
import sqlite3
import json

class DBGraph(Graph):
	def __init__(self, data=None, **attr):
		super().__init__(*data,**attr)

	def __eq__(self, other):
		return nx.is_isomorphic(self, other)

	def draw(self):
		plt.close()
		nx.spring_layout(self)
		nx.draw(self)
		plt.savefig(self.gid + ".png")

	def deg_seq(self):
		return ','.join(sorted((str(value) for node, value in nx.degree(self)), reverse=True))

def easy_graph(graph_description, **kwargs):
	create_using = kwargs.get("create_using", None)
	G = nx.make_small_graph(graph_description, create_using = create_using)
	G.__class__ = DBGraph
	G.name = graph_description[1]
	return G

class DBRef:
	def __init__(self, bib):
		parser = BibTexParser()
		self.bib = parser.parse(bib)
		if not self.bib.entries:
			self.bib.entries = [json.loads(bib)]
		self.bib.entries[0].pop('pages',None)

		self.title = self.bib.entries[0]['title']
		self.author = self.bib.entries[0]['author']
		self.year = self.bib.entries[0]['year']

		self.snippet = (self.title, self.author, self.year)

	def __eq__(self,other):
		return self.snippet == other.snippet

class DBEntry:
	def __init__(self, bib, contrib, num_vert, edges, name='', **kwargs):
		graph_description = ['edgelist', name, num_vert, edges]
		self.dbgraph = easy_graph(graph_description, **kwargs)
		self.dbref = DBRef(bib)

		#parser = BibTexParser()
		# self.links = set()
		# for link in kwargs.get('links',[]):
		# 	t = parser.parse(link) 
		# 	self.links.add(t)
		self.comments = kwargs.get('comments',None)
		self.image = kwargs.get('image',None)
		self.pages = kwargs.get('pages',None)
		self.contrib = contrib

class encoder:
	def encode_edge_list(edges):
		return ','.join(['-'.join(map(str,e)) for e in edges])

	def encode_bib(bib, fmt='bibtex'):
		if fmt == 'json':
			return json.dumps(bib.entries[0])
		return btx.dumps(bib)

class decoder:
	def decode_graph(enc_graph):
		gid, deg_seq, name, vert, edges_str = enc_graph
		edges = decoder.decode_edges_str(edges_str)
		graph_description = ['edgelist', name, vert, edges]
		result = easy_graph(graph_description)
		result.gid = gid
		return result

	def decode_edges_str(edges_str):
		t = edges_str.split(',')
		result = [[int(v)+1 for v in e.split('-')] for e in t]
		return result

	def decode_ref(enc_ref):
		rid, bib = enc_ref
		result = DBRef(bib)
		result.rid = rid
		return result


class GraphDatabase:
	def __init__(self, file):
		self.conn = sqlite3.connect(file)
		self.cursor = self.conn.cursor()
		with self.conn:
			self.cursor.execute("""CREATE TABLE IF NOT EXISTS Graphs (
				gid integer,
				deg_seq text,
				name text,
				vert integer,
				edges text
				)""")
			self.cursor.execute("""CREATE TABLE IF NOT EXISTS Refs (
				rid integer,
				bib text
				)""")
			self.cursor.execute("""CREATE TABLE IF NOT EXISTS GraphRefDetails (
				rid integer,
				gid integer,
				pages text,
				image text,
				comments text,
				contrib text
				)""")
			self.cursor.execute("""CREATE TABLE IF NOT EXISTS max_ids (
				max_rid integer,
				max_gid integer
				)""")

		max_ids = self.cursor.execute("SELECT * FROM max_ids").fetchone()
		if not max_ids:
			self.max_rid = 0
			self.max_gid = 0
			with self.conn:
				self.cursor.execute("INSERT INTO max_ids VALUES (0,0)")
		else:
			self.max_rid, self.max_gid = max_ids
			#print("AAAAAAAAAAAAAA", max_ids)



	def add_entry(self, entry):
#Needs fixing to be more efficient. Check refs after finding graph to make sure it's not already there
		ref_result = self.fetch('ref', entry.dbref)
		#print('BBBBBBBBB', ref_result)
		if not ref_result:
			sbib = encoder.encode_bib(entry.dbref.bib, fmt='json')
			self.max_rid += 1
			rid = self.max_rid
			entry.dbref.rid = rid
			with self.conn:
				self.cursor.execute("INSERT INTO Refs VALUES (:rid, :bib)", {"rid": rid, "bib": sbib})
			self._update_max_ids()
		else:
			rid = ref_result.rid

		graph_result = self.fetch('graph', entry.dbgraph)
		#print('CCCCCCCCC', graph_result)
		if not graph_result:
			sedges = encoder.encode_edge_list(entry.dbgraph.edges)
			self.max_gid += 1
			gid = self.max_gid
			entry.dbgraph.gid = gid
			with self.conn:
				self.cursor.execute("INSERT INTO Graphs VALUES (:gid, :deg_seq, :name, :vert, :edges)", {"gid": gid, "deg_seq": entry.dbgraph.deg_seq() , "name": entry.dbgraph.name, "vert": len(entry.dbgraph), "edges": sedges})
			self._update_max_ids()
		else:
			gid = graph_result.gid

		entry_exists = self.fetch('entry', (gid, rid))
		#print('DDDDDDDDDDDD', entry_exists)
		if not entry_exists:
			with self.conn:
				self.cursor.execute("INSERT INTO GraphRefDetails VALUES (:rid, :gid, :pages, :image, :comments, :contrib)",{"gid": gid, "rid": rid, "pages": entry.pages, "image": entry.image, "comments": entry.comments, "contrib": entry.contrib})
		else:
			print('ENTRY ALREADY EXISTS')

			

	def fetch(self, qtype, arg):
		if qtype == 'graph':
			graph = arg
			potentials = self.fetch('graph_deg_seq', graph.deg_seq())
			for dgraph in potentials:
				if dgraph == graph:
					return dgraph

		if qtype == 'ref':
			ref = arg
			raw_vals = self.cursor.execute("SELECT * FROM Refs").fetchall()
			potentials = [_ for _ in map(decoder.decode_ref, raw_vals)]
			for dref in potentials:
				if dref == ref:
					return dref

		if qtype == 'graph_deg_seq':
			deg_seq = arg
			raw_vals = self.cursor.execute("SELECT * FROM Graphs WHERE deg_seq=:deg",{'deg': deg_seq}).fetchall()
			potentials = [_ for _ in map(decoder.decode_graph, raw_vals)]
			return potentials

		if qtype == 'entry':
			gid, rid = arg
			result = self.cursor.execute("SELECT * FROM GraphRefDetails WHERE gid=:gid AND rid=:rid",{'gid': gid, 'rid': rid}).fetchone()
			return result

		return None

	def search(self, qtype, arg):
		if qtype == 'deg_seq':
			like = "'" + arg + "%" +"'"
			raw_entries = self.cursor.execute("""SELECT Refs.bib, GraphRefDetails.contrib, Graphs.vert, Graphs.edges, Graphs.name FROM GraphRefDetails 
											INNER JOIN Graphs ON GraphRefDetails.gid = Graphs.gid 
											INNER JOIN Refs ON GraphRefDetails.rid = Refs.rid 
											WHERE deg_seq LIKE"""+' '+like).fetchall()
			entries = [DBEntry(e[0],e[1],e[2],decoder.decode_edges_str(e[3]), name=e[4]) for e in raw_entries]

			return entries

	def _update_max_ids(self):
		with self.conn:
			t = self.cursor.execute("SELECT * FROM max_ids").fetchall()
			#print(t)
			self.cursor.execute("UPDATE max_ids SET max_rid = :max_rid, max_gid = :max_gid WHERE rowid=1", {'max_rid': self.max_rid, 'max_gid': self.max_gid})

	def close(self):
		self.conn.close()





