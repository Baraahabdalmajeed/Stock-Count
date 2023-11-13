
from datetime import datetime
import frappe
from frappe.model.document import Document
from stock_count.stock_count.doctype.stock_count_transaction.stock_count_transaction import insert_material_transactions_child

class StockCountConflict(Document):

    def on_change(self):
        if self.workflow_state == 'Approved':
            for row in self.stock_count_transaction_child:
                if (row.conflict_check == 0):
                    trans = frappe.get_doc('Stock Count Transaction',row.reference)
                    trans.conflict_check = 0
                    trans.resolver = frappe.session.user
                    trans.conf_res_date_time = datetime.now()
                    trans.save()
            frappe.db.commit()
            parent_doc = frappe.get_doc('Stock Count',self.parent_stock_count)
            parent_doc.has_inserted_after_close = 0
            parent_doc.save()
            frappe.db.commit()
    
                  

@frappe.whitelist(allow_guest=True)
def reorder_conflicts(doc_name):
 
  child_table = frappe.get_list('Stock Count Transaction Child',  
    filters={'parent': doc_name},
    fields=['name', 'item_code'],
    order_by='item_code')
  for index, row in enumerate(child_table):
    docc = frappe.get_doc('Stock Count Transaction Child',row.name)
    docc.idx = index + 1
    docc.save()
    frappe.db.commit()

  