"""Basic Elephantasm SDK usage.

This example shows how to capture events and retrieve memory packs
using the module-level convenience functions.

Environment variables required:
    ELEPHANTASM_API_KEY: Your API key
    ELEPHANTASM_ANIMA_ID: Your anima ID
"""

from elephantasm import inject, extract, EventType

# Get memory context for LLM injection
# Uses ELEPHANTASM_ANIMA_ID from environment
pack = inject()

print(f"Loaded pack with {pack.session_memory_count} session memories")
print(f"Token count: {pack.token_count}/{pack.max_tokens}")
print()
print("Context for LLM:")
print("-" * 40)
print(pack.as_prompt())
print("-" * 40)

# Capture a user message
user_event = extract(
    EventType.MESSAGE_IN,
    "Hello, how are you today?",
    role="user",
    author="example-user",
    session_id="example-session-001",
)
print(f"\nCaptured user event: {user_event.id}")

# Capture an assistant response
assistant_event = extract(
    EventType.MESSAGE_OUT,
    "I'm doing well, thank you for asking! How can I help you today?",
    role="assistant",
    author="gpt-4",
    session_id="example-session-001",
)
print(f"Captured assistant event: {assistant_event.id}")

# Access pack details
if pack.identity:
    print(f"\nIdentity: {pack.identity.personality_type}")
    print(f"Style: {pack.identity.communication_style}")

if pack.temporal_context:
    print(f"\nLast interaction: {pack.temporal_context.hours_ago:.1f} hours ago")

print(f"\nSession memories: {len(pack.session_memories)}")
for mem in pack.session_memories:
    print(f"  - {mem.summary} (score: {mem.score:.2f})")
