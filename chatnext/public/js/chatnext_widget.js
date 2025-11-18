/**
 * Chatnext Widget - Floating Chat Assistant for ERPNext Desk
 * Provides AI-powered help across all modules
 */

class ChatnextWidget {
    constructor() {
        this.session_id = null;
        this.is_open = false;
        this.is_minimized = false;
        this.current_doctype = null;
        this.current_docname = null;
        this.language = localStorage.getItem('chatnext_language') || 'Auto Detect';
        this.init();
    }

    init() {
        // Wait for page to load
        $(document).ready(() => {
            this.render();
            this.bind_events();
            this.detect_context();
            this.load_proactive_suggestions();
        });
    }

    render() {
        // Create widget HTML
        const widget_html = `
            <div id="chatnext-widget" class="chatnext-widget">
                <!-- Floating Button -->
                <div class="chatnext-float-btn" title="Open Chatnext Assistant">
                    <svg class="chatnext-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        <path d="M8 10h.01M12 10h.01M16 10h.01"></path>
                    </svg>
                    <span class="chatnext-notification-badge" style="display:none;">0</span>
                </div>

                <!-- Chat Window -->
                <div class="chatnext-window" style="display:none;">
                    <div class="chatnext-header">
                        <div class="chatnext-header-content">
                            <h3>Chatnext Assistant</h3>
                            <p class="chatnext-subtitle">Your ERPNext AI Helper</p>
                        </div>
                        <div class="chatnext-header-actions">
                            <select class="chatnext-language-select">
                                <option value="Auto Detect">Auto Detect</option>
                                <option value="English">English</option>
                                <option value="Urdu">اردو</option>
                            </select>
                            <button class="chatnext-minimize-btn" title="Minimize">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path d="M5 12h14"></path>
                                </svg>
                            </button>
                            <button class="chatnext-close-btn" title="Close">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path d="M18 6L6 18M6 6l12 12"></path>
                                </svg>
                            </button>
                        </div>
                    </div>

                    <div class="chatnext-messages-container">
                        <div class="chatnext-messages" id="chatnext-messages">
                            <!-- Welcome message -->
                            <div class="chatnext-message chatnext-bot-message">
                                <div class="chatnext-message-avatar">AI</div>
                                <div class="chatnext-message-content">
                                    <p>Hello! I'm Chatnext, your ERPNext assistant. How can I help you today?</p>
                                    <p class="chatnext-urdu">السلام علیکم! میں Chatnext ہوں، آپ کا ERPNext assistant۔ میں آپ کی کیسے مدد کر سکتا ہوں؟</p>
                                </div>
                            </div>
                        </div>

                        <!-- Proactive Suggestions -->
                        <div class="chatnext-suggestions" id="chatnext-suggestions" style="display:none;">
                            <div class="chatnext-suggestions-header">Suggestions:</div>
                            <div class="chatnext-suggestions-list"></div>
                        </div>
                    </div>

                    <div class="chatnext-input-container">
                        <textarea
                            id="chatnext-input"
                            class="chatnext-input"
                            placeholder="Type your question here... (Ctrl+Enter to send)"
                            rows="1"
                        ></textarea>
                        <button class="chatnext-send-btn" id="chatnext-send-btn">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"></path>
                            </svg>
                        </button>
                    </div>

                    <div class="chatnext-footer">
                        <small>Powered by Chatnext • Press Ctrl+Shift+C to toggle</small>
                    </div>
                </div>
            </div>
        `;

        $('body').append(widget_html);

        // Set saved language
        $('.chatnext-language-select').val(this.language);
    }

    bind_events() {
        const self = this;

        // Float button click
        $('.chatnext-float-btn').on('click', function() {
            self.toggle_window();
        });

        // Close button
        $('.chatnext-close-btn').on('click', function() {
            self.close_window();
        });

        // Minimize button
        $('.chatnext-minimize-btn').on('click', function() {
            self.minimize_window();
        });

        // Language change
        $('.chatnext-language-select').on('change', function() {
            self.language = $(this).val();
            localStorage.setItem('chatnext_language', self.language);
        });

        // Send button
        $('#chatnext-send-btn').on('click', function() {
            self.send_message();
        });

        // Enter key
        $('#chatnext-input').on('keydown', function(e) {
            // Ctrl+Enter to send
            if (e.ctrlKey && e.keyCode === 13) {
                e.preventDefault();
                self.send_message();
            }
            // Auto-resize textarea
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 150) + 'px';
        });

        // Global keyboard shortcut: Ctrl+Shift+C
        $(document).on('keydown', function(e) {
            if (e.ctrlKey && e.shiftKey && e.keyCode === 67) {
                e.preventDefault();
                self.toggle_window();
            }
        });

        // Context detection on page change
        frappe.router.on('change', () => {
            self.detect_context();
            self.load_proactive_suggestions();
        });
    }

    toggle_window() {
        if (this.is_open) {
            this.close_window();
        } else {
            this.open_window();
        }
    }

    open_window() {
        $('.chatnext-window').slideDown(300);
        $('.chatnext-float-btn').addClass('chatnext-hidden');
        this.is_open = true;
        this.is_minimized = false;
        $('#chatnext-input').focus();
    }

    close_window() {
        $('.chatnext-window').slideUp(300);
        $('.chatnext-float-btn').removeClass('chatnext-hidden');
        this.is_open = false;
    }

    minimize_window() {
        $('.chatnext-messages-container').slideToggle(200);
        $('.chatnext-input-container').slideToggle(200);
        $('.chatnext-footer').slideToggle(200);
        this.is_minimized = !this.is_minimized;
    }

    detect_context() {
        // Detect current page context
        const route = frappe.get_route();

        if (route[0] === 'Form') {
            this.current_doctype = route[1];
            this.current_docname = route[2];
        } else if (route[0] === 'List') {
            this.current_doctype = route[1];
            this.current_docname = null;
        } else {
            this.current_doctype = null;
            this.current_docname = null;
        }

        // Show context indicator
        if (this.current_doctype) {
            this.show_context_indicator(this.current_doctype, this.current_docname);
        }
    }

    show_context_indicator(doctype, docname) {
        const context_html = `
            <div class="chatnext-context-indicator">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="12" height="12">
                    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path>
                </svg>
                Context: ${doctype}${docname ? ` - ${docname}` : ''}
            </div>
        `;

        $('.chatnext-subtitle').html(context_html);
    }

    async send_message() {
        const message = $('#chatnext-input').val().trim();

        if (!message) return;

        // Add user message to UI
        this.add_message(message, 'user');

        // Clear input
        $('#chatnext-input').val('').css('height', 'auto');

        // Show typing indicator
        this.show_typing_indicator();

        try {
            // Call API
            const response = await frappe.call({
                method: 'chatnext.chatnext.api.query',
                args: {
                    message: message,
                    session_id: this.session_id,
                    context_doctype: this.current_doctype,
                    context_docname: this.current_docname,
                    language: this.language
                }
            });

            // Remove typing indicator
            this.remove_typing_indicator();

            if (response.message && response.message.success) {
                // Save session ID
                this.session_id = response.message.session_id;

                // Add bot response
                this.add_message(
                    response.message.answer,
                    'bot',
                    response.message.message_id,
                    response.message.source,
                    response.message.confidence
                );

                // Show suggestions if any
                if (response.message.suggestions && response.message.suggestions.length > 0) {
                    this.show_suggestions(response.message.suggestions);
                }
            } else {
                this.add_message(
                    'Sorry, I encountered an error. Please try again.',
                    'bot'
                );
            }

        } catch (error) {
            this.remove_typing_indicator();
            this.add_message(
                'Sorry, I encountered a technical error. Please try again.',
                'bot'
            );
            console.error('Chatnext Error:', error);
        }
    }

    add_message(text, type, message_id = null, source = null, confidence = null) {
        const is_user = type === 'user';
        const avatar = is_user ? frappe.user.abbr() : 'AI';

        // For user messages, escape HTML. For bot messages, allow HTML rendering
        const formatted_text = is_user
            ? frappe.utils.escape_html(text).replace(/\n/g, '<br>')
            : text;

        let message_html = `
            <div class="chatnext-message ${is_user ? 'chatnext-user-message' : 'chatnext-bot-message'}" ${message_id ? `data-message-id="${message_id}"` : ''}>
                <div class="chatnext-message-avatar">${avatar}</div>
                <div class="chatnext-message-content">
                    <div>${formatted_text}</div>
                    ${source ? `<small class="chatnext-source">Source: ${source}${confidence ? ` (${confidence}% confidence)` : ''}</small>` : ''}
                </div>
            </div>
        `;

        // Add feedback buttons for bot messages
        if (!is_user && message_id) {
            message_html = message_html.replace('</div></div>', `
                <div class="chatnext-feedback-btns">
                    <button class="chatnext-feedback-btn chatnext-helpful" data-rating="Helpful" title="Helpful">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
                            <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
                        </svg>
                    </button>
                    <button class="chatnext-feedback-btn chatnext-not-helpful" data-rating="Not Helpful" title="Not Helpful">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
                            <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"></path>
                        </svg>
                    </button>
                </div>
            </div></div>`);
        }

        $('#chatnext-messages').append(message_html);
        this.scroll_to_bottom();

        // Bind feedback buttons
        if (!is_user && message_id) {
            this.bind_feedback_buttons(message_id);
        }
    }

    bind_feedback_buttons(message_id) {
        const self = this;

        $(`[data-message-id="${message_id}"] .chatnext-feedback-btn`).on('click', function() {
            const rating = $(this).data('rating');
            self.submit_feedback(message_id, rating);

            // Visual feedback
            $(this).addClass('selected');
            $(this).siblings().removeClass('selected');
        });
    }

    async submit_feedback(message_id, rating) {
        try {
            await frappe.call({
                method: 'chatnext.chatnext.api.submit_feedback',
                args: {
                    message_id: message_id,
                    rating: rating
                }
            });

            frappe.show_alert({
                message: 'Thank you for your feedback!',
                indicator: 'green'
            }, 3);

        } catch (error) {
            console.error('Feedback Error:', error);
        }
    }

    show_typing_indicator() {
        const typing_html = `
            <div class="chatnext-message chatnext-bot-message chatnext-typing">
                <div class="chatnext-message-avatar">AI</div>
                <div class="chatnext-message-content">
                    <div class="chatnext-typing-dots">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
        `;
        $('#chatnext-messages').append(typing_html);
        this.scroll_to_bottom();
    }

    remove_typing_indicator() {
        $('.chatnext-typing').remove();
    }

    show_suggestions(suggestions) {
        const suggestions_html = suggestions.map(s =>
            `<button class="chatnext-suggestion-chip">${s}</button>`
        ).join('');

        $('#chatnext-suggestions .chatnext-suggestions-list').html(suggestions_html);
        $('#chatnext-suggestions').show();

        // Bind click events
        $('.chatnext-suggestion-chip').on('click', function() {
            $('#chatnext-input').val($(this).text());
            $('#chatnext-input').focus();
        });
    }

    async load_proactive_suggestions() {
        try {
            const response = await frappe.call({
                method: 'chatnext.chatnext.api.get_proactive_suggestions',
                args: {
                    doctype: this.current_doctype,
                    docname: this.current_docname
                }
            });

            if (response.message && response.message.length > 0) {
                this.show_proactive_badge(response.message.length);
                // Could show these suggestions in a special section
            }

        } catch (error) {
            console.error('Proactive Suggestions Error:', error);
        }
    }

    show_proactive_badge(count) {
        if (count > 0) {
            $('.chatnext-notification-badge').text(count).show();
        } else {
            $('.chatnext-notification-badge').hide();
        }
    }

    scroll_to_bottom() {
        const messages = document.getElementById('chatnext-messages');
        if (messages) {
            messages.scrollTop = messages.scrollHeight;
        }
    }
}

// Initialize widget when page is ready
function initChatnext() {
    if (typeof frappe !== 'undefined' && frappe.session && frappe.session.user !== 'Guest') {
        window.chatnext_widget = new ChatnextWidget();
    } else if (typeof frappe !== 'undefined') {
        // Retry after a short delay
        setTimeout(initChatnext, 500);
    }
}

// Start initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChatnext);
} else {
    // DOM already loaded
    initChatnext();
}
