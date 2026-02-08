from datetime import date
from src.models.claim import ClaimForm, Dependant, ReceiptItem

# Test the models work
test_claim = ClaimForm(
    claim_id="TEST-001",
    membership_number="LAYA-9999",
    surname="Test",
    forenames="User",
    date_of_birth=date(1990, 1, 1),
    telephone="0123456789",
    correspondence_address="Test Address",
    submission_date=date(2026, 2, 7),
    status="PENDING"
)

test_claim.receipt_items = [
    ReceiptItem(claim_id="TEST-001", treatment_type="GP Visit", receipt_date=date(2026, 2, 6), cost=60.0)
]

test_claim.dependants = [
    Dependant(claim_id="TEST-001", name="Test Child", relationship="Child")
]

print("✅ Pydantic Models Working!")
print(f"Claim: {test_claim.surname}, Status: {test_claim.status}")
print(f"Receipts: {len(test_claim.receipt_items)}")
print(f"Dependants: {len(test_claim.dependants)}")

print("\n✅ File structure is correct!")
