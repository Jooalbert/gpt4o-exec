# gpt4o_exec

`gpt4o_exec` is an advanced Python client designed to seamlessly execute GPT-4 output with additional functionalities. It specializes in file manipulation and image generation, leveraging OpenAI's API for interactive and automated tool calls. This client is built for extensibility, providing robust context window management and a solid framework for asynchronous tool execution.

**Note:** The asynchronous handling of tool calls is currently experimental. We might revert to synchronous execution if it better suits typical use cases. Stay tuned!

## Features

- **Execute Python Code**: Run arbitrary Python code and get immediate results.
- **File Manipulation**: Perform complex file operations and data management tasks.
- **Image Generation**: Create images dynamically using the power of OpenAI's DALL-E model.
- **Rich UI**: Enjoy a visually appealing interface displaying tool call status updates.

## Installation

### Quick Installation

Install directly from GitHub using `pip`:

```sh
pip install git+https://github.com/exec/gpt4o_exec.git
```

### Traditional Installation

For a more manual setup:

1. Clone the repository and navigate to the project directory:

    ```sh
    git clone https://github.com/exec/gpt4o_exec.git
    cd gpt4o_exec
    ```

2. Install the required dependencies:

    ```sh
    poetry install
    ```

3. Securely configure your environment variables for API keys as described below.

## Setting Up Environment Variables

Handling API keys securely is crucial. Instead of placing them in your `.bashrc`, consider the following alternatives:

### Using a `.env` File

1. Create a `.env` file in your project directory:

    ```sh
    touch .env
    ```

2. Add your API keys to the `.env` file:

    ```env
    OPENAI_API_KEY='your_openai_api_key'
    ```

3. Load these variables in your Python script using `python-dotenv`:

    ```python
    from dotenv import load_dotenv
    import os

    load_dotenv()

    openai_api_key = os.getenv('OPENAI_API_KEY')
    ```

4. Install `python-dotenv` if you haven't already:

    ```sh
    pip install python-dotenv
    ```

### Using Environment Variable Management Tools

Consider using tools like `direnv` or `dotenv` for automatic environment variable management:

- **direnv**: Automatically loads environment variables from `.envrc` files. Install `direnv` and set up your `.envrc`:

    ```sh
    echo 'export OPENAI_API_KEY="your_openai_api_key"' >> .envrc
    direnv allow
    ```

- **dotenv**: Manages environment variables from `.env` files at runtime. Follow the `.env` setup as described above.

### Direct Environment Variables (for Advanced Users)

For server or CI/CD pipeline configurations, set environment variables directly:

```sh
export OPENAI_API_KEY='your_openai_api_key'
```

## Usage

1. Ensure your environment variables are set up before proceeding.

2. Add the path where `pip` installs packages to your `PATH` environment variable:

    ```sh
    export PATH=$PATH:/path/to/python/lib/python3.8/site-packages
    ```

3. Start the main script:

    ```sh
    gpt4o_exec
    ```

    Or run it as a module:

    ```sh
    python -m gpt4o_exec
    ```

Follow the interactive prompts to:
- Provide your OpenAI API key if not already set as an environment variable.
- Choose whether to use file storage for thread contexts.
- Specify a directory path for storage if file storage is selected.
- Engage with the assistant by typing your queries and commands.

## Implementation Examples

### Example 1: Manipulating a CSV File

```python
from gpt4o_exec.client import GPT4oExecClient
import asyncio

# Initialize the client
client = GPT4oExecClient()

# Create a new thread
thread_id = client.create_thread()

# Define the messages
system_message = {"role": "system", "content": "You are a file manipulation assistant."}
user_message = {"role": "user", "content": "Can you read and summarize the contents of '/path/to/data.csv'?"}

# Add the system message to the thread
client._add_message(thread_id, system_message)

# Send the user message to the client
response = asyncio.run(client.chat(thread_id, user_message))

print(response['content'])
```

### Example 2: Generating an Image

```python
from gpt4o_exec.client import GPT4oExecClient
import asyncio

# Initialize the client
client = GPT4oExecClient(api_key='your_openai_api_key')

# Create a new thread
thread_id = client.create_thread()

# Define the messages
system_message = {"role": "system", "content": "You are an image generation assistant."}
user_message = {"role": "user", "content": "Can you generate an image of a futuristic cityscape at dusk?"}

# Add the system message to the thread
client._add_message(thread_id, system_message)

# Send the user message to the client
response = asyncio.run(client.chat(thread_id, user_message))

# Process and display the generated image
image_url = response['content']
print(f"Generated Image URL: {image_url}")
```

### Example 3: Executing Python Code

```python
from gpt4o_exec.client import GPT4oExecClient
import asyncio

# Initialize the client
client = GPT4oExecClient(api_key='your_openai_api_key')

# Create a new thread
thread_id = client.create_thread()

# Define the messages
system_message = {"role": "system", "content": "You are a Python code execution assistant."}
user_message = {"role": "user", "content": "Can you write a function to calculate the factorial of a number in Python?"}

# Add the system message to the thread
client._add_message(thread_id, system_message)

# Send the user message to the client
response = asyncio.run(client.chat(thread_id, user_message))

print(response['content'])
```

## Contributing

We welcome contributions! To get started:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add a new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request, and let's make something great together.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

- [OpenAI](https://www.openai.com) for their groundbreaking API and GPT-4 models that power and amplify my development efforts tenfold.
- [Rich](https://github.com/willmcgugan/rich) for the vibrant terminal formatting that makes development enjoyable.