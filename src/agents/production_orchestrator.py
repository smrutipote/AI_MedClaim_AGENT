from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from src.services.claim_service import claim_service
from src.services.cosmos_service import cosmos_service
from src.services.policy_search_service import policy_search_service
import os
from dotenv import load_dotenv
import json

load_dotenv()

class ProductionOrchestrator:
    """
    Production-grade orchestrator using Microsoft Semantic Kernel v1.x.
    Coordinates between Claims, Members, and Policy systems.
    """
    
    def __init__(self):
        # Initialize Semantic Kernel
        self.kernel = Kernel()
        
        # Add OpenAI service
        api_key = os.getenv("OPENAI_API_KEY")
        self.kernel.add_service(
            OpenAIChatCompletion(
                service_id="gpt-4o",
                model_id="gpt-4o",
                api_key=api_key
            )
        )
        
        # Register all plugin functions
        self._register_plugins()
    
    def _register_plugins(self):
        """Register all available tools as kernel functions."""
        
        # Store reference to self for use in nested functions
        orchestrator_self = self
        
        @kernel_function(
            name="search_claim",
            description="Searches for claim details by claim ID. Returns full claim information including status, amounts, receipts."
        )
        def search_claim(claim_id: str) -> str:
            """Searches for claim details."""
            claim = claim_service.get_claim_by_id(claim_id)
            if not claim:
                return f"Claim {claim_id} not found"
            
            total = sum(r.cost for r in claim.receipt_items)
            return f"""Claim ID: {claim.claim_id}
Member: {claim.forenames} {claim.surname} ({claim.membership_number})
Status: {claim.status}
Submission Date: {claim.submission_date}
Total Claimed: €{total:.2f}
Assessed Amount: €{claim.assessed_amount or 0:.2f}
Rejection Reason: {claim.rejection_reason or 'N/A'}
Number of Receipts: {len(claim.receipt_items)}
Number of Dependants: {len(claim.dependants)}"""
        
        @kernel_function(
            name="get_member_profile",
            description="Retrieves member profile with interaction history and uploaded documents. Use member ID (format: LAYA-XXXX)."
        )
        def get_member_profile(member_id: str) -> str:
            """Gets member profile from Cosmos."""
            member = cosmos_service.get_member_profile(member_id)
            if not member:
                return f"Member {member_id} not found"
            
            docs = member.get('uploaded_documents', [])
            interactions = member.get('interaction_notes', [])
            
            doc_list = "\n".join([f"- {d['type']} (uploaded {d['upload_date']})" for d in docs[:3]]) if docs else "None"
            interaction_list = "\n".join([f"- {i['date']}: {i['note'][:100]}" for i in interactions[:3]]) if interactions else "None"
            
            return f"""Member ID: {member.get('id')}
Name: {member.get('name')}
Plan: {member.get('plan')}
Email: {member.get('email')}
Phone: {member.get('phone')}
Uploaded Documents: {len(docs)}
Recent Interactions: {len(interactions)}

Recent Documents:
{doc_list}

Recent Interactions:
{interaction_list}"""
        
        @kernel_function(
            name="find_member_document",
            description="Searches for specific document type in member's history. Common types: 'GP Referral Letter', 'Receipt', 'Medical Report'."
        )
        def find_member_document(member_id: str, document_type: str) -> str:
            """Finds a specific document for a member."""
            doc = cosmos_service.find_uploaded_document(member_id, document_type)
            if not doc:
                return f"No {document_type} found for member {member_id}"
            
            return f"""Document Found: {doc.get('type')}
Document ID: {doc.get('document_id')}
Upload Date: {doc.get('upload_date')}
Valid Until: {doc.get('valid_until', 'N/A')}
Provider: {doc.get('provider', 'N/A')}
Reason: {doc.get('reason', 'N/A')}"""
        
        @kernel_function(
            name="search_policy_rules",
            description="Searches Laya Healthcare policy rules by keyword. Use for checking coverage rules, requirements, rejection reasons."
        )
        def search_policy_rules(query: str) -> str:
            """Searches policy rules via Azure AI Search."""
            results = policy_search_service.search_by_keyword(query, top=2)
            if not results:
                return f"No policy rules found for: {query}"
            
            output = []
            for r in results:
                output.append(f"""Rule: {r.get('title')}
Category: {r.get('category')}
Requires Referral: {r.get('requires_referral', 'N/A')}
Description: {r.get('description')}
Common Rejection Reasons: {r.get('rejection_reasons', 'None listed')}""")
            
            return "\n\n---\n\n".join(output)
        
        @kernel_function(
            name="adjudicate_claim",
            description="Performs full adjudication on a claim including rescue attempts. Returns decision with reasoning."
        )
        def adjudicate_claim(claim_id: str) -> str:
            """Adjudicates a claim using the self-healing agent."""
            from src.agents.self_healing_agent import self_healing_agent
            result = self_healing_agent.adjudicate_claim(claim_id)
            
            trace = "\n".join(result.get('reasoning_trace', []))
            return f"""ADJUDICATION RESULT:
Decision: {result['decision']}
Reason: {result['reason']}

Reasoning Trace:
{trace}"""
        
        # Register functions with kernel
        self.kernel.add_function("orchestrator_functions", search_claim)
        self.kernel.add_function("orchestrator_functions", get_member_profile)
        self.kernel.add_function("orchestrator_functions", find_member_document)
        self.kernel.add_function("orchestrator_functions", search_policy_rules)
        self.kernel.add_function("orchestrator_functions", adjudicate_claim)
    
    async def process_query(self, user_query: str) -> str:
        """
        Main entry point. Processes natural language queries.
        Uses kernel functions to answer questions about claims and members.
        """
        
        # Create a prompt for the LLM to determine which functions to call
        system_prompt = """You are an AI assistant for Laya Healthcare claim processing.
You have access to these functions:
- search_claim(claim_id): Find claim details
- get_member_profile(member_id): Get member info
- find_member_document(member_id, document_type): Find uploaded documents
- search_policy_rules(query): Search policy database
- adjudicate_claim(claim_id): Make claim decision

Analyze the user's request and call the appropriate functions to gather information.
Provide a comprehensive answer based on the results."""
        
        # Prepare arguments for the LLM
        arguments = KernelArguments(
            user_query=user_query,
            system_prompt=system_prompt
        )
        
        # Create a simple chat-based approach
        # The LLM will determine which functions to call
        chat_prompt = f"""
{system_prompt}

User Request: {user_query}

Based on this request, what functions would you call and what would you do with the results?
Please respond with concrete function calls and answers.
"""
        
        try:
            # Use the chat completion service directly
            service = self.kernel.get_service(type=OpenAIChatCompletion)
            from semantic_kernel.contents.chat_history import ChatHistory
            
            history = ChatHistory()
            history.add_system_message(system_prompt)
            history.add_user_message(user_query)
            
            response = await service.get_chat_message_content(chat_history=history)
            
            return str(response)
        except Exception as e:
            return f"Error processing query: {str(e)}"


# Singleton
orchestrator = ProductionOrchestrator()