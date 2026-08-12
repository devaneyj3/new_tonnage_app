import os

# Define string constants
JSON_FILE_STR = 'products.json'
UPLOAD_FOLDER_STR = 'uploads'
PRODUCT_NAME_STR = 'Product Name'
QUANTITY_STR = 'Quantity'
SHIPPING_STATE_STR = 'Shipping State'
SHIPPING_CITY_STR = 'Shipping City'
SHIPPING_CODE_STR = 'Shipping Code'
SHIPPING_STATE_STR = 'Shipping State'
SHIPPED_STR = 'Shipped'
ORDERED_STR = 'Ordered'
AMOUNT_STR = 'Amount'
PACKAGE_SIZE_STR = 'PACKAGE_SIZE'
POUNDS_PER_GALLON_STR = 'POUNDS_PER_GALLON'
NPK_STR = 'NPK'
TONNAGE_STR = 'Tonnage'
COUNTY_STR = 'County'

# Define the path to the JSON file relative to the script's location
JSON_FILE_PATH = os.path.join(os.path.dirname(__file__), JSON_FILE_STR)
