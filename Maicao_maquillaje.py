import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import re

baseUrl = "https://www.maicao.cl/"
searchUrl = "https://www.maicao.cl/maquillaje/?start={}&sz=18&maxsize=18"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
}
productlinks = []

# Obtener enlaces de la primera página
first_page_url = "https://www.maicao.cl/maquillaje/?start=0&sz=18&maxsize=18"
r = requests.get(first_page_url, headers=headers)
if r.status_code == 200:
    soup = BeautifulSoup(r.content, "lxml")
    productlist = soup.find_all("a", class_="w-100 text-center no-outline")
    for link in productlist:
        href = link.get("href", "")
        if href:
            productlinks.append(baseUrl + href)

# Obtener enlaces de las páginas siguientes
page = 2
increment = 18

while True:
    offset = (page - 1) * increment + 1
    url = searchUrl.format(offset)
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        break  # Si hay un error en la solicitud, detener el bucle
    
    soup = BeautifulSoup(r.content, "lxml")
    productlist = soup.find_all("a", class_="w-100 text-center no-outline")
    
    if not productlist:
        break  # Si no hay productos en la página, detener el bucle
    
    for link in productlist:
        href = link.get("href", "")
        if href:
            productlinks.append(baseUrl + href)
    
    page += 1

print(f"Total product links: {len(productlinks)}")

lista_belleza = []
for link in productlinks:
    r = requests.get(link, headers=headers)
    if r.status_code != 200:
        continue  # Si hay un error en la solicitud, omitir este link
    soup = BeautifulSoup(r.content, "lxml")
    items = soup.find_all("div", class_="container pt-4 product-detail-container")

    for item in items:
        try:
            brand = item.find("a", class_="product-brand m-0").text.strip()
        except AttributeError:
            brand = ""

        try:
            producto = item.find("h2", class_="product-name").text.strip()
        except AttributeError:
            producto = ""

        # Obtener el precio desde el span con clase value
        try:
            precio_span = item.find("span", class_="value")
            if precio_span:
                # Extraer solo el precio usando una expresión regular
                precio_text = precio_span.text.strip()
                precio_match = re.search(r'\$\d+(\.\d{1,3})?', precio_text)
                if precio_match:
                    precio = precio_match.group()
                else:
                    precio = ""
            else:
                precio = ""
        except AttributeError:
            precio = ""

        # Si el precio no se encontró en value, buscar en price-original
        if not precio:
            try:
                precio_span = item.find("span", class_="price-original")
                if precio_span:
                    precio_text = precio_span.text.strip()
                    precio_match = re.search(r'\$\d+(\.\d{1,3})?', precio_text)
                    if precio_match:
                        precio = precio_match.group()
                    else:
                        precio = ""
                else:
                    precio = ""
            except AttributeError:
                precio = ""

        belleza = {
            "brand": brand,
            "producto": producto,
            "precio": precio
        }

        lista_belleza.append(belleza)
        print(f"Saving: {belleza['brand']}, {belleza['producto']}, {belleza['precio']}")

df = pd.DataFrame(lista_belleza)
print(df)

#Obtener la fecha y hora actual
now = datetime.datetime.now()
# Formatear la fecha y hora
formatted_time = now.strftime("%Y%m%d%H%M%S")
# Guardar el DataFrame como un archivo CSV con la fecha y hora en el nombre del archivo
df.to_csv(f'Maicao_belleza_{formatted_time}.csv', index=False)
