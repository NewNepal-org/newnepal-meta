from datetime import date
from dateutil.parser import parse as parse_date
from typing import Union
from nepali.datetime import nepalidate


dates = """6 March 2024
15 July 2024
26 December 2022
27 January 2023
6 March 2024
15 July 2024
26 December 2022
27 January 2023
29 January 2023
1 July 2022
27 January 2023
28 April 2023
22 December 2022
27 January 2023"""

def ad_to_bs(date_obj: Union[date, str]):
    if isinstance(date_obj, str):
        date_obj = parse_date(date_obj).date()
    
    return str(nepalidate.from_date(date_obj))

for d in dates.split("\n"):
    res = ad_to_bs(d)

    print(f"{d} -> {res}")
    print()

# print(converter.ad_to_bs(str(parse_date(d).date()).replace('-', '/')))