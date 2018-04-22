#!/usr/bin/python
import cgi, cgitb; cgitb.enable()
print "Content-type: text/html\n\n"
print \
"""
<html>
<head>
<title>Graphlopedia Demo Python 2.6</title>
</head>
<body>
<h1>Graphlopedia</h1>
<h2>A Searchable Online Database of Graphs</h2>
<h3>SITE STILL IN PROGRESS</h3>
<form name="form" method="POST" action="form.cgi">
  <p>
	<input type="radio" name="qtype" id="deg_seq" value="deg_seq" checked/> By Degree Sequence
	<input type="radio" name="qtype" id="graph" value="graph"/> By Graph ID
	<input type="radio" name="qtype" id="ref" value="ref"/> By Citation
  </p>
  <input type="text" name="query" size=60 id="input" placeholder="4,3,2..."/>
  <input type="submit" name="submit" value="Submit" />
</form>
<script>
	var deg_seq = document.getElementById("deg_seq")
	var graph = document.getElementById("graph")
	var ref = document.getElementById("ref")
	var input = document.getElementById("input")

	deg_seq.onclick = function(){
		input.placeholder = "4,3,2..."
	}
	graph.onclick = function(){
		input.placeholder = "G000001"
	}
	ref.onclick = function(){
		input.placeholder = "Stanley, Combinatorics"
	}
</script>
"""
print "</head>"
print "<body>"
print "<p>Hello, World.</p>"
form = cgi.FieldStorage()
query = form['query'].value
qtype = form['qtype'].value
from web_classes import web_search
s = web_search()
result = s.search(qtype,query)
print "<style> b {color: rgb(0,176,0); text-decoration: none;} b:hover {text-decoration: underline;} </style>"
print "<pre>"
for r in result:
	print r.display()
print "</pre>"
print "</body>"
print "</html>"