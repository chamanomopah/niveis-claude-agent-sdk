"""
NERO Voice Assistant - Agent Handler Module

Integration with Claude Agent SDK for processing voice prompts.
Handles hooks, tool execution, and response generation.
"""

import asyncio
from typing import Dict, List, Optional, Callable
import os
from .logger import NeroLogger


class AgentHandler:
    """Claude Agent SDK handler for NERO voice assistant."""

    def __init__(self, logger: NeroLogger, api_key_claude: Optional[str] = None):
        """Initialize Agent Handler.

        Args:
            logger: NeroLogger instance
            api_key_claude: Optional Claude API key (uses installed CLI if None)
        """
        self.logger = logger
        self.api_key_claude = api_key_claude
        self._claude_agent = None
        self._tts_callback: Optional[Callable] = None

        self.logger.debug("Agent Handler initialized")

    def set_tts_callback(self, callback: Callable) -> None:
        """Set callback function for TTS on completion.

        Args:
            callback: Async function to call with final response text
        """
        self._tts_callback = callback
        self.logger.debug("TTS callback registered")

    async def processar_prompt(
        self,
        transcricao: str,
        system_prompt: Optional[str] = None,
        locale: str = "pt-BR",
    ) -> Dict:
        """Send transcribed text to Claude Agent SDK for processing.

        Args:
            transcricao: User's transcribed prompt
            system_prompt: Optional custom system prompt
            locale: Language locale for responses (default: pt-BR)

        Returns:
            Result dict:
                {
                    'resultado': str,  # Final response text
                    'ferramentas_usadas': list,  # List of tools used
                    'custo_usd': float,  # Estimated cost
                    'sucesso': bool,
                }
        """
        if not transcricao or not transcricao.strip():
            self.logger.warning("Empty transcription provided to agent")
            return {
                "resultado": "",
                "ferramentas_usadas": [],
                "custo_usd": 0.0,
                "sucesso": False,
            }

        self.logger.agent(f"Processing prompt: '{transcricao[:100]}...'")

        try:
            # Import Claude Agent SDK
            from claude_agent_sdk import query, ClaudeAgentOptions
            from claude_agent_sdk.tools import HookMatcher

            # Set default system prompt
            if system_prompt is None:
                system_prompt = (
                    "Você é NERO, um assistente de voz inteligente em português brasileiro. "
                    "Você é prestativo, conciso e responde sempre em português do Brasil. "
                    "Quando executar tarefas, forneça respostas breves e claras, "
                    "adequadas para serem lidas em voz alta."
                )

            # Configure agent options
            options = ClaudeAgentOptions(
                system_prompt=system_prompt,
                locale=locale,
                permission_mode="auto",  # Auto-approve for voice interaction
                hooks=[self._criar_hook_finalizacao_tts()],
            )

            self.logger.debug("Sending query to Claude Agent SDK...")

            # Execute query
            response = await query(
                prompt=transcricao,
                options=options,
            )

            # Parse response
            ferramentas_usadas = []
            resultado_texto = ""

            # Extract messages and tool usage
            if hasattr(response, "messages") and response.messages:
                for message in response.messages:
                    # Check for tool use
                    if hasattr(message, "tool_use") and message.tool_use:
                        tool_name = message.tool_use.name
                        tool_input = message.tool_use.input
                        ferramentas_usadas.append({
                            "nome": tool_name,
                            "input": str(tool_input)[:100],  # Truncate for logging
                        })
                        self.logger.tool(tool_name)

                    # Extract assistant message (final response)
                    if hasattr(message, "role") and message.role == "assistant":
                        if hasattr(message, "content"):
                            resultado_texto = message.content

            # If no assistant message found, try to get result directly
            if not resultado_texto and hasattr(response, "result"):
                resultado_texto = str(response.result)

            # Fallback: convert response to string
            if not resultado_texto:
                resultado_texto = str(response)

            self.logger.complete(f"Agent response received: '{resultado_texto[:100]}...'")

            # Estimate cost (rough approximation)
            input_tokens = len(transcricao.split()) * 1.3  # Rough estimate
            output_tokens = len(resultado_texto.split()) * 1.3
            custo_estimado = (input_tokens * 3.0 + output_tokens * 15.0) / 1_000_000

            return {
                "resultado": resultado_texto,
                "ferramentas_usadas": ferramentas_usadas,
                "custo_usd": custo_estimado,
                "sucesso": True,
            }

        except ImportError as e:
            self.logger.error("Claude Agent SDK not installed. Install with: pip install claude-agent-sdk", e)
            return {
                "resultado": "Desculpe, o SDK do Claude Agent não está instalado.",
                "ferramentas_usadas": [],
                "custo_usd": 0.0,
                "sucesso": False,
            }
        except Exception as e:
            self.logger.error("Failed to process prompt with agent", e)
            return {
                "resultado": f"Desculpe, ocorreu um erro ao processar sua solicitação: {str(e)}",
                "ferramentas_usadas": [],
                "custo_usd": 0.0,
                "sucesso": False,
            }

    def _criar_hook_finalizacao_tts(self):
        """Create a Stop hook to trigger TTS on agent completion.

        Returns:
            HookMatcher configured for Stop event
        """
        from claude_agent_sdk.tools import HookMatcher

        def _on_stop(context):
            """Callback when agent completes processing."""
            self.logger.debug("Agent completion hook triggered")

            # Extract final response from context
            final_response = ""
            if hasattr(context, "messages"):
                for message in reversed(context.messages):
                    if hasattr(message, "role") and message.role == "assistant":
                        if hasattr(message, "content"):
                            final_response = message.content
                            break

            # Generate simplified summary for TTS
            resumo_tts = self._gerar_resumo_tts(final_response)

            # Call TTS callback if registered
            if self._tts_callback and resumo_tts:
                self.logger.debug("Triggering TTS callback")
                # Schedule TTS in background
                asyncio.create_task(self._tts_callback(resumo_tts))

            # Return empty dict (hook doesn't modify agent behavior)
            return {}

        # Create Stop hook
        return HookMatcher(
            hook_type="Stop",
            callback=_on_stop,
        )

    def _gerar_resumo_tts(self, texto: str) -> str:
        """Generate simplified summary for text-to-speech.

        Long responses are truncated to brief summaries suitable for voice output.

        Args:
            texto: Full response text

        Returns:
            Simplified summary for TTS
        """
        if not texto:
            return ""

        # Truncate to max 200 characters for voice
        max_chars = 200

        if len(texto) <= max_chars:
            return texto

        # Truncate at word boundary
        truncado = texto[:max_chars]
        last_space = truncado.rfind(" ")

        if last_space > max_chars * 0.8:  # If space is in last 20%
            truncado = truncado[:last_space]

        # Add ellipsis if truncated
        if len(truncado) < len(texto):
            truncado += "..."

        return truncado

    async def testar_conexao(self) -> bool:
        """Test connection to Claude Agent SDK.

        Returns:
            True if connection successful, False otherwise
        """
        self.logger.info("Testing Claude Agent SDK connection...")

        try:
            from claude_agent_sdk import query, ClaudeAgentOptions

            options = ClaudeAgentOptions(
                system_prompt="Você é NERO.",
                locale="pt-BR",
            )

            response = await query(
                prompt="Olá, responda apenas: OK",
                options=options,
            )

            self.logger.complete("Claude Agent SDK connection successful")
            return True

        except Exception as e:
            self.logger.error("Claude Agent SDK connection failed", e)
            return False
