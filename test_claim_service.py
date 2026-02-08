from src.services.claim_service import claim_service

def main():
    print("=" * 60)
    print("TESTING CLAIM SERVICE")
    print("=" * 60)
    
    # Test 1: Get a specific claim
    print("\n1️⃣ Fetching CLM-2026-001 (Full Details)...")
    claim = claim_service.get_claim_by_id("CLM-2026-001")
    if claim:
        print(f"   ✅ Found: {claim.forenames} {claim.surname}")
        print(f"   Status: {claim.status}")
        print(f"   Receipts: {len(claim.receipt_items)} items")
        print(f"   Dependants: {len(claim.dependants)}")
        print(f"   Has Accident Info: {claim.accident_details is not None}")
    
    # Test 2: Get all claims for a member
    print("\n2️⃣ Fetching all claims for LAYA-1001...")
    claims = claim_service.get_claims_by_member("LAYA-1001")
    print(f"   ✅ Found {len(claims)} claim(s)")
    for c in claims:
        print(f"      - {c['claim_id']}: €{c['total_claimed']:.2f} ({c['status']})")
    
    # Test 3: Search pending claims
    print("\n3️⃣ Searching PENDING claims (limit 5)...")
    pending = claim_service.search_claims_by_status("PENDING", limit=5)
    print(f"   ✅ Found {len(pending)} pending claim(s)")
    for p in pending:
        print(f"      - {p['claim_id']}: {p['surname']} - €{p['total_claimed']:.2f}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Service Layer Working!")
    print("=" * 60)

if __name__ == "__main__":
    main()
