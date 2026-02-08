from azure.cosmos import CosmosClient
from typing import Optional, Dict, List
from src.config.settings import settings

class CosmosService:
    def __init__(self):
        self.client = CosmosClient(settings.COSMOS_ENDPOINT, credential=settings.COSMOS_KEY)
        self.database = self.client.get_database_client("MemberDB")
        self.container = self.database.get_container_client("MemberContainer")

    def get_member_profile(self, member_id: str) -> Optional[Dict]:
        """Fetches full member profile with interaction history."""
        try:
            item = self.container.read_item(item=member_id, partition_key=member_id)
            return item
        except Exception as e:
            print(f"⚠️ Member {member_id} not found: {e}")
            return None
    
    def search_interaction_notes(self, member_id: str, keyword: str) -> List[Dict]:
        """
        Searches member's interaction history for specific keywords.
        This is the 'Detective' capability.
        """
        member = self.get_member_profile(member_id)
        if not member or 'interaction_notes' not in member:
            return []
        
        matching_notes = [
            note for note in member['interaction_notes']
            if keyword.lower() in note['note'].lower()
        ]
        return matching_notes
    
    def find_uploaded_document(self, member_id: str, doc_type: str) -> Optional[Dict]:
        """
        Searches for a specific document type in member's upload history.
        Example: doc_type = "GP Referral Letter"
        """
        member = self.get_member_profile(member_id)
        if not member or 'uploaded_documents' not in member:
            return None
        
        for doc in member['uploaded_documents']:
            if doc['type'].lower() == doc_type.lower():
                return doc
        return None

# Singleton
cosmos_service = CosmosService()