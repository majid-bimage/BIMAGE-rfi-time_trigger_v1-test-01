import datetime
import logging

import azure.functions as func

app = func.FunctionApp()
server_name = "bimageforge.database.windows.net"
database_name = "bimageforge"
username = "forge"
password = "BimageNow2020"

conn_str = (
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server={server_name};"
        f"Database={database_name};"
        f"UID={username};"
        f"PWD={password};"
    )


async def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    access_token = await get_access_token()
    logging.info(access_token)
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

async def get_access_token():
    # conn = pyodbc.connect(conn_str)

    # cursor = conn.cursor() 

    # get_token_query = "SELECT TOP (1) [email]      ,[access_token]      ,[headers]      ,[expiry_epoch]      ,[expiry]  FROM [dbo].[AccLoginTokens]"
    # cursor.execute(get_token_query)
    # token_data = cursor.fetchone()
    # access_token = token_data.access_token if token_data else None
    # cursor.close()
    # conn.close()
    # access_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjY0RE9XMnJoOE9tbjNpdk1NU0xlNGQ2VHEwUV9SUzI1NiIsInBpLmF0bSI6ImFzc2MifQ.eyJzY29wZSI6WyJhY2NvdW50OnJlYWQiLCJhY2NvdW50OndyaXRlIiwiYnVja2V0OmNyZWF0ZSIsImJ1Y2tldDpyZWFkIiwiYnVja2V0OnVwZGF0ZSIsImJ1Y2tldDpkZWxldGUiLCJkYXRhOnJlYWQiLCJkYXRhOndyaXRlIiwiZGF0YTpjcmVhdGUiLCJkYXRhOnNlYXJjaCIsInVzZXI6cmVhZCIsInVzZXI6d3JpdGUiLCJ1c2VyLXByb2ZpbGU6cmVhZCIsInZpZXdhYmxlczpyZWFkIl0sImNsaWVudF9pZCI6IktrSmZwTVoyZ2NBWEEzZ25EUkdod3Z5UDdaSG1tV25aIiwiaXNzIjoiaHR0cHM6Ly9kZXZlbG9wZXIuYXBpLmF1dG9kZXNrLmNvbSIsImF1ZCI6Imh0dHBzOi8vYXV0b2Rlc2suY29tIiwianRpIjoiQWk4UFRPSmx6WExPamNoTFk5eDc0WGQzQzhNdVBhaXRoV0lQYzdPNGtHNWNkeWhpZlBLVjlFV3NSRkdKTlNueiIsImV4cCI6MTcwODc3OTQ2OCwidXNlcmlkIjoiRjRSMjdaTEhKM0RNRkRENiJ9.G4lfRWmQZpOjUgTsniWjCt2usHBj0ofxkj5-ET5kRhKKlUX-Rh8MBk156-YBzMBhDiUgSkaXjL5z2T2A9ahKJVssspPP7ZTSgW3qYcn8epruogluuTy9O-2RMdC-PTGM-aLgdyw5Q84_svFCgav8S0btl7aJlfubuc0Se9pgjWoVYxGu_oGUwHkIqw1uty9gyhLfM6zzqsBmEfGligs7Byu7nLMzSk7s2hiOYpKOX5V4oTUxEDIok6hfzSBqnl5a_CT4e_1msODOE2zmgr3mPr_Bzj0abHxwOwxaaxKn3wV7cJmNBx3fRDIuksa5xWQaGJLS6LOAuX68wSSEJEUt7g"


    conn = pymssql.connect('bimageforge.database.windows.net', 'forge', 'BimageNow2020', 'bimageforge')
    cursor = conn.cursor()
        
    cursor.execute('select access_token from AccLoginTokens where expiry > getdate()')

    access_token = ''

    for r in cursor:    
        access_token = r[0]
        print(access_token)
    
    if access_token == '':
        cursor.execute('select headers from AccLoginTokens')
        for r in cursor:    
            headers = json.loads(r[0])  
                
            rs = requests.get('https://login.acc.autodesk.com/api/v1/authentication/refresh?currentUrl=https%3A%2F%2Facc.autodesk.com%2Fprojects', headers=headers, data='')
            
            js = json.loads(rs.text)
            access_token = js['accessToken']
            expiry = js['expiresAt']
            cursor.execute(f"update AccLoginTokens set access_token = '{access_token}' , expiry = '{expiry}'")
            conn.commit()

    return access_token