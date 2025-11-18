#!/usr/bin/env python3
"""
Load default knowledge base articles for Chatnext
Pre-populated Q&A for common ERPNext queries
"""

import frappe
import json

def load_knowledge_base():
    """Load all default knowledge base articles"""

    articles = get_default_articles()

    created_count = 0
    skipped_count = 0

    for article_data in articles:
        try:
            # Check if already exists
            if frappe.db.exists("Knowledge Base Article", article_data["title"]):
                print(f"⚠️  {article_data['title']} already exists, skipping...")
                skipped_count += 1
                continue

            # Create article
            article = frappe.get_doc({
                "doctype": "Knowledge Base Article",
                **article_data
            })
            article.insert(ignore_permissions=True)
            frappe.db.commit()

            print(f"✅ Created: {article_data['title']}")
            created_count += 1

        except Exception as e:
            print(f"❌ Error creating {article_data.get('title', 'Unknown')}: {str(e)}")
            frappe.db.rollback()

    print(f"\n✅ Knowledge Base loaded successfully!")
    print(f"   Created: {created_count} articles")
    print(f"   Skipped: {skipped_count} articles")

def get_default_articles():
    """Return list of default KB articles"""

    return [
        # SALES MODULE
        {
            "title": "How to create a Sales Invoice",
            "category": "Sales",
            "keywords": "sales invoice, create invoice, billing, customer invoice",
            "question": "How do I create a Sales Invoice in ERPNext?",
            "answer": """<p>To create a Sales Invoice in ERPNext:</p>
<ol>
<li>Go to <strong>Selling → Sales Invoice → New</strong></li>
<li>Select the <strong>Customer</strong></li>
<li>Add <strong>Items</strong> with quantities and rates</li>
<li>Set the <strong>Posting Date</strong></li>
<li>Select <strong>Payment Terms</strong> if applicable</li>
<li>Click <strong>Save</strong> and then <strong>Submit</strong></li>
</ol>
<p><strong>Tip:</strong> You can also create a Sales Invoice from a Sales Order or Delivery Note.</p>""",
            "answer_urdu": """<p>ERPNext میں Sales Invoice بنانے کے لیے:</p>
<ol>
<li><strong>Selling → Sales Invoice → New</strong> پر جائیں</li>
<li><strong>Customer</strong> منتخب کریں</li>
<li>مقدار اور قیمتوں کے ساتھ <strong>Items</strong> شامل کریں</li>
<li><strong>Posting Date</strong> سیٹ کریں</li>
<li>اگر ضروری ہو تو <strong>Payment Terms</strong> منتخب کریں</li>
<li><strong>Save</strong> اور پھر <strong>Submit</strong> کر کریں</li>
</ol>
<p><strong>نوٹ:</strong> آپ Sales Order یا Delivery Note سے بھی Sales Invoice بنا سکتے ہیں۔</p>""",
            "language": "Bilingual",
            "related_doctype": "Sales Invoice",
            "is_active": 1
        },
        {
            "title": "How to create a Quotation",
            "category": "Sales",
            "keywords": "quotation, quote, customer quote, sales quote",
            "question": "How do I create a Quotation for a customer?",
            "answer": """<p>To create a Quotation:</p>
<ol>
<li>Go to <strong>Selling → Quotation → New</strong></li>
<li>Select <strong>Customer</strong> or <strong>Lead</strong></li>
<li>Add <strong>Items</strong> with quantities</li>
<li>Set <strong>Valid Till</strong> date</li>
<li><strong>Save</strong> and <strong>Submit</strong></li>
<li>Use <strong>Print</strong> to send to customer</li>
</ol>
<p>Once approved, you can convert it to a <strong>Sales Order</strong> directly.</p>""",
            "answer_urdu": """<p>Quotation بنانے کے لیے:</p>
<ol>
<li><strong>Selling → Quotation → New</strong> پر جائیں</li>
<li><strong>Customer</strong> یا <strong>Lead</strong> منتخب کریں</li>
<li>مقداروں کے ساتھ <strong>Items</strong> شامل کریں</li>
<li><strong>Valid Till</strong> تاریخ سیٹ کریں</li>
<li><strong>Save</strong> اور <strong>Submit</strong> کریں</li>
<li>Customer کو بھیجنے کے لیے <strong>Print</strong> استعمال کریں</li>
</ol>
<p>منظور ہونے کے بعد، آپ اسے براہ راست <strong>Sales Order</strong> میں تبدیل کر سکتے ہیں۔</p>""",
            "language": "Bilingual",
            "related_doctype": "Quotation",
            "is_active": 1
        },

        # PURCHASE MODULE
        {
            "title": "How to create a Purchase Order",
            "category": "Purchase",
            "keywords": "purchase order, PO, supplier order, buying",
            "question": "How do I create a Purchase Order?",
            "answer": """<p>To create a Purchase Order:</p>
<ol>
<li>Go to <strong>Buying → Purchase Order → New</strong></li>
<li>Select the <strong>Supplier</strong></li>
<li>Add <strong>Items</strong> with required quantities</li>
<li>Set <strong>Required By</strong> date for each item</li>
<li>Review pricing and terms</li>
<li><strong>Save</strong> and <strong>Submit</strong></li>
</ol>
<p>You can create a Purchase Order from a <strong>Material Request</strong> or <strong>Supplier Quotation</strong>.</p>""",
            "answer_urdu": """<p>Purchase Order بنانے کے لیے:</p>
<ol>
<li><strong>Buying → Purchase Order → New</strong> پر جائیں</li>
<li><strong>Supplier</strong> منتخب کریں</li>
<li>ضروری مقداروں کے ساتھ <strong>Items</strong> شامل کریں</li>
<li>ہر item کے لیے <strong>Required By</strong> تاریخ سیٹ کریں</li>
<li>قیمت اور شرائط کا جائزہ لیں</li>
<li><strong>Save</strong> اور <strong>Submit</strong> کریں</li>
</ol>
<p>آپ <strong>Material Request</strong> یا <strong>Supplier Quotation</strong> سے Purchase Order بنا سکتے ہیں۔</p>""",
            "language": "Bilingual",
            "related_doctype": "Purchase Order",
            "is_active": 1
        },

        # HR MODULE
        {
            "title": "How to create an Employee",
            "category": "HR",
            "keywords": "employee, new employee, add employee, staff",
            "question": "How do I add a new Employee?",
            "answer": """<p>To create a new Employee:</p>
<ol>
<li>Go to <strong>HR → Employee → New</strong></li>
<li>Enter <strong>First Name</strong> and <strong>Last Name</strong></li>
<li>Set <strong>Date of Joining</strong></li>
<li>Select <strong>Company</strong> and <strong>Department</strong></li>
<li>Choose <strong>Designation</strong></li>
<li>Enter <strong>Employee Number</strong> (auto-generated if not specified)</li>
<li>Add contact details and personal information</li>
<li><strong>Save</strong></li>
</ol>
<p>Make sure to set up <strong>Salary Structure Assignment</strong> for payroll processing.</p>""",
            "answer_urdu": """<p>نیا Employee بنانے کے لیے:</p>
<ol>
<li><strong>HR → Employee → New</strong> پر جائیں</li>
<li><strong>First Name</strong> اور <strong>Last Name</strong> درج کریں</li>
<li><strong>Date of Joining</strong> سیٹ کریں</li>
<li><strong>Company</strong> اور <strong>Department</strong> منتخب کریں</li>
<li><strong>Designation</strong> چنیں</li>
<li><strong>Employee Number</strong> درج کریں (خودکار ہو گا اگر نہ دیا)</li>
<li>رابطہ کی تفصیلات اور ذاتی معلومات شامل کریں</li>
<li><strong>Save</strong> کریں</li>
</ol>
<p>تنخواہ کی پروسیسنگ کے لیے <strong>Salary Structure Assignment</strong> سیٹ کرنا یقینی بنائیں۔</p>""",
            "language": "Bilingual",
            "related_doctype": "Employee",
            "is_active": 1
        },
        {
            "title": "How to mark Employee Attendance",
            "category": "Attendance",
            "keywords": "attendance, mark attendance, present, absent, leave",
            "question": "How do I mark employee attendance?",
            "answer": """<p>To mark attendance:</p>
<ol>
<li>Go to <strong>HR → Attendance → New</strong></li>
<li>Select <strong>Employee</strong></li>
<li>Set <strong>Attendance Date</strong></li>
<li>Choose <strong>Status</strong> (Present/Absent/Half Day/Work From Home)</li>
<li><strong>Save</strong> and <strong>Submit</strong></li>
</ol>
<p><strong>Bulk Attendance:</strong> Use <strong>Attendance Tool</strong> to mark attendance for multiple employees at once.</p>""",
            "answer_urdu": """<p>حاضری مارک کرنے کے لیے:</p>
<ol>
<li><strong>HR → Attendance → New</strong> پر جائیں</li>
<li><strong>Employee</strong> منتخب کریں</li>
<li><strong>Attendance Date</strong> سیٹ کریں</li>
<li><strong>Status</strong> چنیں (Present/Absent/Half Day/Work From Home)</li>
<li><strong>Save</strong> اور <strong>Submit</strong> کریں</li>
</ol>
<p><strong>بلک حاضری:</strong> ایک ساتھ کئی ملازمین کی حاضری مارک کرنے کے لیے <strong>Attendance Tool</strong> استعمال کریں۔</p>""",
            "language": "Bilingual",
            "related_doctype": "Attendance",
            "is_active": 1
        },

        # INVENTORY MODULE
        {
            "title": "How to create a Stock Entry",
            "category": "Inventory",
            "keywords": "stock entry, material transfer, material receipt, stock movement",
            "question": "How do I create a Stock Entry?",
            "answer": """<p>To create a Stock Entry:</p>
<ol>
<li>Go to <strong>Stock → Stock Entry → New</strong></li>
<li>Select <strong>Stock Entry Type</strong>:
   <ul>
   <li>Material Receipt - Receiving goods</li>
   <li>Material Issue - Issuing goods</li>
   <li>Material Transfer - Moving between warehouses</li>
   <li>Manufacture - Production</li>
   </ul>
</li>
<li>Select <strong>Source Warehouse</strong> and <strong>Target Warehouse</strong></li>
<li>Add <strong>Items</strong> with quantities</li>
<li><strong>Save</strong> and <strong>Submit</strong></li>
</ol>""",
            "answer_urdu": """<p>Stock Entry بنانے کے لیے:</p>
<ol>
<li><strong>Stock → Stock Entry → New</strong> پر جائیں</li>
<li><strong>Stock Entry Type</strong> منتخب کریں:
   <ul>
   <li>Material Receipt - سامان وصول کرنا</li>
   <li>Material Issue - سامان جاری کرنا</li>
   <li>Material Transfer - گوداموں کے درمیان منتقلی</li>
   <li>Manufacture - پیداوار</li>
   </ul>
</li>
<li><strong>Source Warehouse</strong> اور <strong>Target Warehouse</strong> منتخب کریں</li>
<li>مقداروں کے ساتھ <strong>Items</strong> شامل کریں</li>
<li><strong>Save</strong> اور <strong>Submit</strong> کریں</li>
</ol>""",
            "language": "Bilingual",
            "related_doctype": "Stock Entry",
            "is_active": 1
        },

        # ACCOUNTING MODULE
        {
            "title": "How to create a Payment Entry",
            "category": "Accounting",
            "keywords": "payment entry, payment, receipt, pay, receive money",
            "question": "How do I record a payment?",
            "answer": """<p>To create a Payment Entry:</p>
<ol>
<li>Go to <strong>Accounting → Payment Entry → New</strong></li>
<li>Select <strong>Payment Type</strong>:
   <ul>
   <li>Receive - Customer payments</li>
   <li>Pay - Supplier payments</li>
   <li>Internal Transfer - Between accounts</li>
   </ul>
</li>
<li>Select <strong>Party</strong> (Customer/Supplier)</li>
<li>Choose <strong>Account Paid From/To</strong></li>
<li>Enter <strong>Amount</strong></li>
<li>Link to invoices if applicable</li>
<li><strong>Save</strong> and <strong>Submit</strong></li>
</ol>""",
            "answer_urdu": """<p>Payment Entry بنانے کے لیے:</p>
<ol>
<li><strong>Accounting → Payment Entry → New</strong> پر جائیں</li>
<li><strong>Payment Type</strong> منتخب کریں:
   <ul>
   <li>Receive - کسٹمر کی ادائیگیاں</li>
   <li>Pay - سپلائر کی ادائیگیاں</li>
   <li>Internal Transfer - اکاؤنٹس کے درمیان</li>
   </ul>
</li>
<li><strong>Party</strong> منتخب کریں (Customer/Supplier)</li>
<li><strong>Account Paid From/To</strong> چنیں</li>
<li><strong>Amount</strong> درج کریں</li>
<li>اگر قابل اطلاق ہو تو invoices سے لنک کریں</li>
<li><strong>Save</strong> اور <strong>Submit</strong> کریں</li>
</ol>""",
            "language": "Bilingual",
            "related_doctype": "Payment Entry",
            "is_active": 1
        },

        # PAYROLL
        {
            "title": "How to process Salary Slips",
            "category": "Payroll",
            "keywords": "salary slip, payroll, salary processing, wages",
            "question": "How do I process monthly salary slips?",
            "answer": """<p>To process Salary Slips:</p>
<ol>
<li>Go to <strong>HR → Salary Slip → Create Salary Slips</strong></li>
<li>Or use <strong>Payroll Entry</strong> for bulk processing</li>
<li>Select <strong>Company</strong> and <strong>Payroll Frequency</strong></li>
<li>Set <strong>Start Date</strong> and <strong>End Date</strong></li>
<li>Click <strong>Create Salary Slips</strong></li>
<li>Review generated slips</li>
<li><strong>Submit</strong> all salary slips</li>
<li>Create <strong>Payment Entry</strong> for bank transfer</li>
</ol>
<p><strong>Note:</strong> Ensure all employees have <strong>Salary Structure Assignment</strong> before processing.</p>""",
            "answer_urdu": """<p>Salary Slips پروسیس کرنے کے لیے:</p>
<ol>
<li><strong>HR → Salary Slip → Create Salary Slips</strong> پر جائیں</li>
<li>یا بلک پروسیسنگ کے لیے <strong>Payroll Entry</strong> استعمال کریں</li>
<li><strong>Company</strong> اور <strong>Payroll Frequency</strong> منتخب کریں</li>
<li><strong>Start Date</strong> اور <strong>End Date</strong> سیٹ کریں</li>
<li><strong>Create Salary Slips</strong> پر کلک کریں</li>
<li>بنائی گئی slips کا جائزہ لیں</li>
<li>تمام salary slips <strong>Submit</strong> کریں</li>
<li>بینک ٹرانسفر کے لیے <strong>Payment Entry</strong> بنائیں</li>
</ol>
<p><strong>نوٹ:</strong> پروسیسنگ سے پہلے یقینی بنائیں کہ تمام ملازمین کے پاس <strong>Salary Structure Assignment</strong> ہے۔</p>""",
            "language": "Bilingual",
            "related_doctype": "Salary Slip",
            "is_active": 1
        },

        # LEAVE MANAGEMENT
        {
            "title": "How to apply for Leave",
            "category": "Leave",
            "keywords": "leave application, apply leave, time off, vacation",
            "question": "How do employees apply for leave?",
            "answer": """<p>To apply for Leave:</p>
<ol>
<li>Go to <strong>HR → Leave Application → New</strong></li>
<li>Select <strong>Employee</strong> (auto-filled if you're applying for yourself)</li>
<li>Choose <strong>Leave Type</strong> (Sick Leave, Casual Leave, etc.)</li>
<li>Set <strong>From Date</strong> and <strong>To Date</strong></li>
<li>Enter <strong>Reason</strong></li>
<li>Select <strong>Leave Approver</strong></li>
<li><strong>Save</strong> and <strong>Submit</strong></li>
</ol>
<p>The leave application will be sent to the approver for approval.</p>""",
            "answer_urdu": """<p>چھٹی کے لیے درخواست دینے کے لیے:</p>
<ol>
<li><strong>HR → Leave Application → New</strong> پر جائیں</li>
<li><strong>Employee</strong> منتخب کریں (اگر آپ خود کے لیے ہے تو خودکار)</li>
<li><strong>Leave Type</strong> چنیں (بیماری کی چھٹی، عام چھٹی وغیرہ)</li>
<li><strong>From Date</strong> اور <strong>To Date</strong> سیٹ کریں</li>
<li><strong>وجہ</strong> درج کریں</li>
<li><strong>Leave Approver</strong> منتخب کریں</li>
<li><strong>Save</strong> اور <strong>Submit</strong> کریں</li>
</ol>
<p>چھٹی کی درخواست منظوری کے لیے approver کو بھیجی جائے گی۔</p>""",
            "language": "Bilingual",
            "related_doctype": "Leave Application",
            "is_active": 1
        },

        # CRM MODULE
        {
            "title": "How to create a Lead",
            "category": "CRM",
            "keywords": "lead, prospect, potential customer, new lead",
            "question": "How do I create a Lead in CRM?",
            "answer": """<p>To create a Lead:</p>
<ol>
<li>Go to <strong>CRM → Lead → New</strong></li>
<li>Enter <strong>Lead Name</strong></li>
<li>Add <strong>Email</strong> and <strong>Phone</strong></li>
<li>Select <strong>Status</strong> (Open, Contacted, Qualified, etc.)</li>
<li>Choose <strong>Lead Source</strong></li>
<li>Add <strong>Notes</strong> about requirements</li>
<li><strong>Save</strong></li>
</ol>
<p>You can convert a qualified Lead to a <strong>Customer</strong> or <strong>Opportunity</strong>.</p>""",
            "answer_urdu": """<p>Lead بنانے کے لیے:</p>
<ol>
<li><strong>CRM → Lead → New</strong> پر جائیں</li>
<li><strong>Lead Name</strong> درج کریں</li>
<li><strong>Email</strong> اور <strong>Phone</strong> شامل کریں</li>
<li><strong>Status</strong> منتخب کریں (Open, Contacted, Qualified وغیرہ)</li>
<li><strong>Lead Source</strong> چنیں</li>
<li>ضروریات کے بارے میں <strong>Notes</strong> شامل کریں</li>
<li><strong>Save</strong> کریں</li>
</ol>
<p>آپ کوالیفائیڈ Lead کو <strong>Customer</strong> یا <strong>Opportunity</strong> میں تبدیل کر سکتے ہیں۔</p>""",
            "language": "Bilingual",
            "related_doctype": "Lead",
            "is_active": 1
        },

        # GENERAL
        {
            "title": "How to use Awesome Bar for quick search",
            "category": "General",
            "keywords": "awesome bar, search, quick search, find, ctrl+k",
            "question": "How do I quickly search in ERPNext?",
            "answer": """<p>Use the <strong>Awesome Bar</strong> for quick search:</p>
<ul>
<li>Press <strong>Ctrl + K</strong> (or Cmd + K on Mac) to open</li>
<li>Type to search for:
  <ul>
  <li>Doctypes (e.g., "Sales Invoice")</li>
  <li>Documents (e.g., "INV-2024-00001")</li>
  <li>Reports</li>
  <li>Pages</li>
  </ul>
</li>
<li>Use <strong>↑↓</strong> arrow keys to navigate</li>
<li>Press <strong>Enter</strong> to open</li>
</ul>
<p><strong>Advanced:</strong> Type <code>new sales invoice</code> to create new document directly.</p>""",
            "answer_urdu": """<p>تیز تلاش کے لیے <strong>Awesome Bar</strong> استعمال کریں:</p>
<ul>
<li>کھولنے کے لیے <strong>Ctrl + K</strong> (یا Mac پر Cmd + K) دبائیں</li>
<li>تلاش کے لیے ٹائپ کریں:
  <ul>
  <li>Doctypes (مثلاً "Sales Invoice")</li>
  <li>Documents (مثلاً "INV-2024-00001")</li>
  <li>Reports</li>
  <li>Pages</li>
  </ul>
</li>
<li>نیویگیٹ کرنے کے لیے <strong>↑↓</strong> arrow keys استعمال کریں</li>
<li>کھولنے کے لیے <strong>Enter</strong> دبائیں</li>
</ul>
<p><strong>ایڈوانس:</strong> نیا document براہ راست بنانے کے لیے <code>new sales invoice</code> ٹائپ کریں۔</p>""",
            "language": "Bilingual",
            "related_doctype": None,
            "is_active": 1
        }
    ]

if __name__ == "__main__":
    load_knowledge_base()
