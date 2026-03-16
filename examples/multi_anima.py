"""Multiple animas for per-user agents.

This example shows how to create and manage multiple animas,
useful for multi-tenant applications where each user has their
own agent with separate memory.

Environment variables required:
    ELEPHANTASM_API_KEY: Your API key
"""

from elephantasm import Elephantasm, EventType


def create_user_agent(client: Elephantasm, user_id: str, user_name: str):
    """Create a new anima for a specific user.

    Args:
        client: Elephantasm client
        user_id: Unique user identifier
        user_name: Human-readable user name

    Returns:
        Created Anima object
    """
    anima = client.create_anima(
        name=f"Agent for {user_name}",
        description=f"Personal assistant for user {user_id}",
        meta={
            "user_id": user_id,
            "user_name": user_name,
            "created_by": "multi_anima_example",
        },
    )
    print(f"Created anima {anima.id} for user {user_name}")
    return anima


def chat_with_user(
    client: Elephantasm,
    anima_id: str,
    user_message: str,
    session_id: str,
):
    """Process a message for a specific user's anima.

    Args:
        client: Elephantasm client
        anima_id: The user's anima ID
        user_message: User's input message
        session_id: Session identifier

    Returns:
        Memory pack for context injection
    """
    # Get this user's memory context
    pack = client.inject(anima_id=anima_id, query=user_message)

    # Capture the user's message
    client.extract(
        EventType.MESSAGE_IN,
        user_message,
        anima_id=anima_id,
        session_id=session_id,
        role="user",
    )

    return pack


def main():
    """Demonstrate multi-anima usage."""
    # Create client (uses ELEPHANTASM_API_KEY from env)
    client = Elephantasm()

    # Simulate two users
    users = [
        {"id": "user-alice-123", "name": "Alice"},
        {"id": "user-bob-456", "name": "Bob"},
    ]

    # Create animas for each user
    user_animas = {}
    for user in users:
        anima = create_user_agent(client, user["id"], user["name"])
        user_animas[user["id"]] = anima

    print("\n" + "=" * 50)
    print("Simulating conversations with each user's agent")
    print("=" * 50)

    # Simulate conversation with Alice
    alice_anima = user_animas["user-alice-123"]
    alice_pack = chat_with_user(
        client,
        str(alice_anima.id),
        "I prefer morning meetings",
        session_id="alice-session-001",
    )
    print(f"\nAlice's context has {alice_pack.session_memory_count} session memories")

    # Simulate conversation with Bob
    bob_anima = user_animas["user-bob-456"]
    bob_pack = chat_with_user(
        client,
        str(bob_anima.id),
        "I work best in the afternoon",
        session_id="bob-session-001",
    )
    print(f"Bob's context has {bob_pack.session_memory_count} session memories")

    # Show that memories are isolated
    print("\n" + "=" * 50)
    print("Memory isolation demonstration")
    print("=" * 50)

    # Get Alice's pack again - should not contain Bob's info
    alice_pack_2 = client.inject(anima_id=str(alice_anima.id))
    print(f"\nAlice's pack (should not mention afternoon):")
    print(f"  Token count: {alice_pack_2.token_count}")

    # Get Bob's pack - should not contain Alice's info
    bob_pack_2 = client.inject(anima_id=str(bob_anima.id))
    print(f"\nBob's pack (should not mention morning):")
    print(f"  Token count: {bob_pack_2.token_count}")


if __name__ == "__main__":
    main()
