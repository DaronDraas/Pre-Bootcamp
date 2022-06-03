import requests
import pandas as pd
from bs4 import BeautifulSoup

baseUrl = "https://www.sodimac.cl"

headers = {
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
}

productlinks = []

for x in range(1, 9):
    r = requests.get(
        f"https://www.sodimac.cl/sodimac-cl/category/scat922339/Ceramicas?currentpage={x}"
    )
    soup = BeautifulSoup(r.content, "lxml")
    productlist = soup.find_all(
        "div", class_="search-results-products-container"
    )
    for item in productlist:
        for link in item.find_all("a", id="title-pdp-link", href=True):
            productlinks.append(baseUrl + link["href"])

Ceramicaslist = []
for link in productlinks:
    r = requests.get(link)
    soup = BeautifulSoup(r.content, "lxml")
    name = soup.find("div", class_="product-brand").text.strip()
    descripcion = soup.find("h1", class_="product-title").text.strip()
    if soup.find("div", class_="product-model"):
        modelo = soup.find("div", class_="product-model").text.strip()
    else:
        modelo = ""  #or none
    #Formato = soup.find('div', class_="simple-table").text ARREGLAR DATO PRINT POR SI FUNCIONA. 

    SKU = soup.find("div", class_="product-cod").text.strip()
    #precio = soup.find("div", class_="price").text.strip()
    if soup.find("div", class_="price"):
        precio = soup.find("div", class_="price").text.strip()
    else:
        precio = ""

    Ceramicas = {
        "name": name,
        "descripcion": descripcion,
        "modelo": modelo,
        "SKU": SKU,
        "precio": precio,
    }

    Ceramicaslist.append(Ceramicas)
    print(
        "Saving: ",
        Ceramicas["name"],
        Ceramicas["descripcion"],
        Ceramicas["modelo"],
        Ceramicas["SKU"],
        Ceramicas["precio"],
    )

df = pd.DataFrame(Ceramicaslist)
print(df)
df.to_csv('CeramicasSodimac.csv', index=False)
