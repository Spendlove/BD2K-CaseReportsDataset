import sys
import io
import os
import re
from openpyxl import load_workbook
from word2number import w2n
import unicodecsv as csv
import pandas as pd
import xlrd

#Arguments to pass to the command line: 1) path to the directory containing input files, ending with "/" 2) base name for output files (ie, output_aug_9.txt)
inputDirectoryPath=sys.argv[1]
outputFileName=sys.argv[2]

#Opens output files
output=io.open('./'+outputFileName,'w',encoding="utf-8")
ages_file=io.open('./AGES_'+outputFileName,'w',encoding="utf-8")
score_file=io.open('./SCORES_'+outputFileName,'w',encoding="utf-8")
ccr_num_file=io.open('./CCR_NUMS_'+outputFileName,'w',encoding="utf-8")
raw_CIC_file=io.open('./RAW_IN_CONTEXT_'+outputFileName,'w',encoding="utf-8")
raw_PMED_file=io.open('./RAW_INDEX_BY_MESH_'+outputFileName,'w',encoding="utf-8")

#Creating two dictionaries: impact_factors maps journal names to the correct impact factor. journal_dict maps the journal name used in impact_factors to other ways to write the same name. Two files, impact_dict.txt and journal_dict.txt should be in the file provided. If not, please run prep_journals.py to create the files that these dictionaries will be read in from.  (Faster to read in from a saved file than to compute the mappings again every time.) NOTE: There is something funky going on with trying to do this all.  I am still not sure whether the problem is in prep_journals.py or ExtractionScript.py.
#also creating not present journals set and stuff
impact_factors={}
journal_dict={}
not_present_journals=set()
impact_error_num1=0
impact_error_num2=0
with open('./impact_dict.txt','r') as impact_js:
	for line in impact_js:
		line=line.split('\t')
		j=line[0].strip()
		i=line[1].strip()
		impact_factors[j]=i
with open('journal_dict.txt','r') as all_js:
	for line in all_js:
		line=line.split('\t')
		name=line[0].strip()
		correct=line[1].strip()
		journal_dict[name]=correct
bad_journals=io.open('./badjournals_'+outputFileName+'.txt','w', encoding="utf-8")

#Write the headers in the output files
ages_file.write(unicode('File'+'\t'+'ByHand'+'\t'+'MeSH'+'\t'+'Age'+'\t'+'Gender'))
ccr_num_file.write(unicode('CR Number'+'\t'+'PMID'+'\t'+'Collector'))
output.write(unicode('CR Number'+'\t'+'PMID'+'\t'+'Citations'+'\t'+'Title'+'\t'+'Year'+'\t'+'Journal'+'\t'+'Impact Factor'+'\t'+'Medical Context Score'+'\t'+'Medical MeSH Score'+'\t'+'Key Words'+'\t'+'Age'+'\t'+'Gender'+'\t'+'Geographic Locations'+'\t'+'Life Style'+'\t'+'Medical History Taking-Family History'+'\t'+'Social Work'+'\t'+'Medical Histoy Taking-Medical/Surgical History'+'\t'+'Cancer'+'\t'+'Nervous System Diseases'+'\t'+'Cardiovascular Diseases'+'\t'+'Musculoskeletal Diseases and Rheumatological Diseasees'+'\t'+'Digestive System Diseases'+'\t'+'Obstetrical and Gynecological Diseases'+'\t'+'Infectious Diseases'+'\t'+'Respiratory Tract Diseases'+'\t'+'Hematologic Diseases'+'\t'+'Kidney Diseases and Urologic Diseases'+'\t'+'Endocrine System Diseases'+'\t'+'Oral and Maxillofacial Diseases'+'\t'+'Ophthalamological Diseases'+'\t'+'Otorhinolaryngologic Diseases'+'\t'+'Skin Diseases'+'\t'+'Signs and Symptoms'+'\t'+'Comorbidity'+'\t'+'Diagnostic Techniques and Procedures'+'\t'+'Diagnosis'+'\t'+'Laboratory Values'+'\t'+'Pathology'+'\t'+'Drug Therapy'+'\t'+'Therapeutics'+'\t'+'Patient Outcome Assesment'+'\t'+'Images'+'\t'+'Graphs or Illustrations'+'\t'+'Videos'+'\t'+'Tables'+'\t'+'Relationship to Other Case Reports'+'\t'+'Relationship with Clinical Trial'+'\t'+'Crosslink with Database'+'\t'+'References'+'\t'+'Access Date'+'\t'+'Errors'))
score_file.write(unicode('Case Report Number'+'\t'+'PMID'+'\t'+'Index'+'\t'+'Total'+'\t'+'Case Report Identification (Findable)'+'\t'+'Medical content (Accessable, Interoperable, Reusable)'+'\t'+'Acknowledgements'+'\t'+'Title'+'\t'+'Authors'+'\t'+'Year'+'\t'+'Journal'+'\t'+'Institution'+'\t'+'Corresponding Author'+'\t'+'PMID'+'\t'+'DOI'+'\t'+'Link'+'\t'+'Language(s)'+'\t'+'Key Words'+'\t'+'Demography'+'\t'+'Geographic Location'+'\t'+'Life Style'+'\t'+'Medical History Taking-Family history'+'\t'+'Social Work'+'\t'+'Medical History Taking-Medical/surgical history'+'\t'+'Disease System'+'\t'+'Signs and Symptoms'+'\t'+'Comorbidity'+'\t'+'Diagnostic Techniques and Procedures'+'\t'+'Diagnosis'+'\t'+'Laboratory Values'+'\t'+'Pathology'+'\t'+'Drug Therapy'+'\t'+'Therapeutics'+'\t'+'Patient Outcome Assessment'+'\t'+'Images or Videos'+'\t'+'Relationship to Other Case Reports'+'\t'+'Relationship to Published Clinical Trials'+'\t'+'Crosslink with Database'+'\t'+'Funding Source'+'\t'+'Award Number'+'\t'+'Disclosures/Conflict of Interest'+'\t'+'References'))

#all_CIC_file.write(unicode('Case Report Number'+'\t'+'PMID'+'\t'+'Citation'+'\t'+'Access Date'+'\t'+'Index'+'\t'+'Case Report Identification (Findable)'+'\t'+
#all_PMED_file.write(unicode('Case Report Number'+'\t'+'PMID'+'\t'+'Citation'+'\t'+'Access Date'+'\t'+'Index'+'\t'+'Case Report Identification (Findable)'+'\t'+
##CHANFGE IMAGES NAME
raw_CIC_file.write(unicode('Case Report Number'+'\t'+'Title'+'\t'+'Authors'+'\t'+'Year'+'\t'+'Journal'+'\t'+'Institution'+'\t'+'Corresponding Author'+'\t'+'PMID'+'\t'+'DOI'+'\t'+'Link'+'\t'+'Language(s)'+'\t'+'Key Words'+'\t'+'Demography'+'\t'+'Geographic Location'+'\t'+'Life Style'+'\t'+'Medical History Taking-Family history'+'\t'+'Social Work'+'\t'+'Medical History Taking-Medical/surgical history'+'\t'+'Disease System'+'\t'+'Signs and Symptoms'+'\t'+'Comorbidity'+'\t'+'Diagnostic Techniques and Procedures'+'\t'+'Diagnosis'+'\t'+'Laboratory Values'+'\t'+'Pathology'+'\t'+'Drug Therapy'+'\t'+'Therapeutics'+'\t'+'Patient Outcome Assessment'+'\t'+'Images or Videos'+'\t'+'Relationship to Other Case Reports'+'\t'+'Relationship to Published Clinical Trials'+'\t'+'Crosslink with Database'+'\t'+'Funding Source'+'\t'+'Award Number'+'\t'+'Disclosures/Conflict of Interest'+'\t'+'References'))
raw_PMED_file.write(unicode('Case Report Number'+'\t'+'Title'+'\t'+'Authors'+'\t'+'Year'+'\t'+'Journal'+'\t'+'Institution'+'\t'+'Corresponding Author'+'\t'+'PMID'+'\t'+'DOI'+'\t'+'Link'+'\t'+'Language(s)'+'\t'+'Key Words'+'\t'+'Demography'+'\t'+'Geographic Location'+'\t'+'Life Style'+'\t'+'Medical History Taking-Family history'+'\t'+'Social Work'+'\t'+'Medical History Taking-Medical/surgical history'+'\t'+'Disease System'+'\t'+'Signs and Symptoms'+'\t'+'Comorbidity'+'\t'+'Diagnostic Techniques and Procedures'+'\t'+'Diagnosis'+'\t'+'Laboratory Values'+'\t'+'Pathology'+'\t'+'Drug Therapy'+'\t'+'Therapeutics'+'\t'+'Patient Outcome Assessment'+'\t'+'Images or Videos'+'\t'+'Relationship to Other Case Reports'+'\t'+'Relationship to Published Clinical Trials'+'\t'+'Crosslink with Database'+'\t'+'Funding Source'+'\t'+'Award Number'+'\t'+'Disclosures/Conflict of Interest'+'\t'+'References'))

#Create dictionaries to help determine which CCR numbers exist and which do not
CRnumsPresent=[]
duplicates=[]

#####
print(u"\n------Selected Problems with Individual Files------")
#Reads in all excell files and extracts the metadata
for f in os.listdir(inputDirectoryPath):
	if f.endswith('.xlsx') and f[0:2]!="~$":
		#Extract Case Report Number and Contributor initials from file name
		CR_Number=re.findall(ur'\d+',re.findall(ur'(?:CCR0?\d+)|(?:CC0?\d+)|(?:CR0?\d+)|(?:HCR0?\d+)',f)[0])[0] #Extracts CCR number from titles
		contributor=f[-7:-5].upper()
		if len(contributor.strip()) !=2: #Catches cases where there is an extra space in the title name
			contributor=f[-8:-6].upper()
		if len(contributor.strip()) !=2:
			e=u"Bad file name, contributor comes out as: "+contributor
			print(e+" in file "+unicode(f))
			errors.append(e)
		if CR_Number in CRnumsPresent:
			duplicates.append(CR_Number)
		else:
			CRnumsPresent.append(CR_Number)


		#Create a pandas dataframe object from excel file.  By default all blank values are turned to NaN. If one were to desire to check and make sure annotators remembered to fill out all sections and didn't forget any, then you would have to change this.
		myX=pd.ExcelFile(inputDirectoryPath+f) #SOURCE!!
		myDF=None
		sheet_num=-1
		#print myX.sheet_names
		if len(myX.sheet_names)==2:
			sheet_num=-2
		if contributor=="JL":
			myDF=pd.read_excel(myX,sheetname=-1, header=None, parse_cols="A:F", encoding="utf-8")
			cols = [0,1,3,2,4,5]
			myDF=myDF[cols]
			#https://stackoverflow.com/questions/13148429/how-to-change-the-order-of-dataframe-columns
		elif contributor=="TC" or contributor=="SM":
			myDF=pd.read_excel(myX,sheetname=sheet_num, header=None, parse_cols="A:F", encoding="utf-8")
			myDF=myDF.drop(4).reset_index(drop=True)
			
#			if unicode(myDF.iloc[7,0]).strip()==u"Field":
#				myDF=myDF.drop(4).reset_index(drop=True)

#			elif unicode(myDF.iloc[0,0]).strip()==u"PMID":
#				myDF
#######EVENTually change so we fix the error. ccr 502 mission CCR number  adn so citations and acess date and stuff messsed up
		else:
			myDF=pd.read_excel(myX,sheetname=sheet_num, header=None, parse_colse="A:F", encoding="utf-8")
		
		
	
		
		#initialize various variables for output files
		errors=[]
		s1_Index=u"Contained in Context"
		s2_Index=u"Index by MeSH"
		
		#Start a new line in output files
		output.write(u"\n")
		ages_file.write(u"\n")
		score_file.write(u"\n")
		ccr_num_file.write(u"\n")
		raw_CIC_file.write(u"\n")
		raw_PMED_file.write(u"\n")
		
		#Extract values from spreadsheet. "s1" and "s2" stand for score 1 and 2. "r1" and "r2" stand for raw contained in context value and raw indexed by MeSH value
		
		citations=myDF.iloc[2,1]
		
		access_date_object=myDF.iloc[3,1]
		access_date=u"nan"
		
		if type(access_date_object)==pd._libs.tslib.Timestamp:
			access_date=unicode(access_date_object.month)+u"/"+unicode(access_date_object.day)+u"/"+unicode(access_date_object.year) ####################
		elif type(access_date_object)==unicode:
			access_date=access_date_object.replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
#		if access_date_object==u"nan" or =="nan" or access_date_object==None:
#				access_date=u"nan"
#		else:
#				access_date="ERROR"
#				e="ERROR: BAD DATE FORMAT "+str(access_date_object)+" IN file "+f
#				print(e)
#				errors.append(e)

		s1_TOTAL=myDF.iloc[5,1]
		s2_TOTAL=myDF.iloc[5,2]
		
		s1_CASE_REPORT_IDENTIFICATION=myDF.iloc[7,1]
		s2_CASE_REPORT_IDENTIFICATION=myDF.iloc[7,2]

		s1_title=myDF.iloc[8,1]
		s2_title=myDF.iloc[8,2]
		r1_title=unicode(myDF.iloc[8,3]).replace(u'\n',u' ').strip()
		r2_title=unicode(myDF.iloc[8,4]).replace(u'\n',u' ').strip()
		title=r2_title
		if r2_title[-1]==u".":
			title=r2_title[:-1]
		
		s1_authors=myDF.iloc[9,1]
		s2_authors=myDF.iloc[9,2]
		r1_authors=unicode(myDF.iloc[9,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_authors=unicode(myDF.iloc[9,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		authors=r1_authors ####################

		s1_year=myDF.iloc[10,1]
		s2_year=myDF.iloc[10,2]
		r1_year=unicode(myDF.iloc[10,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_year=unicode(myDF.iloc[10,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		year=r1_year

		s1_journal=myDF.iloc[11,1]
		s2_journal=myDF.iloc[11,2]
		r1_journal=unicode(myDF.iloc[11,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_journal=unicode(myDF.iloc[11,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r3_impact=u"nan"
		if len(myDF.columns) >=6:
			r3_impact=unicode(myDF.iloc[11,5]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		journal=r1_journal.lower().replace(u'.',u'').replace(u'the journal',u'journal')
		impact=r3_impact

		s1_institution=myDF.iloc[12,1]
		s2_institution=myDF.iloc[12,2]
		r1_institution=unicode(myDF.iloc[12,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_institution=unicode(myDF.iloc[12,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		institution=r1_institution ####################

		s1_senior_author=myDF.iloc[13,1]
		s2_senior_author=myDF.iloc[13,2]
		r1_senior_author=unicode(myDF.iloc[13,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_senior_author=unicode(myDF.iloc[13,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		senior_author=r1_senior_author ####################

		s1_pmid=myDF.iloc[14,1]
		s2_pmid=myDF.iloc[14,2]
		r1_pmid=unicode(myDF.iloc[14,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_pmid=unicode(myDF.iloc[14,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		PMID=r1_pmid
		if r1_pmid==u"nan":
			PMID=r2_pmid

		s1_doi=myDF.iloc[15,1]
		s2_doi=myDF.iloc[15,2]
		r1_doi=unicode(myDF.iloc[15,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_doi=unicode(myDF.iloc[15,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		doi=r1_pmid ####################
		if r1_pmid==u"nan":
			doi=r2_pmid

		s1_link=myDF.iloc[16,1]
		s2_link=myDF.iloc[16,2]
		r1_link=unicode(myDF.iloc[16,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_link=unicode(myDF.iloc[16,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		article_link=r1_link
		if r1_link ==u"nan": #######################DOES THIS WORK?
			article_link=r2_link

		s1_languages=myDF.iloc[17,1]
		s2_languages=myDF.iloc[17,2]
		r1_languages=unicode(myDF.iloc[17,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_languages=unicode(myDF.iloc[17,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		languages=r1_languages ####################

		s1_MEDICAL_CONTENT=myDF.iloc[19,1]
		s2_MEDICAL_CONTENT=myDF.iloc[19,2]
		MedContextScore=s1_MEDICAL_CONTENT
		MedMeshScore=s2_MEDICAL_CONTENT

		s1_key_words=myDF.iloc[20,1]
		s2_key_words=myDF.iloc[20,2]
		r1_key_words=unicode(myDF.iloc[20,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_key_words=unicode(myDF.iloc[20,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		keyWords=r1_key_words

		s1_demographics=myDF.iloc[21,1]
		s2_demographics=myDF.iloc[21,2]
		r1_demographics=unicode(myDF.iloc[21,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_demographics=unicode(myDF.iloc[21,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		age=u'ERROR'
		gender=u'ERROR'
		######################PARSE______AGES_____AND____GENDER__#######################################

		s1_geographic_location=myDF.iloc[22,1]
		s2_geographic_location=myDF.iloc[22,2]
		r1_geographic_location=unicode(myDF.iloc[22,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_geographic_location=unicode(myDF.iloc[22,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		geographicLocations=r1_geographic_location

		s1_life_style=myDF.iloc[23,1]
		s2_life_style=myDF.iloc[23,2]
		r1_life_style=unicode(myDF.iloc[23,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_life_style=unicode(myDF.iloc[23,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		lifeStyle=r1_life_style
		if r1_life_style==u"nan":
			lifeStyle=r2_life_style

		s1_family_history=myDF.iloc[24,1]
		s2_family_history=myDF.iloc[24,2]
		r1_family_history=unicode(myDF.iloc[24,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_family_history=unicode(myDF.iloc[24,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		familyHistory=r1_family_history

		s1_social_background=myDF.iloc[25,1]
		s2_social_background=myDF.iloc[25,2]
		r1_social_background=unicode(myDF.iloc[25,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_social_background=unicode(myDF.iloc[25,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		socialWork=r1_social_background
		if r1_social_background==u"nan":
			socialWork=r2_social_background

		s1_medical_surgical_history=myDF.iloc[26,1]
		s2_medical_surgical_history=myDF.iloc[26,2]
		r1_medical_surgical_history=unicode(myDF.iloc[26,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_medical_surgical_history=unicode(myDF.iloc[26,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		medicalHistory=r1_medical_surgical_history
		if r1_medical_surgical_history==u"nan":
			medicalHistory=r2_medical_surgical_history

		s1_organ_system=myDF.iloc[27,1]
		s2_organ_system=myDF.iloc[27,2]
		r1_organ_system=unicode(myDF.iloc[27,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip().lower()
		r2_organ_system=unicode(myDF.iloc[27,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip().lower()
		OrganSystem=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		######################__PARSE______Organ_____System__#######################################

		s1_symptoms_and_signs=myDF.iloc[28,1]
		s2_symptoms_and_signs=myDF.iloc[28,2]
		r1_symptoms_and_signs=unicode(myDF.iloc[28,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_symptoms_and_signs=unicode(myDF.iloc[28,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		signsAndSymptoms=r1_symptoms_and_signs
		if r1_symptoms_and_signs==u"nan":
			signsAndSymptoms=r2_symptoms_and_signs

		s1_comorbidities=myDF.iloc[29,1]
		s2_comorbidities=myDF.iloc[29,2]
		r1_comorbidities=unicode(myDF.iloc[29,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_comorbidities=unicode(myDF.iloc[29,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		comorbidity=r1_comorbidities
		if r1_comorbidities==u"nan":
			comorbidity=r2_comorbidities

		s1_diagnostic_procedure=myDF.iloc[30,1]
		s2_diagnostic_procedure=myDF.iloc[30,2]
		r1_diagnostic_procedure=unicode(myDF.iloc[30,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_diagnostic_procedure=unicode(myDF.iloc[30,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		diagnosticTechs=r1_diagnostic_procedure
		if r1_diagnostic_procedure==u"nan":
			diagnosticTechs=r2_diagnostic_procedure

		s1_disease_diagnosis=myDF.iloc[31,1]
		s2_disease_diagnosis=myDF.iloc[31,2]
		r1_disease_diagnosis=unicode(myDF.iloc[31,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_disease_diagnosis=unicode(myDF.iloc[31,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		diagnosis=r1_disease_diagnosis
		if r1_disease_diagnosis==u"nan":
			diagnosis=r2_disease_diagnosis

		s1_laboratory_values=myDF.iloc[32,1]
		s2_laboratory_values=myDF.iloc[32,2]
		r1_laboratory_values=unicode(myDF.iloc[32,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_laboratory_values=unicode(myDF.iloc[32,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		labVals=r1_laboratory_values
		if r1_laboratory_values==u"nan":
			labVals=r2_laboratory_values

		s1_pathology=myDF.iloc[33,1]
		s2_pathology=myDF.iloc[33,2]
		r1_pathology=unicode(myDF.iloc[33,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_pathology=unicode(myDF.iloc[33,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		pathology=r1_pathology
		if r1_pathology==u"nan":
			pathology=r2_pathology

		s1_pharmacological_therapy=myDF.iloc[34,1]
		s2_pharmacological_therapy=myDF.iloc[34,2]
		r1_pharmacological_therapy=unicode(myDF.iloc[34,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_pharmacological_therapy=unicode(myDF.iloc[34,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		drugTherapy=r1_pharmacological_therapy
		if r1_pharmacological_therapy==u"nan":
			drugTherapy=r2_pharmacological_therapy

		s1_therapeutic_intervention=myDF.iloc[35,1]
		s2_therapeutic_intervention=myDF.iloc[35,2]
		r1_therapeutic_intervention=unicode(myDF.iloc[35,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_therapeutic_intervention=unicode(myDF.iloc[35,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		therapeutics=r1_therapeutic_intervention
		if r1_therapeutic_intervention==u"nan":
			therapeutics=r2_therapeutic_intervention

		s1_outcome=myDF.iloc[36,1]
		s2_outcome=myDF.iloc[36,2]
		r1_outcome=unicode(myDF.iloc[36,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_outcome=unicode(myDF.iloc[36,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		patientOutcome=r1_outcome
		if r1_outcome==u"nan":
			patientOutcome=r2_outcome

		s1_images_or_videos=myDF.iloc[37,1]
		s2_images_or_videos=myDF.iloc[37,2]
		r1_images_or_videos=unicode(myDF.iloc[37,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_images_or_videos=unicode(myDF.iloc[37,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		######################__PARSE______Organ_____System__#######################################
		images=u'ERROR'
		graphs_or_illustrations=u'ERROR'
		videos=u'ERROR'
		tables=u'ERROR'

		s1_relationship_to_other_case_reports=myDF.iloc[38,1]
		s2_relationship_to_other_case_reports=myDF.iloc[38,2]
		r1_relationship_to_other_case_reports=unicode(myDF.iloc[38,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_relationship_to_other_case_reports=unicode(myDF.iloc[38,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		relationshipToOtherCRs=r1_relationship_to_other_case_reports
		######################__PARSE

		s1_relationship_to_published_clinical_trials=myDF.iloc[39,1]
		s2_relationship_to_published_clinical_trials=myDF.iloc[39,2]
		r1_relationship_to_published_clinical_trials=unicode(myDF.iloc[39,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_relationship_to_published_clinical_trials=unicode(myDF.iloc[39,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		relationshipWithCT=r1_relationship_to_published_clinical_trials
		######################__PARSE

		s1_crosslink_with_database=myDF.iloc[40,1]
		s2_crosslink_with_database=myDF.iloc[40,2]
		r1_crosslink_with_database=unicode(myDF.iloc[40,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_crosslink_with_database=unicode(myDF.iloc[40,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		crosslinkWithDatabase=r2_crosslink_with_database

		s1_ACKNOWLEDGEMENTS=myDF.iloc[41,1]
		s2_ACKNOWLEDGEMENTS=myDF.iloc[41,2]
		r1_ACKNOWLEDGEMENTS=unicode(myDF.iloc[41,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_ACKNOWLEDGEMENTS=unicode(myDF.iloc[41,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()

		s1_funding_source=myDF.iloc[43,1]
		s2_funding_source=myDF.iloc[43,2]
		r1_funding_source=unicode(myDF.iloc[43,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_funding_source=unicode(myDF.iloc[43,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		funding_source=r1_funding_source  ##################################
		if r1_funding_source==u"nan":
			funding_source=r2_funding_source


		s1_award_number=myDF.iloc[44,1]
		s2_award_number=myDF.iloc[44,2]
		r1_award_number=unicode(myDF.iloc[44,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_award_number=unicode(myDF.iloc[44,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		award_number=r1_award_number##################################
		if r1_award_number==u"nan":
			award_number=r2_award_number


		s1_disclosures_conflict_of_interest=myDF.iloc[45,1]
		s2_disclosures_conflict_of_interest=myDF.iloc[45,2]
		r1_disclosures_conflict_of_interest=unicode(myDF.iloc[45,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		r2_disclosures_conflict_of_interest=unicode(myDF.iloc[45,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
		disclosures_conflict_of_interest=r1_disclosures_conflict_of_interest##################################
		if r1_disclosures_conflict_of_interest==u"nan":
			disclosures_conflict_of_interest=r2_disclosures_conflict_of_interest


		if len(myDF) > 46:
			s1_references=myDF.iloc[46,1]
			s2_references=myDF.iloc[46,1]
			r1_references=unicode(myDF.iloc[46,3]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
			r2_references=unicode(myDF.iloc[46,4]).replace(u'\n',u' ').replace(u'\xa0',u' ').strip()
			references=r1_references
		else:
			e=u"Error: No references row in file"
			errors.append(e)
			print(e+u": "+unicode(f))
	
		
		#Now that we have saved all the information into variables, we will parse some of the raw input values (like demographics, images/videos, etc.)
		#########_MOVE_PARSING__JOURNAL#######################
		if journal in journal_dict:
			journal=journal_dict[journal]
			impact=impact_factors[journal]
		elif r3_impact ==u"nan":
			impact=r3_impact
			e=u'ERROR: '+journal+u' not listed in impact factor table and not in excel sheet'
			errors.append(e)
			#print(e)
			not_present_journals.add(journal)
			impact_error_num1=impact_error_num1+1
			###########################FIX#########FIX#####################FIX#################FIX#################FIX
#			bad_journals.write(journal+u'\n')
		else:
			impact=r3_impact
			e=u'WARNING '+journal+u' not listed in impact factor table'
			not_present_journals.add(journal)
			impact_error_num2=impact_error_num2+1
			###########################FIX#########FIX#####################FIX#################FIX#################FIX
			#print(e)
#			bad_journals.write(journal+u'\n')
			errors.append(e)
	
		####_CHECK_PMID_##########
		if PMID not in f:
			print u'ERROR! PMID does not match file name.  PMID is '+PMID+u' and file name is '+f
			errors.append(u'ERROR: PMID does not match file name. PMID is '+PMID+u' and file name is '+f)

		#####_PARSE_AGE_########
#####################################MAKE_IT_SO_IT_HANDLES_UNICODE
		age_string=re.sub(ur'\< 18 yo','less than 18 years old',r1_demographics.lower())##
		years=re.findall(ur'(\d+(?:\.\d+)?)([^\w\d]+)(year|yr|yo|y\/o)',age_string)
		more_years=re.findall(ur'(?:aged?|age of)[^\w\d]+(\d+(?:\.\d+)?)',age_string)#AGE OF ONE?
		writ_years=re.findall(ur'((?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|one hundred|one hundred and)(?:[^\w\d]+)(?:(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(?:[^\w\d]+))?)(year|yr|yo|y\/o)',age_string)
		decades=re.findall(ur'twenties|thirties|forties|fifties|sixties|seventies|eighties|nineties|20s|30s|40s|50s|60s|70s|80s|90s|20\'s|30\'s|40\'s|50\'s|60\'s|70\'s|80\'s|90\'s',age_string)#20's-->and switch all bad ' to '
		months=re.findall(ur'(\d+(?:\.\d+)?)([^\w\d]+)(month)',age_string)
		days=re.findall(ur'(\d+(?:\.\d+)?)([^\w\d]+)(day)',age_string)
		weeks=re.findall(ur'(\d+(?:\.\d+)?)([^\w\d]+)(week|wk)(?! premature)',age_string)
		newborn=re.findall(ur'(?:newborn|infant|neonate)',age_string)
		decade_conv={'twenties':25,'20s':25,'20\'s':25,'thirties':35,'30s':35,'30\'s':35,'fourties':45,'40s':45,'40\'s':45,'50s':55,'50\'s':55,'fifties':55,'sixties':65,'60s':65,'60\'s':65,'seventies':75,'70s':75,'70\'s':75,'eighties':85,'80s':85,'80\'s':85,'nineties':95,'90s':95,'90\'s':95}
		if len(years)>=1:
			age=years[0][0]
		elif len(more_years)>=1:
			age=more_years[0]
		elif len(months)>=1:
			age=float(months[0][0])/12.0
		elif len(writ_years)>=1:
			age=w2n.word_to_num(str(writ_years[0][0]))
		elif len(decades)>=1:
			age=decade_conv[decades[0]]
		elif len(days)>=1:
			month=1
			if float(days[0][0])/30.0 > month:
				month=float(days[0][0])/30.0
			age=month/12.0
		elif len(weeks)>=1:
			month=1
			if float(weeks[0][0])/4.0 > month :
				month=float(weeks[0][0])/4.0
			age=month/12.0
		elif len(newborn)>=1:
			age=1/12.0
		else:
			age=u'NA'
		age=unicode(age) ##
		age_string=re.sub(ur'(?<!(?:wo|hu))man|(?<!wo)men|boy','male',age_string)
		age_string=re.sub(ur'woman|women|girl|lady|femal|sister','female',age_string)
		gender_string=str(r2_demographics.lower()) ##
		gender_string=re.sub(ur'woman|women|girl|lady|femal|sister','female',gender_string)
		gender_string=re.sub(ur'(?<!(?:wo|hu))man|(?<!wo)men|boy','male',gender_string)
		genders=set(re.findall(ur'female|male',age_string,re.I))
		g2=set(re.findall(ur'female|male',gender_string,re.I))

		#####_PARSE_GENDER_########
		if len(genders)==1:
			gender=unicode(genders.pop().lower())
		elif len(genders)==2:
			if len(g2)==1:
				gender=unicode(g2.pop().lower())
				e=u'Warning!!!! gender may be wrong in file'
				errors.append(e)
				print(e+u" "+f)
			else:
				gender=u'male & female'
		elif len(genders)==0:
			if len(g2)==0:
				gender=u"NA"
			elif len(g2)==1:
				gender=unicode(g2.pop().lower())
			elif len(g2)==2:
				gender=u'male & female'
			else:
				print(g2)
				g_str=u""
				for g in g2:
					g_str=g_str+g+u"_"
				e=u"ERROR! LENGTH OF GENDER STRING GREATER THAN TWO: "+g_str
				errors.append(e)
				print(e+u" in file "+f)
		else:
			e=u"ERROR! LENGTH OF GENDER STRING GREATER THAN TWO"
			errors.append(e)
			print(e+u" in file "+f)

		#####_PARSE_DISEASE_SYSTEM_########
		if r1_organ_system==u"nan":
			OrganSystem=[u'NA',u'NA',u'NA',u'NA',u'NA',u'NA',u'NA',u'NA',u'NA',u'NA',u'NA',u'NA',u'NA',u'NA',u'NA']
			e=u"Error, no disease system listed"
			errors.append(e)
			#print(e+u" in file "+f)
		else:
			bad=[] ############################make it handle unicode
			text=re.split(',|;',str(r1_organ_system.lower())) ###
			#print text
			error=u""
			if len(text)<=0:
				OrganSystem=['ERROR','ERROR','ERROR','ERROR','ERROR','ERROR','ERROR','ERROR','ERROR','ERROR','ERROR','ERROR','ERROR','ERROR','ERROR']##
			for s in text:
				s.strip() #is not getting rid of all whitespace. Had to change s==cancer to cancer in s
				if len(s)==0:
					s="nan"
				elif 'cancer' in s:
					OrganSystem[0]=1#systems.append('Cancer')
				elif 'nervous' in s or 'neurologic' in s or 'neruological' in s:
					OrganSystem[1]=1#systems.append('Nervous System Diseases')
				elif 'cardio' in s:
					OrganSystem[2]=1#systems.append('Cardiovascular Diseases')
				elif 'musculoskeletal' in s or 'rheumatologic' in s:
					OrganSystem[3]=1#systems.append('Musculoskeletal Diseases and Rheumatological Diseases')
				elif s=='gi' or 'digestive' in s or 'gastrointestinal' in s:
					OrganSystem[4]=1#systems.append('Digestive System Diseases')
				elif 'obstetrical' in s or 'gynecological' in s:
					OrganSystem[5]=1#systems.append('Obstetrical and Gynecological Diseases')
				elif 'infectious' in s:
					OrganSystem[6]=1#systems.append('Infectious Diseases')
				elif 'respiratory' in s:
					OrganSystem[7]=1#systems.append('Respiratory Tract Diseases')
				elif 'hematologic' in s or 'blood' in s: # or 'hemotological' in s:
					OrganSystem[8]=1#systems.append('Hematologic Diseases')
				elif 'kidney' in s or 'urologic' in s or 'urinary' in s or 'nephrologic' in s:
					OrganSystem[9]=1#systems.append('Kidney Diseases and Urologic Diseases')
				elif 'endocrin' in s or 'endorine' in s:
					OrganSystem[10]=1#systems.append('Endocrine System Diseases')
				elif 'oral' in s or 'maxillofacial' in s:
					OrganSystem[11]=1#systems.append('Oral and Maxillofacial Diseases')
				elif 'ophthalm' in s or 'eye' in s:
					OrganSystem[12]=1#systems.append('Ophthalmological Diseases')
				elif 'otorhinolaryngologic' in s:
					OrganSystem[13]=1#systems.append('Otorhinolaryngologic Diseases')
				elif 'skin' in s or 'dermotological' in s:
					OrganSystem[14]=1#systems.append('Skin Diseases')
				else:
					bad.append(unicode(s)) ###########i should make it all unicode. if unicode in bad then this ocnverting wont fix prob because messed up already trying to read as ascii. and redundant if same as ascii
			if len(bad)>0:
				error=u'Warning: In file '+unicode(f)+u' Organ System has following invalid tokens: '
				for i in bad:
					error=error+u' '+i+u','
				error=error[:-1]
			if len(error)>0:
				errors.append(error)
#				print error
		#######_PARSE_CROSSLINK_WITH_DATABASE########################
		if r2_crosslink_with_database!=u"nan":
			nums=re.findall(ur'(?:^\d+ | \d+)', str(r2_crosslink_with_database)) #######handle unicode!!!!!
			my_sum=0
			if len(nums)>0:
				for n in nums:
					my_sum=my_sum+int(n.strip())
					crosslinkWithDatabase=unicode(my_sum)
			else:
				urls=re.findall(ur'https:\S*', str(r2_crosslink_with_database))
				if len(urls)>0:
					crosslinkWithDatabase=unicode(len(urls))#+'*'
					#print 'WARNING: Crosslinks in file '+f+' in wrong format. Computing answer assuming only 1 per link'
					errors.append(u"WARNING: Crosslinks in wrong format, computing answer assuming only 1 crosslink per link")
				else:
					crosslinkWithDatabase=u"ERROR"
					e=u"ERROR: Parsing error in crosslink with database row"
					errors.append(e)
					print(e+u" in file "+f)
		#########_PARSE_Images_Or_Videos##############
		if r1_images_or_videos==u"nan":
			#image_string=u"ERROR"
			e=u"Error: Cannot parse Images or Videos because not listed"
			errors.append(e)
#			print(e+u" in file "+f)
		else:
			image_nums=re.findall(ur'\d+(?<! Figure)',r1_images_or_videos) ####handle unicode!
			if len(image_nums)==4:
				images=image_nums[0]
				graphs_or_illustrations=image_nums[1]
				videos=image_nums[2]
				tables=image_nums[3]
			elif len(image_nums)==2:
				images=image_nums[0]
				videos=image_nums[1]
				e="Warning: Missing number of illustrations/graphs and number of tables"
				errors.append(e)
			elif len(image_nums)==1:
				images=image_nums[0]
				videos=0
				e="Warning: Missing numbers of illustrations/graphs, videos, and tables"
				errors.append(e)
			else:
				e=u"ERROR: IMAGE NUMBERS IN WRONG FORMAT"
				errors.append(e)
				print(e+u": "+r1_images_or_videos+u" (in file "+unicode(f)+u")")
#				images=r1_images_or_videos
#				graphs_or_illustrations=r1_images_or_videos
#				videos=r1_images_or_videos
#				tables=r1_images_or_videos


		#########_PARSE_REFERENCES_##############
		if r1_references!=u"nan":
			ref_nums=re.findall(ur'\d+',r1_references) #####handle unicode
			if len(ref_nums)>=1:
				references=ref_nums[0]
				if len(ref_nums)>1:
					e=u'Warning, references cell has multiple numbers. Taking first one.'
					errors.append(e)
					print(e+u" In file "+unicode(f))
			elif len(ref_nums)==0:
				references==u"ERROR"
				e=u"ERROR: references in wrong format"
				errors.append(e)
				print(e+u": "+r1_references+u" (in file "+unicode(f)+")")


#https://s3.amazonaws.com/assets.datacamp.com/blog_assets/PandasPythonForDataScience.pdf
#https://stackoverflow.com/questions/23594878/pandas-dataframe-and-character-encoding-when-reading-excel-file
#https://stackoverflow.com/questions/38228098/pandas-no-column-names-in-data-file
#https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_excel.html
#https://pandas.pydata.org/pandas-docs/stable/indexing.html
#https://stackoverflow.com/questions/33216180/move-columns-within-pandas-data-frame
#https://stackoverflow.com/questions/17977540/pandas-looking-up-the-list-of-sheets-in-an-excel-file
#https://stackoverflow.com/questions/20490274/how-to-reset-index-in-a-pandas-data-frame
#https://stackoverflow.com/questions/393843/python-and-regular-expression-with-unicode


#						s1_TOTAL_TEXT=re.findall(r'\d+',str(line[1]).strip())  ##????????????????????????????????????????
#						s2_TOTAL_TEXT=re.findall(r'\d+',str(line[1]).strip())	##???????????????????????????????????????
#						num=re.findall(r'\d+',line[3].strip())   ##????????????????????????????????????????pmid
#						num=re.findall(r'\d+',line[4].strip())   ##????????????????????????????????????????pmid

		error_string=u""
		for e in errors:
			if error_string==u"":
				error_string=error_string+e
			else:
				error_string=error_string+u'; '+e
		my_string=unicode(CR_Number)+u'\t'+unicode(PMID)+u'\t'+unicode(citations)+u'\t'+unicode(title)+u'\t'+unicode(year)+u'\t'+journal+u'\t'+unicode(impact)+u'\t'+unicode(MedContextScore)+u'\t'+unicode(MedMeshScore)+u'\t'+keyWords+u'\t'
		my_string=my_string+age
		my_string=my_string+u'\t'+gender+u'\t'
		my_string=my_string+geographicLocations+u'\t'
		my_string=my_string+lifeStyle+u'\t'
		my_string=my_string+familyHistory+u'\t'
		my_string=my_string+socialWork+u'\t'
		my_string=my_string+medicalHistory+u'\t'+unicode(OrganSystem[0])+u'\t'+unicode(OrganSystem[1])+u'\t'+unicode(OrganSystem[2])+u'\t'+unicode(OrganSystem[3])+u'\t'+unicode(OrganSystem[4])+u'\t'+unicode(OrganSystem[5])+u'\t'+unicode(OrganSystem[6])+u'\t'+unicode(OrganSystem[7])+u'\t'+unicode(OrganSystem[8])+u'\t'+unicode(OrganSystem[9])+u'\t'+unicode(OrganSystem[10])+u'\t'+unicode(OrganSystem[11])+u'\t'+unicode(OrganSystem[12])+u'\t'+unicode(OrganSystem[13])+u'\t'+unicode(OrganSystem[14])+u'\t'+signsAndSymptoms+u'\t'+comorbidity+u'\t'+diagnosticTechs+u'\t'+diagnosis+u'\t'+labVals+u'\t'+pathology+u'\t'+drugTherapy+u'\t'+therapeutics+u'\t'+patientOutcome+u'\t'+unicode(images)+u'\t'+unicode(graphs_or_illustrations)+u'\t'+unicode(videos)+u'\t'+unicode(tables)+'\t'+relationshipToOtherCRs+'\t'+relationshipWithCT+'\t'+crosslinkWithDatabase+u'\t'+unicode(references)+u'\t'+access_date+u'\t'+error_string
		output.write(my_string)
		ages_file.write(unicode(f)+u'\t'+r1_demographics+u'\t'+r2_demographics+u'\t'+age+'\t'+gender)
		ccr_num_file.write(CR_Number+u'\t'+PMID+u'\t'+contributor)
		score_file.write(CR_Number+'\t'+PMID+'\t'+unicode(s1_Index)+'\t'+unicode(s1_TOTAL)+'\t'+unicode(s1_CASE_REPORT_IDENTIFICATION)+'\t'+unicode(s1_MEDICAL_CONTENT)+'\t'+unicode(s1_ACKNOWLEDGEMENTS)+'\t'+unicode(s1_title)+'\t'+unicode(s1_authors)+'\t'+unicode(s1_year)+'\t'+unicode(s1_journal)+'\t'+unicode(s1_institution)+'\t'+unicode(s1_senior_author)+'\t'+unicode(s1_pmid)+'\t'+unicode(s1_doi)+'\t'+unicode(s1_link)+'\t'+unicode(s1_languages)+'\t'+unicode(s1_key_words)+'\t'+unicode(s1_demographics)+'\t'+unicode(s1_geographic_location)+'\t'+unicode(s1_life_style)+'\t'+unicode(s1_family_history)+'\t'+unicode(s1_social_background)+'\t'+unicode(s1_medical_surgical_history)+'\t'+unicode(s1_organ_system)+'\t'+unicode(s1_symptoms_and_signs)+'\t'+unicode(s1_comorbidities)+'\t'+unicode(s1_diagnostic_procedure)+'\t'+unicode(s1_disease_diagnosis)+'\t'+unicode(s1_laboratory_values)+'\t'+unicode(s1_pathology)+'\t'+unicode(s1_pharmacological_therapy)+'\t'+unicode(s1_therapeutic_intervention)+'\t'+unicode(s1_outcome)+'\t'+unicode(s1_images_or_videos)+'\t'+unicode(s1_relationship_to_other_case_reports)+'\t'+unicode(s1_relationship_to_published_clinical_trials)+'\t'+unicode(s1_crosslink_with_database)+'\t'+unicode(s1_funding_source)+'\t'+unicode(s1_award_number)+'\t'+unicode(s1_disclosures_conflict_of_interest)+'\t'+unicode(s1_references))
		score_file.write('\n'+'\t'+PMID+'\t'+s2_Index+'\t'+unicode(s2_TOTAL)+'\t'+unicode(s2_CASE_REPORT_IDENTIFICATION)+'\t'+unicode(s2_MEDICAL_CONTENT)+'\t'+unicode(s2_ACKNOWLEDGEMENTS)+'\t'+unicode(s2_title)+'\t'+unicode(s2_authors)+'\t'+unicode(s2_year)+'\t'+unicode(s2_journal)+'\t'+unicode(s2_institution)+'\t'+unicode(s2_senior_author)+'\t'+unicode(s2_pmid)+'\t'+unicode(s2_doi)+'\t'+unicode(s2_link)+'\t'+unicode(s2_languages)+'\t'+unicode(s2_key_words)+'\t'+unicode(s2_demographics)+'\t'+unicode(s2_geographic_location)+'\t'+unicode(s2_life_style)+'\t'+unicode(s2_family_history)+'\t'+unicode(s2_social_background)+'\t'+unicode(s2_medical_surgical_history)+'\t'+unicode(s2_organ_system)+'\t'+unicode(s2_symptoms_and_signs)+'\t'+unicode(s2_comorbidities)+'\t'+unicode(s2_diagnostic_procedure)+'\t'+unicode(s2_disease_diagnosis)+'\t'+unicode(s2_laboratory_values)+'\t'+unicode(s2_pathology)+'\t'+unicode(s2_pharmacological_therapy)+'\t'+unicode(s2_therapeutic_intervention)+'\t'+unicode(s2_outcome)+'\t'+unicode(s2_images_or_videos)+'\t'+unicode(s2_relationship_to_other_case_reports)+'\t'+unicode(s2_relationship_to_published_clinical_trials)+'\t'+unicode(s2_crosslink_with_database)+'\t'+unicode(s2_funding_source)+'\t'+unicode(s2_award_number)+'\t'+unicode(s2_disclosures_conflict_of_interest)+'\t'+unicode(s2_references))
		raw_CIC_file.write(unicode(CR_Number)+u'\t'+r1_title+u'\t'+r1_authors+u'\t'+r1_year+u'\t'+r1_journal+u'\t'+r1_institution+u'\t'+r1_senior_author+u'\t'+r1_pmid+u'\t'+r1_doi+u'\t'+r1_link+u'\t'+r1_languages+u'\t'+r1_key_words+u'\t'+r1_demographics+u'\t'+r1_geographic_location+u'\t'+r1_life_style+u'\t'+r1_family_history+u'\t'+r1_social_background+u'\t'+r1_medical_surgical_history+u'\t'+r1_organ_system+u'\t'+r1_symptoms_and_signs+u'\t'+r1_comorbidities+u'\t'+r1_diagnostic_procedure+u'\t'+r1_disease_diagnosis+u'\t'+r1_laboratory_values+u'\t'+r1_pathology+u'\t'+r1_pharmacological_therapy+u'\t'+r1_therapeutic_intervention+u'\t'+r1_outcome+u'\t'+r1_images_or_videos+u'\t'+r1_relationship_to_other_case_reports+u'\t'+r1_relationship_to_published_clinical_trials+u'\t'+r1_crosslink_with_database+u'\t'+r1_funding_source+u'\t'+r1_award_number+u'\t'+r1_disclosures_conflict_of_interest+u'\t'+r1_references)
		raw_PMED_file.write(unicode(CR_Number)+u'\t'+r2_title+u'\t'+r2_authors+u'\t'+r2_year+u'\t'+r2_journal+u'\t'+r2_institution+u'\t'+r2_senior_author+u'\t'+r2_pmid+u'\t'+r2_doi+u'\t'+r2_link+u'\t'+r2_languages+u'\t'+r2_key_words+u'\t'+r2_demographics+u'\t'+r2_geographic_location+u'\t'+r2_life_style+u'\t'+r2_family_history+u'\t'+r2_social_background+u'\t'+r2_medical_surgical_history+u'\t'+r2_organ_system+u'\t'+r2_symptoms_and_signs+u'\t'+r2_comorbidities+u'\t'+r2_diagnostic_procedure+u'\t'+r2_disease_diagnosis+u'\t'+r2_laboratory_values+u'\t'+r2_pathology+u'\t'+r2_pharmacological_therapy+u'\t'+r2_therapeutic_intervention+u'\t'+r2_outcome+u'\t'+r2_images_or_videos+u'\t'+r2_relationship_to_other_case_reports+u'\t'+r2_relationship_to_published_clinical_trials+u'\t'+r2_crosslink_with_database+u'\t'+r2_funding_source+u'\t'+r2_award_number+u'\t'+r2_disclosures_conflict_of_interest+u'\t'+r2_references)

#Write all of the journals we do not have an impact factor for in a file
e1=u"ERROR: "+unicode(impact_error_num1)+u" files did not have an impact factor listed and the impact factor can't be inferred from the journal name."
e2=u"Warning: "+unicode(impact_error_num2)+u" files had impact factors listed, but the updated impact factor can't be inferred from the journal name, so the impact factor in the output file may be wrong."
e3=u"Total unrecognized journal names: "+unicode(len(not_present_journals))

print(u"\n ------Impact Factor Probs------")
print e1
print e2
print e3
print(u"\n------Missing and Duplicate Case Report Numbers------")

for b in not_present_journals:
	bad_journals.write(b+u'\n')

#Calculate which CCR numbers are duplicated, and which are missing NOTE: CHange the CCR number range in for loop below to match the total number of CCRs that should be present.
missing=set()
for n in range(1,1801):
	if str(n) not in CRnumsPresent:
		if '0'+str(n) not in CRnumsPresent:
			if '00'+str(n) not in CRnumsPresent:
					missing.add(n)
print"Missing: "
print missing
print"Duplicates: "
print duplicates

#Close output files
output.close()
score_file.close()
ages_file.close()
bad_journals.close()
ccr_num_file.close()
raw_CIC_file.close()
raw_PMED_file.close()


#LINKS of a few of the many websites and Stack Overflow posts that helped me:
#https://pypi.python.org/pypi/word2number/1.1
#https://stackoverflow.com/questions/41211619/how-to-convert-xlsx-to-tab-delimited-files
#https://stackoverflow.com/questions/27423199/python-xlrd-read-from-last-sheet-in-a-workbook
##https://stackoverflow.com/questions/1189111/unicode-to-utf8-for-csv-files-python-via-xlrd
#https://openpyxl.readthedocs.io/en/default/index.html
#https://stackoverflow.com/questions/9347419/python-strip-with-n
#https://stackoverflow.com/questions/3437059/does-python-have-a-string-contains-substring-method
#https://stackoverflow.com/questions/7907928/openpyxl-check-for-empty-cell
#https://stackoverflow.com/questions/10393157/splitting-a-string-with-multiple-delimiters-in-python
