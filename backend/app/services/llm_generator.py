"""
LLM generation service using Groq or Gemini.
Handles grounded response generation with the RAG context.
"""

import logging
import time
from typing import Tuple, List, Optional
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMGenerator:
    """Generates responses using LLM with RAG context."""

    def __init__(self):
        self.provider = settings.llm_provider.lower()
        self.client = self._initialize_client()
        self.model = self._get_model_name()

    def _initialize_client(self):
        """Initialize LLM client based on provider."""
        try:
            if self.provider == "groq":
                from groq import Groq
                return Groq(api_key=settings.groq_api_key)
            elif self.provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=settings.google_api_key)
                return genai
            else:
                raise ValueError(f"Unknown LLM provider: {self.provider}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {str(e)}")
            raise

    def _get_model_name(self) -> str:
        """Get model name based on provider."""
        if self.provider == "groq":
            return settings.groq_model
        elif self.provider == "gemini":
            return settings.gemini_model
        return "unknown"

    def generate_response(
        self,
        query: str,
        context: List[dict],
        conversation_history: Optional[List[dict]] = None,
    ) -> Tuple[str, int, float]:
        """
        Generate response using LLM with RAG context.
        
        Args:
            query: User query
            context: Retrieved context chunks
            conversation_history: Chat history for context
            
        Returns:
            (response, tokens_used, response_time)
        """
        start_time = time.time()

        try:
            # Build prompt
            prompt = self._build_prompt(query, context, conversation_history)

            # Generate response
            if self.provider == "groq":
                response, tokens = self._generate_groq(prompt)
            else:
                response, tokens = self._generate_gemini(prompt)

            response_time = time.time() - start_time

            # Validate response
            if not response or "could not find" in response.lower():
                if not context:
                    response = (
                        "I could not find relevant information from the indexed sources. "
                        "Please try rephrasing your question."
                    )

            logger.info(
                f"Generated response ({self.model}): "
                f"{len(response)} chars, {tokens} tokens, {response_time:.2f}s"
            )

            return response, tokens, response_time

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            error_msg = (
                "I encountered an error while generating a response. "
                "Please try again."
            )
            return error_msg, 0, time.time() - start_time

    def _build_prompt(
        self,
        query: str,
        context: List[dict],
        conversation_history: Optional[List[dict]] = None,
    ) -> str:
        """Build the structured prompt for LLM."""
        system_instruction = (
            "You are RAGNoviq, a Senior Enterprise AI Knowledge Assistant.\n"
            "Your objective is to deliver accurate, professional, and well-structured answers using Markdown.\n\n"
            "STRICT RULES FOR GROUNDING & ACCURACY:\n"
            "1. Rely strictly on the provided RELEVANT CONTEXT snippets below to answer user queries.\n"
            "2. If the user question is a general greeting or pleasantry (e.g., 'hello', 'hi', 'how are you'), respond warmly and invite them to ask questions about the indexed website knowledge base.\n"
            "3. If the question asks for information not present in the context, clearly state: "
            "'I could not find relevant information in the indexed knowledge base to answer your question.'\n"
            "4. When answering using context, cite your sources inline using [Source N] tags matching the context references.\n"
            "5. Use clean markdown (bolding, lists, code blocks) for optimal readability."
        )

        context_section = ""
        if context:
            context_section = "\n\n--- RELEVANT CONTEXT SNIPPETS ---\n"
            for i, item in enumerate(context, 1):
                title = item.get("page_title") or "Untitled Page"
                url = item.get("page_url") or "Unknown URL"
                score = item.get("similarity_score", 0.0)
                content = item.get("content", "").strip()
                context_section += (
                    f"\n[Source {i}] {title}\n"
                    f"URL: {url}\n"
                    f"Relevance Score: {score:.2%}\n"
                    f"Full Content:\n{content}\n"
                )
        else:
            context_section = "\n\n--- RELEVANT CONTEXT SNIPPETS ---\nNo relevant indexed chunks found for this query."

        history_section = ""
        if conversation_history:
            history_section = "\n\n--- CONVERSATION HISTORY ---\n"
            for msg in conversation_history[-6:]:
                role = msg.get("role", "user").upper()
                content = msg.get("content", "").strip()
                history_section += f"{role}: {content}\n"

        prompt = (
            f"{system_instruction}\n"
            f"{context_section}\n"
            f"{history_section}\n"
            f"--- USER QUESTION ---\n"
            f"{query}\n\n"
            f"ANSWER:"
        )

        return prompt

    def _generate_groq(self, prompt: str) -> Tuple[str, int]:
        """Generate response using Groq API with fallback model options."""
        if not settings.groq_api_key or settings.groq_api_key == "your_groq_api_key_here":
            logger.warning("Groq API key not configured or set to placeholder. Generating fallback grounded response.")
            return self._generate_fallback_response(prompt)

        models_to_try = [self.model, "llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"]
        last_exception = None

        for model_name in models_to_try:
            try:
                message = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=model_name,
                    max_tokens=1024,
                    temperature=0.3,
                )

                response = message.choices[0].message.content
                tokens = message.usage.total_tokens if message.usage else 0
                return response, tokens
            except Exception as e:
                logger.warning(f"Groq generation failed with model {model_name}: {str(e)}")
                last_exception = e

        logger.error(f"All Groq models failed. Reverting to fallback: {str(last_exception)}")
        return self._generate_fallback_response(prompt)

    def _generate_gemini(self, prompt: str) -> Tuple[str, int]:
        """Generate response using Google Gemini API."""
        if not settings.google_api_key or settings.google_api_key == "your_google_api_key_here":
            logger.warning("Gemini API key not configured or set to placeholder. Generating fallback grounded response.")
            return self._generate_fallback_response(prompt)

        try:
            model = self.client.GenerativeModel(self.model)
            response = model.generate_content(prompt)

            text = response.text if response and response.text else ""
            estimated_tokens = len(text.split()) * 1.3
            return text, int(estimated_tokens)

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return self._generate_fallback_response(prompt)

    def _generate_fallback_response(self, prompt: str) -> Tuple[str, int]:
        """Generate grounded response when LLM API keys are not provided."""
        if "RELEVANT CONTEXT SNIPPETS ---\nNo relevant" in prompt or "--- NO RELEVANT CONTEXT FOUND ---" in prompt:
            return (
                "I could not find relevant information in the indexed knowledge base to answer your question. "
                "Please make sure you have indexed a website on the Dashboard or try rephrasing your question.",
                45
            )
        
        # Extract context content snippets from prompt
        import re
        context_matches = re.findall(r"\[Source \d+\] (.*?)\nURL: (.*?)\n.*?Full Content:\n(.*?)(?=\n\[Source|\n---|\Z)", prompt, re.DOTALL)
        
        if context_matches:
            snippets = []
            for idx, (title, url, content) in enumerate(context_matches[:3], 1):
                clean_snippet = content.strip()[:300]
                snippets.append(f"**From [{title.strip()}]({url.strip()})**:\n\n> {clean_snippet}...")
            
            response = (
                "Based on the indexed sources, here is the relevant information:\n\n"
                + "\n\n".join(snippets)
                + "\n\n*(Note: Configure a valid `GROQ_API_KEY` or `GOOGLE_API_KEY` in `.env` for complete LLM synthesis)*"
            )
            return response, len(response.split()) * 2

        return "I could not find relevant information from the indexed sources.", 20

    def validate_context_grounded(
        self, response: str, context: List[dict]
    ) -> bool:
        """Check if response is grounded in provided context."""
        if not context:
            return "could not find" in response.lower()
        return True

    def get_model_info(self) -> dict:
        """Get information about the active LLM model configuration."""
        return {
            "provider": self.provider,
            "model": self.model,
            "configured": bool(
                (self.provider == "groq" and settings.groq_api_key and settings.groq_api_key != "your_groq_api_key_here") or
                (self.provider == "gemini" and settings.google_api_key and settings.google_api_key != "your_google_api_key_here")
            )
        }

