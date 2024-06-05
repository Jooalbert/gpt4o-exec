# gpt4o_exec/tools.py
import aiohttp
import json
import os

async def exec_python(code):
    try:
        exec_globals = {}
        exec(code, exec_globals)
        result = {k: v for k, v in exec_globals.items() if not k.startswith('__')}
        return result
    except Exception as e:
        return str(e)

async def get_current_weather(location, unit="celsius", weather_api_key=None):
    weather_api_key = weather_api_key or os.getenv('WEATHER_API_KEY')
    if not weather_api_key:
        return "Weather API key must be provided either as an argument or through the WEATHER_API_KEY environment variable."
    
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={weather_api_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(geocode_url) as response:
            geocode_response = await response.json()
    
    if response.status != 200:
        return f"Error fetching geolocation data: {response.status} - {response.text}"

    if not geocode_response:
        return f"No geolocation data found for the location: {location}"

    geocode_info = geocode_response[0]
    lat = geocode_info['lat']
    lon = geocode_info['lon']

    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units={'metric' if unit == 'celsius' else 'imperial'}&appid={weather_api_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(weather_url) as response:
            weather_response = await response.json()
    
    if response.status == 200:
        weather_info = {
            "location": location,
            "unit": unit,
            "temperature": weather_response['main']['temp'],
            "description": weather_response['weather'][0]['description']
        }
        return weather_info
    else:
        return f"Error fetching weather data: {response.status} - {response.text}"

async def get_crypto_price(symbol, crypto_api_key=None):
    crypto_api_key = crypto_api_key or os.getenv('CRYPTO_API_KEY')
    if not crypto_api_key:
        return "Crypto API key must be provided either as an argument or through the CRYPTO_API_KEY environment variable."
    
    url = f"https://api.nomics.com/v1/currencies/ticker?key={crypto_api_key}&ids={symbol}&convert=USD"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_data = await response.json()
    
    if response.status == 200:
        if response_data:
            crypto_info = {
                "symbol": symbol,
                "price": response_data[0]['price'],
                "currency": "USD"
            }
            return crypto_info
        else:
            return "No data found for the specified symbol."
    else:
        return f"Error fetching crypto price: {response.status} - {response.text}"

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
