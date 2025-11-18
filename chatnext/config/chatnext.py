"""
Chatnext Workspace Configuration
Creates a dedicated workspace for Chatnext with all related doctypes and tools
"""

from frappe import _


def get_data():
    return {
        "Chatnext": {
            "icon": "fa fa-comments",
            "color": "#667eea",
            "label": _("Chatnext"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Chat Session",
                    "label": _("Chat Sessions"),
                    "description": _("View all chat sessions")
                },
                {
                    "type": "doctype",
                    "name": "Chat Message",
                    "label": _("Chat Messages"),
                    "description": _("View all chat messages")
                },
                {
                    "type": "doctype",
                    "name": "Knowledge Base Article",
                    "label": _("Knowledge Base"),
                    "description": _("Manage knowledge base articles")
                },
                {
                    "type": "doctype",
                    "name": "Chatnext Feedback",
                    "label": _("User Feedback"),
                    "description": _("View user feedback and ratings")
                },
                {
                    "type": "doctype",
                    "name": "Proactive Rule",
                    "label": _("Proactive Rules"),
                    "description": _("Configure proactive suggestions")
                },
                {
                    "type": "doctype",
                    "name": "Chatnext Settings",
                    "label": _("Settings"),
                    "description": _("Configure AI and general settings")
                }
            ]
        }
    }
