from . import __version__ as app_version

app_name = "stock_count"
app_title = "Stock Count"
app_publisher = "BIS"
app_description = "StockCount"
app_email = "BIS"
app_license = "MIT"

# Includes in <head>
# ------------------
scheduler_events = {
    
    "cron": {
        "*/1 * * * *": [
            "stock_count.stock_count.doctype.stock_count_transaction.stock_count_transaction.check_job"
        ]
    }
}
# # include js, css files in header of desk.html
# app_include_css = "/assets/stock_count/css/stock_count.css"
# app_include_js = "/assets/stock_count/js/stock_count.js"

# include js, css files in header of web template
# web_include_css = "/assets/stock_count/css/stock_count.css"
# web_include_js = "/assets/stock_count/js/stock_count.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "stock_count/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "stock_count.utils.jinja_methods",
#	"filters": "stock_count.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "stock_count.install.before_install"
# after_install = "stock_count.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "stock_count.uninstall.before_uninstall"
# after_uninstall = "stock_count.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "stock_count.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"stock_count.tasks.all"
#	],
#	"daily": [
#		"stock_count.tasks.daily"
#	],
#	"hourly": [
#		"stock_count.tasks.hourly"
#	],
#	"weekly": [
#		"stock_count.tasks.weekly"
#	],
#	"monthly": [
#		"stock_count.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "stock_count.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "stock_count.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "stock_count.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["stock_count.utils.before_request"]
# after_request = ["stock_count.utils.after_request"]

# Job Events
# ----------
# before_job = ["stock_count.utils.before_job"]
# after_job = ["stock_count.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"stock_count.auth.validate"
# ]
