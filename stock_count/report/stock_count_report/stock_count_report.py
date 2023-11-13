# Copyright (c) 2023, BIS and contributors
# For license information, please see license.txt

# import frappe


import frappe

def execute(filters=None):
	frappe.msgprint('hi from filter change')
	columns, data = [], []
	datesql = filters.date if filters.date else frappe.utils.today()
	data = frappe.db.sql("""
	SELECT item_code, SUM(quantity) AS quantity
	FROM `tabStock Count Transaction` tsct
	WHERE parent_stock_count = %(parent_stock_count)s
	AND conflict_check = 0
	AND scan_date_time <= %(datesql)s
	AND ( type <> 'Count' OR ( type = 'Count' AND tsct.scan_date_time = (
                SELECT MAX(scan_date_time)
                FROM `tabStock Count Transaction`
                WHERE item_code = tsct.item_code
                  AND type = 'Count'
                  AND conflict_check = 0
                  AND scan_date_time <=  %(datesql)s
           		 )
       		 )
   		 )
		 
	GROUP BY item_code; """,{'datesql': datesql,'parent_stock_count':filters.parent_stock_count},as_dict=1)
	# data = [{'item_code': 10080,"quantity":2}]
	columns = [ 
		{"fieldname": "item_code",
			 "label": "Item Code",
			 "fieldtype": "Link", 
			 "options": 'Item',
			 'width': 350},
		{"fieldname": "quantity",
	         "label": "Quantity",
			 "fieldtype": "Int",
			 "width": 350}
					
		]

	return columns, data
