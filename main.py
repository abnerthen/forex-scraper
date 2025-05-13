import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
import os
import json
import base64
import datetime
from dotenv import load_dotenv

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

load_dotenv()

credential_file = json.loads(base64.b64decode(os.environ['GOOGLE_CREDENTIALS']))

# print(type(credential_file))

creds = Credentials.from_service_account_info(credential_file, scopes=scopes)

client = gspread.authorize(creds)

sheet_id = "1JPoSfhVYdmt6MXzk1b7W8lsge5UOZNKLq0B6JjyTCi0"

sheet = client.open_by_key(sheet_id)

worksheet = sheet.sheet1

values_list = sheet.sheet1.row_values(1)


def get_rates(bank):
    if bank == 'cimb':
        url = 'https://www.cimbniaga.co.id/content/cimb/id/personal/treasury/kurs-valas/jcr:content/responsivegrid/kurs_copy_copy_copy.get-content'
    elif bank == 'bca':
        url = 'https://www.bca.co.id/id/informasi/kurs'
    else:
        print("Invalid bank! Please try again.")

    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.select("table tr")
    for row in rows:
        columns = row.find_all('td')
        if columns:
            currency = columns[0].text.strip()
            buy = columns[1].text.strip()
            sell = columns[2].text.strip()
            if bank == 'bca':
                replacer = lambda x: x.replace('.', '').replace(',', '.')
                buy, sell = map(replacer, (buy, sell))
            # print(f"{currency}: Buy={buy}, Sell={sell}")
            if currency == 'USD':
                withdrawal_value = float(buy)
                deposit_value = float(sell)
    return bank, withdrawal_value, deposit_value




if __name__ == '__main__':
    '''
    bank = input('Please select the bank which you want to extract the exchange rate of (B: BCA, C: CIMB)')
    if bank not in ('B', 'C'):
        print("Invalid bank!")
        pass
    if bank == 'B':
        print(get_rates('bca'))
    elif bank == 'C':
        print(get_rates('cimb'))
    '''
    b = list(get_rates('bca'))
    b.insert(0, datetime.datetime.now().isoformat())
    c = list(get_rates('cimb'))
    c.insert(0, datetime.datetime.now().isoformat())
    print(b)
    print(c)
    worksheet.insert_row(b, index = (len(worksheet.get()) + 1))
    worksheet.insert_row(c, index = (len(worksheet.get()) + 1))
    print("Appended.")

