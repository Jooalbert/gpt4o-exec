# gpt4o_exec

`gpt4o_exec` is an advanced Python client for executing GPT-4 output with additional functionalities, including weather updates, cryptocurrency prices, and dynamic Python code execution. The project leverages OpenAI's API to facilitate interactive and automated tool calls. This client is designed to be highly extensible, allowing for robust context window management and a solid framework for handling tool call execution asynchronously.

**Note:** The asynchronous tool call handling is experimental and may be reverted to synchronous execution if it proves to be more effective for typical use cases.

## Features

- **Execute Python Code:** Run arbitrary Python code and get the results.
- **Get Current Weather:** Fetch current weather information for a specified location.
- **Get Cryptocurrency Price:** Retrieve the current price of a specified cryptocurrency.
- **Rich UI:** Display tool call status updates using a rich user interface.

## Installation

### Quick Installation

```sh
pip install git+https://github.com/exec/gpt4o_exec.git
```

### Traditional Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/exec/gpt4o_exec.git
    cd gpt4o_exec
    ```

2. Install dependencies:

    ```sh
    pip install -r requirements.txt
    ```

3. Configure environment variables for API keys securely.

### Setting Up Environment Variables

It's important to handle API keys securely. Instead of storing them directly in your `.bashrc`, consider these alternatives:

#### Using a `.env` File

1. Create a `.env` file in your project directory:

    ```sh
    touch .env
    ```

2. Add your API keys to the `.env` file:

    ```sh
    OPENAI_API_KEY='your_openai_api_key'
    WEATHER_API_KEY='your_weather_api_key'
    CRYPTO_API_KEY='your_crypto_api_key'
    ```

3. Load these variables in your Python script using `python-dotenv`:

    ```python
    from dotenv import load_dotenv
    import os

    load_dotenv()

    openai_api_key = os.getenv('OPENAI_API_KEY')
    weather_api_key = os.getenv('WEATHER_API_KEY')
    crypto_api_key = os.getenv('CRYPTO_API_KEY')
    ```

4. Install the `python-dotenv` package if you haven't already:

    ```sh
    pip install python-dotenv
    ```

#### Using Environment Variable Management Tools

Consider using tools like `direnv` or `dotenv` for automatic loading of environment variables when you enter your project directory.

- **direnv**: Automatically loads environment variables from `.envrc` files. [Install direnv](https://direnv.net/).

    ```sh
    echo 'export OPENAI_API_KEY="your_openai_api_key"' >> .envrc
    echo 'export WEATHER_API_KEY="your_weather_api_key"' >> .envrc
    echo 'export CRYPTO_API_KEY="your_crypto_api_key"' >> .envrc
    direnv allow
    ```

- **dotenv**: Load environment variables from `.env` files during runtime. Use the same `.env` setup as described above.

#### Direct Environment Variables (for Advanced Users)

For secure storage on servers or CI/CD pipelines, set environment variables directly in your environment configuration or deployment settings.

```sh
export OPENAI_API_KEY='your_openai_api_key'
export WEATHER_API_KEY='your_weather_api_key'
export CRYPTO_API_KEY='your_crypto_api_key'
```

## Usage

1. Run the main script:

    ```sh
    gpt4o_exec
    ```

    Or, if you prefer using Python directly:

    ```sh
    python -m gpt4o_exec
    ```

2. Follow the prompts:
    - Provide your OpenAI API key if not set as an environment variable.
    - Choose whether to use file storage for thread contexts.
    - Provide a directory path for storage if file storage is used.
    - Interact with the assistant by typing your queries and commands.

## Implementation Examples

### Example 1: Discussing a Dataset

```python
from gpt4o_exec.client import GPT4oExecClient
import asyncio

# Initialize the client
client = GPT4oExecClient()

# Create a new thread
thread_id = client.create_thread()

# Define the messages
system_message = {"role": "system", "content": "You are a data analyst."}
user_message = {"role": "user", "content": "I have a dataset located at '/path/to/dataset.csv'. Can you please have a look at it and make sense of it? Perhaps limit output to the first 1000 characters."}

# Add the system message to the thread
client._add_message(thread_id, system_message)

# Send the user message to the client
response = asyncio.run(client.chat(thread_id, user_message))

print(response['content'])
```

### Example 2: Plotting Data with Matplotlib

```python
from gpt4o_exec.client import GPT4oExecClient
import asyncio

# Initialize the client
client = GPT4oExecClient(api_key='your_openai_api_key')

# Create a new thread
thread_id = client.create_thread()

# Define the messages
system_message = {"role": "system", "content": "You are a data analyst."}
user_message = {"role": "user", "content": "I have sales data for the past year in '/path/to/sales_data.csv'. Can you plot it using Matplotlib?"}

# Add the system message to the thread
client._add_message(thread_id, system_message)

# Send the user message to the client
response = asyncio.run(client.chat(thread_id, user_message))

print(response['content'])
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

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenAI](https://www.openai.com) for the API and GPT-4 family of models.
- [Rich](https://github.com/willmcgugan/rich) for the beautiful terminal formatting.