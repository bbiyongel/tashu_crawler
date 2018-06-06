import pymysql
import datetime

class DB_controller:
	def __init__(self, userId, userPwd, dbName):
		self.connect = pymysql.connect(host = 'localhost', user = userId, password = userPwd, db = dbName)
		self.cursor = self.connect.cursor()

	def createTable(self, tableName):
		sql = "create table "+tableName+" (datetime varchar(20), month int, weekday int, season int, hour int, temperature int, humidity int, windspeed int, rainfall int)"
		self.cursor.execute(sql)

	def insertDataToTable(self, crnt_datetime, tableName, crnt_feature_data):
		sql = "insert into "+tableName+" (datetime, month, weekday, season, hour, temperature, humidity, windspeed, rainfall) values ('"+str(crnt_datetime)+"', "+str(crnt_feature_data['month'])+", "+str(crnt_feature_data['weekday'])+", "+str(crnt_feature_data['season'])+", "+str(crnt_feature_data['hour'])+", "+str(crnt_feature_data['temperature'])+", "+str(crnt_feature_data['humidity'])+", "+str(crnt_feature_data['windspeed'])+", "+str(crnt_feature_data['rainfall'])+")"
		self.cursor.execute(sql)
		self.connect.commit()

	