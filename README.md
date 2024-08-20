# Python Context Server

This project is a lightweight framework for creating context servers compatible with Zed's Assistant. It allows you to easily define and implement custom slash commands that can be used within Zed's AI-powered assistant.

## Features

- Simple decorator-based API for defining slash commands
- Automatic handling of JSON-RPC communication
- Easy integration with Zed's Assistant
- Support for command arguments with type hints

## Installation

To use Python Context Server, clone this repository and install it:

```bash
git clone https://github.com/zed-industries/python-context-server.git
cd python-context-server
pip install .
```

## Usage

```python
import asyncio
from context_server import ContextServer

ctx = ContextServer()

@ctx.slash_command(name="rot13", description="Perform a rot13 transformation")
@ctx.argument(name="input", type=str, help="String to rot13")
async def rot13(input: str) -> str:
    return "".join(
        chr((ord(c) - 97 + 13) % 26 + 97) if c.isalpha() else c for c in input.lower()
    )

if __name__ == "__main__":
    asyncio.run(ctx.run())
```

## Configuring Zed

To use your Python Context Server with Zed, add the following configuration to your Zed settings:

```json
{
  "experimental.context_servers": {
    "servers": [
      {
        "id": "python_context_server",
        "executable": "python",
        "args": ["-m", "your_context_server_module"]
      }
    ]
  }
}
```

To quickly try the Rot13 example in this repo, install this project and add the following configuration to your Zed settings:
```json
{
  "experimental.context_servers": {
    "servers": [
      {
        "id": "rot13",
        "executable": "python",
        "args": ["/path/to/repo/examples/rot13.py"]
      }
    ]
  }
}
```

## Contributing

Contributions to Python Context Server are welcome! Please feel free to submit issues, fork the repository and send pull requests.

## License

[GPL v3.0](./LICENSE)

## More Information

For more details on Context Servers and how they integrate with Zed's Assistant, please refer to the [Zed documentation on Context Servers](https://zed.dev/docs/assistant/context-servers).
