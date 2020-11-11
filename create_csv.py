import csv, json

"""
this is a really basic way of getting the json into
a format i can make graphs in excel with lol
i was thinking about keeping this out of the git, but hey
it might be useful to someone.
"""
def get_data():
    with open("covid_data.json") as f:
        rawData = json.load(f)
    with open("covid_data.csv", 'w', newline='') as g:
        writer = csv.writer(g)
        writer.writerow(["Date", "Confirmed", "Active", "Recovered", "Deaths"])
        for day in rawData:
            writer.writerow([day["DATE"], day["CONFIRMED"], day["ACTIVE"], day["RECOVERED"], day["DEATHS"]])

if __name__ == '__main__':
	get_data()
