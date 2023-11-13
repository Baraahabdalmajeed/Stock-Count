// Copyright (c) 2023, BIS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Count Report"] = {
	"filters": [
	
				{
					fieldname: "parent_stock_count",
					label: __("Stock Count"),
					fieldtype: "Link",
					reqd: 1,
					options : 'Stock Count',
		
				  },
				  {
					fieldname: "date",
					label: __("Untill Date"),
					fieldtype: "Date",
					reqd: 0,
					default : frappe.datetime.now_datetime()
		
				  }
			]
		};
