import asyncio
import json
import sys
import functools as ft
from typing import Any, Callable, Dict


class ContextServer:
    def __init__(self):
        self.commands: Dict[str, Callable] = {}
        self.command_info: Dict[str, Dict[str, Any]] = {}
        self._temp_command_info: Dict[str, Dict[str, Any]] = {}
        self.handlers = {
            "initialize": self.handle_initialize,
            "prompts/list": self.handle_prompts_list,
            "prompts/get": self.handle_prompts_get,
        }

    def _register_command(self, name: str, func: Callable, description: str):
        self.commands[name] = func
        self.command_info[name] = {
            "name": name,
            "description": description,
            "arguments": self._temp_command_info.get(func.__name__, {}).get(
                "arguments", []
            ),
        }
        self._temp_command_info.pop(func.__name__, None)

    def slash_command(self, name: str, description: str):
        def decorator(func: Callable):
            @ft.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            self._register_command(name, wrapper, description)
            return wrapper

        return decorator

    def argument(self, name: str, type: type, help: str):
        def decorator(func: Callable):
            @ft.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            if func.__name__ not in self._temp_command_info:
                self._temp_command_info[func.__name__] = {"arguments": []}

            self._temp_command_info[func.__name__]["arguments"].append(
                {"name": name, "type": type.__name__, "description": help}
            )

            return wrapper

        return decorator

    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "protocolVersion": 1,
            "capabilities": {"prompts": {}},
            "serverInfo": {"name": "Python Context Server", "version": "0.1.0"},
        }

    async def handle_prompts_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        prompts = [
            {
                "name": name,
                "arguments": [
                    {
                        "name": arg["name"],
                        "description": arg["description"],
                        "required": True,
                    }
                    for arg in info["arguments"]
                ],
            }
            for name, info in self.command_info.items()
        ]
        return {"prompts": prompts}

    async def handle_prompts_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        name = params.get("name")
        arguments = params.get("arguments", {})

        if name not in self.commands:
            raise ValueError(f"Command '{name}' not found")

        result = await self.commands[name](**arguments)
        return {"prompt": str(result)}

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get("method")
        params = request.get("params", {})

        handler = self.handlers.get(method)
        if not handler:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32601, "message": f"Method '{method}' not found"},
            }

        try:
            result = await handler(params)
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": result,
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32000, "message": str(e)},
            }

    async def run(self):
        while True:
            try:
                request = json.loads(
                    await asyncio.get_event_loop().run_in_executor(
                        None, sys.stdin.readline
                    )
                )
                response = await self.handle_request(request)
                print(json.dumps(response), flush=True)
            except EOFError:
                break
            except json.JSONDecodeError:
                print(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": None,
                            "error": {"code": -32700, "message": "Parse error"},
                        }
                    ),
                    flush=True,
                )
