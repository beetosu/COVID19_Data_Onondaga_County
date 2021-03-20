import urllib.request, urllib.parse, json, datetime, time

monthAbbr = {"JAN": "1", "FEB": "2", "MAR": "3", "APR": "4", "MAY": "5", "JUN": "6", "JUL": "7", "AUG": "8", "SEP": "9", "OCT": "10", "NOV": "11", "DEC": "12"}

# this is mostly just because i don't like how the county labels dates
def convert_date(date):
	date_split = date.split(" ")
	month = monthAbbr[date_split[0][:3]]
	day = date_split[0][3:]
	return month + "/" + day + "/" + date_split[1]

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
	# since the actual filename we want is always changing, we find the current one that we actually need
	# (Case_Mapping_By_Municipality) and then work with that
	dataParams = "/1/query?f=json&where=1=1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outSR=102100&resultOffset=0&resultRecordCount=4000&resultType=standard&cacheHint=true"
	allServices = "https://services3.arcgis.com/6QuzuucBh0MLJk7u/arcgis/rest/services?f=pjson"
	allContent = urllib.request.urlopen(allServices).read().decode()
	allSites = json.loads(allContent)["services"]
	site = None
	for service in allSites:
		serviceName = " ".join(service["name"].split("_")[:4])
		if serviceName == "Case mapping by municipality":
			site = service["url"]
			break
	# should the expected service not be there, print an error message
	if site == None:
		print("!!ERROR!! COVID data service not found!")
		print("Check the county's API site to see if the site has changed the name scheme: ")
		print("https://services3.arcgis.com/6QuzuucBh0MLJk7u/arcgis/rest/services")
		return
	url = site + dataParams
	content = urllib.request.urlopen(url).read().decode()
	data = json.loads(content)
	#should the parameters be invalid, print an error message
	if "error" in data:
		print("!!ERROR!! INVALID DATA PARAMS")
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
