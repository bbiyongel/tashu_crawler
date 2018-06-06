from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
import json
import datetime
from tashu_status_DB_controller import DB_controller

"""
	function Name : currentStatusCrawler
	- crawl the current status(the number of rest bikes) of total tashu system
"""
def currentStatusCrawler():
	url = 'https://www.tashu.or.kr/userpage/station/mapStatus.jsp?flg=main'

	## execute chrome incognito mode
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument("--incognito")
	chrome_options.add_argument('headless')
	driver = webdriver.Chrome("/home/minjiwon/tashu_crawler/linux_chromedriver/chromedriver", chrome_options=chrome_options)

	## connect to tashu web server
	driver.get(url)
	stationStatus = []
	#jsSourcecode = ("var strData;"+
	#	"strData = GDownloadUrl('/mapAction.do?process=statusMapView',"+
	#	" function(data, responseCode) {return data;}); ")

	jsSourcecode = ("var strData;"+
		"GDownloadUrl('/mapAction.do?process=statusMapView',"+
		"function(data, response){ dataDiv = document.createElement('div');"+
		"dataDiv.setAttribute('id', 'dataDiv');dataDiv.innerHTML = data;"+
		"document.body.appendChild(dataDiv);"+
		"}); ")

	# execute js code and get current status data
	data = driver.execute_script(jsSourcecode)

	time.sleep(10)
	dataDIV = driver.find_element_by_id('dataDiv')
	dataTxt = dataDIV.text

	return dataTxt

"""
	function Name : parseData
	- parse data from tashu web and convert it to pandas.DataFrame
"""
def parseData(data):
	# Convert data from tashu web to json format
	jsonData = json.loads(data)
	stationData = jsonData['markers']
	returnDF = pd.DataFrame()

	currentDateTime = datetime.datetime.now()
	currentDateTime = datetime.datetime(currentDateTime.year, currentDateTime.month, currentDateTime.day, currentDateTime.hour)
	for station in stationData:
		stationNum = int(station['kiosk_no'])
		cntRackTotal = 0
		cntRentable = 0

		if stationNum > 0 and stationNum < 145:
			cntRackTotal = int(station['cntRackTotal'])
			cntRentable = int(station['cntRentable'])
			kiosk_no = int(station['kiosk_no'])

			returnDF = returnDF.append({'currentDateTime':currentDateTime, 'kiosk_no':stationNum, 'currentRentable':cntRentable, 'currentRackTotal':cntRackTotal},ignore_index=True)

	return returnDF

"""
	function Name : processOnDB
	- store current tashu status data to DB
"""

def processOnDB(db_controller, current_tashu_status):
	# get current time
	currentDateTime = datetime.datetime.now()
	currentDateTime = datetime.datetime(currentDateTime.year, currentDateTime.month, currentDateTime.day, currentDateTime.hour)
	# table Name
	tableName = str(currentDateTime.year)+"%02d"%(currentDateTime.month)+"%02d"%(currentDateTime.day)+"_tashu_status"

	if db_controller.isTableExist(tableName):
		# today's table already exist

		latest_datetime = db_controller.get_latest_datetime(tableName)
		latest_datetime = datetime.datetime.strptime(latest_datetime, "%Y-%m-%d %H:%M:%S")

		if currentDateTime.hour != latest_datetime.hour:
			db_controller.insertDataToTable(currentDateTime, tableName, current_tashu_status)

		else:
			db_controller.updateTable(currentDateTime, tableName, current_tashu_status)
	else:
		# start of the day & create new Table
		db_controller.createTable(tableName)
		db_controller.insertDataToTable(currentDateTime,tableName, current_tashu_status)


def main():
	# crawl current status data
	currentTashuData = currentStatusCrawler()
	# parse current status data
	currentTashuStatus = parseData(currentTashuData)
	# file write - parsed data

	userId = "root"
	userPwd = "1234"
	dbName = "tashu_prediction"
	db_controller = DB_controller(userId, userPwd, dbName)
	processOnDB(db_controller, currentTashuStatus)

if __name__ == "__main__":
	main()