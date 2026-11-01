import data
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


# no modificar
def retrieve_phone_code(driver) -> str:
    """Este código devuelve un número de confirmación de teléfono y lo devuelve como un string.
    Utilízalo cuando la aplicación espere el código de confirmación para pasarlo a tus pruebas.
    El código de confirmación del teléfono solo se puede obtener después de haberlo solicitado en la aplicación."""

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
    # 1. LOCALIZADORES
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')
    comfort_tariff = (By.XPATH, "//div[contains(@class, 'tcard')][.//div[contains(@class, 'tcard-title') and text()='Comfort']]")
    order_taxi_button = (By.XPATH, "//button[contains(text(), 'Pedir un taxi')]")
    phone_button = (By.CLASS_NAME, 'np-button')
    phone_input = (By.ID, 'phone')
    phone_next_button = (By.XPATH, "//button[text()='Siguiente']")

    # Tarjeta
    payment_method_button = (By.CLASS_NAME, 'pp-text')
    add_card_option = (By.XPATH, "//div[contains(@class, 'pp-title') and text()='Agregar tarjeta']")
    card_number_field = (By.ID, 'number')
    card_code_field = (By.CSS_SELECTOR, '#code.card-input')
    add_card_button = (By.XPATH, "//button[contains(@class, 'button full') and text()='Agregar']")
    sms_code_field = (By.CSS_SELECTOR, "#code[placeholder='xxxx']")
    confirm_button = (By.XPATH, "//button[text()='Confirmar']")
    close_section_button = (By.CLASS_NAME, 'section-close')

    # Mensaje, manta, helados, pedido final
    message_field = (By.ID, 'comment')
    blanket_checkbox = (By.CSS_SELECTOR, '.switch-input')
    ice_cream_plus = (By.XPATH, "//div[contains(@class, 'r-counter-label') and text()='Helado']/ancestor::div[contains(@class, 'r-counter')]//div[contains(@class, 'counter-plus')]")
    ice_cream_value = (By.XPATH, "//div[contains(@class, 'r-counter-label') and text()='Helado']/ancestor::div[contains(@class, 'r-counter')]//div[contains(@class, 'counter-value')]")
    order_button = (By.XPATH, "//button[contains(@class, 'smart-button')]")
    search_modal = (By.CLASS_NAME, 'order-body')

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    # MÉTODOS DE ACCIÓN
    def set_from(self, from_address):
        self.wait.until(expected_conditions.presence_of_element_located(self.from_field)).send_keys(from_address)

    def set_to(self, to_address):
        self.wait.until(expected_conditions.presence_of_element_located(self.to_field)).send_keys(to_address)

    def set_route(self, from_address, to_address):
        self.set_from(from_address)
        self.set_to(to_address)

    def select_comfort_tariff(self):
        element = self.wait.until(expected_conditions.presence_of_element_located(self.comfort_tariff))
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        self.driver.execute_script("arguments[0].click();", element)

    def click_order_taxi(self):
        btn = self.wait.until(expected_conditions.visibility_of_element_located(self.order_taxi_button))
        self.driver.execute_script("arguments[0].scrollIntoView();", btn)
        self.driver.execute_script("arguments[0].click();", btn)

    def set_phone(self, phone):
        phone_btn = self.wait.until(expected_conditions.visibility_of_element_located(self.phone_button))
        self.driver.execute_script("arguments[0].scrollIntoView();", phone_btn)
        self.driver.execute_script("arguments[0].click();", phone_btn)

        phone_field = self.wait.until(expected_conditions.visibility_of_element_located(self.phone_input))
        phone_field.clear()
        phone_field.send_keys(phone)

        next_btn = self.wait.until(expected_conditions.visibility_of_element_located(self.phone_next_button))
        self.driver.execute_script("arguments[0].click();", next_btn)

    def add_credit_card(self, card_number, card_code):
        pp_btn = self.wait.until(expected_conditions.visibility_of_element_located(self.payment_method_button))
        self.driver.execute_script("arguments[0].click();", pp_btn)

        add_card = self.wait.until(expected_conditions.element_to_be_clickable(self.add_card_option))
        self.driver.execute_script("arguments[0].click();", add_card)

        number_input = self.wait.until(expected_conditions.visibility_of_element_located(self.card_number_field))
        number_input.clear()
        number_input.send_keys(card_number)

        code_input = self.driver.find_element(*self.card_code_field)
        code_input.clear()
        code_input.send_keys(card_code)
        code_input.send_keys(Keys.TAB)

        add_btn = self.wait.until(expected_conditions.element_to_be_clickable(self.add_card_button))
        self.driver.execute_script("arguments[0].click();", add_btn)

        try:
            sms_input = WebDriverWait(self.driver, 5).until(
                expected_conditions.visibility_of_element_located(self.sms_code_field)
            )
            sms_code = retrieve_phone_code(self.driver)
            sms_input.clear()
            sms_input.send_keys(sms_code)
            confirm_btn = self.wait.until(expected_conditions.element_to_be_clickable(self.confirm_button))
            self.driver.execute_script("arguments[0].click();", confirm_btn)
        except Exception:
            pass

        try:
            close_btn = WebDriverWait(self.driver, 5).until(
                expected_conditions.element_to_be_clickable(self.close_section_button)
            )
            self.driver.execute_script("arguments[0].click();", close_btn)
        except Exception:
            pass

    def set_message(self, message):
        msg_input = self.wait.until(expected_conditions.visibility_of_element_located(self.message_field))
        msg_input.clear()
        msg_input.send_keys(message)

    def request_blanket(self):
        checkbox = self.wait.until(
            expected_conditions.presence_of_element_located(self.blanket_checkbox)
        )
        self.driver.execute_script("arguments[0].click();", checkbox)

    def request_ice_creams(self, count=2):
        plus_btn = self.wait.until(expected_conditions.element_to_be_clickable(self.ice_cream_plus))
        for _ in range(count):
            self.driver.execute_script("arguments[0].click();", plus_btn)

    def click_final_order_button(self):
        btn = self.wait.until(expected_conditions.element_to_be_clickable(self.order_button))
        self.driver.execute_script("arguments[0].scrollIntoView();", btn)
        self.driver.execute_script("arguments[0].click();", btn)

    def wait_for_search_modal(self):
        self.wait.until(expected_conditions.visibility_of_element_located(self.search_modal))

    # MÉTODOS DE CONSULTA
    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    def is_comfort_selected(self):
        return "active" in self.driver.find_element(*self.comfort_tariff).get_attribute("class")

    def get_phone(self):
        return self.driver.find_element(*self.phone_input).get_property('value')

    def get_payment_method(self):
        return self.driver.find_element(By.CLASS_NAME, 'pp-value-text').text

    def get_message(self):
        return self.driver.find_element(*self.message_field).get_property('value')

    def is_blanket_selected(self):
        return self.driver.find_element(*self.blanket_checkbox).is_selected()

    def get_ice_cream_count(self):
        return int(self.driver.find_element(*self.ice_cream_value).text)


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
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_route(data.address_from, data.address_to)
        assert routes_page.get_from() == data.address_from
        assert routes_page.get_to() == data.address_to

    def test_select_comfort_tariff(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_route(data.address_from, data.address_to)
        routes_page.select_comfort_tariff()
        assert routes_page.is_comfort_selected()

    def test_set_phone(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_route(data.address_from, data.address_to)
        routes_page.select_comfort_tariff()
        routes_page.click_order_taxi()
        routes_page.set_phone(data.phone_number)
        assert routes_page.get_phone() == data.phone_number

    def test_add_credit_card(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_route(data.address_from, data.address_to)
        routes_page.select_comfort_tariff()
        routes_page.click_order_taxi()
        routes_page.set_phone(data.phone_number)
        routes_page.add_credit_card(data.card_number, data.card_code)
        assert "Tarjeta" in routes_page.get_payment_method()

    def test_set_message(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_route(data.address_from, data.address_to)
        routes_page.select_comfort_tariff()
        routes_page.click_order_taxi()
        routes_page.set_phone(data.phone_number)
        routes_page.set_message(data.message_for_driver)
        assert routes_page.get_message() == data.message_for_driver

    def test_request_blanket(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_route(data.address_from, data.address_to)
        routes_page.select_comfort_tariff()
        routes_page.click_order_taxi()
        routes_page.set_phone(data.phone_number)
        routes_page.request_blanket()
        assert routes_page.is_blanket_selected()

    def test_request_ice_creams(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_route(data.address_from, data.address_to)
        routes_page.select_comfort_tariff()
        routes_page.click_order_taxi()
        routes_page.set_phone(data.phone_number)
        routes_page.request_ice_creams(2)
        assert routes_page.get_ice_cream_count() == 2

    def test_final_order(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_route(data.address_from, data.address_to)
        routes_page.select_comfort_tariff()
        routes_page.click_order_taxi()
        routes_page.set_phone(data.phone_number)
        routes_page.add_credit_card(data.card_number, data.card_code)
        routes_page.set_message(data.message_for_driver)
        routes_page.request_blanket()
        routes_page.request_ice_creams(2)
        routes_page.click_final_order_button()
        routes_page.wait_for_search_modal()

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()