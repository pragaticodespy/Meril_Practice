// Copyright (c) 2026, Pragati Hegde and contributors
// For license information, please see license.txt

frappe.query_reports["Asset Register"] = {
	filters: [
		{
			fieldname: "category",
			label: __("Category"),
			fieldtype: "Link",
			options: "Asset Category",
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nAvailable\nAssigned\nUnder Maintenance\nDisposed",
		},
		{
			fieldname: "department",
			label: __("Department"),
			fieldtype: "Data",
		},
	],
};

