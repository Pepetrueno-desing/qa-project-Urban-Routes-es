import data
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


# no modificar
def retrieve_phone_code(driver) -> str:
    import json
    import time
    from selenium.common import WebDriverException
    code = None
    for i in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance') if log.get("message")
                    and 'api/v1/number?number' in log.get("message")]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd('Network.getResponseBody',
                                              {'requestId': message_data["params"]["requestId"]})
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception("No se encontró el código de confirmación del teléfono.\n"
                            "Utiliza 'retrieve_phone_code' solo después de haber solicitado el código en tu aplicación.")
        return code


class UrbanRoutesPage:
    # LOCALIZADORES
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')
    order_taxi_button = (By.XPATH, "//button[contains(text(), 'Pedir un taxi')]")
    comfort_tariff = (By.XPATH, "//div[contains(@class, 'tcard')][.//div[contains(@class, 'tcard-title') and text()='Comfort']]")

    # Teléfono
    phone_button = (By.CLASS_NAME, 'np-button')
    phone_input = (By.ID, 'phone')
    phone_next_button = (By.XPATH, "//button[text()='Siguiente']")
    sms_code_field = (By.CSS_SELECTOR, "#code[placeholder='xxxx']")
    phone_confirm_button = (By.XPATH, "//button[text()='Confirmar']")
    phone_display = (By.CLASS_NAME, 'np-text')

    # Tarjeta
    payment_method_button = (By.CLASS_NAME, 'pp-text')
    add_card_option = (By.XPATH, "//div[contains(@class, 'pp-title') and text()='Agregar tarjeta']")
    card_number_field = (By.ID, 'number')
    card_code_field = (By.CSS_SELECTOR, '#code.card-input')
    add_card_button = (By.XPATH, "//button[contains(@class, 'button full') and text()='Agregar']")
    close_section_button = (By.CLASS_NAME, 'section-close')
    overlay = (By.CLASS_NAME, 'overlay')

    # Mensaje, manta, helados, pedido final
    message_field = (By.ID, 'comment')
    blanket_checkbox = (By.CSS_SELECTOR, '.switch-input')
    ice_cream_plus = (By.XPATH, "//div[contains(@class, 'r-counter-label') and text()='Helado']/ancestor::div[contains(@class, 'r-counter')]//div[contains(@class, 'counter-plus')]")
    ice_cream_value = (By.XPATH, "//div[contains(@class, 'r-counter-label') and text()='Helado']/ancestor::div[contains(@class, 'r-counter')]//div[contains(@class, 'counter-value')]")
    final_order_button = (By.XPATH, "//button[contains(@class, 'smart-button')]")
    search_modal = (By.CLASS_NAME, 'order-body')

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    # ACCIONES
    def set_route(self, from_address, to_address):
        self.wait.until(EC.presence_of_element_located(self.from_field)).send_keys(from_address)
        self.wait.until(EC.presence_of_element_located(self.to_field)).send_keys(to_address)

    def click_order_taxi(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.order_taxi_button))
        btn.click()

    def select_comfort_tariff(self):
        element = self.wait.until(EC.visibility_of_element_located(self.comfort_tariff))
        element.click()

    def set_phone(self, phone):
        phone_btn = self.wait.until(EC.element_to_be_clickable(self.phone_button))
        phone_btn.click()

        phone_field = self.wait.until(EC.visibility_of_element_located(self.phone_input))
        phone_field.clear()
        phone_field.send_keys(phone)

        next_btn = self.wait.until(EC.element_to_be_clickable(self.phone_next_button))
        next_btn.click()

        sms_field = self.wait.until(EC.visibility_of_element_located(self.sms_code_field))
        sms_code = retrieve_phone_code(self.driver)
        sms_field.clear()
        sms_field.send_keys(sms_code)

        confirm_btn = self.wait.until(EC.element_to_be_clickable(self.phone_confirm_button))
        confirm_btn.click()

        self.wait.until(EC.invisibility_of_element_located(self.sms_code_field))

    def add_credit_card(self, card_number, card_code):
        pp_btn = self.wait.until(EC.element_to_be_clickable(self.payment_method_button))
        pp_btn.click()

        add_card = self.wait.until(EC.element_to_be_clickable(self.add_card_option))
        add_card.click()

        number_input = self.wait.until(EC.visibility_of_element_located(self.card_number_field))
        number_input.clear()
        number_input.send_keys(card_number)

        code_input = self.wait.until(EC.visibility_of_element_located(self.card_code_field))
        code_input.clear()
        code_input.send_keys(card_code)
        code_input.send_keys(Keys.TAB)

        add_btn = self.wait.until(EC.element_to_be_clickable(self.add_card_button))
        add_btn.click()

        try:
            close_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.close_section_button)
            )
            close_btn.click()
        except Exception:
            pass

        self.wait.until(EC.invisibility_of_element_located(self.overlay))

    def set_message(self, message):
        msg_input = self.wait.until(EC.visibility_of_element_located(self.message_field))
        msg_input.clear()
        msg_input.send_keys(message)

    def request_blanket(self):
        checkbox = self.wait.until(EC.presence_of_element_located(self.blanket_checkbox))
        self.driver.execute_script("arguments[0].click();", checkbox)

    def request_ice_creams(self, count=2):
        for _ in range(count):
            plus_btn = self.wait.until(EC.presence_of_element_located(self.ice_cream_plus))
            self.driver.execute_script("arguments[0].click();", plus_btn)

    def click_final_order_button(self):
        # Esperar a que el overlay desaparezca antes de hacer clic
        try:
            self.wait.until(EC.invisibility_of_element_located(self.overlay))
        except Exception:
            pass
        btn = self.wait.until(EC.element_to_be_clickable(self.final_order_button))
        self.driver.execute_script("arguments[0].click();", btn)

    # CONSULTAS
    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    def is_comfort_selected(self):
        return "active" in self.driver.find_element(*self.comfort_tariff).get_attribute("class")

    def get_phone(self):
        return self.driver.find_element(*self.phone_display).text

    def get_payment_method(self):
        return self.driver.find_element(By.CLASS_NAME, 'pp-value-text').text

    def get_message(self):
        return self.driver.find_element(*self.message_field).get_property('value')

    def is_blanket_selected(self):
        return self.driver.find_element(*self.blanket_checkbox).is_selected()

    def get_ice_cream_count(self):
        return int(self.driver.find_element(*self.ice_cream_value).text)

    def get_search_modal_text(self):
        modal = self.wait.until(EC.visibility_of_element_located(self.search_modal))
        return modal.text


class TestUrbanRoutes:
    driver = None

    @classmethod
    def setup_class(cls):
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.set_capability("goog:loggingPrefs", {'performance': 'ALL'})
        cls.driver = webdriver.Chrome(options=options)

    def test_set_route(self):
        self.driver.get(data.urban_routes_url)
        page = UrbanRoutesPage(self.driver)
        page.set_route(data.address_from, data.address_to)
        assert page.get_from() == data.address_from
        assert page.get_to() == data.address_to

    def test_select_comfort_tariff(self):
        self.driver.get(data.urban_routes_url)
        page = UrbanRoutesPage(self.driver)
        page.set_route(data.address_from, data.address_to)
        page.click_order_taxi()
        page.select_comfort_tariff()
        assert page.is_comfort_selected()

    def test_set_phone(self):
        self.driver.get(data.urban_routes_url)
        page = UrbanRoutesPage(self.driver)
        page.set_route(data.address_from, data.address_to)
        page.click_order_taxi()
        page.select_comfort_tariff()
        page.set_phone(data.phone_number)
        assert data.phone_number in page.get_phone()

    def test_add_credit_card(self):
        self.driver.get(data.urban_routes_url)
        page = UrbanRoutesPage(self.driver)
        page.set_route(data.address_from, data.address_to)
        page.click_order_taxi()
        page.select_comfort_tariff()
        page.set_phone(data.phone_number)
        page.add_credit_card(data.card_number, data.card_code)
        assert "Tarjeta" in page.get_payment_method()

    def test_set_message(self):
        self.driver.get(data.urban_routes_url)
        page = UrbanRoutesPage(self.driver)
        page.set_route(data.address_from, data.address_to)
        page.click_order_taxi()
        page.select_comfort_tariff()
        page.set_phone(data.phone_number)
        page.set_message(data.message_for_driver)
        assert page.get_message() == data.message_for_driver

    def test_request_blanket(self):
        self.driver.get(data.urban_routes_url)
        page = UrbanRoutesPage(self.driver)
        page.set_route(data.address_from, data.address_to)
        page.click_order_taxi()
        page.select_comfort_tariff()
        page.set_phone(data.phone_number)
        page.request_blanket()
        assert page.is_blanket_selected()

    def test_request_ice_creams(self):
        self.driver.get(data.urban_routes_url)
        page = UrbanRoutesPage(self.driver)
        page.set_route(data.address_from, data.address_to)
        page.click_order_taxi()
        page.select_comfort_tariff()
        page.set_phone(data.phone_number)
        page.request_ice_creams(2)
        assert page.get_ice_cream_count() == 2

    def test_final_order(self):
        self.driver.get(data.urban_routes_url)
        page = UrbanRoutesPage(self.driver)
        page.set_route(data.address_from, data.address_to)
        page.click_order_taxi()
        page.select_comfort_tariff()
        page.set_phone(data.phone_number)
        page.add_credit_card(data.card_number, data.card_code)
        page.set_message(data.message_for_driver)
        page.request_blanket()
        page.request_ice_creams(2)
        page.click_final_order_button()
        modal_text = page.get_search_modal_text()
        assert "Buscar automóvil" in modal_text, f"Modal no contiene 'Buscar automóvil'. Texto: '{modal_text}'"

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()