#! /usr/bin/python

import sys
import re
import urllib2
import pycurl
import os
import urllib
import shutil

from HTMLParser import HTMLParser
from bs4 import BeautifulSoup


###URL Patterns

tcgaRoot = "https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/"
sortingClickURL = "?C=M;O=I"
clinicalPath = "/bcr/biotab/clin/"
urlEnd_RNASeqV2 = "/cgcc/unc.edu/illuminahiseq_rnaseqv2/rnaseqv2/"
urlEnd_miRNASeq_hi = "/cgcc/bcgsc.ca/illuminahiseq_mirnaseq/mirnaseq/"


###System information
print "##########################################################################"
print "######                   TCGA Data Downloader                       ######"
print "######                  Ver. 0.05a by Eric Lee                      ######"
print "######                                                              ######"
print "##########################################################################"


###Select Cancer Type 

print "Please select the TCGA cancer data you want to download: "
print "1.  (ACC)  Adrenocortical carcinoma"
print "2.  (AML)  Acute Myeloid Leukemia"
print "3.  (BRCA) Breast invasive carcinoma "
print "4.  (CESC) Cervical squamous cell carcinoma and endocervical adenocarcinoma "
print "5.  (COAD) Colon adenocarcinoma "
print "6.  (LGG)  Brain Lower Grade Glioma "
print "7.  (OV)   Ovarian serous cystadenocarcinoma "
print "8.  (LIHC) Liver hepatocellular carcinoma "
print "9.  (LUSC) Lung squamous cell carcinoma "
print "10. (HNSC) Head and Neck squamous cell carcinoma "
print "11. (STAD) Stomach adenocarcinoma "
print "                                   "

cancerSel = raw_input('Enter the number : ')

cancerType = ""

if cancerSel == "1":
	cancerType = "acc"
elif cancerSel == "2":
	cancerType = "laml"
elif cancerSel == "3":
	cancerType = "brca"
elif cancerSel == "4":
	cancerType = "cesc"
elif cancerSel == "5":
	cancerType = "coad"
elif cancerSel == "6":
	cancerType = "lgg"
elif cancerSel == "7":
	cancerType = "ov"
elif cancerSel == "8":
	cancerType = "lihc"
elif cancerSel == "9":
	cancerType = "lusc"
elif cancerSel == "10":
	cancerType = "hnsc"
elif cancerSel == "11":
	cancerType = "stad"

print "Your selection is "+ cancerType.upper()

#### Clinical Part

clinicalPatient = "nationwidechildrens.org_clinical_patient_"
clinicalAnalyte =  "nationwidechildrens.org_biospecimen_analyte_"

fullClinical_Patient = tcgaRoot + cancerType + clinicalPath + clinicalPatient + cancerType + ".txt"
fullClinical_Analyte = tcgaRoot + cancerType + clinicalPath + clinicalAnalyte + cancerType + ".txt"

urlRNASeqV2 = tcgaRoot+cancerType+urlEnd_RNASeqV2

actualFiles_RNASeqV2 = ""
actualFiles_miRNA_hi =""


def checkFolderExist(cancer):
	if os.path.exists("./"+cancer) == True :
		print(cancer+"folder already exist, deleting it ...")
		shutil.rmtree("./"+cancer)

def create_folder(path):
	os.mkdir(path)

def getLatestData(urlOfData, htmlSavedFile, dataCategory):
	
	htmlfile=urllib.URLopener()
	htmlfile.retrieve( urlOfData+sortingClickURL, htmlSavedFile)

	fetchPage = open(htmlSavedFile, 'r')
	soup = BeautifulSoup(fetchPage)

	files=[]

	hl_files = soup.find_all('a')

	###Insert file links to list 
	for link in hl_files:
		files.insert(1,link.get_text())

	###Remove the useless items from list (files_RNASeqV2) and create a new list (actualFiles_RNASeqV2).
	actualFiles = filter( lambda s: not (s.endswith("md5") or s.endswith("/") or s.endswith("Size") or s.endswith("Name") or "mage" in s or s.startswith("Last")  or s.startswith("Parent")), files)
	i = 0
	FileAmount = len(actualFiles)

	for actualFile in actualFiles:
			i+=1
			#print str(i) + ".  " + actualFile

	userSelFile = 1

	returnActualFile = actualFiles[int(userSelFile)-1]
	print "Latest " + dataCategory + " data is " + returnActualFile

	if dataCategory == "RNASeqV2":
		global actualFiles_RNASeqV2
		actualFiles_RNASeqV2 = str(returnActualFile)
	elif dataCategory == "miRNASeq_hi":
		global actualFiles_miRNA_hi
		actualFiles_miRNA_hi = str(returnActualFile)


checkFolderExist(cancerType)

### Ask user for file names
## RNASeqV2

urlRNASeqV2 = tcgaRoot+cancerType+urlEnd_RNASeqV2

getLatestData(urlRNASeqV2, "rnaseqv2", "RNASeqV2")

## miRNA hiSeq
urlmiRNA_hi = tcgaRoot+cancerType+urlEnd_miRNASeq_hi

getLatestData(urlmiRNA_hi, "mirnaseq_hi", "miRNASeq_hi")



print "Create folder of " + cancerType

create_folder(cancerType)
create_folder(cancerType + "/Clinical")


def downloadData(fileInList, folderName, fullURL):
	print "Downloading " + fileInList  + " ..."
	dataFile = open( "./"+cancerType+ folderName + fileInList , "wb")
	curl = pycurl.Curl()
	curl.setopt(pycurl.URL, str(fullURL + fileInList) )
	curl.setopt(pycurl.WRITEDATA, dataFile)
	curl.perform()
	curl.close()
	dataFile.close()

print "Start to download TCGA Clinical data..."

cliFiles = [fullClinical_Patient , fullClinical_Analyte]

for cliFile in cliFiles:
	#print cliFile
	file = re.sub(tcgaRoot + cancerType + clinicalPath,"",cliFile)
	print "Downloading " + file + " ..."
	fp = open( "./"+cancerType+"/Clinical/" +file, "wb")
	curl = pycurl.Curl()
	curl.setopt(pycurl.URL, cliFile)
	curl.setopt(pycurl.WRITEDATA, fp)
	curl.perform()
	curl.close()
	fp.close()

### RNASeqV2 Data
## example tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/acc/cgcc/unc.edu/illuminahiseq_rnaseqv2/rnaseqv2

print "Start to download TCGA RNASeqV2 data..."

create_folder(cancerType + "/RNASeqV2")
downloadData(actualFiles_RNASeqV2,"/RNASeqV2/",urlRNASeqV2)

### miRNASeq Data
## example /tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/cesc/cgcc/bcgsc.ca/illuminahiseq_mirnaseq/mirnaseq

print "Start to download TCGA miRNASeq HiSeq data..."

create_folder(cancerType + "/miRNASeq")
downloadData(actualFiles_miRNA_hi,"/miRNASeq/",urlmiRNA_hi)
