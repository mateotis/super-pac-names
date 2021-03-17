from bs4 import BeautifulSoup as bs
import requests
import urllib
import csv

YEAR = 2020 # Change this to select which year's data to parse/analyse 

def parser(): # Parses super PAC data from OpenSecrets database
	fileName = "OpenSecrets-" + str(YEAR) + ".html"
	soup = bs(open(fileName),"html.parser") # We have the file downloaded as the website uses a Captcha

	table = soup.find("table", class_="DataTable datadisplay dataTable no-footer")

	pacList = []

	for i in range(1,2000):
		row = table.find_all("tr")[i]
		pacMoney = row.find_all("td")[1].text
		if(pacMoney == "$0"): # Only consider PACs that have actually spent something
			break
		pacMoney = int(pacMoney.translate({ord(i): None for i in '$,'})) # A handy function to remove all specified characters from the string
		pacName = row.find("a").text
		pacName = pacName.strip() # Remove trailing whitespaces
		pacLean = row.find_all("td")[2].text

		#print(pacName, pacMoney, pacLean)
		pacList.append([pacName, pacMoney, pacLean])

	with open("superPACs.csv", mode='w', encoding = "UTF-8") as superPACs: # Write results to csv
		fieldnames = ["Name", "Money", "Lean"]
		writer = csv.DictWriter(superPACs, fieldnames=fieldnames)
		writer.writeheader()
		for i in pacList:
			writer.writerow({"Name": i[0], "Money": i[1],"Lean": i[2]})	

	return pacList

def analyser(pacList): # Puts together list of all the words that occur in PAC names, adding up the sum of money belonging to each word and its frequency
	wordList = []

	i = 0
	for entry in pacList:
		pacWords = entry[0].split(" ")
		pacMoney = entry[1]
		pacLean = entry[2]

		for word in pacWords:
			wordInList = False

			if(i == 0): # Add the first entry's words without any checks as they don't repeat and thus we'll have something to check against later
				wordList.append([word, pacLean, pacMoney, 1]) # The last element is the number of PAC names this word shows up in
				continue

			for w in wordList: # For each word in a name, we see if it's already in the list WITH the same political lean
				if(w[0] == word and w[1] == pacLean):
					w[2] += pacMoney # Add the amount to the tally
					w[3] += 1 # Increment the word's PAC counter
					wordInList = True
					break

			if(wordInList == False):
				wordList.append([word, pacLean, pacMoney, 1]) # If not in the list, add it

		i += 1

	wordList = sorted(wordList, key=lambda x: x[3], reverse = True) # Sort list by frequency in descending order

	for i in wordList:
		print(i[0], i[1], i[2], i[3])

	csvName = "superPACs-" + str(YEAR) + ".csv"
	with open(csvName, mode='w', encoding = "UTF-8") as pacWords: # Write results to csv
		fieldnames = ["Name", "Lean", "Money", "Frequency"]
		writer = csv.DictWriter(pacWords, fieldnames=fieldnames)
		writer.writeheader()
		for i in wordList:
			writer.writerow({"Name": i[0], "Lean": i[1], "Money": i[2], "Frequency": i[3]})	

pacList = parser()
analyser(pacList)