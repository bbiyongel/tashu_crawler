import csv
import sys
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import datetime
import json
import os
from feature_data_DB_controller import DB_controller

def get_time_id(datetime):
	day = datetime.day
	hour = datetime.hour
	datetime_str = str(day)+".%2d"%hour+"H"
	return datetime_str

def weatherDataCrawler(crnt_datetime):
	# get html
	req = urllib.request.Request("http://www.weather.go.kr/weather/observation/currentweather.jsp?stn=133")
	weather_data_page = urllib.request.urlopen(req).read()

	#parse html
	soup = BeautifulSoup(weather_data_page, 'html.parser')
	trList = soup.find_all('tr')

	crnt_feature_data = {}
	for tr in trList:
		if get_time_id(crnt_datetime) in str(tr):
			tdList = tr.find_all('td')
			crnt_feature_data['temperature'] = float(tdList[5].getText())
			crnt_feature_data['rainfall'] = tdList[8].getText()
			crnt_feature_data['humidity'] = float(tdList[9].getText())
			crnt_feature_data['windspeed'] = float(tdList[11].getText())
			break

	for key, value in crnt_feature_data.items():
		if value == '\xa0':
			crnt_feature_data[key] = 0

	crnt_feature_data['hour'] = crnt_datetime.hour
	crnt_feature_data['weekday'] = crnt_datetime.weekday()
	crnt_feature_data['month'] = crnt_datetime.month

	if crnt_datetime.month >= 3 and crnt_datetime.month < 6:
		crnt_feature_data['season'] = "1" # spring
	if crnt_datetime.month >= 6 and crnt_datetime.month < 9:
		crnt_feature_data['season'] = "2" # summer
	if crnt_datetime.month >= 9 and crnt_datetime.month < 12:
		crnt_feature_data['season'] = "3" # fall
	if crnt_datetime.month >= 12 or crnt_datetime.month < 3:
		crnt_feature_data['season'] = "4" # winter

	return crnt_feature_data

def processOnDB(db_controller, crnt_weather_data):
	currentDateTime = datetime.datetime.now()
	currentDateTime = datetime.datetime(currentDateTime.year, currentDateTime.month, currentDateTime.day, currentDateTime.hour)

	tableName = str(currentDateTime.year)+"%02d"%(currentDateTime.month)+"%02d"%(currentDateTime.day)+"_weather_status"
	if not db_controller.isTableExist(tableName):
		db_controller.createTable(tableName)
	db_controller.insertDataToTable(currentDateTime, tableName, crnt_weather_data)

def main():
	crnt_datetime = datetime.datetime.now()
	crnt_weather_data = weatherDataCrawler(crnt_datetime)
	print(crnt_weather_data)
	userId = "root"
	userPwd = "1234"
	dbName = "tashu_prediction"
	db_controller = DB_controller(userId, userPwd, dbName)
	processOnDB(db_controller, crnt_weather_data)


if __name__ == "__main__":
	main()
