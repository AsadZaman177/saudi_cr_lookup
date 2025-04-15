// Copyright (c) 2025, BOT SOlutions and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Saudi Company National Address", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Saudi Company National Address", {
    refresh(frm) {
        if (frm.doc.status !== "Converted") {
            frm.add_custom_button(__('Convert to Customer'), function () {
                frappe.call({
                    method: 'saudi_cr_lookup.saudi_cr_lookup.doctype.saudi_company_national_address.saudi_company_national_address.convert_to_customer',
                    args: {
                        docname: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.exc) {
                            frappe.msgprint({
                                title: __('Failed'),
                                indicator: 'red',
                                message: __('Failed to convert.')
                            });
                        } else {
                            frappe.db.set_value('Saudi Company National Address', frm.doc.name, 'status', 'Converted');
                            frm.reload_doc();
                            frm.refresh();
                            frappe.show_alert({
                                message: __('Converted Successfully'),
                                indicator: 'green'
                            });
                        }
                    }
                });
            });
        }
    },
    
    fetch_address: function(frm) {
        frm.call('fetch_national_address').then((r) => {
            if (!r.exc) {
                frm.refresh();
                frm.save();
                frappe.show_alert({
                    message: __('Data fetched and saved successfully'),
                    indicator: 'green'
                });
            }
        }).catch((err) => {
            frappe.msgprint({
                title: __('Error'),
                message: err.message || __('Failed to fetch address'),
                indicator: 'red'
            });
        });
    }
});
