import requests
import json
import math
import re
import statistics
import tkinter as tk
from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)

# Initialize variables
region_price_ratio = 350
region_code = "ar"

# Create the main application window
window = tk.Tk()
window.title("Steam Game Details")
window.geometry("800x600")

# Create labels and entry fields
game_id_label = tk.Label(window, text="Enter the game ID:")
game_id_label.pack()

game_id_entry = tk.Entry(window)
game_id_entry.pack()


# Create the text area for displaying game details
game_details_text = tk.Text(window, height=30, width=50)
game_details_text.pack()

# Callback function for the "Get Details" button
def get_game_details():
    # Get the user-provided game ID and region code
    game_id = game_id_entry.get()


    # Create a new session
    session = requests.Session()

    # Send a GET request to the URL with the user-provided game ID and region code
    url = f"https://store.steampowered.com/api/appdetails?appids={game_id}&cc={region_code}"
    url_trade = f"https://steamcommunity.com/market/search/render/?q=&category_753_Event%5B%5D=any&category_753_Game%5B%5D=tag_app_{game_id}&category_753_cardborder%5B%5D=tag_cardborder_0&category_753_item_class%5B%5D=tag_item_class_2&appid=753&norender=1&cc={region_code}"

    response = session.get(url)
    response_trade = session.get(url_trade)

    # Extract the JSON data
    data = json.loads(response.text)
    data_trade = json.loads(response_trade.text)

    # Check if the request was successful
    if response.status_code == 200 and data.get(game_id, {}).get("success"):
        # Access the desired part of the JSON
        name = data[game_id]["data"]["name"]
        if data[game_id]["data"]["is_free"]:
            game_details_text.insert(tk.END, f"{name} is a free game and it doesn't drop cards\n")
            return

        price = data[game_id]["data"]["price_overview"]["final_formatted"]
        price_int = filter_numbers(price)

        cards = data_trade["total_count"]
        obtainable_cards = math.ceil(cards / 2)
        sum_card = sum(int(result["sell_price"]) for result in data_trade["results"])
        sum_card /= 100


        # Insert the game details into the text area
        game_details_text.insert(tk.END, f"Name: {name}\n")
        game_details_text.insert(tk.END, f"Price: {price}\n")
        game_details_text.insert(tk.END, f"Cards Count: {cards}\n")
        game_details_text.insert(tk.END, f"You can obtain {obtainable_cards} cards.\n")
        game_details_text.insert(tk.END, "- - - - - - - - - - - - - - - - - - - - - - - - \n")

        results = data_trade['results']
        market_hash_names = [result['asset_description']['market_hash_name'] for result in results]
        market_names = [result['asset_description']['market_name'] for result in results]
        sell_prices = []

        for market_name, market_hash_name in zip(market_names, market_hash_names):
            url = f"https://steamcommunity.com/market/priceoverview/?appid=753&currency=34&market_hash_name={market_hash_name}"
            response = session.get(url)
            regional_price_data = json.loads(response.text)
            lowest_price = regional_price_data["lowest_price"]
            sell_prices.append(convert_price(lowest_price))
            game_details_text.insert(tk.END, f"Name: {market_name}\nSell Price: {lowest_price}\n")

        min_sell_price = min(sell_prices)
        
        game_details_text.insert(tk.END, "- - - - - - - - - - - - - - - - - - - - - - - - \n")

        game_details_text.insert(tk.END, f"Profitability: \n")
        game_details_text.insert(tk.END, f"      * Bad Luck boy: ARS$ {obtainable_cards * min_sell_price} \n")
        game_details_text.insert(tk.END, f"      * Avg: ARS$ {obtainable_cards *(statistics.median(sell_prices))} \n")

        game_details_text.insert(tk.END, f" \n")
        
        game_details_text.insert(tk.END, f"      * Final balance: \n")
        game_details_text.insert(tk.END, f"      * Bad Luck boy: ARS$ { (obtainable_cards * min_sell_price) - convert_price(price) } \n")
        game_details_text.insert(tk.END, f"      * Avg: ARS$ { (obtainable_cards *(statistics.median(sell_prices))) - convert_price(price) } \n")



        
# Create the "Get Details" button
get_details_button = tk.Button(window, text="Get Details", command=get_game_details)
get_details_button.pack()

# Define the filter_numbers function
def filter_numbers(string):
    numbers = ""
    for char in string:
        if char.isdigit():
            numbers += char
    return float(numbers)

def convert_price(price_str):
    # Utilizamos una expresión regular para extraer solo los números y el punto.
    clean_price = re.sub(r'[^\d.]', '', price_str.replace(",", "."))
    
    # Convertimos la cadena en un número en punto flotante.
    price_float = float(clean_price)
    
    return price_float

# Start the Tkinter event loop
window.mainloop()
