frappe.ui.form.on('Stock Count Conflict', {
    refresh: function (frm) {
        frm.add_custom_button(__("Reorder"), function () {
            var doc_name = frm.doc.name;
            frappe.call({
                method: "stock_count.stock_count.doctype.stock_count_conflict.stock_count_conflict.reorder_conflicts",
                type: "POST",
                args: { 'doc_name': doc_name },
                callback: function (res) {
                    window.location.reload();
                }
            });
        });
    },
})
