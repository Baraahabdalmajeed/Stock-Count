import ast

import json
from logging import raiseExceptions
from math import ceil
import frappe
import sys
from datetime import datetime
from frappe.model.document import Document
from frappe.exceptions import AuthenticationError, DoesNotExistError
from rq import get_current_job
from rq.exceptions import InvalidJobOperation, NoSuchJobError
from frappe.utils import get_link_to_form


class StockCountTransaction(Document):
   pass
            

###################################################################################################################
@frappe.whitelist()
def get_user_countings(user):
    data = frappe.db.sql("""
    SELECT tsc.name,type,manual_site_check,manual_item_check
    FROM `tabStock Count` tsc
    INNER JOIN `tabCount Counters` tc ON tsc.name = tc.parent 
    WHERE tc.counter = %(counter)s
      AND tsc.count_status='Approved'
      AND tsc.start_date <= CURDATE()
      AND (tsc.end_date >= CURDATE() OR tsc.end_date IS NULL);
    """, {'counter': user}, as_dict=1)
    return data
##########################################################################################################
@frappe.whitelist()
def get_counting_materials(count_name, page, page_size):
        offset = int(page) * int(page_size)
        records_count = len(frappe.db.get_all('Count Material',filters={'parent':count_name}))
        max_page = ceil((records_count / int(page_size)))
        item_material = frappe.db.get_all('Count Material',
        filters={'parent':count_name},
        fields=['barcode','item_name','item_code'],
        start=offset,
        order_by ='item_code',
        page_length=page_size,
        as_list=False)
        return {"items" :item_material,'max_page':max_page}

######################################################################################################
@frappe.whitelist(allow_guest=True)
def get_counting_info(count_name):
    counting = frappe.get_doc("Stock Count", count_name)
    number_item = len(counting.items)
    delattr(counting, "counters_list")
    counting_dict = counting.as_dict()
    counting_dict["number_item"] = number_item
    asset_check = counting.get("asset_check") 
    material_check = counting.get("material_check") 
    warehouse_check = counting.get("warehouse_check") 
    location_check= counting.get("location_check") 
    department_check= counting.get("department_check")

    if asset_check == 1:
        item_assets = frappe.db.sql("""
            SELECT tt.item_name, tt.item_code, tib.barcode
            FROM `tabItem` tt
            INNER JOIN `tabItem Barcode` tib ON tt.item_code = tib.parent
            WHERE tt.is_fixed_asset = 1
        """, as_dict=True)
        counting_dict["assets_list"] = item_assets

    if material_check == 1:
        item_material = frappe.db.sql("""
            SELECT tt.item_name, tt.item_code, tib.barcode
            FROM `tabItem` tt
            INNER JOIN `tabItem Barcode` tib ON tt.item_code = tib.parent
            WHERE tt.is_fixed_asset = 0
        """, as_dict=True)
        counting_dict["items"] = item_material
        
    if warehouse_check == 1:
        warehouse = frappe.db.sql("""
          SELECT name from `tabWarehouse` tw
        """, as_dict=True)
        counting_dict["material_warehouse"] = warehouse


    if department_check == 1:
            departments = frappe.db.sql("""
            SELECT  name   from tabDepartment td 
            """, as_dict=True)
            counting_dict["departments"] = departments
    
    if location_check ==1 :
        location = frappe.db.sql("""
         SELECT  name , barcode_location  from `tabLocation` tcl""", as_dict=True)
        counting_dict["locations"] = location

    return counting_dict
######################################################################################################

@frappe.whitelist()
def get_counting_warehouses(count_name, page, page_size):
        offset = int(page) * int(page_size)
        records_count = len(frappe.db.get_all('Count Warehouse',
        filters={'parent':count_name}))
        max_page = ceil((records_count / int(page_size)))
        warehouse = frappe.db.get_all('Count Warehouse',
        filters={'parent':count_name},
        fields=['material_warehouse','barcode'],
        start=offset,
        page_length=page_size,
        as_list=False)
        return {"warehouse" : warehouse,'max_page':max_page}

#########################################################################################################
@frappe.whitelist()
def get_counting_locations(count_name, page, page_size):
        offset = int(page) * int(page_size)
        records_count = len(frappe.db.get_all('Count Location',
        filters={'parent':count_name}))
        max_page = ceil((records_count / int(page_size)))
        location = frappe.db.get_all('Count Location',
        filters={'parent':count_name},
        fields=['location','barcode'],
        start=offset,
        page_length=page_size,
        as_list=False)
        return {"locations" : location,'max_page':max_page}
##########################################################################################################
@frappe.whitelist()
def get_counting_departments(count_name, page, page_size):
        offset = int(page) * int(page_size)
        records_count = len(frappe.db.get_all('Count Department',
        filters={'parent':count_name}))
        max_page = ceil((records_count / int(page_size)))
        departments = frappe.db.get_all('Count Department',
        filters={'parent':count_name},
        fields=['deparment_name'],
        start=offset,
        page_length=page_size,
        as_list=False)
        return {"departments" :departments,'max_page':max_page}

#########################################################################################################
@frappe.whitelist()
def get_counting_assets(count_name, page, page_size):
        offset = int(page) * int(page_size)
        records_count = len(frappe.db.get_all('Count Asset',
        filters={'parent':count_name}))
        max_page = ceil((records_count / int(page_size)))
        assets_list = frappe.db.get_all('Count Asset',
        filters={'parent':count_name},
        fields=['item_name','item_code','barcode'],
        start=offset,
        page_length=page_size,
        as_list=False)
        return {"assets_list" :assets_list,'max_page':max_page}

##########################################################################################################
@frappe.whitelist()
def back_sync_record(counter_name,device_mac,page,page_size):
    offset = int(page) * int(page_size)
    records_count = frappe.db.sql("""SELECT count(*) as total_records
        FROM `tabStock Count` tsc
        INNER JOIN `tabStock Count Transaction` tsct ON tsc.name = tsct.parent_stock_count 
        INNER JOIN `tabCount Counters` tc ON tsc.name = tc.parent 
        WHERE tsc.count_status='Approved' 
        AND tc.counter = %s
        AND device_mac != %s """,(counter_name,device_mac),as_dict=True)
    max_page = ceil((records_count[0]['total_records'] / int(page_size)))
    records = frappe.db.sql("""
        SELECT tsct.*
        FROM `tabStock Count` tsc
        INNER JOIN `tabStock Count Transaction` tsct ON tsc.name = tsct.parent_stock_count 
        INNER JOIN `tabCount Counters` tc ON tsc.name = tc.parent 
        WHERE tsc.count_status='Approved' 
        AND tc.counter = %s
        AND device_mac != %s
        order by creation ASC
        LIMIT %s OFFSET %s
        """, (counter_name,device_mac, int(page_size), offset), as_dict=1)
    return  {"records":records,"max_page":max_page}

####################################################################################################################

@frappe.whitelist()
def calculate_progress_percentage(count_name,count_type):
    if count_type == 'Material':
        items_count = len(frappe.db.get_all('Count Material', filters={'parent': count_name}))
    if count_type == 'Asset':
        items_count = len(frappe.db.get_all('Count Asset', filters={'parent': count_name}))
    counts_count = frappe.db.sql("""
        SELECT count(DISTINCT item_code)
        FROM `tabStock Count Transaction`
        WHERE type = 'Count' AND parent_stock_count = %s
    """, count_name)[0][0]
    if items_count:  
        percentage = (counts_count / items_count) * 100  
        parent_doc = frappe.get_doc('Stock Count',count_name)
        parent_doc.db_set("progress", str(round(percentage,2)) + '  %', update_modified=False)
        frappe.db.commit()
        return {'answer': str(round(percentage,2)) + '  %'}
    else:
        return {'answer':' '}
    

#################################################################################################################
@frappe.whitelist()
def insert_material_conflicts(parent,trans_docs):
        
        doc_name = frappe.get_all('Stock Count Conflict', filters={'parent_stock_count': parent})
        if doc_name:
            doc = frappe.get_doc('Stock Count Conflict', doc_name[0].name)
        else:
            doc = frappe.new_doc('Stock Count Conflict')
            doc.parent_stock_count = parent
        doc.workflow_state = 'Draft'
        for trans in trans_docs:
            for item in doc.stock_count_transaction_child:
                if trans.name == item.reference:
                    frappe.delete_doc('Stock Count Transaction Child',item.name)
            trans_doc = frappe.get_doc('Stock Count Transaction', trans.name)
            row = doc.append('stock_count_transaction_child', {})
            row.update(trans_doc.as_dict()) 
            row.reference = trans.name
        doc.save()
        frappe.db.commit()
        return 1
   
###############################################################################################################
@frappe.whitelist()
def insert_material_transactions_child(parent):
    trans_docs = frappe.get_all('Stock Count Transaction', filters={'parent_stock_count': parent })
    doc = frappe.get_doc('Stock Count', parent)
    doc.set('stock_count_transaction_child', [])
    for trans in trans_docs:
        trans_doc = frappe.get_doc('Stock Count Transaction', trans.name)
        row = doc.append('stock_count_transaction_child', {})
        row.update(trans_doc.as_dict()) 
        row.save()
    doc.save()
    frappe.db.commit()

#######################################################################################

@frappe.whitelist()
def insert_material_transactions():
    data = frappe.request.data.decode('utf-8')
    job = frappe.enqueue(
        insert_material_transaction,
        queue="default",
        data=data,
        timeout=900,
        is_async=True, 
        now=False,
        job_name='Stock Count'
    )
    return  {'job_id':job.id}

################################################################################################################

@frappe.whitelist()
def insert_material_transaction(data):
        job = get_current_job()
        exceptions = []
        has_failed = False
        json_data = json.loads(data)
        data_dict = {}
        if isinstance(json_data["data"], str):
            data_list = ast.literal_eval(json_data["data"])
        elif isinstance(json_data["data"], list):
            data_list = json_data["data"]
        else:
            return "Invalid data format: 'data' field must be a string or a list"
        rq_job = frappe.get_doc('RQ Job',job.id) 
        stock_count_job = frappe.new_doc('Stock Count Job')
        stock_count_job.job_id = rq_job.name
        stock_count_job.job_name = rq_job.job_name
        stock_count_job.status = rq_job.status
        stock_count_job.queue = rq_job.queue
        stock_count_job.arguments = rq_job.arguments
        stock_count_job.count_of_total_records = len(data_list)
        stock_count_job.save()
        frappe.db.commit()
        for data_dict in data_list:
            try:
                parent_doc = frappe.get_doc('Stock Count',data_dict['parent_stock_count'])
                if frappe.session.user in frappe.get_all('Count Counters',fields=['counter'],filters={'parent':data_dict['parent_stock_count']}, pluck='counter'):
                        if parent_doc.end_date > datetime.strptime(data_dict['scan_date_time'], "%Y-%m-%d %H:%M:%S").date():
                            doc = frappe.new_doc('Stock Count Transaction')
                            doc.update(data_dict)
                            if  data_dict['type'] == 'Issuing':
                                 doc.quantity = -abs(int(data_dict["quantity"]))
                            doc.device_mac = json_data["device_mac"]
                            doc.server_date_time = datetime.now()
                            doc.job_id = job.id                        
                            if parent_doc.count_status == 'Closed':
                                parent_doc.has_inserted_after_close = 1
                                doc.after_closed = 1
                                parent_doc.save()
                            doc.save()
                            if data_dict['type'] == 'Count':
                                if not data_dict['is_corrective']:
                                    count = frappe.db.count('Stock Count Transaction', {"item_code":data_dict['item_code'],'parent_stock_count':data_dict['parent_stock_count'],'type':'Count'})
                                    if count > 1:
                                        records = frappe.get_all('Stock Count Transaction',filters={'parent_stock_count':data_dict['parent_stock_count'],"item_code":data_dict['item_code']})
                                        for record in records:
                                            record_ = frappe.get_doc('Stock Count Transaction',record.name)
                                            record_.conflict_check = 1
                                            record_.save()
                                            frappe.db.commit()
                                        insert_material_conflicts(data_dict['parent_stock_count'],records)
                        else: frappe.throw("scan date & time have exceeded end date & time")
                           

                else: frappe.throw("You do not have permission for this count") 
            except Exception:
                has_failed = True
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_message = str(exc_value)
                insert_request_log({'method_called': 'insert_material_transactions',
                                    'time': datetime.now(), 'device_mac': json_data["device_mac"], 'user': data_dict["counter_name"],
                                    'status': "Failed", 'error_message': error_message,'parameters':str(data_dict)})
                exceptions.append(str(data_dict['device_transaction_id']) + "  :  "+ error_message )
        job_name = frappe.db.get_value('Stock Count Job', {'job_id':job.id})
        job_ = frappe.get_doc('Stock Count Job', job_name) 
        if(has_failed):
            job_.status = 'failed'
            job_.exc_info = str(exceptions)
            job_.save()
            frappe.db.commit()
            frappe.msgprint(frappe._("There is exception, review the 'Stock Count Log' doctype to see the error"), raise_exception=True)  
        else:
            job_.status = 'finished'
            job_.save()
            frappe.db.commit()
        return
###########################################################################################################################################
@frappe.whitelist()
def check_is_conflicts_approved(stock_count_name):
     if (frappe.db.get_value('Stock Count Conflict',{'parent_stock_count':stock_count_name},['workflow_state']) == 'Approved') or (frappe.db.get_value('Stock Count Conflict',{'parent_stock_count':stock_count_name}) == None):
        insert_material_transactions_child(stock_count_name)
        parent_doc = frappe.get_doc('Stock Count',stock_count_name)
        parent_doc.has_inserted_after_close = 0
        parent_doc.save()
        return {'check':True}
     if frappe.db.get_value('Stock Count Conflict',{'parent_stock_count':stock_count_name},['workflow_state']) == 'Draft':
        frappe.msgprint('There is conflicts for this stock count, solve it first in document : {0}'
            .format(get_link_to_form('Stock Count Conflict',frappe.db.get_value('Stock Count Conflict',{'parent_stock_count':stock_count_name}))))
        return {'check':False}
#############################################################################################
@frappe.whitelist()
def check_job():
    frappe.enqueue(
       update_jobs_status,
        queue="default",
        timeout=None,
        is_async=True, 
        now=False,
        job_name='Update Job Status'
        )
#################################################################################################################################################
@frappe.whitelist()
def update_jobs_status():
    stockCountJobs = frappe.db.get_all('Stock Count Job', filters={'status': ['not in', ['finished', 'failed']]})
    for sc_job_name in stockCountJobs:
        sc_job_doc = frappe.get_doc('Stock Count Job',sc_job_name) 
        try:
                job = frappe.get_doc('RQ Job', sc_job_doc.job_id)
        except NoSuchJobError:
                job = None   
                if job:
                    if job.status  in ['finished','failed']: 
                        if sc_job_doc.count_of_total_records == frappe.db.count('Stock Count Transaction', {"job_id": sc_job_doc.job_id}):
                                    if sc_job_doc.status == 'finished':
                                        continue
                                    else:
                                        sc_job_doc.status = 'finished'
                                        sc_job_doc.save()
                                        frappe.db.commit()
                        else:
                                    if sc_job_doc.status == 'failed':
                                        continue
                                    else:    
                                        sc_job_doc.status = 'failed'
                                        sc_job_doc.save()
                                        frappe.db.commit()
                else: 
                        successed_records = frappe.db.get_all('Stock Count Transaction',
                                                        filters={"job_id": sc_job_doc.job_id},
                                                        fields=['device_transaction_id'],
                                                        pluck='device_transaction_id')
                        if sc_job_doc.count_of_total_records == frappe.db.count('Stock Count Transaction', {"job_id": sc_job_doc.job_id}):
                                    sc_job_doc.status = 'finished'
                                    sc_job_doc.save()
                                    frappe.db.commit()
                                    return {'job_status': 'finished', 'successed_records': successed_records}
                        else:
                                    sc_job_doc.status = 'failed'
                                    sc_job_doc.save()
                                    frappe.db.commit()
                                    return {'job_status': 'failed', 'successed_records': successed_records}             

############################################################################################################################################


@frappe.whitelist()
def check_job_status(jobId):
    try:
        try:
                job = frappe.get_doc('RQ Job', jobId)
        except NoSuchJobError:
                job = None     
        stockCountJob = frappe.db.get_value('Stock Count Job', {'job_id':jobId})
        stockCountJob_ = frappe.get_doc('Stock Count Job', stockCountJob) 
        if job:
                    if job.status not in ['finished','failed']: 
                        result =  {'job_status' : job.status,'successed_records': []}
                        return result
                    if job.status == 'failed': 
                        successed_records =  frappe.db.get_all('Stock Count Transaction',
                                                               filters={"job_id":jobId},
                                                               fields=['device_transaction_id'],
                                                               pluck = 'device_transaction_id')
                        # stockCountJob_.status = 'failed'
                        # stockCountJob_.save()
                        result =  {'job_status' : 'failed' , 'successed_records': successed_records}
                        return result 
                    if job.status == 'finished':
                        if stockCountJob_.count_of_total_records == frappe.db.count('Stock Count Transaction',{"job_id":jobId}):
                            successed_records =  frappe.db.get_all('Stock Count Transaction',
                                                                   filters={"job_id":jobId},
                                                                   fields=['device_transaction_id'],
                                                                   pluck = 'device_transaction_id')
                            stockCountJob_.status = 'finished'
                            stockCountJob_.save()
                            frappe.db.commit()
                            result =  {'job_status' : 'finished', 'successed_records': successed_records}
                            return result
                        else:
                            stockCountJob_.status = 'failed'
                            stockCountJob_.save()
                            frappe.db.commit()
                            result =  {'job_status' : 'failed' , 'successed_records': successed_records} 
                            return result 
        else:
        
            successed_records = frappe.db.get_all('Stock Count Transaction',
                                                        filters={"job_id": jobId},
                                                        fields=['device_transaction_id'],
                                                        pluck='device_transaction_id')
            if stockCountJob_.count_of_total_records == frappe.db.count('Stock Count Transaction', {"job_id": jobId}):
                        stockCountJob_.status = 'finished'
                        stockCountJob_.save()
                        frappe.db.commit()
                        return {'job_status': 'finished', 'successed_records': successed_records}
            else:
                        stockCountJob_.status = 'failed'
                        stockCountJob_.save()
                        frappe.db.commit()
                        return {'job_status': 'failed', 'successed_records': successed_records}
    except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_message = str(exc_value)

                return error_message
###########################################################################################################################################

def insert_request_log(record):
    doc = frappe.new_doc('Stock Count Log')
    doc.update(record) 
    doc.save()
    frappe.db.commit()
        
    return record
#########################################################################################################################################
@frappe.whitelist()
def get_all_warehouse():
     warehouses = frappe.get_all("Warehouse",  fields=["name","barcode"])
     return warehouses
#################################################################################################
@frappe.whitelist()
def get_all_departments():
     departments = frappe.get_all("Department",  fields=["name"])
     return departments
##############################################################################################################

@frappe.whitelist()
def get_all_location():
    location = frappe.get_all("Location",  fields=["name","barcode_location"])
    return location
############################################################################################################
@frappe.whitelist()
def get_all_materials():
    items = frappe.db.sql("""
            SELECT tt.item_name, tt.item_code, tib.barcode
            FROM `tabItem` tt
            INNER JOIN `tabItem Barcode` tib ON tt.item_code = tib.parent
            WHERE tt.is_fixed_asset = 0
            """,as_dict=True)
    return items

##############################################################################################################
@frappe.whitelist()
def get_all_assets():
    items = frappe.db.sql("""
            SELECT tt.item_name, tt.item_code, tib.barcode
            FROM `tabItem` tt
            INNER JOIN `tabItem Barcode` tib ON tt.item_code = tib.parent
            WHERE tt.is_fixed_asset = 1
            """,as_dict=True)
    return items
##########################################################################################################
# import requests
# import json
# @frappe.whitelist()
# def test():
#     # Set up the URL
#     url = 'http://erpnext.main/api/method/stock_count.stock_count.doctype.stock_count_transaction.stock_count_transaction.insert_material_transactions'

#     # Set up the headers
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': 'token 0a260cdc333e03d:80ed3e7234e3fcc'
#     }

#     # Set up the request body
#     payload = [
#         {
#             "user": "dania@dania.com",
#             "device_mac": "0c:23:69:4f:21:11",
#             "data": [
#                 {
#                     "device_transaction_id": 1,
#                     "parent_stock_count": "Class B-Asset-7173",
#                     "item_code": 500,
#                     "quantity": "10.00",
#                     "scan_date_time": "2022-09-06 10:43:57",
#                     "item_site": "Warehouse",
#                     "site": "Finished Goods - W",
#                     "counter_name": "dania@dania.com",
#                     "is_corrective": 0,
#                     "type": "Count"
#                 }
#             ]
#         }
#     ]
#     json_payload = json.dumps(payload)

#     # Make the POST request
#     response = requests.post(url, headers=headers, data=json_payload, verify=False)

#     # Check the response
#     if response.status_code == 200:
#         print('Request successful!')
#         print(response.json())
#     else:
#         print('Request failed!')
#         print(response.text)






#####################################################################################
import random
@frappe.whitelist(allow_guest=True)
def populate(counter_value):
    strlist = ['All Item Groups', 'Products', 'Consumable']
    count = 0
    while count < int(counter_value):
        doc = frappe.new_doc('Item')
        doc.item_code = str(7000 + count)
        doc.item_name = 'item asset ' + str(count)
        doc.item_group = random.choice(strlist)
        doc.is_stock_item = 0
        doc.asset_category = 'e'
        doc.is_fixed_asset = 1
        barcode = str(7000 + count)
    
        doc.append('barcodes', {'barcode': barcode})
        doc.save()
        count += 1
        frappe.db.commit()