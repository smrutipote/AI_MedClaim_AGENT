from typing import TypedDict, Annotated, Sequence
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
import operator
import os
from dotenv import load_dotenv

# Import services
from src.services.claim_service import claim_service
from src.services.cosmos_service import cosmos_service
from src.services.policy_search_service import policy_search_service
from src.agents.self_healing_agent import self_healing_agent

load_dotenv()

# Define tools
@tool
def search_claim(claim_id: str) -> str:
    """
    Searches for claim details by claim ID. 
    Returns full claim information including status, amounts, receipts, dependants.
    
    Args:
        claim_id: The claim ID (format: CLM-2026-XXX)
    """
    claim = claim_service.get_claim_by_id(claim_id)
    if not claim:
        return f"Claim {claim_id} not found in system"
    
    total = sum(r.cost for r in claim.receipt_items)
    receipts_detail = "\n".join([
        f"  - {r.treatment_type}: €{r.cost} on {r.receipt_date}"
        for r in claim.receipt_items
    ])
    
    return f"""
Claim ID: {claim.claim_id}
Member: {claim.forenames} {claim.surname} ({claim.membership_number})
Status: {claim.status}
Submission Date: {claim.submission_date}
Total Claimed: €{total:.2f}
Assessed Amount: €{claim.assessed_amount or 0:.2f}
Rejection Reason: {claim.rejection_reason or 'N/A'}

Receipts ({len(claim.receipt_items)}):
{receipts_detail}

Dependants: {len(claim.dependants)}
Has Accident Info: {claim.accident_details is not None}
    """.strip()

@tool
def get_member_profile(member_id: str) -> str:
    """
    Retrieves member profile with interaction history and uploaded documents.
    
    Args:
        member_id: Member ID (format: LAYA-XXXX)
    """
    member = cosmos_service.get_member_profile(member_id)
    if not member:
        return f"Member {member_id} not found"
    
    docs = member.get('uploaded_documents', [])
    interactions = member.get('interaction_notes', [])
    
    docs_detail = "\n".join([
        f"  - {d['type']} (uploaded {d['upload_date']}, valid until {d.get('valid_until', 'N/A')})"
        for d in docs[:5]
    ])
    
    interactions_detail = "\n".join([
        f"  - {i['date']} ({i['type']}): {i['note'][:80]}..."
        for i in interactions[:3]
    ])
    
    return f"""
Member ID: {member['id']}
Name: {member['name']}
Plan: {member['plan']} ({member['tier']} tier)
Email: {member['email']}
Phone: {member['phone']}

Uploaded Documents ({len(docs)}):
{docs_detail or '  None'}

Recent Interactions ({len(interactions)}):
{interactions_detail or '  None'}

Policy Details:
  - Annual Limit: €{member['policy_details']['annual_limit']}
  - Used to Date: €{member['policy_details']['used_to_date']}
  - Loyalty Bonus: {member['policy_details']['loyalty_bonus_active']}
    """.strip()

@tool
def find_member_document(member_id: str, document_type: str) -> str:
    """
    Searches for a specific document type in member's upload history.
    
    Args:
        member_id: Member ID (format: LAYA-XXXX)
        document_type: Type of document (e.g., 'GP Referral Letter', 'Receipt')
    """
    doc = cosmos_service.find_uploaded_document(member_id, document_type)
    if not doc:
        return f"No '{document_type}' found for member {member_id}"
    
    return f"""
✅ Document Found!

Type: {doc['type']}
Document ID: {doc['document_id']}
Upload Date: {doc['upload_date']}
Valid Until: {doc.get('valid_until', 'N/A')}
Provider: {doc.get('provider', 'N/A')}
Reason/Purpose: {doc.get('reason', 'N/A')}
    """.strip()

@tool
def search_policy_rules(query: str) -> str:
    """
    Searches Laya Healthcare policy rules by keyword.
    Use for checking coverage rules, requirements, rejection reasons.
    
    Args:
        query: Search query (e.g., 'MRI referral', 'consultant visit', 'receipt requirements')
    """
    results = policy_search_service.search_by_keyword(query, top=2)
    if not results:
        return f"No policy rules found matching: {query}"
    
    output = []
    for r in results:
        output.append(f"""
📋 {r['title']}
Category: {r['category']}
Coverage: {r.get('coverage_percentage', 0)}%
Requires Referral: {r.get('requires_referral', 'N/A')}

Description:
{r['description']}

Common Rejection Reasons:
{r.get('rejection_reasons', 'None listed')}
        """.strip())
    
    return "\n\n" + "="*60 + "\n\n".join(output)

@tool
def adjudicate_claim_with_rescue(claim_id: str) -> str:
    """
    Performs full claim adjudication including automatic rescue attempts.
    This checks all data sources to approve claims that appear rejected.
    
    Args:
        claim_id: The claim ID to adjudicate
    """
    result = self_healing_agent.adjudicate_claim(claim_id)
    
    trace = "\n".join([f"  {t}" for t in result.get('reasoning_trace', [])])
    
    return f"""
🔍 ADJUDICATION COMPLETE

Final Decision: {result['decision']}
Reason: {result['reason']}

Reasoning Trace:
{trace}
    """.strip()

# Define agent state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# Create LangGraph orchestrator
class LangGraphOrchestrator:
    """
    Production orchestrator using LangGraph for state management.
    Implements tool-calling agent with memory and conditional routing.
    """
    
    def __init__(self):
        # Initialize LLM with tools (supports Azure OpenAI or public OpenAI)
        api_key = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        if azure_endpoint and api_key and deployment:
            # Azure OpenAI - use AzureChatOpenAI class
            self.llm = AzureChatOpenAI(
                model=deployment,
                temperature=0,
                api_key=api_key,
                azure_endpoint=azure_endpoint,
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
            )
        elif api_key:
            # Public OpenAI
            self.llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=api_key)
        else:
            raise RuntimeError(
                "Missing OpenAI credentials. Set AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT + "
                "AZURE_OPENAI_DEPLOYMENT for Azure, or OPENAI_API_KEY for public OpenAI."
            )
        
        self.tools = [
            search_claim,
            get_member_profile,
            find_member_document,
            search_policy_rules,
            adjudicate_claim_with_rescue
        ]
        
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build graph
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Constructs the LangGraph state machine."""
        
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Define nodes
        def call_model(state: AgentState):
            messages = state["messages"]
            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}
        
        def should_continue(state: AgentState):
            messages = state["messages"]
            last_message = messages[-1]
            
            # If LLM makes tool calls, continue to tools
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            # Otherwise end
            return "end"
        
        # Add nodes
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                "end": END
            }
        )
        
        # After tools, go back to agent
        workflow.add_edge("tools", "agent")
        
        # Compile with memory
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    
    def process_query(self, user_query: str, thread_id: str = "default") -> str:
        """
        Processes a natural language query.
        
        Args:
            user_query: The user's question or command
            thread_id: Conversation thread ID for memory persistence
        """
        
        # Create config with thread ID
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invoke graph
        response = self.graph.invoke(
            {"messages": [HumanMessage(content=user_query)]},
            config=config
        )
        
        # Extract final answer
        final_message = response["messages"][-1]
        return final_message.content

# Singleton
orchestrator = LangGraphOrchestrator()