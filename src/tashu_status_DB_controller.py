import pymysql
import datetime

class DB_controller:
	def __init__(self, userId, userPwd, dbName):
		self.connect = pymysql.connect(host = 'localhost', user = userId, password = userPwd, db = dbName)
		self.cursor = self.connect.cursor()

	"""
		function Name : isTableExist
		- check whether table "tableName" exist in DB
	"""
	def isTableExist(self, tableName):
		sql = "show tables;"

		self.cursor.execute(sql)
		table_list = self.cursor.fetchall()
	
		for table in table_list:
			if tableName in table[0]:
				return True

		return False

	"""
		function Name : createTable
		- create table
	"""
	def createTable(self, tableName):
		sql = "create table "+tableName+" (datetime varchar(20), kioskNum int, number_of_rental int, number_of_return int, crnt_rentable int)"
		self.cursor.execute(sql)

	"""
		function Name : insertDataToInitTable
		- insert new data into new table.
	"""
	def insertDataToTable(self,crnt_datetime, tableName, current_tashu_status):
		for kioskNum in range(1, 145):
			# collect status data on each kiosk_data
			status_on_kiosk = current_tashu_status.loc[current_tashu_status['kiosk_no'] == kioskNum,]
			crnt_rentable_on_kiosk = status_on_kiosk['currentRentable'].tolist()[0]
			sql = "insert into "+tableName+" (datetime, kioskNum, number_of_rental, number_of_return, crnt_rentable) values ('"+str(crnt_datetime)+"', "+str(kioskNum)+", 0, 0,"+ str(crnt_rentable_on_kiosk)+");"
			self.cursor.execute(sql)
			self.connect.commit()

	"""
		function Name : calculate_change
		- calculate change of rest bikes for 3 minutes
	"""
	def calculate_change(self,tableName, kioskNum, current_status_on_one_kiosk):
		# call previous data from db
		sql = "select * from "+tableName+" where kioskNum = "+str(kioskNum)+" and datetime in (select max(datetime) from" +tableName+")"
		self.cursor.execute(sql)
		prev_record = self.cursor.fetchall()[0]
		prev_rest_bikes = prev_record[4]

		# get current data from argument
		crnt_rest_bikes = current_status_on_one_kiosk['currentRentable'].tolist()[0]

		change_of_rest_bikes = crnt_rest_bikes - prev_rest_bikes
		
		return change_of_rest_bikes

	"""
		function Name :  get_latest_datetime
		- get latest datetime from table
	"""
	def get_latest_datetime(self, tableName):
		sql = "select max(datetime) from "+tableName
		self.cursor.execute(sql)
		result = self.cursor.fetchall()[0]
		return result[0]

	def updateTable(self,crnt_datetime, tableName, current_tashu_status):
		for kioskNum in range(1, 145):
			status_on_kiosk = current_tashu_status.loc[current_tashu_status['kiosk_no'] == kioskNum,]
			change_of_rest_bikes = self.calculate_change(tableName,kioskNum, status_on_kiosk)
			sql = ""

			if change_of_rest_bikes >= 0: # rental < return
				prev_numOfReturn = self.get_prev_record(crnt_datetime, tableName, "number_of_return")
				sql = "update "+tableName+" set number_of_return = " + str(abs(change_of_rest_bikes)+prev_numOfReturn) + ", crnt_rentable = "+str(status_on_kiosk['currentRentable'].tolist()[0])+" where datetime = '"+str(crnt_datetime)+"' and kioskNum = "+str(kioskNum)
			else: # rental > return
				prev_numOfRental = self.get_prev_record(crnt_datetime, tableName, "number_of_rental")
				sql = "update "+tableName+" set number_of_rental = " + str(abs(change_of_rest_bikes)+prev_numOfRental) + ", crnt_rentable = "+str(status_on_kiosk['currentRentable'].tolist()[0])+" where datetime = '"+str(crnt_datetime)+"' and kioskNum = "+str(kioskNum)

			self.cursor.execute(sql)
			self.connect.commit()

	def get_prev_record(self, crnt_datetime, tableName, column_name):
		sql = "select "+column_name +" from "+tableName+" where datetime = '"+str(crnt_datetime)+"'"
		self.cursor.execute(sql)
		result = self.cursor.fetchall()[0]
		return result[0]