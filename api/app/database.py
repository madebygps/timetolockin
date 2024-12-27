import os
from azure.cosmos import CosmosClient, PartitionKey
from dotenv import load_dotenv

load_dotenv()

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DB_NAME = os.getenv("COSMOS_DB_NAME")

client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.create_database_if_not_exists(id=COSMOS_DB_NAME)

users_container = database.create_container_if_not_exists(
    id="users",
    partition_key=PartitionKey(path="/id"),
    offer_throughput=400
)

sessions_container = database.create_container_if_not_exists(
    id="sessions",
    partition_key=PartitionKey(path="/user_id"),
    offer_throughput=400
)