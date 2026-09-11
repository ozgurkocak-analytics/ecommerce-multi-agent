import asyncio
from agents.graph_flow import build_ecommerce_graph
from langgraph.types import Command

async def main():
    graph = build_ecommerce_graph()
    
    # Thread ID for session state management
    config = {"configurable": {"thread_id": "session-demo-terminal"}}
    
    user_query = "Which product has the highest total revenue but suffers from deteriorating customer reviews?"
    print(f"\n[User Query]: {user_query}")
    print("=" * 70)

    # Run the graph until the first breakpoint/interrupt
    state = await graph.ainvoke({"user_query": user_query}, config=config)

    # Check if graph paused on human approval
    snapshot = graph.get_state(config)
    
    if snapshot.next:
        print("\n" + "!" * 22 + " [HUMAN-IN-THE-LOOP INTERRUPT] " + "!" * 22)
        tasks = snapshot.tasks
        if tasks and tasks[0].interrupts:
            details = tasks[0].interrupts[0].value
            print(f"Notification: {details.get('message')}\n")
            pending_list = details.get('pending_data', [])
            
            print(f"{'ID':<6} | {'SENTIMENT':<10} | {'ISSUE TYPE':<15} | {'OPS FLAG':<10} | REASON")
            print("-" * 75)
            for p in pending_list:
                flag_str = "CRITICAL" if p.get('flagged_for_ops') else "OK"
                print(f"#{p['review_id']:<5} | {p['sentiment']:<10} | {p['issue_type']:<15} | {flag_str:<10} | {p['reason']}")
        
        user_choice = input("\nApprove committing these updates to SQLite DB? (y/n or e/h): ").strip().lower()
        is_approved = user_choice in ["y", "yes", "e", "evet"]

        print(f"\nUser decision: {'APPROVED' if is_approved else 'REJECTED'}. Resuming graph flow...")
        
        # Resume graph with human decision
        final_state = await graph.ainvoke(Command(resume={"approved": is_approved}), config=config)
        
        print("\n" + "=" * 25 + " [EXECUTIVE SUMMARY] " + "=" * 25)
        print(final_state.get("final_summary"))
        print(f"\nTotal rows updated in database: {final_state.get('db_updated_count')}")

if __name__ == "__main__":
    asyncio.run(main())