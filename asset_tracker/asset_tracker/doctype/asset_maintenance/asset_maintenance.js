// Copyright (c) 2026, Pragati Hegde and contributors
// For license information, please see license.txt

frappe.ui.form.on("Asset Maintenance", {
	refresh(frm) {
		if (frm.doc.status === "Scheduled") {
			frm.page.set_indicator(__("Scheduled"), "blue");

			if (!frm.is_new()) {
				frm.add_custom_button(__("Start Maintenance"), () => {
					frm.set_value("status", "In Progress");
					frm.save();
				}, __("Status"));

				frm.add_custom_button(__("Mark as Completed"), () => {
					complete_maintenance_dialog(frm);
				}, __("Status"));
			}
		} else if (frm.doc.status === "In Progress") {
			frm.page.set_indicator(__("In Progress"), "orange");

			frm.add_custom_button(__("Mark as Completed"), () => {
				complete_maintenance_dialog(frm);
			}, __("Status"));
		} else if (frm.doc.status === "Completed") {
			frm.page.set_indicator(__("Completed"), "green");
		} else if (frm.doc.status === "Cancelled") {
			frm.page.set_indicator(__("Cancelled"), "gray");
		}
	},
});

function complete_maintenance_dialog(frm) {
	let d = new frappe.ui.Dialog({
		title: __("Complete Maintenance"),
		fields: [
			{
				label: __("Completion Date"),
				fieldname: "completion_date",
				fieldtype: "Date",
				default: frappe.datetime.get_today(),
				reqd: 1,
			},
			{
				label: __("Maintenance Cost"),
				fieldname: "maintenance_cost",
				fieldtype: "Currency",
				default: frm.doc.maintenance_cost || 0.0,
			},
			{
				label: __("Notes"),
				fieldname: "maintenance_notes",
				fieldtype: "Small Text",
				default: frm.doc.maintenance_notes || "",
			},
		],
		primary_action_label: __("Complete"),
		primary_action(values) {
			frm.set_value("status", "Completed");
			frm.set_value("completion_date", values.completion_date);
			frm.set_value("maintenance_cost", values.maintenance_cost);
			frm.set_value("maintenance_notes", values.maintenance_notes);
			frm.save();
			d.hide();
		},
	});
	d.show();
}

