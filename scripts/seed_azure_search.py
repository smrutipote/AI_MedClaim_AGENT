import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType
)
from src.config.settings import settings

def create_policy_index():
    """Creates the Azure Search index for policy rules."""
    
    endpoint = settings.SEARCH_ENDPOINT
    key = settings.SEARCH_KEY
    index_name = "laya-policy-rules"
    
    credential = AzureKeyCredential(key)
    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
    
    # Delete existing index if it exists
    try:
        print(f"🗑️  Deleting existing index '{index_name}'...")
        index_client.delete_index(index_name)
        print(f"   ✅ Index deleted")
    except Exception as e:
        print(f"   ℹ️ Index doesn't exist yet: {type(e).__name__}")
    
    # Define index schema - simplified (no arrays for now)
    fields = [
        SimpleField(name="rule_id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="plan", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="description", type=SearchFieldDataType.String),
        SimpleField(name="coverage_percentage", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
        SimpleField(name="requires_referral", type=SearchFieldDataType.Boolean, filterable=True),
        SearchableField(name="rejection_reasons", type=SearchFieldDataType.String),
        SearchableField(name="notes", type=SearchFieldDataType.String)
    ]
    
    index = SearchIndex(name=index_name, fields=fields)
    
    try:
        print(f"🔧 Creating index '{index_name}'...")
        index_client.create_or_update_index(index)
        print(f"   ✅ Index created successfully")
    except Exception as e:
        print(f"   ⚠️ Error creating index: {e}")
    
    return index_name

def seed_policy_documents():
    """Seeds Azure Search with Laya policy rules."""
    
    endpoint = settings.SEARCH_ENDPOINT
    key = settings.SEARCH_KEY
    index_name = "laya-policy-rules"
    
    # Create index first
    create_policy_index()
    
    # Initialize search client
    credential = AzureKeyCredential(key)
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
    
    # Policy documents - rejection_reasons as comma-separated string
    policy_docs = [
        {
            "rule_id": "RULE-001",
            "category": "GP_VISITS",
            "plan": "Simply Connect Plus",
            "title": "GP Visits Coverage",
            "description": "50% cover up to €30 per visit. Maximum 10 GP visits per policy year. No referral required. Direct reimbursement available. Prescription charges not covered.",
            "coverage_percentage": 50,
            "requires_referral": False,
            "rejection_reasons": "Prescription charges claimed; More than 10 visits claimed; Receipt not stamped",
            "notes": "Submit receipts via app or member area within 12 months"
        },
        {
            "rule_id": "RULE-002",
            "category": "CONSULTANT_VISITS",
            "plan": "Simply Connect Plus",
            "title": "Consultant Out-patient Visits",
            "description": "50% refund of costs. GP referral letter required (valid for 6 months). Must be from a registered consultant. Subject to €500 annual out-patient cap.",
            "coverage_percentage": 50,
            "requires_referral": True,
            "rejection_reasons": "No GP referral letter provided; Referral expired (older than 6 months); Consultant not registered with Laya; Receipt not on headed paper or stamped",
            "notes": "Referral must be dated within 6 months of consultation"
        },
        {
            "rule_id": "RULE-003",
            "category": "MRI_SCANS",
            "plan": "Simply Connect Plus",
            "title": "MRI/CT Diagnostic Scans",
            "description": "Full cover in participating centers with Direct Settlement. GP or Consultant referral required. Clinical indicators must be met. Beacon Hospital, Mater Private, Blackrock Clinic included.",
            "coverage_percentage": 100,
            "requires_referral": True,
            "rejection_reasons": "No referral letter attached; Clinical indicators not met; Non-participating center used; Scan not medically necessary",
            "notes": "Pre-authorization required for some scans. Check participating centers."
        },
        {
            "rule_id": "RULE-004",
            "category": "PHYSIOTHERAPY",
            "plan": "Simply Connect Plus",
            "title": "Physiotherapy Sessions",
            "description": "50% refund of costs. Therapist must be registered with Irish Society of Chartered Physiotherapists or CORU. Subject to €500 annual out-patient cap. No referral required for initial assessment.",
            "coverage_percentage": 50,
            "requires_referral": False,
            "rejection_reasons": "Therapist not registered with ISCP or CORU; Receipt missing stamp or letterhead; Annual €500 out-patient cap exceeded",
            "notes": "Always check therapist registration on CORU website"
        },
        {
            "rule_id": "RULE-005",
            "category": "RECEIPT_REQUIREMENTS",
            "plan": "All Plans",
            "title": "Receipt Submission Rules",
            "description": "All receipts must be submitted within 12 months from end of policy year. Must be on stamped or headed paper. Must show: Date, Provider name, Treatment type, Cost, Patient name.",
            "coverage_percentage": 0,
            "requires_referral": False,
            "rejection_reasons": "Receipt submitted after 12-month deadline; Receipt not on headed paper or unstamped; Missing required fields (date, provider, cost); Receipt illegible or damaged; Duplicate claim",
            "notes": "Keep originals for 6 years. Digital copies accepted via member portal."
        },
        {
            "rule_id": "RULE-006",
            "category": "PRE_EXISTING_CONDITIONS",
            "plan": "All Plans",
            "title": "Pre-existing Condition Definition",
            "description": "An ailment where signs or symptoms existed in 6 months before: (a) first health insurance, (b) rejoining after 13+ week gap, (c) upgrading to higher cover. Medical advisors determine pre-existing status.",
            "coverage_percentage": 0,
            "requires_referral": False,
            "rejection_reasons": "Condition existed within 6 months of joining; Symptoms documented before policy start; Treatment for same condition in last 6 months; Medical records show pre-existing diagnosis",
            "notes": "5-year waiting period applies. Accident/injury covered immediately."
        },
        {
            "rule_id": "RULE-007",
            "category": "OUTPATIENT_CAP",
            "plan": "Simply Connect Plus",
            "title": "Annual Out-patient Expense Cap",
            "description": "€500 maximum refund per member per year for everyday medical expenses. €1 annual excess applies first. Some benefits exempt (maternity, cancer, child healthcare).",
            "coverage_percentage": 50,
            "requires_referral": False,
            "rejection_reasons": "Annual €500 cap already reached; Excess €1 not yet met",
            "notes": "Cap resets each policy year. Check remaining balance in member portal."
        },
        {
            "rule_id": "RULE-008",
            "category": "CLINICAL_INDICATORS",
            "plan": "All Plans",
            "title": "Clinical Indicators for Procedures",
            "description": "Certain procedures require clinical indicators from GP or Consultant to justify medical necessity. Must match Schedule of Benefits. Examples: MRI requires neurological symptoms, Orthopedic surgery requires failed conservative treatment.",
            "coverage_percentage": 0,
            "requires_referral": True,
            "rejection_reasons": "Clinical indicators not provided; Indicators do not match Schedule of Benefits; Treatment not medically necessary; Conservative treatment not attempted first",
            "notes": "Always check Schedule of Benefits before booking procedures."
        },
        {
            "rule_id": "RULE-009",
            "category": "HOSPITAL_DAYCASE",
            "plan": "Simply Connect Plus",
            "title": "Day-case Hospital Treatment",
            "description": "Full cover in public and private hospitals. €50 excess for private day-case. Direct settlement available. Consultant fees fully covered if using participating consultant.",
            "coverage_percentage": 100,
            "requires_referral": True,
            "rejection_reasons": "Treatment could have been done as out-patient; Non-participating hospital; No prior authorization for hi-tech hospitals",
            "notes": "Always get pre-authorization for private hospitals to confirm cover."
        },
        {
            "rule_id": "RULE-010",
            "category": "WAITING_PERIODS",
            "plan": "All Plans",
            "title": "Waiting Periods for New Members",
            "description": "Accident/injury: Immediate cover. New illness after membership: 26 weeks. Pre-existing conditions: 5 years. Maternity: 12 months (under age 55).",
            "coverage_percentage": 0,
            "requires_referral": False,
            "rejection_reasons": "Waiting period not yet completed; Claim submitted during waiting period; Pre-existing condition within 5-year wait",
            "notes": "Waiting periods start from policy start date. No waiting for accident/injury."
        }
    ]
    
    print(f"\n📤 Uploading {len(policy_docs)} policy documents to Azure AI Search...")
    
    try:
        result = search_client.upload_documents(documents=policy_docs)
        success_count = sum(1 for r in result if r.succeeded)
        print(f"   ✅ {success_count}/{len(policy_docs)} documents uploaded successfully")
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
    
    print("\n🎉 Azure AI Search seeding complete!")

if __name__ == "__main__":
    seed_policy_documents()
