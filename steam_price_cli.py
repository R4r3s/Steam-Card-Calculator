from asyncio import DatagramTransport
import requests
import json
import sys
from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)

#Initialize variable , region_ratio is set to Argentina, I could've used an api but I am lazy
#You can change the ratio and region_code to your desired country, the region_code represents the price of the game in that region of steam.

region_price_ratio = 256
region_code = "ar"

# Prompt the user to enter the game ID and region code
game_id = input("Enter the game ID: ")

# Create a new session
session = requests.Session()

#print defaults
def game_detail_print():
    print(Fore.GREEN + Style.BRIGHT + "-" * 50)
    print(Fore.GREEN + Style.BRIGHT + " " * 20 +"GAME DETAILS")
    print(Fore.GREEN + Style.BRIGHT + "-" * 50)

#filtering
def filter_numbers(string):
    numbers = ""
    for char in string:
        if char.isdigit():
            numbers += char
    return float(numbers)

# Send a GET request to the URL with the user-provided game ID and region code
url = f"https://store.steampowered.com/api/appdetails?appids={game_id}&cc={region_code}"
url_trade = f"https://steamcommunity.com/market/search/render/?q=&category_753_Event%5B%5D=any&category_753_Game%5B%5D=tag_app_{game_id}&category_753_cardborder%5B%5D=tag_cardborder_0&category_753_item_class%5B%5D=tag_item_class_2&appid=753&norender=1&cc={region_code}"

response = session.get(url)
response_trade = session.get(url_trade)

print (url_trade)

# Extract the JSON data
data = json.loads(response.text)
data_trade = json.loads(response_trade.text)

# Check if the request was successful
if response.status_code == 200 and data.get(game_id, {}).get("success"):
    # Access the desired part of the JSON
    name = data[game_id]["data"]["name"]
    if data[game_id]["data"]["is_free"]:
        game_detail_print()
        print(Fore.CYAN + f"Name: {name}")
        print(Fore.RED + f"{name} is a free game and it doesn't drop cards")
        print(Fore.GREEN + Style.BRIGHT + "-" * 50)
        sys.exit()

    price = data[game_id]["data"]["price_overview"]["final_formatted"]
    price_int = filter_numbers(price)

    cards = data_trade["total_count"]
    sum_card = sum(int(result["sell_price"]) for result in data_trade["results"])

    sum_card /= 100
    


    # Create the menu-style presentation
    game_detail_print()
    print(Fore.CYAN + f"Name: {name}")
    print(Fore.CYAN + f"Price: {price}")
    print(Fore.CYAN + f"Cards Count: {cards}")

    results = data_trade['results']
    market_names = [result['asset_description']['market_name'] for result in results]
    sell_prices = [result['sell_price_text'] for result in results]

    for market_name, sell_price in zip(market_names, sell_prices):
        print(Fore.MAGENTA + Style.BRIGHT + f"Name: {market_name}\nSell Price: {sell_price}")

    print(Fore.CYAN + f"Cards Total Price: {sum_card}$ ~ ARS$ {sum_card*region_price_ratio}")
    profit = round( ((sum_card*region_price_ratio) / 2) - price_int/100, 2 )
    if profit > 10:
        print(Fore.GREEN + f"Profitability: ARS$ {profit}")
    else :
        if profit >0:
            print(Fore.YELLOW + f"Profitability: ARS$ {profit}")
        else: print(Fore.RED + f"Profitability: ARS$ {profit}")

    print(Fore.GREEN + Style.BRIGHT + "-" * 50)

else:
    print(Fore.RED + "Request was not successful.")
