# gpt4o_exec

`gpt4o_exec` is an advanced Python client for executing GPT-4 output with additional functionalities, including weather updates, cryptocurrency prices, and dynamic Python code execution. The project leverages OpenAI's API to facilitate interactive and automated tool calls. This client is designed to be highly extensible, allowing for robust context window management and a solid framework for handling tool call execution asynchronously.

Please note that the asynchronous tool call handling is experimental and might be reverted to synchronous executions if it is determined to be a better approach for most use cases.

## Features

- **Execute Python Code:** Run arbitrary Python code and get the results.
- **Get Current Weather:** Fetch current weather information for a specified location.
- **Get Cryptocurrency Price:** Retrieve the current price of a specified cryptocurrency.
- **Rich UI:** Display tool call status updates using a rich user interface.

## Installation

The fast way:
```sh
pip install git+https://github.com/exec/gpt4o_exec.git
```

The traditional way:

1. Clone the repository:
    ```sh
    git clone https://github.com/exec/gpt4o_exec.git
    cd gpt4o_exec
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Set up environment variables:
    - `OPENAI_API_KEY`: Your OpenAI API key. Required.
    - `WEATHER_API_KEY`: Your API key for the weather service (OpenWeatherMap). Optional. Will error on `get_current_weather` calls if not provided.
    - `CRYPTO_API_KEY`: Your API key for the cryptocurrency service. Optional. Will error on `get_crypto_price` calls if not provided.

    You can set these in your shell configuration file (e.g., `.bashrc` or `.zshrc`):
    ```sh
    export OPENAI_API_KEY='your_openai_api_key'
    export WEATHER_API_KEY='your_weather_api_key'
    export CRYPTO_API_KEY='your_crypto_api_key'
    ```

## Usage

1. Run the main script:

    The proper way:
    ```sh
    # be sure $PATH contains pip script dir, usually ~/.local/bin on linux
    export PATH="$HOME/.local/bin:$PATH"
    # add that to your .bashrc or similar config at your will
    gpt4o_exec
    ```

    The universal way:
    ```sh
    python -m gpt4o_exec
    ```

2. Follow the prompts:
    - Provide your OpenAI API key if not set as an environment variable.
    - Choose whether to use file storage for thread contexts.
    - Provide a directory path for storage if file storage is used.
    - Interact with the assistant by typing your queries and commands.

# Implementation Examples

The main client file serves as an example implementation of the GPT4oExecClient class. It demonstrates properly managing threads and context window, utilizing functions within the client reasonably well.

A web API implementation will be developed to facilitate a future GPT-4o tool-use web interface project I would like to build on top of this in the near future.

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

These examples ensure that the system message is added once, and the user message is sent through the `chat` method, avoiding any duplication.
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