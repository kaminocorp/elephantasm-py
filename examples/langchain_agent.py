"""Elephantasm integration with LangChain.

This example shows how to use Elephantasm with LangChain to build
an AI assistant with persistent memory.

Requirements:
    pip install langchain-anthropic

Environment variables required:
    ELEPHANTASM_API_KEY: Your Elephantasm API key
    ELEPHANTASM_ANIMA_ID: Your anima ID
    ANTHROPIC_API_KEY: Your Anthropic API key
"""

from elephantasm import Elephantasm, EventType

# Optional: Only import if langchain is available
try:
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import SystemMessage, HumanMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain not installed. Run: pip install langchain-anthropic")


def create_chat_agent():
    """Create a chat agent with Elephantasm memory."""
    el = Elephantasm()
    llm = ChatAnthropic(model="claude-sonnet-4-20250514")
    return el, llm


def chat(el: Elephantasm, llm, user_message: str, session_id: str) -> str:
    """Process a chat message with memory context.

    Args:
        el: Elephantasm client
        llm: LangChain LLM
        user_message: User's input message
        session_id: Session identifier for grouping events

    Returns:
        Assistant's response text
    """
    # Get memory pack for context
    pack = el.inject(query=user_message)

    # Build system prompt with memory context
    system_content = f"""You are a helpful AI assistant with persistent memory.

{pack.as_prompt()}

Use the context above to provide personalized, contextual responses."""

    # Get response from LLM
    response = llm.invoke([
        SystemMessage(content=system_content),
        HumanMessage(content=user_message),
    ])

    response_text = response.content

    # Capture both events for memory synthesis
    el.extract(
        EventType.MESSAGE_IN,
        user_message,
        session_id=session_id,
        role="user",
    )
    el.extract(
        EventType.MESSAGE_OUT,
        response_text,
        session_id=session_id,
        role="assistant",
        author="claude-sonnet-4-20250514",
    )

    return response_text


def main():
    """Run an interactive chat session."""
    if not LANGCHAIN_AVAILABLE:
        return

    el, llm = create_chat_agent()
    session_id = "langchain-example-001"

    print("Chat with memory-enabled assistant (type 'quit' to exit)")
    print("-" * 50)

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break

        response = chat(el, llm, user_input, session_id)
        print(f"\nAssistant: {response}")


if __name__ == "__main__":
    main()
