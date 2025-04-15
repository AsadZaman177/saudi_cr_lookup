frappe.listview_settings['Saudi Company National Address'] = {
    get_indicator: function (doc) {
		var indicator = [__(doc.status), frappe.utils.guess_colour(doc.status), "status,=," + doc.status];
		indicator[1] = { Converted: "green", Draft: "red" }[doc.status];
		return indicator;
	},

    button: {
        show(doc) {
            return doc.status === "Draft";
        },
        get_label() {
            return 'Convert to Customer'; 
        },
        get_description(doc) {
            return __('Click to convert this to customer.'); 
        },
        action(doc) {
            // frappe.db.get_doc('BotSqlSyncedInvoices', doc.name)
            // .then(doc => {
            // console.log(doc)
            // })
            frappe.call({
                method: 'saudi_cr_lookup.saudi_cr_lookup.doctype.saudi_company_national_address.saudi_company_national_address.convert_to_customer',
                args: {
                    docname: doc.name  
                },
                callback: function(r) {
                    console.log(r);
                    if (r.exc) {
                        frappe.msgprint({
                            title: __('Failed'),
                            indicator: 'red',
                            message: __('Failed to convert.')
                        });
                    } else {
                        frappe.db.set_value('Saudi Company National Address', doc.name, 'status', 'Converted')
                        frappe.publish_realtime('list_refresh', {"doctype": "Saudi Company National Address"})
                        frappe.msgprint({
                            title: __('Converted Successfully'),
                            indicator: 'green',
                            message: r.message
                        });
                    }
                }
            }); 
        }
    },
    
};