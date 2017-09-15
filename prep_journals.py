import xml.etree.ElementTree as ET
import sys
import io
import copy
import re
import pandas as pd
import xlrd

journal_syns={}
impact_factors={}
journal_dict={}
journal_dict_file=io.open('journal_dict.txt','w',encoding='utf-8')
impact_factors_file=io.open('impact_dict.txt','w',encoding='utf-8')

tree=ET.parse('nlmcatalog_result.xml')
root=tree.getroot()
for journal in root.iter('NCBICatalogRecord'):
	if journal is not None:		
		title=u"--"
		syns=set()
		for t in journal.iter('TitleMain'):
			for n in t.iter('Title'):
				title=n.text.lower().replace(u'.',u'').strip()
				syns.add(re.sub(ur'\s*&\s*',' and ',title))
				syns.add(title.replace(u' and ',u' & '))
		for a in journal.iter('MedlineTA'): #abbreviation
			abbrev=a.text.lower().replace(u'.',u'').strip()
			syns.add(abbrev)
			syns.add(re.sub(ur'\s*&\s*',' and ',title))
			syns.add(abbrev.replace(u' and ',u' & '))
		for alt in journal.iter('TitleAlternate'):
			for n in alt.iter('Title'):
				n_title=n.text.lower().replace(u'.',u'').strip()
				syns.add(n_title)
				syns.add(re.sub(ur'\s*&\s*',' and ',title))
				syns.add(n_title.replace(u' and ',u' & '))
		for s in journal.iter('SortSerialName'):
			s_title=s.text.lower().replace(u'.',u'').strip()
			syns.add(s_title)
			syns.add(re.sub(ur'\s*&\s*',' and ',title))
			syns.add(s_title.replace(u' and ',u' & '))
		#for x in journal.iter('CrossReferenceList'):
		#	for r in journal.iter('CrossReference'):
		#		for i in r.findall("CrossReference[@XrType='A']"):
		#			i_title=i.text.lower().replace(u'.',u'').strip()
		#			syns.add(i_title)
		#			syns.add(i_title.replace(u' & ',u' and '))
		#			syns.add(i_title.replace(u' and ',u' & '))
		#	#	for j in r.findall("CrossReference[@XrType='X']"):
		#	#		crossRefX.add(j.text.lower().replace(u'.',u''))
		#	#		all.add(j.text.lower().replace(u'.',u''))		
		if "" in syns:
			syns.remove("")
		toadd=set()
		for s in syns:
			toadd.add(s.replace(u'-',u' '))
			toadd.add(s.replace(u'the journal',u'journal'))
		for s in toadd:
			if s !="":
				syns.add(s)
		journal_syns[title]=syns

myJI=pd.ExcelFile('./Journal Impact factor_2017.xls')
JI=pd.read_excel(myJI,0, header=None, parse_cols="A:F", encoding="utf-8")
for index, row in JI.iterrows():
	if row[1]!=u"nan" and row[1]!= u"Full Journal Title":
		journal=unicode(row[1]).strip().lower().replace(u'.',u'')
		impact=unicode(row[4]).strip()
		impact_factors[journal]=impact
		if journal not in journal_syns:
			syns=set()
			syns.add(re.sub(ur'\s*&\s*',' and ',journal))
			syns.add(journal.replace(u' and ',u' & '))
			toadd=set()
			for s in syns:
				toadd.add(s.replace(u'-',u' '))
				toadd.add(s.replace(u'the journal',u'journal'))
			for s in toadd:
				if s !="":
					syns.add(s)
			journal_syns[journal]=syns
#		else:
#			print("Journal "+journal+" already present in journal_syns")
		impact_factors_file.write(unicode(journal)+u'\t'+unicode(impact)+u'\n')

journal_syns_copy=copy.deepcopy(journal_syns)

for title in journal_syns:
	jlist=journal_syns[title]
	present=False
	duplicate=False
	ds=[]
	correct=""
	if title in impact_factors:
		correct=title
		present=True
	else:
		for j in jlist:
			if j != title:
				if j in journal_syns_copy:
					journal_syns_copy[title].remove(j)
					duplicate=True
					#ds.append([j]) #Or should I keep and print as duplicate??
				elif j in impact_factors:
					present=True
					if correct=="":
						correct=j
#						ds.append(j)
#						duplicate=False
					else:
						duplicate=True
						print("DUP: "+correct+" "+j)
#						ds.append([correct,j])
	if correct !="":
		if correct != title:
			if correct not in journal_syns_copy:
				journal_syns_copy[title].add(title)
				journal_syns_copy[title].remove(correct)
				journal_syns_copy[correct]=journal_syns_copy[title]
				del journal_syns_copy[title]
			else:
				print "Error, "+correct+" in impact table but already in journal_syns_copy"
		journal_dict[correct]=correct
		for n in journal_syns_copy[correct]:
			journal_dict[n]=correct
	elif present==False:
		del journal_syns_copy[title]
#	if duplicate==True:
##		if len(ds)>1:
#			print 'Error 2: '
#			print ds
##journal_syns=journal_syns_copy

for j in journal_dict:
	correct=journal_dict[j]
	journal_dict_file.write(unicode(j)+u'\t'+unicode(correct)+u'\n')
journal_dict_file.close()
impact_factors_file.close()


#https://stackoverflow.com/questions/222375/elementtree-xpath-select-element-based-on-attribute
