import sys
sys.path.insert(0, '.')

from src.services.policy_service import policy_service

print("=" * 70)
print("POLICY SERVICE TEST")
print("=" * 70)

# Test 1: Search by category
print("\n🔍 TEST 1: GP Visit Rules")
gp_rules = policy_service.search_by_category("GP_VISITS")
print(f"Found {len(gp_rules)} rule(s)")
for rule in gp_rules:
    print(f"   {rule['title']}: {rule['coverage_percentage']}% coverage")

# Test 2: Check referral requirement
print("\n🔍 TEST 2: Does MRI require referral?")
mri_check = policy_service.check_referral_requirement("MRI")
print(f"   Requires referral: {mri_check['requires_referral']}")
print(f"   Coverage: {mri_check['coverage']}")

# Test 3: Get rejection reasons
print("\n🔍 TEST 3: Common rejection reasons for consultant visits")
reasons = policy_service.get_rejection_reasons("CONSULTANT_VISITS")
for i, reason in enumerate(reasons, 1):
    print(f"   {i}. {reason}")

print("\n✅ Policy Service Working!")
