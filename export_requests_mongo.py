import pandas as pd
from pymongo import MongoClient

def export_mongo_service_requests(mongo_uri='mongodb://localhost:27017/', db_name='service_portal', collection_name='service_request', csv_path='service_requests_export.csv'):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    data = list(collection.find())
    if data:
        df = pd.DataFrame(data)
        print(df)
        df.to_csv(csv_path, index=False)
        print(f"Exported service requests to {csv_path}")
    else:
        print("No data found in MongoDB collection.")

    client.close()


if __name__ == '__main__':
    export_mongo_service_requests()
