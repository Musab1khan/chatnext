"""
AI Engine for Chatnext
Integrates local AI models (Hugging Face Transformers) and external AI APIs for intelligent responses
Supports: Local Transformers, OpenRouter, Google Gemini, DeepSeek
"""

import frappe
import os
import json
import requests
import re

# Try to import transformers, but don't fail if it's not installed
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    # Warning will be logged when AI is actually used

# Global model cache
_model_cache = None
_model_name = "facebook/opt-125m"  # Small, fast model (125M parameters, ~250MB)

# API Endpoints
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-latest:generateContent"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
OLLAMA_API_URL = "http://localhost:11434/api/generate"


def remove_markdown_formatting(text):
    """Remove markdown formatting from text to make it plain"""
    if not text:
        return text

    # Remove headers (### Header -> Header)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

    # Remove bold (**text** or __text__ -> text)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)

    # Remove italic (*text* or _text_ -> text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)

    # Remove horizontal rules (---, ***, ___)
    text = re.sub(r'^[\-\*_]{3,}$', '', text, flags=re.MULTILINE)

    # Remove inline code (`code` -> code)
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # Remove links ([text](url) -> text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # Convert bullet points (- item or * item -> item)
    text = re.sub(r'^\s*[\-\*]\s+', '', text, flags=re.MULTILINE)

    # Convert numbered lists (1. item -> item)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

    # Remove tables (simple approach - remove | characters)
    text = re.sub(r'\|', '', text)

    # Clean up extra blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def get_ai_model():
    """
    Get or initialize the AI model
    Uses a lightweight model that auto-downloads on first use
    """
    global _model_cache

    # Return None if transformers is not available
    if not TRANSFORMERS_AVAILABLE:
        return None

    if _model_cache is None:
        try:
            frappe.logger().info("Loading AI model for Chatnext...")

            # Create cache directory
            cache_dir = os.path.join(frappe.get_site_path(), "private", "chatnext_models")
            os.makedirs(cache_dir, exist_ok=True)

            # Initialize text generation pipeline with small model
            _model_cache = pipeline(
                "text-generation",
                model=_model_name,
                cache_dir=cache_dir,
                device=-1  # Use CPU
            )

            frappe.logger().info("AI model loaded successfully!")

        except Exception as e:
            frappe.log_error(f"AI Model Load Error: {str(e)}")
            _model_cache = None

    return _model_cache


def generate_ai_response(question, context=None, max_length=200):
    """
    Generate AI-powered response to user question

    Args:
        question (str): User's question
        context (str): Optional context information
        max_length (int): Maximum response length

    Returns:
        str: Generated response or None if failed
    """
    try:
        model = get_ai_model()

        if model is None:
            return None

        # Build prompt
        if context:
            prompt = f"""Context: {context}

Question: {question}

Answer:"""
        else:
            prompt = f"""You are a helpful ERPNext assistant. Answer the following question clearly and concisely.

Question: {question}

Answer:"""

        # Generate response
        response = model(
            prompt,
            max_length=max_length,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            pad_token_id=model.tokenizer.eos_token_id
        )

        # Extract generated text
        generated_text = response[0]['generated_text']

        # Remove the prompt from response
        answer = generated_text.replace(prompt, "").strip()

        # Clean up response
        if answer:
            # Take only the first paragraph
            answer = answer.split('\n\n')[0].strip()
            return answer

        return None

    except Exception as e:
        frappe.log_error(f"AI Generation Error: {str(e)}")
        return None


def get_ai_settings():
    """Get AI settings from Chatnext Settings"""
    try:
        if frappe.db.exists("Chatnext Settings", "Chatnext Settings"):
            settings = frappe.get_doc("Chatnext Settings", "Chatnext Settings")
            return settings
        return None
    except Exception as e:
        frappe.log_error(f"Error fetching AI settings: {str(e)}")
        return None


def call_openrouter_api(prompt, context=None, max_tokens=500):
    """Call OpenRouter API for AI response"""
    try:
        settings = get_ai_settings()
        if not settings or not settings.openrouter_api_key:
            return None

        messages = []
        if context:
            messages.append({
                "role": "system",
                "content": f"You are a helpful ERPNext assistant. Use this context to answer: {context}. Always respond in plain text without markdown formatting (no **, ###, ---, or bullet points)."
            })
        else:
            messages.append({
                "role": "system",
                "content": "You are a helpful ERPNext assistant. Always respond in plain text without markdown formatting (no **, ###, ---, or bullet points)."
            })
        messages.append({
            "role": "user",
            "content": prompt
        })

        headers = {
            "Authorization": f"Bearer {settings.get_password('openrouter_api_key')}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repo/chatnext",
        }

        data = {
            "model": "google/gemini-flash-1.5-8b:free",  # Free Gemini model via OpenRouter
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": settings.ai_temperature or 0.7
        }

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        return remove_markdown_formatting(result['choices'][0]['message']['content'])

    except Exception as e:
        frappe.log_error(f"OpenRouter API Error: {str(e)}")
        return None


def call_gemini_api(prompt, context=None, max_tokens=500):
    """Call Google Gemini API for AI response"""
    try:
        settings = get_ai_settings()
        if not settings or not settings.gemini_api_key:
            return None

        api_key = settings.get_password('gemini_api_key')
        url = f"{GEMINI_API_URL}?key={api_key}"

        full_prompt = prompt
        if context:
            full_prompt = f"Context: {context}\n\nQuestion: {prompt}\n\nProvide a helpful answer for ERPNext users in plain text without any markdown formatting (no **, ###, ---, or bullet points). Use simple paragraphs only."

        data = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": settings.ai_temperature or 0.7,
                "maxOutputTokens": max_tokens
            }
        }

        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        # Handle response structure - Gemini 2.5 may have thinking tokens
        candidate = result['candidates'][0]
        content = candidate.get('content', {})
        parts = content.get('parts', [])

        if parts and 'text' in parts[0]:
            return remove_markdown_formatting(parts[0]['text'])
        else:
            # Response truncated or no text generated
            return None

    except Exception as e:
        frappe.log_error(f"Gemini API Error: {str(e)}")
        return None


def call_deepseek_api(prompt, context=None, max_tokens=500):
    """Call DeepSeek API for AI response"""
    try:
        settings = get_ai_settings()
        if not settings or not settings.deepseek_api_key:
            return None

        messages = []
        if context:
            messages.append({
                "role": "system",
                "content": f"You are a helpful ERPNext assistant. Use this context: {context}. Always respond in plain text without markdown formatting (no **, ###, ---, or bullet points)."
            })
        else:
            messages.append({
                "role": "system",
                "content": "You are a helpful ERPNext assistant. Always respond in plain text without markdown formatting (no **, ###, ---, or bullet points)."
            })
        messages.append({
            "role": "user",
            "content": prompt
        })

        headers = {
            "Authorization": f"Bearer {settings.get_password('deepseek_api_key')}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": settings.ai_temperature or 0.7
        }

        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        return remove_markdown_formatting(result['choices'][0]['message']['content'])

    except Exception as e:
        frappe.log_error(f"DeepSeek API Error: {str(e)}")
        return None


def call_ollama_api(prompt, context=None, max_tokens=500):
    """Call Ollama local API for AI response"""
    try:
        settings = get_ai_settings()

        # Build full prompt with context
        full_prompt = "You are a helpful ERPNext assistant. Always respond in plain text without markdown formatting (no **, ###, ---, or bullet points).\n\n"
        if context:
            full_prompt += f"Context: {context}\n\n"
        full_prompt += f"Question: {prompt}\n\nAnswer:"

        # Ollama API format
        data = {
            "model": "llama3.2:3b",  # Fast 3B model, can be changed in settings
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": settings.ai_temperature if settings else 0.7,
                "num_predict": max_tokens
            }
        }

        response = requests.post(OLLAMA_API_URL, json=data, timeout=180)  # 3 minutes for CPU mode
        response.raise_for_status()

        result = response.json()
        return remove_markdown_formatting(result.get('response', '').strip())

    except Exception as e:
        frappe.log_error(f"Ollama API Error: {str(e)}")
        return None


def get_ai_enhanced_response(question, kb_articles, language="English"):
    """
    Get AI-enhanced response using knowledge base context
    Routes to appropriate AI provider based on settings

    Args:
        question (str): User's question
        kb_articles (list): List of relevant KB articles
        language (str): Response language

    Returns:
        dict: Response with answer, source, confidence
    """
    try:
        settings = get_ai_settings()
        if not settings or not settings.enable_ai_responses:
            return None

        # Build context from top KB articles
        context_parts = []
        for article in kb_articles[:3]:  # Use top 3 articles
            context_parts.append(f"- {article.get('title')}: {article.get('answer', '')[:300]}")

        context = "\n".join(context_parts) if context_parts else "No specific knowledge base articles found."

        # Add language instruction
        prompt = question
        if language == "Urdu":
            prompt = f"{question}\n\nPlease respond in Urdu (اردو میں جواب دیں)."

        # Route to appropriate AI provider
        ai_answer = None
        provider = settings.ai_provider or "Local (Transformers)"

        if provider == "OpenRouter":
            ai_answer = call_openrouter_api(prompt, context, settings.ai_max_tokens or 500)
        elif provider == "Google Gemini":
            ai_answer = call_gemini_api(prompt, context, settings.ai_max_tokens or 500)
        elif provider == "DeepSeek":
            ai_answer = call_deepseek_api(prompt, context, settings.ai_max_tokens or 500)
        elif provider == "Ollama (Local)":
            ai_answer = call_ollama_api(prompt, context, settings.ai_max_tokens or 500)
        else:  # Local (Transformers)
            ai_answer = generate_ai_response(prompt, context, max_length=settings.ai_max_tokens or 150)

        if ai_answer and len(ai_answer) > 20:  # Ensure meaningful response
            return {
                "answer": ai_answer,
                "source": "LLM",  # Must match Chat Message source options
                "confidence": 85 if provider != "Local (Transformers)" else 75,
                "suggestions": [a.get('title') for a in kb_articles[:3]]
            }

        return None

    except Exception as e:
        frappe.log_error(f"AI Enhanced Response Error: {str(e)}")
        return None


def is_ai_enabled():
    """
    Check if AI responses are enabled in settings

    Returns:
        bool: True if AI is enabled
    """
    try:
        # Check if Chatnext Settings exists and AI is enabled
        if frappe.db.exists("Chatnext Settings", "Chatnext Settings"):
            settings = frappe.get_doc("Chatnext Settings", "Chatnext Settings")
            return getattr(settings, 'enable_ai_responses', False)

        # Default: AI disabled (only use KB)
        return False

    except Exception:
        return False


def preload_model():
    """
    Preload AI model in background (call during server start)
    """
    try:
        get_ai_model()
        frappe.logger().info("Chatnext AI model preloaded")
    except Exception as e:
        frappe.log_error(f"AI Model Preload Error: {str(e)}")
