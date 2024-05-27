# gpt4o_exec/__main__.py
import asyncio
import os
from gpt4o_exec.client import GPT4oExecClient, ToolCallMismatchError

def ask_yes_no(question):
    while True:
        response = input(f"{question} (yes/no): ").strip().lower()
        if response in ['yes', 'no']:
            return response == 'yes'
        print("Please answer 'yes' or 'no'.")

def ask_for_filepath():
    while True:
        filepath = input("Please provide a directory path for storage: ").strip()
        if os.path.isdir(filepath):
            return filepath
        print("Invalid directory path. Please try again.")

async def main():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        api_key = input("Please provide your OpenAI API key: ").strip()
    
    use_file_storage = ask_yes_no("Do you want to use file storage for thread contexts?")
    storage_dir = None
    if use_file_storage:
        storage_dir = ask_for_filepath()
    
    client = GPT4oExecClient(api_key=api_key, storage_dir=storage_dir)
    
    print("Creating a new chat thread...")
    thread_id = client.create_thread()
    print(f"New thread created with ID: {thread_id}")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break

        user_message = {"role": "user", "content": user_input}
        try:
            response_message = await client.chat(thread_id, user_message)
            print(f"Assistant: {response_message.content}")
        except ToolCallMismatchError as e:
            print(f"Error: {e}")

        if use_file_storage:
            await client.save_thread(thread_id)
            print(f"Thread context saved to {storage_dir}/{thread_id}.json")

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
