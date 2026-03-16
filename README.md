# elephantasm

[![PyPI version](https://badge.fury.io/py/elephantasm.svg)](https://badge.fury.io/py/elephantasm)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Long-Term Agentic Memory SDK for Python.

Give your AI agents persistent, evolving memory across sessions.

## Installation

```bash
pip install elephantasm
```

## Quick Start

```python
from elephantasm import inject, extract, EventType

# Get memory context for LLM injection
pack = inject()
system_prompt = f"You are a helpful assistant.\n\n{pack.as_prompt()}"

# Capture events during conversation
extract(EventType.MESSAGE_IN, "Hello!", role="user")
extract(EventType.MESSAGE_OUT, "Hi there!", role="assistant")
```

## Configuration

Set these environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ELEPHANTASM_API_KEY` | Yes | - | Your API key (starts with `sk_live_`) |
| `ELEPHANTASM_ANIMA_ID` | No | - | Default anima ID for operations |
| `ELEPHANTASM_ENDPOINT` | No | `https://api.elephantasm.com` | API endpoint URL |
| `ELEPHANTASM_TIMEOUT` | No | `30` | Request timeout in seconds |

## Usage

### Module-Level Functions

The simplest way to use Elephantasm:

```python
from elephantasm import inject, extract, create_anima, EventType

# Create an anima (agent entity)
anima = create_anima("my-assistant", description="Personal helper")

# Set ELEPHANTASM_ANIMA_ID or pass anima_id explicitly
pack = inject(anima_id=str(anima.id))

# Capture events
extract(EventType.MESSAGE_IN, "User message", anima_id=str(anima.id))
extract(EventType.MESSAGE_OUT, "Assistant response", anima_id=str(anima.id))
```

### Explicit Client

For more control, use the `Elephantasm` class:

```python
from elephantasm import Elephantasm, EventType

# Initialize with credentials
client = Elephantasm(
    api_key="sk_live_...",
    anima_id="your-anima-id",
)

# Or use as context manager
with Elephantasm(api_key="sk_live_...") as client:
    pack = client.inject()
    client.extract(EventType.MESSAGE_IN, "Hello!")
```

### Memory Pack

The `MemoryPack` object contains assembled context for LLM injection:

```python
pack = inject()

# Get formatted prompt string
prompt = pack.as_prompt()

# Access structured data
print(f"Session memories: {pack.session_memory_count}")
print(f"Knowledge items: {pack.knowledge_count}")
print(f"Token count: {pack.token_count}/{pack.max_tokens}")

# Access identity context
if pack.identity:
    print(f"Personality: {pack.identity.personality_type}")

# Access individual memories
for mem in pack.session_memories:
    print(f"- {mem.summary} (score: {mem.score:.2f})")
```

### Event Types

```python
from elephantasm import EventType

EventType.MESSAGE_IN   # User messages
EventType.MESSAGE_OUT  # Assistant responses
EventType.TOOL_CALL    # Tool invocations
EventType.TOOL_RESULT  # Tool outputs
EventType.SYSTEM       # System events
```

### Error Handling

```python
from elephantasm import Elephantasm
from elephantasm.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    ServerError,
)

try:
    pack = inject()
except AuthenticationError:
    print("Invalid API key")
except NotFoundError:
    print("Anima not found")
except RateLimitError:
    print("Rate limit exceeded, retry later")
except ValidationError as e:
    print(f"Invalid request: {e}")
except ServerError:
    print("Server error, retry later")
```

## Examples

See the [examples/](examples/) directory for complete examples:

- **[basic_usage.py](examples/basic_usage.py)** - Simple event capture and pack retrieval
- **[langchain_agent.py](examples/langchain_agent.py)** - Integration with LangChain
- **[multi_anima.py](examples/multi_anima.py)** - Multi-tenant per-user agents

## API Reference

### `Elephantasm` Class

```python
class Elephantasm:
    def __init__(
        self,
        api_key: str | None = None,      # Falls back to ELEPHANTASM_API_KEY
        anima_id: str | None = None,      # Falls back to ELEPHANTASM_ANIMA_ID
        endpoint: str | None = None,      # Falls back to ELEPHANTASM_ENDPOINT
        timeout: int | None = None,       # Falls back to ELEPHANTASM_TIMEOUT
    ): ...

    def inject(
        self,
        anima_id: str | None = None,      # Override default anima
        query: str | None = None,         # Semantic search query
        preset: str | None = None,        # "conversational" or "self_determined"
    ) -> MemoryPack: ...

    def extract(
        self,
        event_type: str | EventType,      # Event type
        content: str,                      # Event content
        anima_id: str | None = None,      # Override default anima
        session_id: str | None = None,    # Group related events
        role: str | None = None,          # user, assistant, system, tool
        author: str | None = None,        # Username, model name, etc.
        occurred_at: datetime | None = None,
        meta: dict | None = None,
        importance_score: float | None = None,
    ) -> Event: ...

    def create_anima(
        self,
        name: str,
        description: str | None = None,
        meta: dict | None = None,
    ) -> Anima: ...

    def close(self) -> None: ...
```

### Module Functions

```python
def inject(anima_id=None, query=None, preset=None) -> MemoryPack: ...
def extract(event_type, content, anima_id=None, **kwargs) -> Event: ...
def create_anima(name, description=None, meta=None) -> Anima: ...
```

## Development

```bash
# Clone and install
git clone https://github.com/kaminocorp/elephantasm-py.git
cd elephantasm-py
pip install -e ".[dev]"

# Run tests
pytest -v

# Lint
ruff check elephantasm tests
```

## Links

- [Documentation](https://docs.elephantasm.com)
- [API Reference](https://api.elephantasm.com/docs)
- [GitHub](https://github.com/kaminocorp/elephantasm-py)
- [PyPI](https://pypi.org/project/elephantasm/)

## License

Apache 2.0
