// Copyright (c) 2023, BIS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Count Transaction', {
	

	refresh: function(frm) {
		frm.set_query("item_site", function() {
			return {
			  filters: {
				"name": ["in",['warehouse','location']],
			  }
			}
		})
	}
});

frappe.ui.form.on("Stock Count Transaction", "validate", function(frm) {
		if (!frm.doc.device_mac) {
			frappe.msgprint(__("you cant insert a transaction from back-office"));
			frappe.validated = false;
		}
});