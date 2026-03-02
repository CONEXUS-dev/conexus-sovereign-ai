"""
Simple LangGraph Test
"""

try:
    from langgraph.graph import StateGraph, END
    from typing import TypedDict, Literal
    print("✅ LangGraph import successful")
    
    # Simple test
    class TestState(TypedDict):
        message: str
        
    def test_node(state: TestState) -> TestState:
        return {"message": "test complete"}
    
    # Create simple graph
    workflow = StateGraph(TestState)
    workflow.add_node("test", test_node)
    workflow.add_edge("test", END)
    workflow.set_entry_point("test")
    
    # Compile
    graph = workflow.compile()
    
    # Test execution
    initial_state = {"message": "start"}
    result = graph.invoke(initial_state)
    
    print(f"✅ Graph execution successful: {result}")
    print("🎉 LangGraph is working!")
    
except Exception as e:
    print(f"❌ LangGraph test failed: {e}")
    exit(1)
