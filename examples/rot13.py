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
