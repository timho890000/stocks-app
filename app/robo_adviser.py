from dotenv import load_dotenv
import json
import os, shutil
import requests
from IPython import embed #what is this for
import csv
import datetime

load_dotenv() # loads environment variables set in a ".env" file, including the value of the ALPHAVANTAGE_API_KEY variable
api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "OOPS. Please set an environment variable named 'ALPHAVANTAGE_API_KEY'."
if api_key == "OOPS. Please set an environment variable named 'ALPHAVANTAGE_API_KEY'.":
    print(api_key)
    exit()

# TODO: Allow it to choose multiple symbols
symbols = []

#found on internet: https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder-in-python
folder = "data"
for the_file in os.listdir(folder):
    file_path = os.path.join(folder, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
        #elif os.path.isdir(file_path): shutil.rmtree(file_path)
    except Exception as e:
        print(e)

while True:#fIX THIS SOMETIMES IT"SACCEPTING BAD ONES right now
    symbol = input("Please enter the ticker of the stock you would like to analyze!, to type 'finish' to stop. ").upper()
    if(symbol=="FINISH"):
        break
    good = True
    i = 0
    for s in symbol:
        i = i+1
        #print(str(s.isalpha()))
        try:
            x = int(s)
            good=(good and False)
        except:
            good=(good and True)
    if(good == False):
        print("Please do not use numbers")
        continue
    if(i<1 or i>5):
        print("Please enter a ticker with 1-5 characters")
        continue
    request_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="+symbol+"&apikey="+api_key
    response = requests.get(request_url)
    if "Error Message" in response.text:
        print("Sorry. There is no information in this database on this ticker.")
        good = False

    if(good==True):
        symbols.append(symbol)
        print(f"{symbol} has been added to your list of stocks!")


print("-----------------------------------------------------------")


# see: https://www.alphavantage.co/documentation/#daily
# TODO: assemble the request url to get daily data for the given stock symbol
#use time-series daily. find url on the wbsite. use your API code.
#print(request_url)

# TODO: issue a "GET" request to the specified url, and store the response in a variable

def write_data_to_file(filename, info):  # data will be a dictionary of dictionaries. Date, then the four datapoints.
    filepath = os.path.join(os.path.dirname(__file__), "data", filename)
    with open(filepath, "a") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp","1. open","2. high","3. low","4. close","5. volume"] , lineterminator = '\n')
        writer.writerow(info)
def write_header_to_file(filename, info):  # data will be a dictionary of dictionaries. Date, then the four datapoints.
    filepath = os.path.join(os.path.dirname(__file__), "data", filename)
    with open(filepath, "a") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp","open","high","low","close","volume"] , lineterminator = '\n')
        writer.writeheader()
def write_symbol_to_file(filename, symbol):  # data will be a dictionary of dictionaries. Date, then the four datapoints.
    filepath = os.path.join(os.path.dirname(__file__), "data", filename)
    with open(filepath, "a") as csv_file:
        writer = csv.writer(csv_file, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL,lineterminator = '\n')
        writer.writerow(symbol)


run_time = datetime.datetime.now()
print("Information request ran at: "+ str(run_time.strftime("%A, %B %d, %Y at %I:%M%p")))
print("-----------------------------------")


for symbol in symbols:
    request_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="+symbol+"&outputsize=full&apikey="+api_key
    response = requests.get(request_url) #this is a json
    response_body = json.loads(response.text) #this is a list of dictionaries
    last_refreshed = response_body["Meta Data"]["3. Last Refreshed"]

    #print(response_body["Meta Data"]) # this is a dictionary
    #rint()
    fieldnames=["1. open","2. high","3. low","4. close","5. volume"]
    fieldnames2=["open","high","low","close","volume"]
    data = response_body["Time Series (Daily)"] # still a dictionary
    keys = data.keys()
    all_dates = list(keys) # a list of the keys
    dates =[]
    i=0
    while(i<252):
        dates.append(all_dates[i])
        i=i+1
    today = dates[0]
    symbol2 = symbol.upper()
    #for loop to make a list of values such as prices and stuff
    #take the values from the dictionary which is response_body
    latest_price_usd = data[today]["4. close"] # TODO: traverse the nested response data structure to find the latest closing price
    print(symbol2)
    print("Last refreshed on "+last_refreshed)
    print("-----------------------------------")
    print("Closing price on "+today+ "for "+symbol2 +" is: "+"(${0:.2f})".format(float(latest_price_usd)))
    high_prices = []
    for d in dates:
        high_prices.append(data[d]["2. high"])
    average_high_price = max(high_prices)
    #fill in the variables. print to find, or just look at websiste
    print("The 52 week high price for "+symbol2+" is: "+"(${0:.2f})".format(float(average_high_price)))
    low_prices = []
    for d in dates:
        low_prices.append(data[d]["3. low"])
    average_low_price = min(low_prices)
    #fill in the variables. print to find, or just look at websiste
    print("The 52 week low price for "+symbol2+" is: "+"(${0:.2f})".format(float(average_low_price)))

    if(float(latest_price_usd)<(float(average_high_price)+float(average_low_price))/2):
        print("The current price is less than the midpoint of the 52 week high and low. This is a cheap stock and you should buy "+symbol)
    else:
        print("The current price is more than the midpoint of the 52 week high and low.  This stock is pretty expensive, so you should not buy "+symbol)
    print("-----------------------------------")

    info = []
    values = {}
    write_header_to_file(f"prices-{symbol2}.csv",fieldnames2)
    for d in dates:
        values["timestamp"] = d
        for f in fieldnames:
            values[f] = data[d][f]
        write_data_to_file(f"prices-{symbol2}.csv",values)
