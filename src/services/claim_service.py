import pyodbc
from typing import List, Optional, Dict
from datetime import date
from src.config.settings import settings
from src.models.claim import ClaimForm, Dependant, AccidentDetails, PaymentDetails, ReceiptItem

class ClaimService:
    """
    Service layer for Claims database operations.
    Handles complex joins and data aggregation.
    """
    
    def __init__(self):
        self.conn_str = (
            f"DRIVER={settings.SQL_DRIVER};"
            f"SERVER={settings.SQL_SERVER};"
            f"DATABASE={settings.SQL_DB};"
            f"UID={settings.SQL_USER};"
            f"PWD={settings.SQL_PASSWORD}"
        )
    
    def get_connection(self):
        """Creates a fresh connection to Azure SQL."""
        return pyodbc.connect(self.conn_str)
    
    def get_claim_by_id(self, claim_id: str) -> Optional[ClaimForm]:
        """
        Fetches a complete claim with all nested data.
        Returns a full ClaimForm object or None.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Get Master Claim
            cursor.execute("""
                SELECT claim_id, membership_number, title, surname, forenames,
                       date_of_birth, telephone, correspondence_address,
                       submission_date, status, assessed_amount, rejection_reason
                FROM Claims
                WHERE claim_id = ?
            """, (claim_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Build base claim
            claim = ClaimForm(
                claim_id=row.claim_id,
                membership_number=row.membership_number,
                title=row.title,
                surname=row.surname,
                forenames=row.forenames,
                date_of_birth=row.date_of_birth,
                telephone=row.telephone,
                correspondence_address=row.correspondence_address,
                submission_date=row.submission_date,
                status=row.status,
                assessed_amount=float(row.assessed_amount) if row.assessed_amount else None,
                rejection_reason=row.rejection_reason
            )
            
            # 2. Get Receipt Items
            cursor.execute("""
                SELECT id, claim_id, treatment_type, receipt_date, cost
                FROM ClaimReceiptItems
                WHERE claim_id = ?
            """, (claim_id,))
            
            claim.receipt_items = [
                ReceiptItem(
                    id=r.id,
                    claim_id=r.claim_id,
                    treatment_type=r.treatment_type,
                    receipt_date=r.receipt_date,
                    cost=float(r.cost)
                )
                for r in cursor.fetchall()
            ]
            
            # 3. Get Dependants
            cursor.execute("""
                SELECT id, claim_id, name, relationship
                FROM ClaimDependants
                WHERE claim_id = ?
            """, (claim_id,))
            
            claim.dependants = [
                Dependant(
                    id=d.id,
                    claim_id=d.claim_id,
                    name=d.name,
                    relationship=d.relationship
                )
                for d in cursor.fetchall()
            ]
            
            # 4. Get Accident Details (if exists)
            cursor.execute("""
                SELECT id, claim_id, description, accident_date, expenses_recoverable,
                       claiming_through_solicitor, claiming_through_piab,
                       third_party_policy_details, member_signed, subscriber_signed
                FROM ClaimAccidentDetails
                WHERE claim_id = ?
            """, (claim_id,))
            
            accident_row = cursor.fetchone()
            if accident_row:
                claim.accident_details = AccidentDetails(
                    id=accident_row.id,
                    claim_id=accident_row.claim_id,
                    description=accident_row.description,
                    accident_date=accident_row.accident_date,
                    expenses_recoverable=bool(accident_row.expenses_recoverable),
                    claiming_through_solicitor=bool(accident_row.claiming_through_solicitor),
                    claiming_through_piab=bool(accident_row.claiming_through_piab),
                    third_party_policy_details=accident_row.third_party_policy_details,
                    member_signed=bool(accident_row.member_signed),
                    subscriber_signed=bool(accident_row.subscriber_signed)
                )
            
            # 5. Get Payment Details
            cursor.execute("""
                SELECT id, claim_id, use_existing_direct_debit, account_holder_name,
                       account_number, bank_sort_code, bank_name_and_address,
                       signature_date, is_signed
                FROM ClaimPaymentDetails
                WHERE claim_id = ?
            """, (claim_id,))
            
            payment_row = cursor.fetchone()
            if payment_row:
                claim.payment_details = PaymentDetails(
                    id=payment_row.id,
                    claim_id=payment_row.claim_id,
                    use_existing_direct_debit=bool(payment_row.use_existing_direct_debit),
                    account_holder_name=payment_row.account_holder_name,
                    account_number=payment_row.account_number,
                    bank_sort_code=payment_row.bank_sort_code,
                    bank_name_and_address=payment_row.bank_name_and_address,
                    signature_date=payment_row.signature_date,
                    is_signed=bool(payment_row.is_signed)
                )
            
            return claim
            
        except Exception as e:
            print(f"❌ Error fetching claim {claim_id}: {e}")
            return None
        finally:
            conn.close()
    
    def get_claims_by_member(self, membership_number: str) -> List[Dict]:
        """
        Gets all claims for a specific member (summary view).
        Returns a list of dictionaries with basic info + totals.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    c.claim_id,
                    c.submission_date,
                    c.status,
                    c.assessed_amount,
                    c.rejection_reason,
                    SUM(r.cost) as total_claimed
                FROM Claims c
                LEFT JOIN ClaimReceiptItems r ON c.claim_id = r.claim_id
                WHERE c.membership_number = ?
                GROUP BY c.claim_id, c.submission_date, c.status, c.assessed_amount, c.rejection_reason
                ORDER BY c.submission_date DESC
            """, (membership_number,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'claim_id': row.claim_id,
                    'submission_date': row.submission_date,
                    'status': row.status,
                    'total_claimed': float(row.total_claimed) if row.total_claimed else 0,
                    'assessed_amount': float(row.assessed_amount) if row.assessed_amount else None,
                    'rejection_reason': row.rejection_reason
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Error fetching claims for member {membership_number}: {e}")
            return []
        finally:
            conn.close()
    
    def search_claims_by_status(self, status: str, limit: int = 10) -> List[Dict]:
        """
        Searches claims by status (PENDING, APPROVED, etc.)
        Returns summary list for Detective Agent.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT TOP (?) 
                    c.claim_id,
                    c.membership_number,
                    c.surname,
                    c.submission_date,
                    c.status,
                    SUM(r.cost) as total_claimed
                FROM Claims c
                LEFT JOIN ClaimReceiptItems r ON c.claim_id = r.claim_id
                WHERE c.status = ?
                GROUP BY c.claim_id, c.membership_number, c.surname, c.submission_date, c.status
                ORDER BY c.submission_date DESC
            """, (limit, status))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'claim_id': row.claim_id,
                    'membership_number': row.membership_number,
                    'surname': row.surname,
                    'submission_date': row.submission_date,
                    'status': row.status,
                    'total_claimed': float(row.total_claimed) if row.total_claimed else 0
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Error searching claims by status {status}: {e}")
            return []
        finally:
            conn.close()

# Singleton instance
claim_service = ClaimService()
