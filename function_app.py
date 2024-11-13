import azure.functions as func
# from azure.identity import DefaultAzureCredential, AzureCliCredential
# from azure.keyvault.secrets import SecretClient
import logging
import pyodbc
import os
import json
import datetime

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="databaseSelectOperation")
def databaseSelectOperation(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # creds = AzureCliCredential(additionally_allowed_tenants=["*"])
    # secret = SecretClient(vault_url="https://funckeyvault08.vault.azure.net/", credential=creds)

    # server = secret.get_secret(name="sqlServer")
    # db_name = secret.get_secret(name="database")
    # user = secret.get_secret(name="user")
    # passw = secret.get_secret(name="pass")

    # sql_conn = "Driver={ODBC Driver 17 for SQL Server};Server={0};Database={1};Uid={2};Pwd={3};".format(server, db_name, user, passw)
    # logging.info(sql_conn)

    sql_conn = os.environ["sqlconnstring"]
    #logging.info(sql_conn)

    name = req.params.get("name")
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get("name")
    
    try:
        conn = pyodbc.connect(sql_conn)
    
    except:
        logging.info("Issues while connecting!")

    else:
        cursor = conn.cursor()

        if name:
            cursor.execute("SELECT * FROM OnlineCourses where Instructor = ?", (name,))
        else:
            cursor.execute("SELECT * FROM OnlineCourses")

        records = list(cursor.fetchall())

        logging.info(records)

        #return_body = '\n'.join([str(elem) for elem in records])
        new_records = [tuple(record) for record in records]
        return_body = json.dumps(obj=new_records, indent= 2)

        return func.HttpResponse(
             return_body,
             status_code=200
        )

@app.route(route="DatabaseInsertOperation", auth_level=func.AuthLevel.FUNCTION)
def DatabaseInsertOperation(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')


    sql_conn = os.environ.get("sqlconnstring")
    try:
        conn = pyodbc.connect(sql_conn)
    except pyodbc.Error as e:
        print(f"Error: {str(e)}")
    else:
        logging.info("Db connection success!")
        cursor = conn.cursor()

        

    revText = req.params.get('rev_text')
    if not revText:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            revText = req_body.get('revText')

    if revText:
        cursor.execute("insert into StudentReviews(ReviewTime, ReviewText) VALUES (CURRENT_TIMESTAMP, ?)", (revText,))
        conn.commit()
        conn.close()
        return func.HttpResponse(f"Hello, {revText} has been inserted in the database. This HTTP triggered function executed successfully.")
    else:
        cursor.execute("insert into StudentReviews(ReviewTime, ReviewText) VALUES (CURRENT_TIMESTAMP, 'BAD_RECORD')")
        conn.commit()
        conn.close()
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a revText in the query string or in the request body for a personalized response.",
             status_code=200
        )

@app.timer_trigger(schedule="0 */2 * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def DatabaseDeleteOperation(myTimer: func.TimerRequest) -> None:

    utc_timestamm = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info(f"Python time trigger executed at {utc_timestamm}")

    conn_string = os.environ["sqlconnstring"]
    conn = pyodbc.connect(conn_string)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM StudentReviews WHERE ReviewText='BAD_RECORD'")
    conn.commit()
    
    logging.info(f"Rows deleted = {cursor.rowcount}")
    logging.info('Python timer trigger function executed.')