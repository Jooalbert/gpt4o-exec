import json
import os
import uuid
import asyncio
import aiofiles
import base64
import psutil
import asyncpg
from datetime import datetime, timedelta
from openai import AsyncOpenAI
from .tools import exec_python, get_current_weather, get_crypto_price, generate_image
from .ui import ToolUI

class ToolCallMismatchError(Exception):
    def __init__(self, missing_tool_calls):
        self.missing_tool_calls = missing_tool_calls
        message = f"Missing tool responses for tool call IDs: {', '.join(missing_tool_calls)}"
        super().__init__(message)

class GPT4oExecClient:
    def __init__(self, api_key=None, weather_api_key=None, crypto_api_key=None, storage_dir=None, pg_conn_str=None, temporary_mode=None, timeout_minutes=30, memory_threshold=75):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("API key must be provided either as an argument or through the OPENAI_API_KEY environment variable.")
        self.weather_api_key = weather_api_key or os.getenv('WEATHER_API_KEY')
        self.crypto_api_key = crypto_api_key or os.getenv('CRYPTO_API_KEY')
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.tools = self._load_tools()
        self.allowed_tools = self._load_allowed_tools()
        self.threads = {}
        self.temporary_mode = self._parse_boolean(temporary_mode or os.getenv('GPT4O_EXEC_TEMPORARY_MODE', 'false'))
        self.storage_dir = storage_dir or os.getenv('GPT4O_EXEC_FILE_DIR')
        self.pg_conn_str = pg_conn_str or os.getenv('GPT4O_EXEC_PG_CONN_STR')
        if not self.temporary_mode and not (self.storage_dir or self.pg_conn_str):
            raise ValueError("Either storage directory or PostgreSQL connection string must be provided.")
        self.ui = ToolUI()
        self.timeout = timedelta(minutes=timeout_minutes)
        self.memory_threshold = memory_threshold
        self.last_check = datetime.now()

    def _parse_boolean(self, value):
        return str(value).lower() in ("1", "true", "yes")

    def _load_tools(self):
        tools_file = os.path.join(os.path.dirname(__file__), 'tools.json')
        with open(tools_file, 'r') as file:
            return json.load(file)

    def _load_allowed_tools(self):
        allowed_tools = os.getenv('GPT4O_EXEC_TOOLS', 'all')
        if allowed_tools == 'all':
            return set(self.tools.keys())
        return set(allowed_tools.split(','))

    def create_thread(self, temporary_mode=None):
        temporary_mode = self._parse_boolean(temporary_mode)
        thread_id = str(uuid.uuid4())
        self.threads[thread_id] = {"messages": [], "temporary_mode": temporary_mode, "last_access": datetime.now()}
        return thread_id

    async def load_thread(self, thread_id):
        if thread_id not in self.threads:
            self.threads[thread_id] = {"messages": [], "temporary_mode": False, "last_access": datetime.now()}

        if self.pg_conn_str:
            conn = await asyncpg.connect(self.pg_conn_str)
            thread_data = await conn.fetchval('SELECT data FROM threads WHERE id=$1', thread_id)
            await conn.close()
            if thread_data:
                self.threads[thread_id]["messages"] = json.loads(thread_data)
            else:
                raise ValueError(f"No stored context found for thread ID: {thread_id}")
        else:
            file_path = os.path.join(self.storage_dir, f"{thread_id}.json")
            if os.path.exists(file_path):
                async with aiofiles.open(file_path, 'r') as file:
                    self.threads[thread_id]["messages"] = json.loads(await file.read())
            else:
                raise ValueError(f"No stored context found for thread ID: {thread_id}")

        self.threads[thread_id]["last_access"] = datetime.now()

    async def save_thread(self, thread_id):
        if self.threads[thread_id].get("temporary_mode", False):
            return

        if self.pg_conn_str:
            conn = await asyncpg.connect(self.pg_conn_str)
            thread_data = json.dumps(self.threads[thread_id]["messages"], default=str)
            await conn.execute('INSERT INTO threads(id, data) VALUES($1, $2) ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data', thread_id, thread_data)
            await conn.close()
        else:
            file_path = os.path.join(self.storage_dir, f"{thread_id}.json")
            async with aiofiles.open(file_path, 'w') as file:
                await file.write(json.dumps(self.threads[thread_id]["messages"], default=str))

        self.threads[thread_id]["last_access"] = datetime.now()

    async def delete_thread(self, thread_id):
        if thread_id in self.threads:
            temporary_mode = self.threads[thread_id].get("temporary_mode", False)
            del self.threads[thread_id]
            if not temporary_mode:
                if self.pg_conn_str:
                    conn = await asyncpg.connect(self.pg_conn_str)
                    await conn.execute('DELETE FROM threads WHERE id=$1', thread_id)
                    await conn.close()
                else:
                    file_path = os.path.join(self.storage_dir, f"{thread_id}.json")
                    if os.path.exists(file_path):
                        os.remove(file_path)
        else:
            raise ValueError(f"No context found for thread ID: {thread_id}")

    async def chat(self, thread_id, user_input):
        if thread_id not in self.threads:
            await self.load_thread(thread_id)

        new_message, images = self._extract_images(user_input)
        if images:
            new_message["content"].extend(images)

        self._add_message(thread_id, new_message)
        self._manage_context_window(thread_id)

        all_messages = self.threads[thread_id]["messages"].copy()
        tool_calls = []

        while True:
            completion = await self.client.chat_completions.create(
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

            if tool_name not in self.allowed_tools:
                result = f"Tool {tool_name} is not permitted."
                tool_call["status"] = "failed"
            else:
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
                elif tool_name == 'generate_image':
                    result = await generate_image(self.client, **tool_args)
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
        if new_message not in self.threads[thread_id]["messages"]:
            self.threads[thread_id]["messages"].append({"message": new_message, "tool_calls": []})
            self.threads[thread_id]["last_access"] = datetime.now()

    def _manage_context_window(self, thread_id, max_chars=20000):
        total_chars = sum(len(message['message']['content']) for message in self.threads[thread_id]["messages"] if 'content' in message['message'])
        while total_chars > max_chars:
            total_chars -= len(self.threads[thread_id]["messages"][0]['message']['content'])
            self.threads[thread_id]["messages"].pop(0)

    def _extract_images(self, message):
        words = message.split()
        images = []
        new_message_content = []

        for word in words:
            if word.startswith('file:'):
                image_path = word[5:]
                if os.path.isfile(image_path):
                    images.append(self._process_image_base64(image_path))
                else:
                    print(f"Invalid file path: {image_path}")
            elif word.startswith('https://') and word.lower().endswith(('jpg', 'jpeg', 'png', 'gif')):
                images.append({"type": "image_url", "image_url": {"url": word}})
            else:
                new_message_content.append(word)

        new_message = {"role": "user", "content": " ".join(new_message_content)}

        return new_message, images

    async def _process_image_base64(self, image_path):
        async with aiofiles.open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(await image_file.read()).decode('utf-8')

        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        }

    async def periodic_check(self):
        while True:
            now = datetime.now()
            await self._offload_threads_if_needed()
            for thread_id in list(self.threads.keys()):
                if not self.threads[thread_id].get("temporary_mode", False):
                    last_access = self.threads[thread_id]["last_access"]
                    if now - last_access > self.timeout:
                        await self.save_thread(thread_id)
                        del self.threads[thread_id]
            self.last_check = now
            await asyncio.sleep(60)

    async def _offload_threads_if_needed(self):
        memory_usage = psutil.virtual_memory().percent
        if memory_usage > self.memory_threshold:
            for thread_id in list(self.threads.keys()):
                if not self.threads[thread_id].get("temporary_mode", False):
                    await self.save_thread(thread_id)
                    del self.threads[thread_id]
