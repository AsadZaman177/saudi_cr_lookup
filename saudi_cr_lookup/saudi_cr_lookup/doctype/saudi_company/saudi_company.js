// Copyright (c) 2025, BOT SOlutions and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Saudi Company", {
// 	refresh(frm) {

// 	},
// });
// frappe.ui.form.on('Saudi Company', {
//     refresh(frm) {
//         // Show "Fetch Data" button only when CR number is entered but data isn't fetched yet
//         frm.add_custom_button(__('Fetch Data'), function() {
//             frm.call('fetch_data').then(() => frm.refresh());
//         }).toggle(frm.doc.cr_national_number && !frm.doc.cr_number);
//     }
// });

// Copyright (c) 2025, BOT Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on("Saudi Company", {
    fetch_data: function(frm) {
        frm.call('fetch_data').then((r) => {
            if (!r.exc && r.message) {
                frappe.show_alert({
                    message: __('Data fetched successfully'),
                    indicator: 'green'
                });
                frm.refresh();
                frm.save();
            } else {
                // Data not updated (e.g. duplicate), just refresh without saving
                frm.refresh();
            }
        });
    }
});