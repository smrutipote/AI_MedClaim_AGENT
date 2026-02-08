import json
import os
from typing import List, Dict, Optional

class PolicyService:
    """
    Service to search Laya Healthcare policy rules.
    Simulates Azure AI Search for hackathon demo.
    """
    
    def __init__(self):
        # Load policy rules from JSON
        policy_file = os.path.join(os.path.dirname(__file__), '../../data/policy_rules.json')
        with open(policy_file, 'r') as f:
            data = json.load(f)
            self.rules = data['policy_rules']
    
    def search_by_category(self, category: str) -> List[Dict]:
        """Search rules by category (e.g., 'GP_VISITS', 'CONSULTANT_VISITS')"""
        return [rule for rule in self.rules if rule['category'] == category]
    
    def search_by_keyword(self, keyword: str) -> List[Dict]:
        """Search rules containing keyword in title or description"""
        keyword_lower = keyword.lower()
        matching_rules = []
        
        for rule in self.rules:
            if (keyword_lower in rule['title'].lower() or 
                keyword_lower in rule['description'].lower()):
                matching_rules.append(rule)
        
        return matching_rules
    
    def get_rejection_reasons(self, category: str) -> List[str]:
        """Get common rejection reasons for a category"""
        rules = self.search_by_category(category)
        reasons = []
        for rule in rules:
            if 'rejection_reasons' in rule:
                reasons.extend(rule['rejection_reasons'])
        return reasons
    
    def check_referral_requirement(self, treatment_type: str) -> Dict:
        """Check if a treatment requires referral"""
        rules = self.search_by_keyword(treatment_type)
        if not rules:
            return {"requires_referral": "Unknown", "message": "Treatment type not found in policy"}
        
        rule = rules[0]
        return {
            "treatment": rule['title'],
            "requires_referral": rule.get('requires_referral', False),
            "coverage": f"{rule.get('coverage_percentage', 0)}%",
            "notes": rule['description']
        }

# Singleton
policy_service = PolicyService()
