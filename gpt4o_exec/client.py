# gpt4o_exec/client.py
import json
import os
import uuid
import asyncio
import aiofiles
from openai import AsyncOpenAI
from .tools import exec_python, get_current_weather, get_crypto_price
from .ui import ToolUI

class ToolCallMismatchError(Exception):
    def __init__(self, missing_tool_calls):
        self.missing_tool_calls = missing_tool_calls
        message = f"Missing tool responses for tool call IDs: {', '.join(missing_tool_calls)}"
        super().__init__(message)

class GPT4oExecClient:
    def __init__(self, api_key=None, weather_api_key=None, crypto_api_key=None, storage_dir=None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("API key must be provided either as an argument or through the OPENAI_API_KEY environment variable.")
        self.weather_api_key = weather_api_key or os.getenv('WEATHER_API_KEY')
        self.crypto_api_key = crypto_api_key or os.getenv('CRYPTO_API_KEY')
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.tools = self._load_tools()
        self.threads = {}
        self.storage_dir = storage_dir
        self.ui = ToolUI()

    def _load_tools(self):
        tools_file = os.path.join(os.path.dirname(__file__), 'tools.json')
        with open(tools_file, 'r') as file:
            return json.load(file)

    def create_thread(self):
        thread_id = str(uuid.uuid4())
        self.threads[thread_id] = []
        return thread_id

    async def load_thread(self, thread_id):
        if self.storage_dir:
            file_path = os.path.join(self.storage_dir, f"{thread_id}.json")
            if os.path.exists(file_path):
                async with aiofiles.open(file_path, 'r') as file:
                    self.threads[thread_id] = json.loads(await file.read())
            else:
                raise ValueError(f"No stored context found for thread ID: {thread_id}")
        else:
            raise ValueError("Storage directory not set")

    async def save_thread(self, thread_id):
        if self.storage_dir:
            file_path = os.path.join(self.storage_dir, f"{thread_id}.json")
            async with aiofiles.open(file_path, 'w') as file:
                await file.write(json.dumps(self.threads[thread_id], default=str))
        else:
            raise ValueError("Storage directory not set")

    async def delete_thread(self, thread_id):
        if thread_id in self.threads:
            del self.threads[thread_id]
            if self.storage_dir:
                file_path = os.path.join(self.storage_dir, f"{thread_id}.json")
                if os.path.exists(file_path):
                    os.remove(file_path)
        else:
            raise ValueError(f"No context found for thread ID: {thread_id}")

    async def chat(self, thread_id, new_message):
        if thread_id not in self.threads:
            raise ValueError(f"No context found for thread ID: {thread_id}")

        self._add_message(thread_id, new_message)
        self._manage_context_window(thread_id)

        all_messages = self.threads[thread_id].copy()
        tool_calls = []

        while True:
            completion = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[msg['message'] for msg in all_messages],
                tools=self.tools,
                tool_choice="auto"
            )
            response_message = completion.choices[0].message
            all_messages.append({"message": response_message.to_dict(), "tool_calls": response_message.tool_calls})
            self._add_message(thread_id, response_message.to_dict())

            if completion.choices[0].finish_reason != 'tool_calls':
                break

            for tool_call in response_message.tool_calls:
                tool_call_id = tool_call.id
                tool_calls.append({
                    "id": tool_call_id,
                    "name": tool_call.function.name,
                    "status": "pending"
                })

        await self.ui.display(tool_calls)

        async def handle_tool_call(tool_call):
            tool_name = tool_call["name"]
            tool_call_id = tool_call["id"]

            try:
                tool_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Problematic JSON: {tool_call.function.arguments}")
                return

            if tool_name == 'exec_python':
                result = await exec_python(**tool_args)
            elif tool_name == 'get_current_weather':
                result = await get_current_weather(**tool_args)
            elif tool_name == 'get_crypto_price':
                result = await get_crypto_price(**tool_args)
            else:
                result = f"Tool {tool_name} not implemented."

            serialized_result = json.dumps(result, default=str)

            tool_response_message = {
                "role": "tool",
                "name": tool_name,
                "content": serialized_result,
                "tool_call_id": tool_call_id
            }

            tool_call["status"] = "completed"
            all_messages.append({"message": tool_response_message})
            self._add_message(thread_id, tool_response_message)

        await asyncio.gather(*[handle_tool_call(tc) for tc in tool_calls])

        return response_message

    def _add_message(self, thread_id, new_message):
        if new_message not in self.threads[thread_id]:
            self.threads[thread_id].append({"message": new_message, "tool_calls": []})

    def _manage_context_window(self, thread_id, max_chars=20000):
        total_chars = sum(len(message['message']['content']) for message in self.threads[thread_id] if 'content' in message['message'])
        while total_chars > max_chars:
            total_chars -= len(self.threads[thread_id][0]['message']['content'])
            self.threads[thread_id].pop(0)
