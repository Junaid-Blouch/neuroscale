import os
import requests
import gzip
import shutil

DATA_URL = "https://storage.googleapis.com/clusterdata-2011-2/task_usage/part-00000-of-00500.csv.gz"

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_folder = os.path.join(base_path, "data")
os.makedirs(data_folder, exist_ok=True)

gz_path = os.path.join(data_folder, "cluster_data.csv.gz")
csv_path = os.path.join(data_folder, "real_workload.csv")

def download_dataset():
    if os.path.exists(csv_path):
        print("✅ Dataset already exists.")
        return

    print("⬇ Downloading dataset...")
    response = requests.get(DATA_URL, stream=True)

    with open(gz_path, "wb") as f:
        f.write(response.content)

    print("✅ Download complete.")

    print("📦 Extracting dataset...")
    with gzip.open(gz_path, 'rb') as f_in:
        with open(csv_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    print("✅ Extraction complete.")

if __name__ == "__main__":
    download_dataset()