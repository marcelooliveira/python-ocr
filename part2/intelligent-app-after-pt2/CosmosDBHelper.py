import os
import azure.cosmos.cosmos_client as cosmos_client

class CosmosDBHelper:
    def __init__(self):
        self.cosmos_database_id = os.environ["COSMOS_DATABASE_ID"]
        self.cosmos_image_analysis_container_id = os.environ["COSMOS_IMAGE_ANALYSIS_CONTAINER_ID"]
        self.cosmos_aggregate_results_container_id = os.environ["COSMOS_AGGREGATE_RESULTS_CONTAINER_ID"]
        cosmos_account_host = os.environ["COSMOS_ACCOUNT_HOST"]
        cosmos_account_key = os.environ["COSMOS_ACCOUNT_KEY"]
        self.client = cosmos_client.CosmosClient(cosmos_account_host, {'masterKey': cosmos_account_key})

    def create_analysis(self, document):
        db = self.client.get_database_client(self.cosmos_database_id)
        container = db.get_container_client(self.cosmos_image_analysis_container_id)
        return container.upsert_item(document)
    
    def create_aggregate_result(self, inserted_id, aggregate_result):
        db = self.client.get_database_client(self.cosmos_database_id)
        container = db.get_container_client(self.cosmos_aggregate_results_container_id)
        entity = {
            "id": inserted_id,
            "partitionKey": "Partition1",
            "sum": float(aggregate_result["sum"]),
            "average": float(aggregate_result["average"]),
            "median": float(aggregate_result["median"]),
            "min": float(aggregate_result["min"]),
            "max": float(aggregate_result["max"])
        }
        return container.upsert_item(entity)
