from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from typing import List, Dict
from src.config.settings import settings

class PolicySearchService:
    """
    RAG service for searching Laya Healthcare policy rules.
    Uses Azure AI Search for semantic search.
    """
    
    def __init__(self):
        self.endpoint = settings.SEARCH_ENDPOINT
        self.key = settings.SEARCH_KEY
        self.index_name = "laya-policy-rules"
        self.search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=AzureKeyCredential(self.key)
        )
    
    def search_by_keyword(self, query: str, top: int = 3) -> List[Dict]:
        """
        Searches policy rules by keyword.
        Returns top N most relevant rules.
        """
        try:
            results = self.search_client.search(
                search_text=query,
                top=top,
                select=["rule_id", "category", "title", "description", "requires_referral", "rejection_reasons"]
            )
            
            return [dict(result) for result in results]
        except Exception as e:
            print(f"⚠️ Search error: {e}")
            return []
    
    def get_rejection_reasons(self, category: str) -> List[str]:
        """
        Gets common rejection reasons for a specific claim category.
        """
        try:
            results = self.search_client.search(
                search_text="",
                filter=f"category eq '{category}'",
                select=["rejection_reasons"]
            )
            
            reasons = []
            for result in results:
                if result.get('rejection_reasons'):
                    reasons.extend(result['rejection_reasons'].split('; '))
            
            return reasons
        except Exception as e:
            print(f"⚠️ Error fetching rejection reasons: {e}")
            return []
    
    def explain_rejection(self, rejection_reason: str) -> Dict:
        """
        Searches for policy context to explain why a claim was rejected.
        """
        results = self.search_by_keyword(rejection_reason, top=1)
        
        if results:
            rule = results[0]
            return {
                "rule_found": True,
                "category": rule.get('category'),
                "explanation": rule.get('description'),
                "common_reasons": rule.get('rejection_reasons', '').split('; ')
            }
        else:
            return {
                "rule_found": False,
                "explanation": "No matching policy rule found"
            }

# Singleton
policy_search_service = PolicySearchService()
