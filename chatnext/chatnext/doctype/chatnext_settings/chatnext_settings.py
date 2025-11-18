# Copyright (c) 2024, Umair Wali and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ChatnextSettings(Document):
    """
    Chatnext Settings - Configuration for AI and general settings
    """

    def validate(self):
        """Validate settings"""
        # Validate AI temperature range
        if self.enable_ai_responses and self.ai_temperature:
            if not (0.1 <= self.ai_temperature <= 1.0):
                frappe.throw("AI Temperature must be between 0.1 and 1.0")

        # Validate max tokens
        if self.enable_ai_responses and self.ai_max_tokens:
            if self.ai_max_tokens < 50 or self.ai_max_tokens > 2000:
                frappe.throw("Max Response Length must be between 50 and 2000")

        # Validate session timeout
        if self.session_timeout and (self.session_timeout < 5 or self.session_timeout > 240):
            frappe.throw("Session Timeout must be between 5 and 240 minutes")

    def on_update(self):
        """Clear cache when settings are updated"""
        frappe.clear_cache()
