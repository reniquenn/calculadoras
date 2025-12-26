import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def configurar_driver():
    options = Options()
    options.add_argument("--headless") # No abre la ventana del navegador
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Es vital usar un User-Agent real para evitar bloqueos
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_gamovi(producto):
    driver = configurar_driver()
    url = f"https://casagamovi.cl/buscar?controller=search&s={producto}"
    
    try:
        driver.get(url)
        time.sleep(3) # Espera a que cargue el contenido dinámico
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        resultados = []
        # Buscamos los contenedores de productos (ajustar según el HTML real del sitio)
        productos = soup.find_all('article', class_='product-miniature')
        
        for p in productos:
            nombre = p.find('h2', class_='product-title').text.strip()
            precio_texto = p.find('span', class_='price').text.strip()
            # Limpiamos el precio: "$1.490" -> 1490
            precio = int(''.join(filter(str.isdigit, precio_texto)))
            
            resultados.append({
                "producto": nombre,
                "proveedor": "Casa Gamovi",
                "precio": precio,
                "marca": "Detectada",
                "ciudad": "San Francisco",
                "fecha": time.strftime("%Y-%m-%d")
            })
        return resultados
    finally:
        driver.quit()