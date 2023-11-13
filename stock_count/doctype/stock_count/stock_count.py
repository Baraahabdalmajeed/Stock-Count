# Copyright (c) 2023, erpnext and contributors
# For license information, please see license.txt

import random
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from collections import defaultdict
from frappe import get_meta

from stock_count.stock_count.doctype.stock_count_transaction.stock_count_transaction import insert_material_conflicts
from stock_count.stock_count.doctype.stock_count_transaction.stock_count_transaction import insert_material_transactions_child


class StockCount(Document):
    pass
   

######################################################################################################

@frappe.whitelist()
def get_all_children(location):
    listt = []
    yy = []
    x = frappe.get_doc('Location',location)
    if not len(list(x.get_children())): 
        listt.append(x)
        return listt
    listt.append(x)
    for child_doc in list(x.get_children()):
        yy = get_all_children(child_doc.name) + yy
    xx = yy + listt
    return xx

#######################################################################################

@frappe.whitelist()
def get_requested_items(item_name, item_group, start_code, end_code, is_asset):
    filters = []
    if start_code and end_code:
        filters.append(["item_code", ">=", int(start_code)])
        filters.append(["item_code", "<=", int(end_code)])
    else :
         if start_code:
              filters.append(["item_code", ">=", int(start_code)])
         if end_code:
              filters.append(["item_code", "<=", int(end_code)]) 
    if item_name:
        filters.append(["item_name", "like", f"%{item_name}%"])
    if item_group:
        filters.append(["item_group", "like", f"%{item_group}%"])
    if is_asset == '0':
        filters.append(["is_fixed_asset", "=", '0'])
    elif is_asset == '1':
        filters.append(["is_fixed_asset", "=", '1'])
    frappe.msgprint(str(filters))
    fields = ["item_name", "item_code", "item_group"]
    data = frappe.get_all("Item",filters=filters,fields=fields,)
    barcode_field = ['barcode']
    for item in data:
        barcode = frappe.get_all('Item Barcode', filters={'parent': item.item_code}, fields=barcode_field)
        if barcode:
            item['barcode'] = barcode[0].barcode
    return data
    
########################################################################    

@frappe.whitelist()
def get_inserted_items(item_list,is_asset):
    items = []
    if item_list is not None:	
        numbers = item_list.split(" ")	
        for number in numbers:
              item = frappe.get_doc('Item',number) 
              if is_asset == '0' and item.is_fixed_asset == 0:
                items.append(item)
              if is_asset == '1' and item.is_fixed_asset == 1:
                items.append(item)
              else: 
                  if (str(item.is_fixed_asset) != is_asset and is_asset == '1'): frappe.throw("Item {selectedItem} is not an Asset".format(selectedItem = item.item_code))  
                  if (str(item.is_fixed_asset) != is_asset and is_asset == '0'): frappe.throw("Item {selectedItem} is not a Material".format(selectedItem = item.item_code))  
    
    return items
    
###################################################################################################################

@frappe.whitelist(allow_guest=True)
def get_item_barcode(parent):
     barcodes = frappe.get_all('Item Barcode',filters={'parent': parent})
     barcode = frappe.get_doc('Item Barcode',barcodes[0].name) 
     return barcode.barcode

############################################################################################################################
