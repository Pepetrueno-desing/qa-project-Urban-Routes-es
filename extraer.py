from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import data

driver = webdriver.Chrome()
driver.get(data.urban_routes_url)

wait = WebDriverWait(driver, 15)

def guardar_html(nombre):
    with open(f"{nombre}.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"✅ Guardado: {nombre}.html")

# 1. Página inicial
wait.until(EC.presence_of_element_located((By.ID, 'from')))
guardar_html("01_inicial")

# 2. Configurar ruta
driver.find_element(By.ID, 'from').send_keys(data.address_from)
driver.find_element(By.ID, 'to').send_keys(data.address_to)

# 3. Esperar a que aparezcan las tarjetas antes de guardar
wait.until(EC.presence_of_element_located(
    (By.XPATH, "//div[contains(@class, 'tcard')]")
))
guardar_html("02_ruta_con_tarjetas")

# 4. Seleccionar Comfort (con wait)
comfort = wait.until(EC.presence_of_element_located(
    (By.XPATH, "//div[contains(@class, 'tcard')][.//div[contains(@class, 'tcard-title') and text()='Comfort']]")
))
driver.execute_script("arguments[0].scrollIntoView();", comfort)
driver.execute_script("arguments[0].click();", comfort)
guardar_html("03_comfort")

# 5. Clic en "Pedir un taxi"
pedir = wait.until(EC.presence_of_element_located(
    (By.XPATH, "//button[contains(text(), 'Pedir un taxi')]")
))
driver.execute_script("arguments[0].scrollIntoView();", pedir)
driver.execute_script("arguments[0].click();", pedir)
guardar_html("04_pedir_taxi")

# 6. Abrir modal de teléfono
phone_btn = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'np-button')))
driver.execute_script("arguments[0].click();", phone_btn)
guardar_html("05_modal_telefono")

# 7. Rellenar teléfono y avanzar
phone_input = wait.until(EC.visibility_of_element_located((By.ID, 'phone')))
phone_input.clear()
phone_input.send_keys(data.phone_number)
next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Siguiente']")))
driver.execute_script("arguments[0].click();", next_btn)
guardar_html("06_tras_telefono")

# 8. Abrir modal de método de pago
pp_btn = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'pp-text')))
driver.execute_script("arguments[0].click();", pp_btn)
guardar_html("07_modal_pago")

# 9. Seleccionar "Agregar tarjeta"
add_card = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//div[contains(@class, 'pp-title') and text()='Agregar tarjeta']")
))
driver.execute_script("arguments[0].click();", add_card)
guardar_html("08_modal_tarjeta")

print("🎉 Todos los HTML han sido guardados.")
input("Presiona Enter para cerrar el navegador...")
driver.quit()