from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain.messages import SystemMessage , HumanMessage , AIMessage, ToolMessage
from langsmith import traceable

MAX_ITERATIONS = 10

load_dotenv()

MODEL = "llama3.1:8b"


@tool
def get_product_price(product: str) -> float:
    """Look up the catalog price of a product. Returns the price as a number."""
    print(f"=====> Executing get_product_price for {product}")
    prices = {"laptop":200.45 , "headphones": 35.6 , "keyboard": 20 }
    return prices.get(product,0)
        

@tool
def apply_discount(price: float ,tier: str) -> float:
    """Apply a customer discount tier to a price and return the final price.

    This tool already knows the discount percentage for every tier, so you
    do not need to know or calculate it. Pass the numeric price and the
    tier name. Valid tiers: bronze, silver, gold.
    """
    print(f"=====> Executing apply_discount price {price} for tier {tier}")
    discount_percentage = {"bronze": 5 , "silver": 10 , "gold": 20}
    discount = discount_percentage.get(tier,0)
    return round(price * (1 - discount / 100), 2)
    

#  --- Agent loop ---

@traceable(name = "Langchain agent loop")
def run_agent(question: str):
    tools = [get_product_price,apply_discount]
    tools_dict = {t.name: t for t in tools}
    
    llm = init_chat_model(f"ollama:{MODEL}" , temperature=0)
    llm_with_tool = llm.bind_tools(tools)
    
    print(f"Question: {question}")
    print("=" * 60)
    
    messages = [
        SystemMessage(
            content=(
                "You are a helpful shopping assistant.\n\n"
                "RULES:\n"
                "1. Call exactly ONE tool per turn, then stop and wait "
                "for its result.\n"
                "2. You do not know any prices. To learn a price you must "
                "look it up with a tool first.\n"
                "3. Never put a tool name or a placeholder in an argument. "
                "Never invent a number.\n"
                "4. Never calculate a discount yourself — use a tool.\n"
                "5. Once you have a real numeric price and the user has "
                "named a tier, apply the discount with a tool.\n"
                "6. Only ask the user for a tier if they never mentioned one."
            )
        ),
        HumanMessage(content=question),
    ]
    
    
    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n--- Iteration {iteration} ---")
        ai_message = llm_with_tool.invoke(messages)
        tool_calls = ai_message.tool_calls
        if not tool_calls:
            print(f"\nFinal Answer: {ai_message.content}")
            return ai_message.content
        
        messages.append(ai_message)

        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            tool_call_id = tool_call.get("id")

            print(f"  [Tool Selected] {tool_name} with args: {tool_args}")

            tool_to_use = tools_dict.get(tool_name)
            if tool_to_use is None:
                observation = f"Unknown tool '{tool_name}'."
            else:
                try:
                    observation = tool_to_use.invoke(tool_args)
                except Exception as e:
                    observation = (
                        f"Tool call failed: {e}. "
                        "Fix the arguments and try again."
                    )

            print(f"  [Tool Result] {observation}")
            messages.append(
                ToolMessage(
                    content=str(observation),
                    tool_call_id=tool_call_id,
                    name=tool_name,
                )
            )

    print("ERROR: Max iterations reached without a final answer")
    return None


if __name__ == "__main__":
    print("Hello langchain agent bind tools")
    
    result = run_agent("what is the price of laptop after applying gold tier")

