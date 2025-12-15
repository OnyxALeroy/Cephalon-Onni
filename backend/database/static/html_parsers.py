import requests
from bs4 import BeautifulSoup

url = "https://www.warframe.com/fr/droptables"
resp = requests.get(url, timeout=10)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "lxml")
tables = soup.find_all("table")

with open("./output.txt", 'w') as file:
    for table in tables:
        h3 = table.find_previous("h3")
        title = h3.get_text(strip=True) if h3 else None
        print("TABLE TITLE:", title)
        file.write(title + '\n')
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            values = [cell.get_text(strip=True) for cell in cells]
            print(values)
            file.write('\t' + str(values) + '\n')
    # table = soup.find("table", {"id": "results"})
