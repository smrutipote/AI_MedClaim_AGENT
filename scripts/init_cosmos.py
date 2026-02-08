import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure.cosmos import CosmosClient, PartitionKey
from src.config.settings import settings

def init_cosmos_structure():
    """Creates the Cosmos Database and Container if they don't exist."""
    print("🔧 Initializing Cosmos DB structure...")
    
    client = CosmosClient(settings.COSMOS_ENDPOINT, credential=settings.COSMOS_KEY)
    
    # Create Database
    try:
        database = client.create_database_if_not_exists(id="MemberDB")
        print("   ✅ Database 'MemberDB' ready")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return
    
    # Create Container with Partition Key (Serverless - no throughput)
    try:
        container = database.create_container_if_not_exists(
            id="MemberContainer",
            partition_key=PartitionKey(path="/id")
        )
        print("   ✅ Container 'MemberContainer' ready")
    except Exception as e:
        print(f"   ❌ Container error: {e}")
        return
    
    print("\n🎉 Cosmos DB initialization complete!")

if __name__ == "__main__":
    init_cosmos_structure()
