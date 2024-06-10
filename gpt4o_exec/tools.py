# gpt4o_exec/tools.py

TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), 'terraform_template.tf')

import aiofiles
import os
import json
import subprocess

async def exec_python(code):
    try:
        exec_globals = {}
        exec(code, exec_globals)
        result = {k: v for k, v in exec_globals.items() if not k.startswith('__')}
        return result
    except Exception as e:
        return str(e)

async def generate_image(client, prompt, orientation="square"):
    size_map = {
        "portrait": "1024x1792",
        "square": "1024x1024",
        "landscape": "1792x1024"
    }
    size = size_map.get(orientation, "1024x1024")

    response = await client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality="hd",
        n=1,
    )

    image_url = response.data[0].url
    return image_url

async def write_file(path, content, overwrite=False, append=False):
    mode = 'w' if overwrite else 'a' if append else 'x'
    try:
        async with aiofiles.open(path, mode) as file:
            await file.write(content)
        return f"File written to {path}"
    except FileExistsError:
        return f"File {path} already exists. Use overwrite or append options to modify it."

async def read_file(path):
    if not os.path.exists(path):
        return f"File {path} does not exist."
    async with aiofiles.open(path, 'r') as file:
        content = await file.read()
    return content

async def list_files(directory):
    if not os.path.exists(directory):
        return f"Directory {directory} does not exist."
    if not os.path.isdir(directory):
        return f"{directory} is not a directory."
    
    files = os.listdir(directory)
    return files

async def delete_file(path):
    if not os.path.exists(path):
        return f"File {path} does not exist."
    os.remove(path)
    return f"File {path} has been deleted."