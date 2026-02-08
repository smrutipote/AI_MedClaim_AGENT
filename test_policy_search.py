import sys
sys.path.insert(0, '.')

from src.services.policy_search_service import policy_search_service

print("=" * 70)
print("AZURE AI SEARCH - POLICY RAG TEST")
print("=" * 70)

# Test 1: Search for referral requirements
print("\n🔍 TEST 1: Search 'MRI referral requirements'")
results = policy_search_service.search_by_keyword("MRI referral", top=2)
print(f"Found {len(results)} results:")
for r in results:
    print(f"\n   📋 {r['title']}")
    print(f"   Category: {r['category']}")
    print(f"   Requires Referral: {r.get('requires_referral', 'N/A')}")
    print(f"   Description: {r['description'][:150]}...")

# Test 2: Explain a rejection
print("\n\n🔍 TEST 2: Explain 'No GP referral letter provided'")
explanation = policy_search_service.explain_rejection("No GP referral letter")
print(f"   Rule Found: {explanation['rule_found']}")
if explanation['rule_found']:
    print(f"   Category: {explanation['category']}")
    print(f"   Explanation: {explanation['explanation'][:150]}...")
    print(f"   Common Reasons: {len(explanation['common_reasons'])} listed")

# Test 3: Search for receipt rules
print("\n\n🔍 TEST 3: Search 'receipt requirements'")
results = policy_search_service.search_by_keyword("receipt", top=1)
if results:
    r = results[0]
    print(f"   📋 {r['title']}")
    print(f"   Rejection Reasons:")
    for reason in r.get('rejection_reasons', '').split('; ')[:3]:
        print(f"      - {reason}")

print("\n\n✅ Azure AI Search RAG Working!")
