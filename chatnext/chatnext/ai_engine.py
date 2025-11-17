"""
AI Engine for Chatnext
Integrates local AI models (Hugging Face Transformers) for intelligent responses
"""

import frappe
from transformers import pipeline
import os

# Global model cache
_model_cache = None
_model_name = "facebook/opt-125m"  # Small, fast model (125M parameters, ~250MB)


def get_ai_model():
    """
    Get or initialize the AI model
    Uses a lightweight model that auto-downloads on first use
    """
    global _model_cache

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


def get_ai_enhanced_response(question, kb_articles, language="English"):
    """
    Get AI-enhanced response using knowledge base context

    Args:
        question (str): User's question
        kb_articles (list): List of relevant KB articles
        language (str): Response language

    Returns:
        dict: Response with answer, source, confidence
    """
    try:
        # Build context from top KB articles
        context_parts = []
        for article in kb_articles[:2]:  # Use top 2 articles
            context_parts.append(f"- {article.get('title')}: {article.get('answer', '')[:200]}")

        context = "\n".join(context_parts) if context_parts else None

        # Generate AI response
        ai_answer = generate_ai_response(question, context, max_length=150)

        if ai_answer and len(ai_answer) > 20:  # Ensure meaningful response
            return {
                "answer": ai_answer,
                "source": "AI Assistant",
                "confidence": 75,
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
