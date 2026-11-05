// Copyright (c) 2026, Pragati Hegde and contributors
// For license information, please see license.txt

frappe.ui.form.on("Asset", {
	refresh(frm) {
		// Custom status indicators
		if (frm.doc.status === "Available") {
			frm.page.set_indicator(__("Available"), "green");
		} else if (frm.doc.status === "Assigned") {
			frm.page.set_indicator(__("Assigned"), "blue");
		} else if (frm.doc.status === "Under Maintenance") {
			frm.page.set_indicator(__("Under Maintenance"), "orange");
		} else if (frm.doc.status === "Disposed") {
			frm.page.set_indicator(__("Disposed"), "gray");
		}

		if (!frm.is_new() && frm.doc.status !== "Disposed") {
			// Quick Action: Assign Asset
			if (frm.doc.status === "Available") {
				frm.add_custom_button(__("Assign to Employee"), () => {
					frappe.new_doc("Asset Assignment", {
						asset: frm.doc.name,
						issue_condition: frm.doc.condition || "Good",
					});
				}, __("Actions"));
			}

			// Quick Action: Schedule Maintenance
			frm.add_custom_button(__("Schedule Maintenance"), () => {
				frappe.new_doc("Asset Maintenance", {
					asset: frm.doc.name,
					scheduled_date: frappe.datetime.add_days(frappe.datetime.get_today(), 7),
				});
			}, __("Actions"));

			// Quick Action: Dispose Asset
			frm.add_custom_button(__("Dispose Asset"), () => {
				let d = new frappe.ui.Dialog({
					title: __("Dispose Asset"),
					fields: [
						{
							label: __("Disposal Date"),
							fieldname: "disposal_date",
							fieldtype: "Date",
							default: frappe.datetime.get_today(),
							reqd: 1,
						},
						{
							label: __("Disposal Reason"),
							fieldname: "disposal_reason",
							fieldtype: "Small Text",
							reqd: 1,
						},
					],
					primary_action_label: __("Confirm Disposal"),
					primary_action(values) {
						frm.set_value("status", "Disposed");
						frm.set_value("disposal_date", values.disposal_date);
						frm.set_value("disposal_reason", values.disposal_reason);
						frm.save();
						d.hide();
					},
				});
				d.show();
			}, __("Actions"));
		}
	},
});

