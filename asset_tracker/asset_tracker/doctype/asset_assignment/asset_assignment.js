// Copyright (c) 2026, Pragati Hegde and contributors
// For license information, please see license.txt

frappe.ui.form.on("Asset Assignment", {
	refresh(frm) {
		if (frm.doc.status === "Active") {
			frm.page.set_indicator(__("Active Assignment"), "blue");

			if (!frm.is_new()) {
				frm.add_custom_button(__("Return Asset"), () => {
					let d = new frappe.ui.Dialog({
						title: __("Process Asset Return"),
						fields: [
							{
								label: __("Return Date"),
								fieldname: "return_date",
								fieldtype: "Date",
								default: frappe.datetime.get_today(),
								reqd: 1,
							},
							{
								label: __("Return Condition"),
								fieldname: "return_condition",
								fieldtype: "Select",
								options: "New\nGood\nFair\nDamaged",
								default: frm.doc.issue_condition || "Good",
								reqd: 1,
							},
							{
								label: __("Return Notes"),
								fieldname: "notes",
								fieldtype: "Small Text",
							},
						],
						primary_action_label: __("Confirm Return"),
						primary_action(values) {
							frm.set_value("status", "Returned");
							frm.set_value("return_date", values.return_date);
							frm.set_value("return_condition", values.return_condition);
							if (values.notes) {
								let current_notes = frm.doc.notes || "";
								frm.set_value(
									"notes",
									current_notes + (current_notes ? "\n" : "") + "Return Note: " + values.notes
								);
							}
							frm.save();
							d.hide();
						},
					});
					d.show();
				}, __("Actions"));
			}
		} else if (frm.doc.status === "Returned") {
			frm.page.set_indicator(__("Returned"), "green");
		}
	},

	employee(frm) {
		if (frm.doc.employee && frm.doc.status === "Active") {
			frappe.call({
				method: "frappe.client.get_count",
				args: {
					doctype: "Asset Assignment",
					filters: {
						employee: frm.doc.employee,
						status: "Active",
					},
				},
				callback(r) {
					let activeCount = r.message || 0;
					if (activeCount >= 3) {
						frappe.msgprint({
							title: __("Holding Limit Notice"),
							indicator: "orange",
							message: __(
								`Notice: Employee <b>${frm.doc.employee}</b> currently holds <b>${activeCount}</b> active assets and is approaching or at the 3-asset holding limit.`
							),
						});
					}
				},
			});
		}
	},
});

