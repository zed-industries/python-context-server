import unittest
import asyncio
from context_server.context_server import ContextServer


class TestContextServer(unittest.TestCase):
    def setUp(self):
        self.server = ContextServer()

    def test_single_command_registration(self):
        @self.server.slash_command(name="test", description="Test command")
        @self.server.argument(name="arg1", type=str, help="First argument")
        async def test_command(arg1: str):
            return f"Test: {arg1}"

        self.assertIn("test", self.server.commands)
        self.assertIn("test", self.server.command_info)
        self.assertEqual(self.server.command_info["test"]["name"], "test")
        self.assertEqual(
            self.server.command_info["test"]["description"], "Test command"
        )
        self.assertEqual(len(self.server.command_info["test"]["arguments"]), 1)
        self.assertEqual(
            self.server.command_info["test"]["arguments"][0]["name"], "arg1"
        )
        self.assertEqual(
            self.server.command_info["test"]["arguments"][0]["type"], "str"
        )
        self.assertEqual(
            self.server.command_info["test"]["arguments"][0]["description"],
            "First argument",
        )

    def test_multiple_arguments(self):
        @self.server.slash_command(name="multi_arg", description="Multiple arguments")
        @self.server.argument(name="arg2", type=int, help="Second argument")
        @self.server.argument(name="arg1", type=str, help="First argument")
        async def multi_arg_command(arg1: str, arg2: int):
            return f"Multi: {arg1}, {arg2}"

        self.assertIn("multi_arg", self.server.commands)
        self.assertEqual(len(self.server.command_info["multi_arg"]["arguments"]), 2)
        self.assertEqual(
            self.server.command_info["multi_arg"]["arguments"][0]["name"], "arg1"
        )
        self.assertEqual(
            self.server.command_info["multi_arg"]["arguments"][1]["name"], "arg2"
        )

    def test_command_execution(self):
        @self.server.slash_command(name="echo", description="Echo command")
        @self.server.argument(name="message", type=str, help="Message to echo")
        async def echo(message: str):
            return f"Echo: {message}"

        async def run_command():
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "prompts/get",
                "params": {"name": "echo", "arguments": {"message": "Hello, World!"}},
            }
            response = await self.server.handle_request(request)
            return response

        response = asyncio.run(run_command())
        self.assertEqual(response["result"]["prompt"], "Echo: Hello, World!")

    def test_prompts_list(self):
        @self.server.slash_command(name="cmd1", description="Command 1")
        @self.server.argument(name="arg1", type=str, help="Argument 1")
        async def cmd1(arg1: str):
            pass

        @self.server.slash_command(name="cmd2", description="Command 2")
        @self.server.argument(name="arg2", type=int, help="Argument 2")
        @self.server.argument(name="arg1", type=str, help="Argument 1")
        async def cmd2(arg1: str, arg2: int):
            pass

        async def get_prompts_list():
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "prompts/list",
            }
            response = await self.server.handle_request(request)
            return response

        response = asyncio.run(get_prompts_list())
        prompts = response["result"]["prompts"]

        self.assertEqual(len(prompts), 2)
        self.assertIn(
            {
                "name": "cmd1",
                "arguments": [
                    {"name": "arg1", "description": "Argument 1", "required": True}
                ],
            },
            prompts,
        )
        self.assertIn(
            {
                "name": "cmd2",
                "arguments": [
                    {"name": "arg1", "description": "Argument 1", "required": True},
                    {"name": "arg2", "description": "Argument 2", "required": True},
                ],
            },
            prompts,
        )


if __name__ == "__main__":
    unittest.main()
