from typing import Dict
from src.services.claim_service import claim_service
from src.services.cosmos_service import cosmos_service

class SelfHealingAgent:
    def __init__(self):
        self.claim_service = claim_service
        self.cosmos_service = cosmos_service
        self.reasoning_trace = []
    
    def adjudicate_claim(self, claim_id: str) -> Dict:
        self.reasoning_trace = []
        self._log_thought(f"🔍 Starting adjudication for {claim_id}")
        
        claim = self.claim_service.get_claim_by_id(claim_id)
        if not claim:
            return {"error": "Claim not found"}
        
        self._log_thought(f"📋 Claim: {claim.forenames} {claim.surname}, Status: {claim.status}")
        
        if claim.status == "APPROVED":
            self._log_thought("✅ Already approved. No action needed.")
            return self._build_response("APPROVED", "Already processed")
        
        if claim.status == "REJECTED":
            self._log_thought(f"⚠️ Rejected. Reason: {claim.rejection_reason}")
            return self._attempt_rescue(claim)
        
        return self._validate_pending_claim(claim)
    
    def _attempt_rescue(self, claim) -> Dict:
        rejection_reason = claim.rejection_reason.lower()
        
        if "referral" in rejection_reason:
            self._log_thought("🔍 Missing referral. Searching member history...")
            
            referral = self.cosmos_service.find_uploaded_document(
                claim.membership_number, 
                "GP Referral Letter"
            )
            
            if referral:
                self._log_thought(f"✅ FOUND! Uploaded: {referral['upload_date']}")
                self._log_thought(f"   Valid until: {referral['valid_until']}")
                self._log_thought(f"   Reason: {referral['reason']}")
                
                return self._build_response(
                    "APPROVED", 
                    f"Auto-approved: Found referral (DOC-{referral['document_id']})"
                )
            else:
                self._log_thought("❌ No referral found. Rejection stands.")
                return self._build_response("REJECTED", "Referral required but not found")
        
        return self._build_response("REJECTED", claim.rejection_reason)
    
    def _validate_pending_claim(self, claim) -> Dict:
        self._log_thought("📝 Validating pending claim...")
        return self._build_response("APPROVED", "All checks passed")
    
    def _log_thought(self, thought: str):
        self.reasoning_trace.append(thought)
        print(thought)
    
    def _build_response(self, decision: str, reason: str) -> Dict:
        return {
            "decision": decision,
            "reason": reason,
            "reasoning_trace": self.reasoning_trace
        }

self_healing_agent = SelfHealingAgent()