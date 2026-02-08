import sys
sys.path.insert(0, '.')

from src.services.cosmos_service import cosmos_service
from src.agents.self_healing_agent import self_healing_agent

print("=" * 70)
print("SELF-HEALING AGENT - CLAIM RESCUE DEMONSTRATION")
print("=" * 70)

# Verify Cosmos
print("\n🔍 Verifying Cosmos DB...")
member = cosmos_service.get_member_profile("LAYA-1001")
if member:
    print(f"✅ Found: {member['name']}")
    print(f"   Documents: {len(member.get('uploaded_documents', []))}")
else:
    print("❌ Cosmos not accessible")
    exit(1)

# Test rejected claim rescue
print("\n\n" + "=" * 70)
print("🧪 TEST: CLM-2026-022 (Rejected - Missing Referral)")
print("=" * 70)
print("Expected: Agent finds referral in Cosmos and auto-approves\n")

result = self_healing_agent.adjudicate_claim("CLM-2026-022")

print("\n" + "=" * 70)
print("📊 DECISION:", result['decision'])
print("📝 REASON:", result['reason'])
print("=" * 70)
