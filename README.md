# Chatnext - AI Assistant for ERPNext

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ERPNext](https://img.shields.io/badge/ERPNext-v14%2B-blue.svg)](https://github.com/frappe/erpnext)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)

**Chatnext** is an intelligent AI assistant for ERPNext that provides contextual help, proactive suggestions, and multilingual support (English & Urdu) across all ERPNext modules.

---

## 🎯 Overview

Chatnext is designed to make ERPNext easier to use by providing:
- **Instant Help**: Chat-based assistance for any ERPNext query
- **Context-Aware**: Automatically understands which document you're working on
- **Multilingual**: Full support for English and Urdu (اردو)
- **Proactive Suggestions**: Smart alerts for low stock, overdue invoices, pending approvals, etc.
- **Knowledge Base**: Pre-loaded answers for common ERPNext questions
- **Feedback System**: Learns from user feedback to improve responses
- **Works Offline**: No internet required - fully local processing

---

## 🌟 Features

### 1. **Smart Chat Widget**
- Floating chat button accessible from any ERPNext page
- Keyboard shortcut: `Ctrl+Shift+C`
- Context-aware responses based on current page
- Real-time typing indicators
- Message feedback (👍/👎)

### 2. **Comprehensive Knowledge Base**
Pre-loaded with answers for:
- Sales & CRM (Invoices, Quotations, Leads)
- Purchase (Purchase Orders, Suppliers)
- HR (Employees, Attendance, Leave, Payroll)
- Inventory (Stock Entries, Stock Balance)
- Accounting (Payment Entries, Accounts)
- General ERPNext tips and shortcuts

### 3. **Proactive Alerts**
Automatic notifications for:
- **Low Stock**: Items below reorder level
- **Overdue Invoices**: Unpaid customer invoices
- **Pending Approvals**: Leave applications awaiting approval
- **Expiring Contracts**: Contracts ending within 30 days
- **Draft Documents**: Unsubmitted POs older than 2 days

### 4. **Multilingual Support**
- Supports **English** and **اردو (Urdu)**
- Auto-detection of user language
- Bilingual knowledge base articles
- Switchable language selector in chat

### 5. **Context Detection**
- Automatically detects current DocType and document
- Provides relevant suggestions based on context
- Links responses to specific ERPNext pages

### 6. **🤖 AI-Powered Responses (NEW!)**
- **Local AI Model**: Uses Hugging Face Transformers (facebook/opt-125m)
- **Auto-Download**: Model automatically downloads on first use (~250MB)
- **No Internet Required**: Fully offline AI processing
- **Optional Feature**: Enable/disable from Chatnext Settings
- **Intelligent Fallback**: Uses AI when knowledge base has partial matches
- **Configurable**: Adjust AI temperature and response length
- **Works on CPU**: No GPU required, runs on any server

---

## 📦 Installation

### Prerequisites
- **Frappe Bench** installed
- **ERPNext v14** or higher
- **Python 3.10+**
- **Ubuntu/Debian** or compatible Linux OS

### Step 1: Get the App

```bash
cd frappe-bench
bench get-app https://github.com/Musab1khan/chatnext.git
```

### Step 2: Install on Your Site

```bash
bench --site yoursite.local install-app chatnext
```

### Step 3: Install AI Dependencies (Optional - for AI features)

If you want to enable AI-powered responses:
```bash
pip install transformers torch sentencepiece protobuf
```

**Note**: This will download ~1GB of dependencies. Skip this if you only want knowledge base responses.

### Step 4: Load Default Data

Load knowledge base articles:
```bash
bench --site yoursite.local execute chatnext.chatnext.load_knowledge_base.load_knowledge_base
```

Load proactive rules:
```bash
bench --site yoursite.local execute chatnext.chatnext.load_proactive_rules.load_proactive_rules
```

### Step 5: Build Assets

```bash
bench build --app chatnext
```

### Step 6: Restart

```bash
bench restart
```

### Step 7: Enable AI Responses (Optional)

1. Go to **Chatnext → Chatnext Settings**
2. Check **Enable AI Responses**
3. Select AI Model (default: facebook/opt-125m)
4. Save

On first AI query, the model will auto-download (~250MB). This takes 2-3 minutes.

---

## 🚀 Usage

### Opening Chatnext

**Option 1:** Click the floating chat button in the bottom-right corner

**Option 2:** Press `Ctrl+Shift+C` anywhere in ERPNext

### Asking Questions

Simply type your question in natural language:

**Examples:**
- "How do I create a Sales Invoice?"
- "کسٹمر invoice کیسے بناتے ہیں؟" (Urdu)
- "Show me overdue invoices"
- "How to mark attendance?"
- "What is a Stock Entry?"

### Language Selection

Use the language dropdown in the chat header to select:
- **Auto Detect** (Default)
- **English**
- **اردو (Urdu)**

### Feedback

After receiving a response, use the 👍 or 👎 buttons to help Chatnext learn and improve.

---

## 📚 DocTypes

Chatnext creates the following DocTypes:

| DocType | Purpose |
|---------|---------|
| **Chat Session** | Stores chat sessions with context tracking |
| **Chat Message** | Individual messages with intent detection |
| **Knowledge Base Article** | Q&A database for common queries |
| **Chatnext Feedback** | User feedback for continuous improvement |
| **Proactive Rule** | Rules for proactive suggestions |
| **Chatnext Settings** | Configuration for AI and general settings |

---

## 🔧 Configuration

### Adding Custom Knowledge Base Articles

1. Go to **Chatnext → Knowledge Base Article → New**
2. Fill in:
   - **Title**: Article title
   - **Category**: Module (Sales, HR, etc.)
   - **Keywords**: Search keywords (comma-separated)
   - **Question**: The question users might ask
   - **Answer**: Detailed answer (supports HTML)
   - **Answer (Urdu)**: Urdu translation (optional)
   - **Language**: English/Urdu/Bilingual
3. Save and activate

### Creating Custom Proactive Rules

1. Go to **Chatnext → Proactive Rule → New**
2. Configure:
   - **Rule Name**: Unique identifier
   - **Rule Type**: Low Stock/Overdue Invoice/etc.
   - **Target DocType**: Which DocType to monitor
   - **Condition**: Python expression (e.g., `docstatus == 0`)
   - **Suggestion Template**: Alert message
   - **Suggestion Template (Urdu)**: Urdu version
   - **Priority**: Low/Medium/High/Critical
   - **Frequency**: How often to check
3. Save and activate

---

## 🛠️ API Methods

Chatnext exposes the following whitelisted APIs:

### `/api/method/chatnext.chatnext.api.query`
Main query handler - processes user questions

**Parameters:**
- `message`: User's question
- `session_id`: Chat session ID (optional)
- `context_doctype`: Current DocType (optional)
- `context_docname`: Current document name (optional)
- `language`: Preferred language

**Returns:**
```json
{
  "success": true,
  "session_id": "CHAT-00001",
  "answer": "To create a Sales Invoice...",
  "source": "Knowledge Base",
  "confidence": 85,
  "suggestions": ["Related article 1", "Related article 2"]
}
```

### `/api/method/chatnext.chatnext.api.search_knowledge_base`
Search knowledge base articles

**Parameters:**
- `query`: Search query
- `category`: Filter by category (optional)
- `language`: Filter by language (optional)
- `limit`: Max results (default: 10)

### `/api/method/chatnext.chatnext.api.submit_feedback`
Submit user feedback

**Parameters:**
- `message_id`: Chat message ID
- `rating`: Helpful/Not Helpful/Partially Helpful
- `feedback_text`: Additional feedback (optional)
- `correction`: Suggested correction (optional)

### `/api/method/chatnext.chatnext.api.get_proactive_suggestions`
Get proactive suggestions

**Parameters:**
- `doctype`: Current DocType (optional)
- `docname`: Current document name (optional)

---

## 🎨 Customization

### Styling

Edit `/chatnext/public/css/chatnext_widget.css` to customize:
- Colors
- Fonts
- Chat bubble styles
- Button appearances

### Widget Behavior

Edit `/chatnext/public/js/chatnext_widget.js` to modify:
- Keyboard shortcuts
- Auto-open conditions
- Animation timings
- Context detection logic

---

## 🧪 Development

### Setting up Development Environment

```bash
cd apps/chatnext
pre-commit install
```

### Running Tests

```bash
bench --site yoursite.local run-tests --app chatnext
```

### Code Quality Tools

Chatnext uses:
- **ruff**: Python linting
- **eslint**: JavaScript linting
- **prettier**: Code formatting
- **pyupgrade**: Python syntax upgrades

---

## 📖 Architecture

### Components

1. **Frontend (JavaScript)**
   - `chatnext_widget.js`: Chat UI and interactions
   - `chatnext_widget.css`: Styling

2. **Backend (Python)**
   - `api.py`: API endpoints and query processing
   - `load_knowledge_base.py`: KB article loader
   - `load_proactive_rules.py`: Proactive rule loader

3. **DocTypes**
   - 5 custom DocTypes for data storage

### Query Processing Flow

```
User Question
    ↓
Language Detection
    ↓
Intent Detection
    ↓
Knowledge Base Search → Rule-Based Response → Default Response
    ↓
Context Enhancement
    ↓
Response Delivery
    ↓
Feedback Collection
```

---

## 🌍 Multilingual Support

### Supported Languages

- **English**: Full support
- **اردو (Urdu)**: Full support with RTL text rendering

### Adding More Languages

1. Add language to `detect_language()` in `api.py`
2. Create KB articles in the new language
3. Update language selector in `chatnext_widget.js`
4. Add response templates in the new language

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Style

- Follow [Frappe Framework Guidelines](https://frappeframework.com/docs/user/en/guides/app-development/coding-standards)
- Use descriptive variable names
- Add docstrings to functions
- Write tests for new features

---

## 📝 License

This project is licensed under the **MIT License**.

Copyright (c) 2024 Umair Wali

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

---

## 👨‍💻 Author

**Umair Wali**
- Email: [umairwali6@gmail.com](mailto:umairwali6@gmail.com)
- GitHub: [@Musab1khan](https://github.com/Musab1khan)

---

## 🙏 Acknowledgments

- [Frappe Framework](https://frappeframework.com/)
- [ERPNext](https://erpnext.com/)
- All contributors and testers

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on [GitHub](https://github.com/Musab1khan/chatnext/issues)
- Email: [umairwali6@gmail.com](mailto:umairwali6@gmail.com)

---

## 🗺️ Roadmap

### Planned Features

- [x] **Local AI Model Integration** ✅ (NEW!)
- [ ] Voice input support
- [ ] Integration with external LLMs (OpenAI, Ollama)
- [ ] More languages (Arabic, Hindi, Spanish)
- [ ] Advanced analytics dashboard
- [ ] Mobile app
- [ ] WebSocket for real-time chat
- [ ] Image/attachment support in chat
- [ ] Chat export functionality
- [ ] Integration with ERPNext Help Articles
- [ ] Custom training on company-specific data
- [ ] Fine-tune AI model on ERPNext documentation

---

## 📊 Stats

- **6 DocTypes**: Comprehensive data structure
- **11 Pre-loaded KB Articles**: Ready to use
- **5 Proactive Rules**: Smart business alerts
- **2 Languages**: English & Urdu
- **🤖 AI-Powered**: Optional local AI model (125M parameters)
- **100% Offline**: No cloud dependency
- **Open Source**: MIT License

---

**Made with ❤️ for the ERPNext Community**
