import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure.cosmos import CosmosClient
from src.config.settings import settings
from datetime import date

def seed_member_profiles():
    """
    Seeds Cosmos DB with member profiles including interaction history.
    This simulates the 'CRM' where call logs and notes are stored.
    """
    client = CosmosClient(settings.COSMOS_ENDPOINT, credential=settings.COSMOS_KEY)
    database = client.get_database_client("MemberDB")
    container = database.get_container_client("MemberContainer")
    
    # Member profiles with rich interaction history
    members = [
        {
            "id": "LAYA-1001",
            "name": "John Doe",
            "plan": "Simply Connect Plus",
            "tier": "Gold",
            "email": "john.doe@email.com",
            "phone": "085-123-4567",
            "address": "123 Main St, Dublin 2",
            "date_of_birth": "1985-03-15",
            "interaction_notes": [
                {
                    "date": "2026-01-20",
                    "type": "Phone Call",
                    "agent": "Sarah Murphy",
                    "note": "Member called to confirm Beacon Hospital is in-network for MRI scans. Confirmed yes, Direct Settlement applies."
                },
                {
                    "date": "2026-01-21",
                    "type": "Document Upload",
                    "agent": "System",
                    "note": "Member uploaded GP Referral Letter (Valid until 2026-07-21) for neurological consultation."
                },
                {
                    "date": "2025-12-10",
                    "type": "Policy Update",
                    "agent": "System",
                    "note": "Loyalty Bonus activated - Additional 10% coverage on diagnostic scans for 2026."
                }
            ],
            "uploaded_documents": [
                {
                    "document_id": "DOC-2026-001",
                    "type": "GP Referral Letter",
                    "upload_date": "2026-01-21",
                    "valid_until": "2026-07-21",
                    "provider": "Dr. Smith GP",
                    "reason": "MRI Brain - Investigation of recurring headaches"
                }
            ],
            "policy_details": {
                "plan_name": "Simply Connect Plus",
                "start_date": "2024-01-01",
                "renewal_date": "2027-01-01",
                "annual_limit": 5000.00,
                "used_to_date": 460.00,
                "loyalty_bonus_active": True
            }
        },
        {
            "id": "LAYA-1022",
            "name": "Laura Nolan",
            "plan": "Simply Connect Plus",
            "tier": "Silver",
            "email": "laura.nolan@email.com",
            "phone": "087-234-8901",
            "address": "78 West End, Roscommon",
            "date_of_birth": "1990-08-14",
            "interaction_notes": [
                {
                    "date": "2026-01-10",
                    "type": "Email",
                    "agent": "System",
                    "note": "Member received automated reminder: Consultant visits require valid GP referral (within 6 months)."
                }
            ],
            "uploaded_documents": [
                {
                    "document_id": "DOC-2025-987",
                    "type": "GP Referral Letter",
                    "upload_date": "2025-06-15",
                    "valid_until": "2025-12-15",
                    "provider": "Dr. O'Brien GP",
                    "reason": "Dermatology consultation - skin condition"
                }
            ],
            "policy_details": {
                "plan_name": "Simply Connect Plus",
                "start_date": "2025-06-01",
                "renewal_date": "2026-06-01",
                "annual_limit": 5000.00,
                "used_to_date": 0.00,
                "loyalty_bonus_active": False
            }
        }
    ]
    
    print("☁️ Seeding Cosmos DB with member profiles...")
    for member in members:
        container.upsert_item(member)
        print(f"   ✅ Added: {member['name']} ({member['id']})")
    
    print(f"\n✅ {len(members)} member profiles seeded successfully!")

if __name__ == "__main__":
    seed_member_profiles()
