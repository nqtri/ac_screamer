import time
import yaml
from bs4 import BeautifulSoup
import requests
from twilio.rest import Client
from playsound import playsound


# Get Twilio credentials from a YAML file
def get_credentials(key):
    """Return the credential string stored in YAML for a given Twilio credential"""
    with open("creds.yaml", "r") as yaml_file:
        creds_dict = yaml.load(yaml_file, Loader=yaml.BaseLoader)
        cred = creds_dict[key]
    yaml_file.close()
    return cred


def get_page_html(url):
    """Return the HTML content given an URL"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"}
    page_html = requests.get(url, headers=headers)
    return page_html.content


def check_in_stock_status(page_html):
    """Check and return true if an item is in stock, otherwise false"""
    soup = BeautifulSoup(page_html, 'html.parser')
    out_of_stock_divs = soup.findAll("img", {"class": "oos-overlay hide"})  # The OOS image is hidden for in stock items
    return len(out_of_stock_divs) != 0


def setup_twilio_client():
    """"Find and set up your Account SID and Auth Token at twilio.com/console"""
    account_sid = get_credentials("TWILIO_ACCOUNT_SID")
    auth_token = get_credentials("TWILIO_AUTH_TOKEN")
    return Client(account_sid, auth_token)


def send_notification(url):
    """Send SMS notification to your phone number from Twilio phone number and play a notification sound here"""
    twilio_client = setup_twilio_client()
    twilio_client.messages.create(
        body="IN STOCK! Buy it now before too late! \n{}".format(url),
        from_=get_credentials("TWILIO_PHONE_NUMBER"),
        to=get_credentials("PHONE_NUMBER_TO_NOTIFY")
    )
    # Play a notification sound here fore 30 seconds
    t_end = time.time() + 30
    while time.time() < t_end:
        playsound('screaming_ben.mp3')


def check_inventory(url):
    """"Combine above helper functions and print out stock messages"""
    page_html = get_page_html(url)
    if check_in_stock_status(page_html):
        print("In stock now!")
        send_notification(url)
        return True
    else:
        print("Still out of stock!")
        return False


if __name__ == '__main__':
    ac_url = "https://www.costco.ca/danby-14%2c000-btu-ultra-quiet-portable-air-conditioner-with-voice-control-and-rapid-cooling.product.100715465.html"
    stock_indicator = False
    while not stock_indicator:
        stock_indicator = check_inventory(ac_url)
        time.sleep(60) # Wait and check again in 1 minute
