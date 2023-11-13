import requests
import json
import frappe 


@frappe.whitelist()
def test(start,end):
    url = 'https://erpnext.main/api/method/stock_count.stock_count.doctype.stock_count_transaction.stock_count_transaction.insert_material_transactions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'token 0a260cdc333e03d:80ed3e7234e3fcc'
    }
    count = start
    while count < end :
        count = count + 1
        payload = {
                "user": "dania@dania.com",
                "device_mac": "0c:23:69:4f:21:11",
                "data": [
                    {
                        "device_transaction_id": 1,
                        "parent_stock_count": "A-Material-4096",
                        "item_code": str(8110 + count),
                        "quantity": "10.00",
                        "scan_date_time": "2022-09-06 10:43:57",
                        "item_site": "Warehouse",
                        "site": "Finished Goods - W",
                        "counter_name": "dania@dania.com",
                        "is_corrective": 0,
                        "type": "Count"
                    }
                ]
            }
        
        json_payload = json.dumps(payload)

        # Make the POST request
        response = requests.post(url, headers=headers, data=json_payload, verify=False)

        # Check the response
        if response.status_code == 200:
            print('Request successful!')
            print(response.json())
        else:
            print('Request failed!')
            print(response.text)