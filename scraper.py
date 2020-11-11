import urllib.request, urllib.parse, json, datetime

#this is mostly just because i don't like how the county labels dates
def convert_date(date):
	monthAbbr = {"JAN": "1", "FEB": "2", "MAR": "3", "APR": "4", "MAY": "5", "JUN": "6", "JUL": "7", "AUG": "8", "SEP": "9", "OCT": "10", "NOV": "11", "DEC": "12"}
	return monthAbbr[date[:3]] + "/" + date[3:]

#since the current days info is usually not uploaded until later in the afternoon,
#its far more likely the data for the day before exists
def get_yesterday():
	theDay = datetime.datetime.now() - datetime.timedelta(days=1)
	formattedTime = theDay.strftime("%B_%d")
	#remove the leading zero from the day (oops)
	dateArr = formattedTime.split("_")
	if dateArr[1][0] == "0":
		dateArr[1] = dateArr[1][1:]
	print(dateArr)
	return dateArr[0] + "_" + dateArr[1]

def get_data():
	clean_data = []
	yesterday = get_yesterday()
	print("finding data for " + yesterday.replace("_", " ") + "...")
	#its entirely possible this format will suddenly change, i'll try to keep on top of that.
	url = "https://services3.arcgis.com/6QuzuucBh0MLJk7u/arcgis/rest/services/Case_mapping_by_municipality_" + yesterday + "/FeatureServer/1/query?f=json&where=1=1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outSR=102100&resultOffset=0&resultRecordCount=4000&resultType=standard&cacheHint=true"
	content = urllib.request.urlopen(url).read().decode()
	data = json.loads(content)
	#should data not exist for the day before, try the last week
	if "error" in data:
		#sleep, so i don't get ip banned
		sleep(2)
		today = datetime.datetime.now()
		days_tried = 0
		day = int(yesterday.split("_")[1])
		month = yesterday.split("_")[0]
		while "error" in data and days_tried < 7:
			print("data for " + month + " " + str(day) + " not found!")
			day -= 1
			if day == 0:
				lastMonth = datetime.date(today.year, today.month, 1) - datetime.timedelta(days=1)
				day = lastMonth.day
				month = lastMonth.strftime("%B")
			print("trying " + month + " " + str(day) + "...")
			url = "https://services3.arcgis.com/6QuzuucBh0MLJk7u/arcgis/rest/services/Case_mapping_by_municipality_" + yesterday + "/FeatureServer/1/query?f=json&where=1=1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outSR=102100&resultOffset=0&resultRecordCount=4000&resultType=standard&cacheHint=true"
			content = urllib.request.urlopen(url).read().decode()
			data = json.loads(content)
			days_tried += 1
		#if data still isn't found, just give up.
		if "error" in data:
			print("data for the past week not found!")
			return
	#this is all the data from the map that seems intresting without the context of the map
	#(ommitted in this is OBJECTID, Shape__Area, and Shape__Length)
	for date in data["features"]:
		dateData = date["attributes"]
		clean_data.append({"DATE": convert_date(dateData["DATE"]), "CONFIRMED": dateData["CONFIRMED"], "ACTIVE": dateData["ACTIVE"], "RECOVERED": dateData["RECOVERED"], "DEATHS": dateData["DEATHS"]})
	#creates (or overrites should covid_data.json already exist) a file named "covid_data.json"
	with open("covid_data.json", 'w') as f:
		f.write(json.dumps(clean_data, indent=4))
	print("data written to covid_data.json!")

if __name__ == '__main__':
	get_data()
