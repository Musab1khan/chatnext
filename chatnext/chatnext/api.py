"""
Chatnext API Methods
Backend APIs for query handling, knowledge base search, and chat functionality
"""

import frappe
from frappe import _
import re
import json
from datetime import datetime
from chatnext.chatnext.ai_engine import get_ai_enhanced_response, is_ai_enabled


@frappe.whitelist()
def query(message, session_id=None, context_doctype=None, context_docname=None, language="Auto Detect"):
    """
    Main query handler - processes user queries and returns responses

    Args:
        message (str): User's query message
        session_id (str): Chat session ID (creates new if None)
        context_doctype (str): DocType from which chat was opened
        context_docname (str): Document name from which chat was opened
        language (str): Preferred language (English/Urdu/Auto Detect)

    Returns:
        dict: Response with answer, session_id, and metadata
    """
    try:
        # Create or get session
        if not session_id:
            session = create_session(
                user=frappe.session.user,
                context_doctype=context_doctype,
                context_docname=context_docname,
                language=language
            )
            session_id = session.name
        else:
            session = frappe.get_doc("Chat Session", session_id)

        # Detect language if auto
        detected_language = detect_language(message) if language == "Auto Detect" else language

        # Save user message
        user_message = save_message(
            session_id=session_id,
            message=message,
            message_type="User",
            language=detected_language
        )

        # Detect query intent
        intent = detect_intent(message)
        user_message.query_intent = intent
        user_message.save()

        # Get response
        response_data = get_response(
            message=message,
            intent=intent,
            session=session,
            language=detected_language
        )

        # Save bot response
        bot_message = save_message(
            session_id=session_id,
            message=response_data["answer"],
            message_type="Bot",
            language=detected_language,
            source=response_data.get("source", "Rule-Based"),
            confidence_score=response_data.get("confidence", 0)
        )

        # Update session
        session.message_count = session.message_count + 2
        session.last_message = message[:200]
        session.save()
        frappe.db.commit()

        return {
            "success": True,
            "session_id": session_id,
            "answer": response_data["answer"],
            "source": response_data.get("source"),
            "confidence": response_data.get("confidence"),
            "suggestions": response_data.get("suggestions", []),
            "message_id": bot_message.name
        }

    except Exception as e:
        frappe.log_error(f"Chatnext Query Error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "answer": _("Sorry, I encountered an error. Please try again.")
        }


@frappe.whitelist()
def search_knowledge_base(query, category=None, language=None, limit=10):
    """
    Search knowledge base for relevant articles

    Args:
        query (str): Search query
        category (str): Filter by category
        language (str): Filter by language
        limit (int): Maximum results to return

    Returns:
        list: Matching knowledge base articles
    """
    try:
        filters = {"is_active": 1}

        if category:
            filters["category"] = category

        if language and language != "Auto Detect":
            filters["language"] = ["in", [language, "Bilingual"]]

        # Search in title, question, keywords
        articles = frappe.get_all(
            "Knowledge Base Article",
            filters=filters,
            fields=["name", "title", "question", "answer", "answer_urdu", "category",
                    "language", "usage_count", "helpful_count", "related_doctype", "keywords"],
            limit_page_length=limit
        )

        # Simple keyword matching (can be enhanced with better search)
        query_lower = query.lower()
        query_keywords = query_lower.split()

        scored_articles = []
        for article in articles:
            score = 0
            # Include keywords field in search
            article_text = f"{article.get('title', '')} {article.get('question', '')} {article.get('keywords', '')}".lower()

            # Score based on keyword matches
            for keyword in query_keywords:
                if keyword in article_text:
                    score += 1

            if score > 0:
                article['relevance_score'] = score
                scored_articles.append(article)

        # Sort by relevance
        scored_articles.sort(key=lambda x: x['relevance_score'], reverse=True)

        return scored_articles

    except Exception as e:
        frappe.log_error(f"KB Search Error: {str(e)}")
        return []


@frappe.whitelist()
def submit_feedback(message_id, rating, feedback_text=None, correction=None):
    """
    Submit user feedback for a message

    Args:
        message_id (str): Chat message ID
        rating (str): Helpful/Not Helpful/Partially Helpful
        feedback_text (str): Additional feedback
        correction (str): Suggested correction

    Returns:
        dict: Success status
    """
    try:
        message = frappe.get_doc("Chat Message", message_id)

        # Create feedback
        feedback = frappe.get_doc({
            "doctype": "Chatnext Feedback",
            "message": message_id,
            "session": message.session,
            "user": frappe.session.user,
            "rating": rating,
            "feedback_text": feedback_text,
            "correction": correction,
            "timestamp": datetime.now()
        })
        feedback.insert()

        # Update message
        message.helpful = "Yes" if rating == "Helpful" else "No"
        message.save()

        # Update KB article if applicable
        if message.source == "Knowledge Base":
            update_kb_stats(message.message, rating)

        frappe.db.commit()

        return {"success": True, "message": _("Thank you for your feedback!")}

    except Exception as e:
        frappe.log_error(f"Feedback Error: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_session_history(session_id, limit=50):
    """
    Get chat history for a session

    Args:
        session_id (str): Chat session ID
        limit (int): Number of messages to retrieve

    Returns:
        list: Chat messages
    """
    try:
        messages = frappe.get_all(
            "Chat Message",
            filters={"session": session_id},
            fields=["name", "message", "message_type", "timestamp", "language",
                    "source", "confidence_score", "helpful"],
            order_by="timestamp asc",
            limit_page_length=limit
        )
        return messages
    except Exception as e:
        frappe.log_error(f"Session History Error: {str(e)}")
        return []


@frappe.whitelist()
def get_proactive_suggestions(doctype=None, docname=None):
    """
    Get proactive suggestions based on active rules

    Args:
        doctype (str): Current doctype
        docname (str): Current document name

    Returns:
        list: Proactive suggestions
    """
    try:
        suggestions = []

        # Get active proactive rules
        rules = frappe.get_all(
            "Proactive Rule",
            filters={"is_active": 1},
            fields=["name", "rule_name", "rule_type", "target_doctype", "condition",
                    "suggestion_template", "suggestion_template_urdu", "priority"]
        )

        for rule in rules:
            # Check if rule applies to current context
            if doctype and rule.target_doctype and rule.target_doctype != doctype:
                continue

            # Execute rule condition (simplified - can be enhanced)
            if check_rule_condition(rule, doctype, docname):
                suggestions.append({
                    "rule": rule.rule_name,
                    "message": rule.suggestion_template,
                    "message_urdu": rule.suggestion_template_urdu,
                    "priority": rule.priority,
                    "type": rule.rule_type
                })

        # Sort by priority
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        suggestions.sort(key=lambda x: priority_order.get(x["priority"], 4))

        return suggestions

    except Exception as e:
        frappe.log_error(f"Proactive Suggestions Error: {str(e)}")
        return []


# Helper Functions

def create_session(user, context_doctype=None, context_docname=None, language="Auto Detect"):
    """Create a new chat session"""
    session = frappe.get_doc({
        "doctype": "Chat Session",
        "session_title": f"Chat - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "user": user,
        "start_time": datetime.now(),
        "status": "Active",
        "context_doctype": context_doctype,
        "context_docname": context_docname,
        "language": language,
        "message_count": 0
    })
    session.insert()
    frappe.db.commit()
    return session


def save_message(session_id, message, message_type, language, source=None, confidence_score=None):
    """Save a chat message"""
    msg = frappe.get_doc({
        "doctype": "Chat Message",
        "session": session_id,
        "message_type": message_type,
        "message": message,
        "timestamp": datetime.now(),
        "language": language,
        "source": source,
        "confidence_score": confidence_score
    })
    msg.insert()
    frappe.db.commit()
    return msg


def detect_language(text):
    """Detect language of text (English or Urdu)"""
    # Simple detection based on character ranges
    urdu_chars = re.findall(r'[\u0600-\u06FF]', text)
    english_chars = re.findall(r'[a-zA-Z]', text)

    if len(urdu_chars) > len(english_chars):
        return "Urdu"
    return "English"


def detect_intent(message):
    """Detect user query intent"""
    message_lower = message.lower()

    # Intent patterns
    intents = {
        "how_to": ["how to", "how do i", "how can i", "kaise", "kaisay"],
        "what_is": ["what is", "what are", "define", "kya hai", "kia hai"],
        "create": ["create", "new", "add", "banao", "banana"],
        "error": ["error", "issue", "problem", "not working", "masla", "kharabi"],
        "find": ["find", "search", "where", "kahan", "dhundo"],
        "report": ["report", "list", "show me", "dikhao", "report"],
        "setup": ["setup", "configure", "settings", "setting", "configuration"]
    }

    for intent_type, keywords in intents.items():
        for keyword in keywords:
            if keyword in message_lower:
                return intent_type

    return "general"


def get_response(message, intent, session, language):
    """
    Get response for user query
    Priority: 1. Knowledge Base, 2. AI-Enhanced, 3. Rule-based, 4. Default
    """
    # Try knowledge base first
    kb_articles = search_knowledge_base(message, language=language, limit=3)

    # Perfect KB match - use it directly
    if kb_articles and kb_articles[0].get('relevance_score', 0) >= 2:
        article = kb_articles[0]

        # Update usage count
        frappe.db.set_value("Knowledge Base Article", article['name'],
                           "usage_count", article.get('usage_count', 0) + 1)

        answer = article.get('answer_urdu') if language == "Urdu" and article.get('answer_urdu') else article.get('answer')

        return {
            "answer": answer,
            "source": "Knowledge Base",
            "confidence": min(article['relevance_score'] * 30, 95),
            "suggestions": [a.get('title') for a in kb_articles[1:]]
        }

    # Try AI-enhanced response if enabled and KB has some relevance
    if is_ai_enabled() and kb_articles:
        ai_response = get_ai_enhanced_response(message, kb_articles, language)
        if ai_response:
            return ai_response

    # Rule-based responses
    response = get_rule_based_response(message, intent, session, language)
    if response:
        return response

    # Default response
    return get_default_response(language)


def get_rule_based_response(message, intent, session, language):
    """Get rule-based response based on intent"""

    # Context-aware responses
    if session.context_doctype:
        context_response = get_context_response(session.context_doctype, message, language)
        if context_response:
            return context_response

    # Intent-based responses
    responses_en = {
        "how_to": "To help you better, could you please specify which module or feature you need help with? For example: Sales, Purchase, HR, Inventory, etc.",
        "what_is": "I can explain ERPNext concepts. Please specify what you'd like to know about.",
        "create": "I can guide you on creating documents in ERPNext. Which document type would you like to create?",
        "error": "I'd be happy to help troubleshoot. Could you please describe the error or issue in more detail?",
        "find": "You can use the Awesome Bar (Ctrl+K) to search globally. What specifically are you looking for?",
        "report": "ERPNext has many built-in reports. Which module's reports are you interested in?",
        "setup": "I can help with ERPNext setup. Which area would you like to configure?"
    }

    responses_ur = {
        "how_to": "آپ کی مدد کرنے کے لیے، براہ کرم بتائیں کہ آپ کو کس ماڈیول یا فیچر میں مدد چاہیے؟ مثال: Sales, Purchase, HR, Inventory",
        "what_is": "میں ERPNext کے تصورات سمجھا سکتا ہوں۔ براہ کرم بتائیں آپ کیا جاننا چاہتے ہیں۔",
        "create": "میں آپ کو ERPNext میں documents بنانے میں مدد کر سکتا ہوں۔ آپ کون سا document بنانا چاہتے ہیں؟",
        "error": "میں مسئلہ حل کرنے میں مدد کروں گا۔ براہ کرم error یا issue کی تفصیل بتائیں۔",
        "find": "آپ Awesome Bar (Ctrl+K) استعمال کر کے تلاش کر سکتے ہیں۔ آپ کیا ڈھونڈ رہے ہیں؟",
        "report": "ERPNext میں بہت سی رپورٹس ہیں۔ آپ کو کس ماڈیول کی رپورٹس چاہیے؟",
        "setup": "میں ERPNext setup میں مدد کر سکتا ہوں۔ آپ کیا configure کرنا چاہتے ہیں؟"
    }

    responses = responses_ur if language == "Urdu" else responses_en

    if intent in responses:
        return {
            "answer": responses[intent],
            "source": "Rule-Based",
            "confidence": 70,
            "suggestions": []
        }

    return None


def get_context_response(doctype, message, language):
    """Get context-aware response based on current doctype"""

    context_responses_en = {
        "Sales Invoice": "I can help you with Sales Invoices. Common actions: Create new invoice, Check payment status, Print invoice, Submit invoice. What would you like to do?",
        "Purchase Order": "I can help with Purchase Orders. You can: Create PO, Receive items, Check status, or Amend PO. What do you need?",
        "Employee": "I can help with Employee records. You can: View attendance, Check leave balance, Update details, or Create salary slip. What would you like to know?",
        "Stock Entry": "I can help with Stock Entries. Common operations: Material Transfer, Receipt, Issue, Manufacture. What do you need help with?",
        "Customer": "I can help manage Customer records. You can: View history, Check outstanding, Create quotation, or Update details. What would you like to do?"
    }

    context_responses_ur = {
        "Sales Invoice": "میں Sales Invoices میں مدد کر سکتا ہوں۔ عام کام: نیا invoice بنانا، payment status چیک کرنا، invoice print کرنا۔ آپ کیا کرنا چاہتے ہیں؟",
        "Purchase Order": "میں Purchase Orders میں مدد کر سکتا ہوں۔ آپ کر سکتے ہیں: PO بنانا، items receive کرنا، status چیک کرنا۔ کیا چاہیے؟",
        "Employee": "میں Employee records میں مدد کر سکتا ہوں۔ آپ دیکھ سکتے ہیں: Attendance، Leave balance، Details update کرنا۔ کیا جاننا چاہتے ہیں؟",
        "Stock Entry": "میں Stock Entries میں مدد کر سکتا ہوں۔ عام operations: Material Transfer، Receipt، Issue، Manufacture۔ کیا مدد چاہیے؟",
        "Customer": "میں Customer records manage کرنے میں مدد کروں گا۔ آپ کر سکتے ہیں: History دیکھنا، Outstanding چیک کرنا، Quotation بنانا۔"
    }

    responses = context_responses_ur if language == "Urdu" else context_responses_en

    if doctype in responses:
        return {
            "answer": responses[doctype],
            "source": "Context-Aware",
            "confidence": 85,
            "suggestions": []
        }

    return None


def get_default_response(language):
    """Get default response when no specific match found"""
    if language == "Urdu":
        return {
            "answer": "میں آپ کی مدد کے لیے حاضر ہوں! براہ کرم اپنا سوال تفصیل سے پوچھیں۔ آپ مجھ سے ERPNext کے کسی بھی module کے بارے میں پوچھ سکتے ہیں: Sales, Purchase, Inventory, HR, Accounting, Manufacturing, وغیرہ۔",
            "source": "Rule-Based",
            "confidence": 50,
            "suggestions": []
        }

    return {
        "answer": "I'm here to help! Please ask your question in detail. You can ask me about any ERPNext module: Sales, Purchase, Inventory, HR, Accounting, Manufacturing, etc. How can I assist you today?",
        "source": "Rule-Based",
        "confidence": 50,
        "suggestions": []
    }


def update_kb_stats(answer_text, rating):
    """Update knowledge base article statistics"""
    try:
        # Find the article by answer text (simplified - could be improved)
        articles = frappe.get_all(
            "Knowledge Base Article",
            filters=[["answer", "like", f"%{answer_text[:100]}%"]],
            fields=["name", "helpful_count", "unhelpful_count"],
            limit=1
        )

        if articles:
            article = articles[0]
            if rating == "Helpful":
                frappe.db.set_value("Knowledge Base Article", article['name'],
                                   "helpful_count", article.get('helpful_count', 0) + 1)
            else:
                frappe.db.set_value("Knowledge Base Article", article['name'],
                                   "unhelpful_count", article.get('unhelpful_count', 0) + 1)
    except Exception as e:
        frappe.log_error(f"KB Stats Update Error: {str(e)}")


def check_rule_condition(rule, doctype=None, docname=None):
    """
    Check if a proactive rule condition is met
    This is a simplified version - can be enhanced with actual condition execution
    """
    try:
        # Rule type based checking
        if rule.rule_type == "Low Stock Alert":
            # Check for low stock items
            low_stock = frappe.db.sql("""
                SELECT COUNT(*) as count FROM `tabBin`
                WHERE actual_qty <= reorder_level AND reorder_level > 0
            """, as_dict=True)
            return low_stock[0].count > 0 if low_stock else False

        elif rule.rule_type == "Overdue Invoice":
            # Check for overdue invoices
            overdue = frappe.db.sql("""
                SELECT COUNT(*) as count FROM `tabSales Invoice`
                WHERE due_date < CURDATE() AND outstanding_amount > 0 AND docstatus = 1
            """, as_dict=True)
            return overdue[0].count > 0 if overdue else False

        # Add more rule type checks as needed

        return False

    except Exception as e:
        frappe.log_error(f"Rule Condition Check Error: {str(e)}")
        return False
