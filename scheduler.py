import schedule
import time
import os

def retrain():
    print("Running scheduled retraining...")
    os.system("python adaptive_retrainer.py")

schedule.every().day.at("02:00").do(retrain)

while True:
    schedule.run_pending()
    time.sleep(60)