# Load environment variables from .env (for API keys, etc.)
from dotenv import load_dotenv

load_dotenv()

# Groq LLM + LangGraph imports
from langchain_groq import ChatGroq
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command


# ---------------------------------------
# 1. Define the State structure
# ---------------------------------------
class State(TypedDict):
    # Stores conversation history.
    # Annotated with add_messages → new messages are appended automatically.
    messages: Annotated[list, add_messages]


# ---------------------------------------
# 2. Define Tools (Functions the LLM can call)
# ---------------------------------------

@tool
def get_stock_price(symbol: str) -> float:
    """Return the current price of a stock based on its symbol."""
    return {"MSFT": 200.3, "AAPL": 100.4, "AMZN": 150.0, "RIL": 87.6}.get(symbol, 0.0)


@tool
def buy_stocks(symbol: str, quantity: int, total_price: float) -> str:
    """
    Buy stocks by asking for user approval.
    Uses 'interrupt' to pause execution and wait for human confirmation.
    """

    # Pause the graph and ask for user input (Yes/No approval)
    decision = interrupt(f"Approve buying {quantity} {symbol} stocks for ${total_price:.2f}?")

    # Normalize input to avoid case-sensitivity issues
    if decision.lower().strip() == "yes":
        result = f"You bought {quantity} shares of {symbol} for a total price of {total_price}"
        print(f"\n--- TOOL EXECUTED: {result} ---\n")  # Debug log to show tool action
        return result
    else:
        return "Buying declined."


# ---------------------------------------
# 3. Setup Graph + LLM
# ---------------------------------------

# List of all tools available to the agent
tools = [get_stock_price, buy_stocks]

# Initialize Groq LLM
llm = ChatGroq(model="llama-3.3-70b-versatile")

# Bind tools → enables automatic tool calling by LLM
llm_with_tools = llm.bind_tools(tools)


# Node where the LLM responds to user messages
def chatbot_node(state: State):
    msg = llm_with_tools.invoke(state["messages"])
    return {"messages": [msg]}


# MemorySaver → enables multi-turn memory using thread_id
memory = MemorySaver()

# Build LangGraph workflow
builder = StateGraph(State)

# Add nodes
builder.add_node("chatbot", chatbot_node)
builder.add_node("tools", ToolNode(tools))

# Graph structure:
# START → chatbot → tools (if needed) → chatbot → END

builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)  # If LLM calls a tool → go to tools node
builder.add_edge("tools", "chatbot")
builder.add_edge("chatbot", END)

# Compile graph with memory support
graph = builder.compile(checkpointer=memory)

# thread_id ensures all turns belong to the same conversation
config = {"configurable": {"thread_id": "buy_thread"}}

# ---------------------------------------
# 4. EXECUTION LOGIC
# ---------------------------------------

# ---- STEP 1: User asks stock price (normal execution, no interrupt)
print("--- STEP 1: ASKING PRICE ---")
state = graph.invoke(
    {"messages": [{"role": "user", "content": "What is the current price of 10 MSFT stocks?"}]},
    config=config
)
print(f"Assistant: {state['messages'][-1].content}\n")

# ---- STEP 2: User requests a buy order → Tool will interrupt for user approval
print("--- STEP 2: STARTING BUY REQUEST ---")

# Graph runs until it hits an interrupt inside buy_stocks()
initial_state = graph.invoke(
    {"messages": [{"role": "user", "content": "Buy 10 MSFT stocks at current price."}]},
    config=config
)

# ---- STEP 3: Check whether graph is paused & waiting for user approval
snapshot = graph.get_state(config)

if snapshot.next:
    # Graph is paused due to interrupt()

    print("\nSYSTEM PAUSED: Approval Required")
    decision = input("Approve (yes/no): ")

    print("\n--- RESUMING GRAPH ---")

    # ---- STEP 4: Resume graph execution with user's decision
    final_state = graph.invoke(Command(resume=decision), config=config)

    # ---- STEP 5: Show last tool + assistant messages
    print("\n--- FINAL OUTPUT ---")
    for msg in final_state["messages"][-2:]:
        role = "TOOL" if msg.type == "tool" else "ASSISTANT"
        print(f"[{role}]: {msg.content}")

else:
    print("Graph finished without interruption.")
