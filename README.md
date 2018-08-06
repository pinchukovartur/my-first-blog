# Yandex Analytics Server


This project allows you to download data from Yandex analytics and work with this data using a server. On the server you can download python scripts that will perform all sorts of tasks.

  The project is divided into two parts:
   1. Django server responsible for launching Python scripts(run, stop and update script);
   2. Script responsible for update the MySQL database Yandex metrics.



 #Update DB algorithm
 
 
 ![alt tag](https://github.com/pinchukovartur/YandexAnalyticsServer/blob/master/doc/YandexAnalytic.png "Algorithm update db")
 
 
 # Create token
 
 1. Go to https://oauth.yandex.ru/authorize?response_type=code&client_id= {Test App. ID} (!!! not app metric app)
 2. Send POST requests.post("https://oauth.yandex.ru/token", data={"grant_type": "authorization_code", "code": "YOU CODE", "client_id": "{Test App. ID}", "client_secret": "{Test App. Key}"}) (!!! not app metric app)
