from pathlib import Path
from config import *
import pandas as pd
import zipcodes

def read_csv():
# Automatically finds the current user's Downloads folder
  downloads_path = Path.home() / "Downloads" / "Tonnage -MI .csv"

  crm_csv = pd.read_csv(downloads_path)
  
  return crm_csv
  


def mergeJSON(products):
  products_df = pd.read_json(JSON_FILE_STR, orient="index")
  products_df = products_df.reset_index().rename(columns={"index": PRODUCT_NAME_STR})
  merged_df = products.merge(products_df, on=PRODUCT_NAME_STR)
  return merged_df


def calculate_tonnage(merged_df):
  grouped_products = merged_df.groupby([PRODUCT_NAME_STR, SHIPPING_CODE_STR, SHIPPING_CITY_STR, PACKAGE_SIZE_STR, POUNDS_PER_GALLON_STR, NPK_STR])[QUANTITY_STR].sum().reset_index()
  PACKAGE_SIZE = grouped_products[PACKAGE_SIZE_STR]
  POUNDS_PER_GALLON = grouped_products[POUNDS_PER_GALLON_STR]
  QUANTIY= grouped_products[QUANTITY_STR]
  
  total_weight = round((PACKAGE_SIZE * POUNDS_PER_GALLON * QUANTIY) / 2000, 3)

  grouped_products[TONNAGE_STR] = total_weight
  return grouped_products
  
def add_county_from_zip(df):
    def lookup(z):
        matches = zipcodes.matching(str(z))
        return matches[0]["county"] if matches else None

    df[COUNTY_STR] = df[SHIPPING_CODE_STR].apply(lookup)
    
products = read_csv()
combined_df = mergeJSON(products)
completed_tonnage_report = calculate_tonnage(combined_df)
add_county_from_zip(completed_tonnage_report)


print(completed_tonnage_report)
print(round(completed_tonnage_report[TONNAGE_STR].sum(), 3))