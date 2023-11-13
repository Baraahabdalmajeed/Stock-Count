frappe.ui.form.on('Stock Count', {
  refresh: function (frm) {
    frm.fields_dict['stock_count_transaction_child'].grid.toggle_display('reference', false);
    frm.refresh_field('stock_count_transaction_child');
    cur_frm.fields_dict.items.grid.grid_pagination.page_length = 20
    cur_frm.refresh_fields('items')
    if (frm.doc.type === 'Material') {
      frm.add_custom_button(("Get items"),
        function () {
          d.show();
          d.frm = frm
        });
    }

    frm.add_custom_button(__("Move Transactions Into Child Table"), function () {
      frappe.call({
        method: "stock_count.stock_count.doctype.stock_count_transaction.stock_count_transaction.check_is_conflicts_approved",
        type: "POST",
        args: { 'stock_count_name': frm.doc.name },
        callback: function (res) {
          console.log(res.message)
          if (res.message.check == true) {
            window.location.reload()
          }
        }
      });
    });
  },

  onload: function (frm) {
    console.log('outside if');
    console.log(frm.doc.type);
    if (frm.doc.type) {
      console.log('inside if');
      frappe.call({
        method: "stock_count.stock_count.doctype.stock_count_transaction.stock_count_transaction.calculate_progress_percentage",
        type: "POST",
        args: {
          'count_name': frm.doc.name,
          'count_type': frm.doc.type
        },
        callback: function (res) {
          frm.doc.progress = res.message.answer
          frm.refresh_field("progress");
        }

      });
    }

    frm.fields_dict['stock_count_transaction_child'].grid.get_field('item_site').set_query = function (frm, a, b) {
      return {
        filters: {
          "name": ["in", ['warehouse', 'location']],
        }
      }
    }
    frm.fields_dict['items'].grid.get_field('item_code').get_query = function (frm, a, b) {
      let choseItems = []
      frm.items.forEach(element => {
        if (element !== undefined && element.item_code !== undefined) { choseItems.push(element.item_code); }
      });
      return {
        filters: [
          ["name", "not in", choseItems],
          ["is_fixed_asset", "=", "0"]
        ]
      }
    }
    frm.fields_dict['assets_list'].grid.get_field('item_code').get_query = function (frm, a, b) {
      let choseItems = []
      frm.assets_list.forEach(element => {

        if (element !== undefined && element.item_code !== undefined) { choseItems.push(element.item_code); }
      });
      return {
        filters: [
          ["name", "not in", choseItems],
          ["is_fixed_asset", "=", "1"]
        ]
      }
    }
    frm.fields_dict['locations'].grid.get_field('location').get_query = function (frm, a, b) {
      let choseItems = []
      frm.locations.forEach(element => {

        if (element !== undefined && element.location !== undefined) { choseItems.push(element.location); }

      });
      return {
        filters: [
          ["name", "not in", choseItems],
        ]
      }
    }
  },
  before_save: function (frm, cdt, cdn) {
    var child_table_items = frm.doc.items || []
    var child_table_departments = frm.doc.departments || []
    var child_table_warehouse = frm.doc.material_warehouse || []
    var child_table_locations = frm.doc.locations || []
    var child_table_assets = frm.doc.assets_list || []
    if (frm.doc.type === 'Material' && child_table_items.length === 0 && frm.doc.material_check === 0) {
      frappe.msgprint({
        title: ('Error'),
        indicator: 'red',
        message: ('You Cannot Save Because No Materials Were Selected')
      });
      frappe.validated = false;
    }
    if (child_table_departments.length === 0 && frm.doc.department_check === 0) {
      frappe.msgprint({
        title: ('Error'),
        indicator: 'red',
        message: ('You Cannot Save Because No Departments Were Selected')
      });
      frappe.validated = false;
    }
    if (frm.doc.type === 'Material' && child_table_warehouse.length === 0 && frm.doc.warehouse_check === 0) {
      frappe.msgprint({
        title: ('Error'),
        indicator: 'red',
        message: ('You Cannot Save Because No Warehouses Were Selected')
      });
      frappe.validated = false;
    }
    if (frm.doc.type === 'Asset' && child_table_assets.length === 0 && frm.doc.asset_check === 0) {
      frappe.msgprint({
        title: ('Error'),
        indicator: 'red',
        message: ('You Cannot Save Because No Assets Were Selected')
      });
      frappe.validated = false;
    }
    if (frm.doc.type === 'Asset' && child_table_locations.length === 0 && frm.doc.location_check === 0) {
      frappe.msgprint({
        title: ('Error'),
        indicator: 'red',
        message: __('You Cannot Save Because No Locations Were Selected')
      });
      frappe.validated = false;
    }
    if (frm.doc.type === 'Asset') {
      cur_frm.clear_table("items")
      cur_frm.clear_table("material_warehouse")
    }
    if (frm.doc.type === 'Material') {
      cur_frm.clear_table("assets_list")
      cur_frm.clear_table("locations")
    }
  },
  material_check: function (frm) {


    if (frm.doc.material_check === 1) {

      frappe.call({
        method: "stock_count.stock_count.doctype.stock_count_transaction.stock_count_transaction.get_all_materials",
        args: {},
        callback: (res) => {
          res.message.forEach((item) => {
            let entry = frm.add_child("items");
            entry.item_code = item.item_code;
            entry.item_name = item.item_name;
            entry.barcode = item.barcode;
          });
          frm.refresh_field("items")
        }
      })

    }
    if (frm.doc.material_check === 0) {
      cur_frm.clear_table("items")
      frm.refresh_field("items")
    }
  },

  warehouse_check: function (frm) {
    if (frm.doc.warehouse_check === 1) {

      frappe.call({
        method: "stock_count.stock_count.doctype.stock_count_transaction.stock_count_transaction.get_all_warehouse",
        args: {},
        callback: (res) => {
          res.message.forEach((item) => {
            let entry = frm.add_child("material_warehouse");
            entry.material_warehouse = item.name;
            entry.barcode = item.barcode;
          });
          frm.refresh_field("material_warehouse")
        }
      })

    }
    if (frm.doc.warehouse_check === 0) {
      cur_frm.clear_table("material_warehouse")
      frm.refresh_field("material_warehouse")
    }
  },


  department_check: function (frm) {
    if (frm.doc.department_check === 1) {

      frappe.call({
        method: "stock_count.stock_count.doctype.stock_count_transaction.stock_count_transaction.get_all_departments",
        args: {},
        callback: (res) => {
          res.message.forEach((item) => {
            let entry = frm.add_child("departments");
            entry.deparment_name = item.name;

          });
          frm.refresh_field("departments")
        }
      })

    }
    if (frm.doc.department_check === 0) {
      cur_frm.clear_table("departments")
      frm.refresh_field("departments")
    }
  },
  asset_check: function (frm) {
    if (frm.doc.asset_check === 1) {

      frappe.call({
        method: "stock_count.stock_count.doctype.stock_count_transaction.stock_count_transaction.get_all_assets",
        args: {},
        callback: (res) => {
          res.message.forEach((item) => {
            let entry = frm.add_child("assets_list");
            entry.item_code = item.item_code;
            entry.item_name = item.item_name;
            entry.barcode = item.barcode;

          });
          frm.refresh_field("assets_list")
        }
      })

    }
    if (frm.doc.asset_check === 0) {
      cur_frm.clear_table("assets_list")
      frm.refresh_field("assets_list")
    }
  },
  location_check: function (frm) {
    if (frm.doc.location_check === 1) {

      frappe.call({
        method: "stock_count.stock_count.doctype.stock_count_transaction.stock_count_transaction.get_all_location",
        args: {},
        callback: (res) => {
          res.message.forEach((item) => {
            let entry = frm.add_child("locations");
            entry.location = item.name;
            entry.barcode = item.barcode_location;

          });
          frm.refresh_field("locations")
        }
      })

    }
    if (frm.doc.location_check === 0) {
      cur_frm.clear_table("locations")
      frm.refresh_field("locations")
    }
  }
})


let d = new frappe.ui.Dialog({
  title: 'Enter details',
  fields: [
    {
      label: 'Multiple Item Insertion',
      fieldname: 'insert_check',
      fieldtype: 'Check',
      default: 0
    },
    {
      label: 'Item-Name List',
      fieldname: 'item_list',
      fieldtype: 'Data',
      depends_on: "eval:doc.insert_check == 1",
      length: '2000'
    },
    {
      label: 'Item Name',
      fieldname: 'item_name',
      fieldtype: 'Data',
      depends_on: "eval:doc.insert_check == 0",
    },
    {
      label: 'Item Group',
      fieldname: 'item_group',
      fieldtype: 'Link',
      options: 'Item Group',
      depends_on: "eval:doc.insert_check == 0",
    },
    {
      label: 'Item Code',
      fieldname: 'from_to',
      fieldtype: 'Section Break',
      depends_on: "eval:doc.insert_check == 0",
    },
    {
      label: 'From',
      fieldname: 'start_code',
      fieldtype: 'Link',
      options: 'Item',
      depends_on: "eval:doc.insert_check == 0",
      get_query: () => {
        const existingItemCodes = (this.frm.doc.items || []).map(existingItem => existingItem.item_code);
        console.log("existingItemCodes");
        console.log(existingItemCodes);
        if (this.frm.doc.type === 'Material') {
          return {
            filters: [
              ['is_fixed_asset', '=', '0'],
              ['name', 'not in', existingItemCodes]
            ]
          }
        }
        if (this.frm.doc.type === 'Asset') {
          return {
            filters: [
              ['is_fixed_asset', '=', '1'],
              ['name', 'not in', existingItemCodes]
            ]
          }
        }
      }

    },
    {
      label: '',
      fieldname: 'from_to',
      fieldtype: 'Column Break',
      depends_on: "eval:doc.insert_check == 0",
    },
    {
      label: 'To',
      fieldname: 'end_code',
      fieldtype: 'Link',
      options: 'Item',
      depends_on: "eval:doc.insert_check == 0",
      get_query: () => {
        const existingItemCodes = (this.frm.doc.items || []).map(existingItem => existingItem.item_code);
        console.log("existingItemCodes");
        console.log(existingItemCodes);
        if (this.frm.doc.type === 'Material') {
          return {
            filters: [
              ['is_fixed_asset', '=', '0'],
              ['name', 'not in', existingItemCodes]
            ]
          }
        }
        if (this.frm.doc.type === 'Asset') {
          return {
            filters: [
              ['is_fixed_asset', '=', '1'],
              ['name', 'not in', existingItemCodes]
            ]
          }
        }
      }
    },
  ],
  primary_action_label: 'Add Items',
  primary_action(values) {
    let frm = cur_frm
    if (frm.doc.type === 'Material') {
      if (values.insert_check == 0) {
        frappe.call({
          freeze: true,
          method: "stock_count.stock_count.doctype.stock_count.stock_count.get_requested_items",
          args: {
            item_name: values.item_name ?? '',
            item_group: values.item_group ?? '',
            start_code: values.start_code ?? '',
            end_code: values.end_code ?? '',
            is_asset: '0'
          },
          callback: (res) => {
            res.message.forEach((item) => {
              let itemExists = false;
              if (frm.doc.items && frm.doc.items.length) {
                frm.doc.items.forEach((existingItem) => {
                  if (existingItem.item_code === item.item_code) {
                    itemExists = true;
                    return false;
                  }
                })
              };
              if (!itemExists) {
                let entry = frm.add_child("items");
                entry.item_code = item.item_code;
                entry.item_name = item.item_name;
                entry.barcode = item.barcode;


              }
            });
            frm.refresh_field('items');
          }
        })

        d.set_value('item_name', '');
        d.set_value('item_group', '');
        d.set_value('start_code', '');
        d.set_value('end_code', '');
        d.set_value('item_list', '');
        d.hide();
      }
      if (values.insert_check == 1) {

        frappe.call({
          freeze: true,
          freeze_message: "inserted_items",
          method: "stock_count.stock_count.doctype.stock_count.stock_count.get_inserted_items",
          args: {
            item_list: values.item_list ?? '',
            is_asset: '0'
          },
          callback: (res) => {
            res.message.forEach((item) => {
              let itemExists = false;
              if (frm.doc.items && frm.doc.items.length) {
                frm.doc.items.forEach((existingItem) => {
                  if (existingItem.item_code === item.item_code) {
                    itemExists = true;
                    return false;
                  }
                })
              };
              if (!itemExists) {
                let entry = frm.add_child("items");
                entry.item_code = item.item_code;
                entry.item_name = item.item_name;
                entry.barcode = item.barcode;
              }
            });
            frm.refresh_field('items');
          }
        })

        d.set_value('item_name', '');
        d.set_value('item_group', '');
        d.set_value('start_code', '');
        d.set_value('end_code', '');
        d.set_value('item_list', '');
        d.hide();
      }
    }

    if (frm.doc.type === 'Asset') {
      if (values.insert_check == 0) {
        frappe.call({
          freeze: true,
          freeze_message: "get_requested_items",
          method: "stock_count.stock_count.doctype.stock_count.stock_count.get_requested_items",
          args: {
            item_name: values.item_name ?? '',
            item_group: values.item_group ?? '',
            start_code: values.start_code ?? '',
            end_code: values.end_code ?? '',
            is_asset: '1'
          },
          callback: (res) => {
            res.message.forEach((item) => {
              let itemExists = false;
              if (frm.doc.assets_list && frm.doc.assets_list.length) {
                frm.doc.assets_list.forEach((existingItem) => {
                  if (existingItem.asset_code === item.item_code) {
                    itemExists = true;
                    return false;
                  }
                })
              };
              if (!itemExists) {
                let entry = frm.add_child("assets_list");
                entry.item_code = item.item_code;
                entry.item_name = item.item_name;
                entry.barcode = item.barcode;
              }
            });
            frm.refresh_field('assets_list');
          }
        })
        // d.clear();
        d.set_value('item_name', '');
        d.set_value('item_group', '');
        d.set_value('start_code', '');
        d.set_value('end_code', '');
        d.set_value('item_list', '');
        d.hide();
      }
      if (values.insert_check == 1) {
        frappe.call({
          freeze: true,
          freeze_message: "inserted_items",
          method: "stock_count.stock_count.doctype.stock_count.stock_count.get_inserted_items",
          args: {
            item_list: values.item_list ?? '',
            is_asset: '1'
          },
          callback: (res) => {
            res.message.forEach((item) => {
              let itemExists = false;
              if (frm.doc.assets_list && frm.doc.assets_list.length) {
                frm.doc.assets_list.forEach((existingItem) => {
                  if (existingItem.asset_code === item.item_code) {
                    itemExists = true;
                    return false;
                  }
                })
              };


              if (!itemExists) {
                let entry = frm.add_child("assets_list");
                entry.item_code = item.item_code;
                entry.item_name = item.item_name;
                entry.barcode = item.barcode;
              }
            });
            frm.refresh_field('assets_list');
          }
        })

        d.set_value('item_name', '');
        d.set_value('item_group', '');
        d.set_value('start_code', '');
        d.set_value('end_code', '');
        d.set_value('item_list', '');
        d.hide();
      }
    }
  }

});

frappe.ui.form.on('Count Location', {
  location(frm, cdt, cdn) {
    let location_ = frappe.get_doc(cdt, cdn).location;
    frappe.call({
      freeze: true,
      freeze_message: "inserted location",
      method: "stock_count.stock_count.doctype.stock_count.stock_count.get_all_children",
      args: {
        location: location_,
      },
      callback: (res) => {
        res.message.forEach((item, idx, array) => {
          let itemExists = false;
          frm.doc.locations.forEach((existingItem) => {
            if (existingItem.location === item.name) {
              itemExists = true;
              return false;
            }
          });
          if (!itemExists) {

            if (idx === array.length - 1) return
            let entry = frm.add_child("locations");
            entry.location = item.name
            entry.barcode = item.barcode_location
          }
        });
        frm.refresh_field('locations');
      }
    });
  },
});

frappe.ui.form.on('Count Material', {
  item_code(frm, cdt, cdn) {
    let item_code_ = frappe.get_doc(cdt, cdn).item_code;
    frm.add_fetch("item_code", "item_name", "item_name");
    frappe.call({
      method: 'stock_count.stock_count.doctype.stock_count.stock_count.get_item_barcode',
      args: {
        parent: item_code_
      },
      callback: function (r) {
        if (r.message) {
          frappe.model.set_value(cdt, cdn, 'barcode', r.message);
        }
      }
    });
  }
})

frappe.ui.form.on('Count Asset', {
  item_code(frm, cdt, cdn) {
    let item_code_ = frappe.get_doc(cdt, cdn).item_code;
    frm.add_fetch("item_code", "item_name", "item_name");
    frappe.call({
      method: 'stock_count.stock_count.doctype.stock_count.stock_count.get_item_barcode',
      args: {
        parent: item_code_
      },
      callback: function (r) {
        if (r.message) {
          frappe.model.set_value(cdt, cdn, 'barcode', r.message);
        }
      }
    });
  }
})