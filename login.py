from datetime import datetime
import frappe 


@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response['http_status_code'] = 401
        frappe.local.response["message"] = {
            "message":"Authentication Error!"
        }
        return

    
    user = frappe.get_doc('User', frappe.session.user)
    frappe.response["message"] = {
         "user" : {
            "username":user.name,
            "api_key":user.api_key,
        },
        "api_secret":frappe.utils.password.get_decrypted_password('User', user.name, fieldname="api_secret"),        
        "server_date_time":datetime.now()
    }
