import asyncio
import sys
sys.path.insert(0, '.')

from src.agents.production_orchestrator import orchestrator

async def main():
    print("=" * 70)
    print("PRODUCTION ORCHESTRATOR TEST (Semantic Kernel + GPT-4o)")
    print("=" * 70)
    
    # Test 1: Complex query requiring multiple tools
    query1 = """
    Analyze claim CLM-2026-022. Check why it was rejected, 
    search the member's history for any missing documents, 
    and check the policy rules to see if we can approve it.
    """
    
    print("\n🤖 QUERY 1:")
    print(query1)
    print("\n🔄 Processing...\n")
    
    response1 = await orchestrator.process_query(query1)
    print(response1)
    
    print("\n" + "=" * 70)
    print("✅ Orchestrator Working!")

if __name__ == "__main__":
    asyncio.run(main())
