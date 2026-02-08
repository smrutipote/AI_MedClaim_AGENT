import sys
sys.path.insert(0, '.')

from src.agents.langgraph_orchestrator import orchestrator

print("=" * 70)
print("PRODUCTION ORCHESTRATOR (LangGraph + GPT-4o)")
print("=" * 70)

# Test 1: Simple claim search
print("\n🤖 TEST 1: Simple Query")
print("Query: Tell me about claim CLM-2026-001\n")

response1 = orchestrator.process_query(
    "Tell me about claim CLM-2026-001",
    thread_id="test-1"
)
print(response1)

# Test 2: Complex multi-step query
print("\n\n" + "=" * 70)
print("🤖 TEST 2: Complex Query (Multi-Tool)")
print("Query: Why was CLM-2026-022 rejected? Check if we have the required documents.\n")

response2 = orchestrator.process_query(
    "Why was claim CLM-2026-022 rejected? Search the member's history to see if they uploaded any required documents. Check policy rules to understand the requirements.",
    thread_id="test-2"
)
print(response2)

# Test 3: Self-healing adjudication
print("\n\n" + "=" * 70)
print("🤖 TEST 3: Autonomous Adjudication")
print("Query: Run full adjudication on CLM-2026-022 and try to rescue it\n")

response3 = orchestrator.process_query(
    "Run full adjudication on claim CLM-2026-022 with automatic rescue attempts",
    thread_id="test-3"
)
print(response3)

print("\n\n" + "=" * 70)
print("✅ ALL TESTS COMPLETE")
print("=" * 70)
