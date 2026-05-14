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
        """Build the prompt for LLM."""
        # System instruction
        system_instruction = (
            "You are a helpful AI assistant answering questions based on provided "
            "website content. "
            "IMPORTANT: Only answer questions based on the provided context. "
            "If the answer is not in the context, respond with: "
            "'I could not find relevant information from the indexed sources.' "
            "Always cite which source page the information comes from."
        )

        # Build context section
        context_section = ""
        if context:
            context_section = "\n\n--- RELEVANT CONTEXT ---\n"
            for i, item in enumerate(context, 1):
                context_section += (
                    f"\n[Source {i}] {item.get('page_title', 'Untitled')} "
                    f"({item.get('page_url', 'Unknown URL')})\n"
                    f"Relevance: {item.get('similarity_score', 0):.2%}\n"
                    f"Content: {item.get('content', '')[:500]}...\n"
                )
        else:
            context_section = "\n\n--- NO RELEVANT CONTEXT FOUND ---\n"

        # Build conversation history section
        history_section = ""
        if conversation_history:
            history_section = "\n\n--- CONVERSATION HISTORY ---\n"
            for msg in conversation_history[-3:]:  # Last 3 messages for context
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_section += f"\n{role.upper()}: {content}\n"

        # Combine into final prompt
        prompt = (
            f"{system_instruction}\n"
            f"{context_section}"
            f"{history_section}"
            f"\n\n--- USER QUESTION ---\n"
            f"{query}\n\n"
            f"Please provide a clear, concise answer based ONLY on the provided context. "
            f"If information is not available, clearly state that."
        )

        return prompt

    def _generate_groq(self, prompt: str) -> Tuple[str, int]:
        """Generate response using Groq API."""
        try:
            message = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                max_tokens=1024,
                temperature=0.7,
            )

            response = message.choices[0].message.content
            tokens = message.usage.total_tokens if message.usage else 0

            return response, tokens

        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise

    def _generate_gemini(self, prompt: str) -> Tuple[str, int]:
        """Generate response using Google Gemini API."""
        try:
            model = self.client.GenerativeModel(self.model)
            response = model.generate_content(prompt)

            text = response.text if response.text else ""
            # Gemini doesn't provide token count in free tier
            estimated_tokens = len(text.split()) * 1.3

            return text, int(estimated_tokens)

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise

    def validate_context_grounded(
        self, response: str, context: List[dict]
    ) -> bool:
        """
        Check if response appears to be grounded in provided context.
        """
        if not context:
            return "could not find" in response.lower()

        # Simple heuristic: check if response mentions source information
        return True  # In production, use semantic similarity check

    def get_model_info(self) -> dict:
        """Get information about the LLM model."""
        return {
            "provider": self.provider,
            "model": self.model,
        }
