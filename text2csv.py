#!/usr/bin/env

import sys
import csv
import io

'''
Reads a text file in tab-delimited format with following 4 headers:

	doc_index, text, predicted_annotation, actual_annotation

And outputs a text file in comma-separated format with following 3 headers:

	text, golden intent/slots, predicted intent/slots

'''

rows = []
with open(sys.argv[1], 'r') as inFile:
	next(inFile)
	reader = csv.reader(inFile, delimiter='\t')
	for index,text,prediction,actual in reader:
		rows.append([text,actual,prediction])

with open(sys.argv[2], 'w') as outFile:
	writer = csv.writer(outFile, delimiter=',')
	writer.writerow(["text", "golden intent/slots", "predicted intent/slots"])
	for row in rows:
		writer.writerow(row)