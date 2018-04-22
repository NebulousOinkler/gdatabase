#!/usr/bin/python
import cgi, cgitb; cgitb.enable()
print "Content-type: text/html\n\n"
print "<html><head><title>CGI</title>"
print "</head>"
print "<body>"
print "<p>Hello, World.</p>"
form = cgi.FieldStorage()
query = form['fname'].value
from web_classes import web_search
s = web_search()
result = s.search('deg_seq',query)
print "<style> b {color: rgb(176,0,0); text-decoration: none;} b:hover {text-decoration: underline;} </style>"
print "<pre>"
for r in result:
	print r.display()
print "</pre>"
print "</body>"
print "</html>"