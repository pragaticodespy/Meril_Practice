import json
import frappe

def create_colorful_workspace():
    print("Setting up Colorful Asset Tracker Dashboard...")

    # 1. CREATE/UPDATE CUSTOM HTML BLOCK FOR WORKFLOW
    block_name = "Asset Lifecycle Workflow"
    html_content = """<div class="asset-tracker-dashboard">
  <div class="at-hero">
    <div class="at-hero-text">
      <div class="at-badge">⚡ Enterprise Asset Management</div>
      <h2 class="at-title">Asset & Equipment Lifecycle Operations</h2>
      <p class="at-subtitle">Centralized tracking of hardware catalog, staff assignments, scheduled maintenance, and automated straight-line depreciation.</p>
    </div>
    <div class="at-hero-actions">
      <a href="/app/asset/new-asset-1" class="at-btn at-btn-primary">+ New Asset</a>
      <a href="/app/asset-assignment/new-asset-assignment-1" class="at-btn at-btn-secondary">+ Assign Asset</a>
      <a href="/app/asset-maintenance/new-asset-maintenance-1" class="at-btn at-btn-secondary">+ Maintenance</a>
      <a href="/app/query-report/Asset%20Register" class="at-btn at-btn-secondary">📊 Asset Register</a>
    </div>
  </div>

  <div class="at-pipeline">
    <a href="/app/asset" class="at-step at-step-blue" style="text-decoration: none; color: inherit;">
      <div class="at-step-icon">📦</div>
      <div class="at-step-content">
        <span class="at-step-num">STAGE 1</span>
        <h4>Asset Catalogue</h4>
        <p>Register specs, purchase cost & category depreciation rate</p>
      </div>
      <div class="at-step-arrow">➔</div>
    </a>

    <a href="/app/asset-assignment" class="at-step at-step-purple" style="text-decoration: none; color: inherit;">
      <div class="at-step-icon">👤</div>
      <div class="at-step-content">
        <span class="at-step-num">STAGE 2</span>
        <h4>Assignment</h4>
        <p>Issue to staff, 3-asset holding check & condition verify</p>
      </div>
      <div class="at-step-arrow">➔</div>
    </a>

    <a href="/app/asset-maintenance" class="at-step at-step-orange" style="text-decoration: none; color: inherit;">
      <div class="at-step-icon">🛠️</div>
      <div class="at-step-content">
        <span class="at-step-num">STAGE 3</span>
        <h4>Maintenance</h4>
        <p>7-day advance auto alert, service logs & status sync</p>
      </div>
      <div class="at-step-arrow">➔</div>
    </a>

    <a href="/app/asset-depreciation-log" class="at-step at-step-green" style="text-decoration: none; color: inherit;">
      <div class="at-step-icon">📉</div>
      <div class="at-step-content">
        <span class="at-step-num">STAGE 4</span>
        <h4>Depreciation</h4>
        <p>Automatic monthly straight-line value reduction</p>
      </div>
      <div class="at-step-arrow">➔</div>
    </a>

    <a href="/app/asset?status=Disposed" class="at-step at-step-red" style="text-decoration: none; color: inherit;">
      <div class="at-step-icon">♻️</div>
      <div class="at-step-content">
        <span class="at-step-num">STAGE 5</span>
        <h4>Disposal</h4>
        <p>Mandatory reason log, locks assignment & service</p>
      </div>
    </a>
  </div>
</div>"""

    css_style = """
.asset-tracker-dashboard {
  font-family: inherit;
  margin-bottom: 20px;
}
.at-hero {
  background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 45%, #2563eb 100%);
  padding: 24px 28px;
  border-radius: 16px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.35);
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 16px;
}
.at-badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  margin-bottom: 6px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}
.at-title {
  color: white;
  margin: 4px 0 6px 0;
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.5px;
}
.at-subtitle {
  margin: 0;
  color: #e0f2fe;
  font-size: 13px;
  max-width: 650px;
  line-height: 1.5;
}
.at-hero-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.at-btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.at-btn-primary {
  background: white;
  color: #1e3a8a;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.at-btn-primary:hover {
  background: #f8fafc;
  transform: translateY(-2px);
  color: #1d4ed8;
  text-decoration: none;
}
.at-btn-secondary {
  background: rgba(255, 255, 255, 0.16);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(4px);
}
.at-btn-secondary:hover {
  background: rgba(255, 255, 255, 0.28);
  color: white;
  text-decoration: none;
  transform: translateY(-2px);
}
.at-pipeline {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px;
}
.at-step {
  position: relative;
  border-radius: 14px;
  padding: 16px 14px;
  background: white;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
}
.at-step:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.1);
  text-decoration: none;
}
.at-step-blue { border-top: 4px solid #3b82f6; }
.at-step-blue:hover { border-color: #3b82f6; background: #eff6ff; }
.at-step-purple { border-top: 4px solid #8b5cf6; }
.at-step-purple:hover { border-color: #8b5cf6; background: #f5f3ff; }
.at-step-orange { border-top: 4px solid #f59e0b; }
.at-step-orange:hover { border-color: #f59e0b; background: #fffbeb; }
.at-step-green { border-top: 4px solid #10b981; }
.at-step-green:hover { border-color: #10b981; background: #ecfdf5; }
.at-step-red { border-top: 4px solid #ef4444; }
.at-step-red:hover { border-color: #ef4444; background: #fef2f2; }

.at-step-icon {
  font-size: 26px;
  margin-bottom: 8px;
}
.at-step-num {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.5px;
  color: #64748b;
  text-transform: uppercase;
}
.at-step h4 {
  margin: 4px 0 4px 0;
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}
.at-step p {
  margin: 0;
  font-size: 11px;
  color: #64748b;
  line-height: 1.4;
}
.at-step-arrow {
  position: absolute;
  right: -11px;
  top: 50%;
  transform: translateY(-50%);
  background: white;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: #94a3b8;
  border: 1px solid #cbd5e1;
  z-index: 2;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}
@media (max-width: 992px) {
  .at-pipeline {
    grid-template-columns: repeat(2, 1fr);
  }
  .at-step-arrow { display: none; }
}
"""

    if frappe.db.exists("Custom HTML Block", block_name):
        doc = frappe.get_doc("Custom HTML Block", block_name)
    else:
        doc = frappe.new_doc("Custom HTML Block")
        doc.name = block_name

    doc.html = html_content
    doc.style = css_style
    doc.script = """
    root_element.querySelectorAll('.at-step, .at-btn').forEach(el => {
      el.addEventListener('click', (e) => {
        let href = el.getAttribute('href');
        if (href && href.startsWith('/app/')) {
          e.preventDefault();
          let route = href.replace('/app/', '').split('/');
          frappe.set_route(route);
        }
      });
    });
    """
    doc.private = 0
    doc.save(ignore_permissions=True)
    print("Created/Updated Custom HTML Block: Asset Lifecycle Workflow")

    # 2. ENSURE NUMBER CARDS HAVE VIBRANT COLORS AND ACCURATE DATA
    cards = {
        "Total Assets": {
            "label": "Total Assets",
            "color": "#2563EB",
            "doc": "Asset",
            "fn": "Count",
            "filter": [["Asset", "status", "!=", "Disposed"]]
        },
        "Total Valuation": {
            "label": "Total Valuation",
            "color": "#059669",
            "doc": "Asset",
            "fn": "Sum",
            "field": "current_value",
            "filter": [["Asset", "status", "!=", "Disposed"]]
        },
        "Assigned Assets": {
            "label": "Assigned Assets",
            "color": "#D97706",
            "doc": "Asset Assignment",
            "fn": "Count",
            "filter": [["Asset Assignment", "status", "=", "Active"]]
        },
        "Maintenance Due (7 Days)": {
            "label": "Maintenance Due (7 Days)",
            "color": "#DC2626",
            "doc": "Asset Maintenance",
            "fn": "Count",
            "filter": [["Asset Maintenance", "status", "=", "Scheduled"]]
        }
    }
    for card_name, info in cards.items():
        if frappe.db.exists("Number Card", card_name):
            c = frappe.get_doc("Number Card", card_name)
        else:
            c = frappe.new_doc("Number Card")
            c.name = card_name
            c.label = info["label"]
            c.document_type = info["doc"]
            c.function = info["fn"]
            c.is_standard = 0
            c.module = "Asset Tracker"

        c.color = info["color"]
        c.currency = "INR"
        c.show_full_number = 0
        c.show_percentage_stats = 0
        if "field" in info:
            c.aggregate_function_based_on = info["field"]
        c.filters_json = json.dumps(info["filter"])
        c.save(ignore_permissions=True)
    print("Created/Updated 4 Vibrant Number Cards.")

    # 3. WORKSPACE CONTENT BLOCKS (EditorJS compliant)
    content_blocks = [
        {"id": "b_workflow", "type": "custom_block", "data": {"custom_block_name": block_name, "col": 12}},
        {"id": "b_spc1", "type": "spacer", "data": {"col": 12}},
        {"id": "b_hdr_kpi", "type": "header", "data": {"text": "<span class=\"h4\"><b>📊 Key Asset &amp; Financial Metrics</b></span>", "col": 12}},
        {"id": "b_nc1", "type": "number_card", "data": {"number_card_name": "Total Assets", "col": 3}},
        {"id": "b_nc2", "type": "number_card", "data": {"number_card_name": "Total Valuation", "col": 3}},
        {"id": "b_nc3", "type": "number_card", "data": {"number_card_name": "Assigned Assets", "col": 3}},
        {"id": "b_nc4", "type": "number_card", "data": {"number_card_name": "Maintenance Due (7 Days)", "col": 3}},
        {"id": "b_spc2", "type": "spacer", "data": {"col": 12}},
        {"id": "b_hdr_charts", "type": "header", "data": {"text": "<span class=\"h4\"><b>📈 Asset Analytics &amp; Distribution</b></span>", "col": 12}},
        {"id": "b_ch1", "type": "chart", "data": {"chart_name": "Assets by Status", "col": 6}},
        {"id": "b_ch2", "type": "chart", "data": {"chart_name": "Assets by Category", "col": 6}},
        {"id": "b_spc3", "type": "spacer", "data": {"col": 12}},
        {"id": "b_hdr_sc", "type": "header", "data": {"text": "<span class=\"h4\"><b>⚡ Quick Actions &amp; Shortcuts</b></span>", "col": 12}},
        {"id": "b_sc1", "type": "shortcut", "data": {"shortcut_name": "Assets", "col": 2}},
        {"id": "b_sc2", "type": "shortcut", "data": {"shortcut_name": "Assignments", "col": 2}},
        {"id": "b_sc3", "type": "shortcut", "data": {"shortcut_name": "Maintenance", "col": 2}},
        {"id": "b_sc4", "type": "shortcut", "data": {"shortcut_name": "Categories", "col": 2}},
        {"id": "b_sc5", "type": "shortcut", "data": {"shortcut_name": "Employees", "col": 2}},
        {"id": "b_sc6", "type": "shortcut", "data": {"shortcut_name": "Asset Register", "col": 2}},
        {"id": "b_spc4", "type": "spacer", "data": {"col": 12}},
        {"id": "b_hdr_cards", "type": "header", "data": {"text": "<span class=\"h4\"><b>📂 Masters &amp; Operations Directory</b></span>", "col": 12}},
        {"id": "b_cd1", "type": "card", "data": {"card_name": "Asset Masters", "col": 4}},
        {"id": "b_cd2", "type": "card", "data": {"card_name": "Operations & Tracking", "col": 4}},
        {"id": "b_cd3", "type": "card", "data": {"card_name": "Financials & Reports", "col": 4}}
    ]

    # 4. UPDATE WORKSPACE DOCUMENT
    ws = frappe.get_doc("Workspace", "Asset Tracker")
    ws.content = json.dumps(content_blocks)
    ws.icon = "box"
    ws.indicator_color = "blue"
    ws.public = 1
    ws.for_user = ""
    ws.is_hidden = 0
    ws.hide_custom = 0

    # Reset child tables
    ws.custom_blocks = []
    ws.append("custom_blocks", {"custom_block_name": block_name, "label": block_name})

    ws.number_cards = []
    for c_name in ["Total Assets", "Total Valuation", "Assigned Assets", "Maintenance Due (7 Days)"]:
        ws.append("number_cards", {"number_card_name": c_name, "label": c_name})

    ws.charts = []
    for ch_name in ["Assets by Status", "Assets by Category"]:
        ws.append("charts", {"chart_name": ch_name, "label": ch_name})

    ws.shortcuts = []
    shortcuts_data = [
        {"label": "Assets", "link_to": "Asset", "type": "DocType", "color": "Blue", "format": "{}"},
        {"label": "Assignments", "link_to": "Asset Assignment", "type": "DocType", "color": "Orange", "format": "{}"},
        {"label": "Maintenance", "link_to": "Asset Maintenance", "type": "DocType", "color": "Red", "format": "{}"},
        {"label": "Categories", "link_to": "Asset Category", "type": "DocType", "color": "Purple", "format": "{}"},
        {"label": "Employees", "link_to": "Employee", "type": "DocType", "color": "Cyan", "format": "{}"},
        {"label": "Asset Register", "link_to": "Asset Register", "type": "Report", "color": "Green"}
    ]
    for s in shortcuts_data:
        ws.append("shortcuts", s)

    ws.links = []
    # Card 1: Asset Masters
    ws.append("links", {"type": "Card Break", "label": "Asset Masters", "link_type": "DocType", "link_count": 2})
    ws.append("links", {"type": "Link", "label": "Asset Master", "link_type": "DocType", "link_to": "Asset"})
    ws.append("links", {"type": "Link", "label": "Asset Categories", "link_type": "DocType", "link_to": "Asset Category"})

    # Card 2: Operations & Tracking
    ws.append("links", {"type": "Card Break", "label": "Operations & Tracking", "link_type": "DocType", "link_count": 3})
    ws.append("links", {"type": "Link", "label": "Asset Assignments", "link_type": "DocType", "link_to": "Asset Assignment"})
    ws.append("links", {"type": "Link", "label": "Asset Maintenance", "link_type": "DocType", "link_to": "Asset Maintenance"})
    ws.append("links", {"type": "Link", "label": "Employee Directory", "link_type": "DocType", "link_to": "Employee"})

    # Card 3: Financials & Reports
    ws.append("links", {"type": "Card Break", "label": "Financials & Reports", "link_type": "Report", "link_count": 2})
    ws.append("links", {"type": "Link", "label": "Asset Register Report", "link_type": "Report", "link_to": "Asset Register", "is_query_report": 1})
    ws.append("links", {"type": "Link", "label": "Depreciation Logs", "link_type": "DocType", "link_to": "Asset Depreciation Log"})

    ws.save(ignore_permissions=True)
    frappe.db.commit()

    # Clear workspace and desk cache
    frappe.clear_cache()
    print("Asset Tracker Workspace successfully updated with colorful UI & workflow blocks!")

if __name__ == "__main__":
    create_colorful_workspace()
