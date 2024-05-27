# gpt4o_exec

`gpt4o_exec` is an advanced Python client for executing GPT-4 output with additional functionalities, including weather updates, cryptocurrency prices, and dynamic Python code execution. The project leverages OpenAI's API to facilitate interactive and automated tool calls.

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