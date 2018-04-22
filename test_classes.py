from classes import *
import json
t = 1969
bib = \
"""
@article{Sh:1,
author = {Shelah, Saharon},
ams-subject = {(02.50)},
journal = {Israel Journal of Mathematics},
review = {MR 40-7102},
pages = {187--202},
title = {{Stable theories}},
volume = {7},
year = {""" + str(t) +\
"""},
}
"""

biblist = [\
"""
@article{Sh:1,
author = {Shelah, Saharon},
ams-subject = {(02.50)},
journal = {Israel Journal of Mathematics},
review = {MR 40-7102},
pages = {187--202},
title = {{Stable theories}},
volume = {7},
year = {""" + str(t) +\
"""},
}
""" for t in range(100)]

contrib = 'Sharat Chandra'

name = 'Test Graph'
edges = [[1,2],[2,3],[3,4],[4,1],[5,1],[5,6],[5,7],[5,8]]
edges2 = [[2,1],[5,1],[1,3],[3,4],[4,2],[5,2],[5,6],[5,7],[5,9]]

working_entry = DBEntry(bib, '188', contrib, 8, edges, name=name)
working_entry2 = DBEntry(bib, '200',contrib,9,edges2, name=name)

gdb = GraphDatabase('gdatabase.db')
gdb.add_entry(working_entry2)
print(gdb.search('deg_seq','4')[0].dbref.bib.entries)
#for bibe in biblist:
#	gdb.add_entry(DBEntry(bibe, contrib,9,edges2, name=name))
gdb.close()