import pyodbc 

sql_conn = "Driver={ODBC Driver 17 for SQL Server};Server=tcp:serverfunc.database.windows.net,1433;Database=sqlfunc;Uid=sqladmin;Pwd=Pantelimon86$;"
   
try:
   conn = pyodbc.connect(sql_conn)
    
except:
   raise("Issues while connecting!")

else:
   cursor = conn.cursor()
   cursor.execute("SELECT * FROM OnlineCourses")

   records = list(cursor.fetchall())
   print(records)

