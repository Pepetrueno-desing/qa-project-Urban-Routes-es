# Proyecto Urban Routes - Automatización de Pruebas con Selenium

## Descripción del Proyecto

Suite de pruebas automatizadas para el flujo completo de pedido de taxi en la aplicación web **Urban Routes**. El proyecto valida el proceso de principio a fin: desde la configuración de la ruta hasta la confirmación del viaje con la aparición del modal de búsqueda de conductor.

La suite cubre los siguientes pasos del flujo:

1. Configuración de dirección de origen y destino.
2. Selección de la tarifa **Comfort**.
3. Relleno del número de teléfono.
4. Adición de una tarjeta de crédito (con manejo opcional de confirmación por SMS).
5. Envío de un mensaje al conductor.
6. Solicitud de "Manta y pañuelos".
7. Pedido de 2 helados.
8. Confirmación del pedido y aparición del modal de búsqueda de taxi.

## Tecnologías y Técnicas Utilizadas

- **Python 3.13**: Lenguaje de programación.
- **Selenium WebDriver 4.52**: Automatización del navegador Chrome.
- **Pytest 9.2**: Framework para la ejecución y organización de pruebas.
- **Page Object Model (POM)**: Patrón de diseño que separa la lógica de la página (`UrbanRoutesPage`) de los tests (`TestUrbanRoutes`).
- **Esperas explícitas (`WebDriverWait`)**: Uso de `expected_conditions` para manejar la carga dinámica de elementos sin recurrir a `time.sleep()`.
- **JavaScript clicks (`execute_script`)**: Para elementos que no son clickeables de forma nativa (tarjetas, checkboxes ocultos, botones con tooltips superpuestos).
- **Manejo de modales y confirmación por SMS**: Uso de la función `retrieve_phone_code()` proporcionada por el repositorio para interceptar el código de confirmación.
- **Git y GitHub**: Control de versiones y publicación del repositorio.

## Estructura del Proyecto
qa-project-Urban-Routes-es/
├── .venv/ # Entorno virtual (no se sube a GitHub)
├── data.py # URL del servidor y datos de prueba
├── main.py # Clases UrbanRoutesPage y TestUrbanRoutes
├── README.md # Este archivo
└── requirements.txt # Dependencias del proyecto

## Instrucciones para Ejecutar las Pruebas

### 1. Clonar el repositorio

```bash
git clone git@github.com:Pepetrueno-desing/qa-project-Urban-Routes-es.git
cd qa-project-Urban-Routes-es