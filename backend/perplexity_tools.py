import pathlib
import requests
import json
import logging
import os
from typing import Any, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _call_perplexity_api(
    model: str,
    request: str,
    reasoning_effort: Optional[str] = None
) -> Dict[str, Any]:
    """
    Call Perplexity API with the specified model and request.

    Args:
        model: Perplexity model name (e.g., "sonar", "sonar-pro")
        request: User query/prompt
        reasoning_effort: Optional reasoning effort level for deep-research models

    Returns:
        Full JSON response from Perplexity API

    Raises:
        ValueError: If PERPLEXITY_API_KEY is not set
        requests.RequestException: If API call fails
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError(
            "PERPLEXITY_API_KEY environment variable is not set. "
            "Please set it in your .env.local file."
        )

    url = "https://api.perplexity.ai/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": request}
        ]
    }

    # Add reasoning_effort for deep-research models
    if reasoning_effort is not None:
        payload["reasoning_effort"] = reasoning_effort

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    logger.info(f"Calling Perplexity API with model: {model}")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Perplexity API call failed: {e}")
        raise


def _extract_json_from_reasoning_response(content: str) -> Optional[Dict[str, Any]]:
    """
    Extract valid JSON from sonar-reasoning-pro response that contains <think> tags.

    The sonar-reasoning-pro model outputs a <think> section containing reasoning tokens,
    followed by a valid JSON object. This function extracts just the JSON portion.

    Args:
        content: Response content that may contain <think> tags

    Returns:
        Parsed JSON object if found, None otherwise
    """
    marker = "</think>"
    idx = content.rfind(marker)

    if idx == -1:
        # No marker found, try parsing entire content
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return None

    # Extract substring after the marker
    json_str = content[idx + len(marker):].strip()

    # Remove markdown code fence markers if present
    if json_str.startswith("```json"):
        json_str = json_str[len("```json"):].strip()
    if json_str.startswith("```"):
        json_str = json_str[3:].strip()
    if json_str.endswith("```"):
        json_str = json_str[:-3].strip()

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


def register_perplexity_tools(local_mcp_instance, json_dir: pathlib.Path):
    """Register all Perplexity search and research tools"""

    @local_mcp_instance.tool()
    def perplexity_sonar(request: str) -> str:
        """
        Fast answers with reliable search results using Perplexity Sonar.

        A lightweight, cost-effective search model optimized for quick, grounded answers
        with real-time web search. Ideal for quick searches and straightforward Q&A tasks.

        Features:
        - Non-reasoning model
        - 128K context length
        - Optimized for speed and cost
        - Real-time web search-based answers with detailed search results
        - No training on customer data

        Real-world use cases:
        - Summarizing books, TV shows, and movies
        - Looking up definitions or quick facts
        - Browsing news, sports, health, and finance content

        Parameters:
            request (str): Your search query or question

        Returns:
            str: Formatted response with file path, citations, search results, and content preview

        Example:
            perplexity_sonar(request="What is the latest news in AI research?")
        """
        logger.info(f"perplexity_sonar invoked with request: {request[:100]}...")

        try:
            # Call Perplexity API
            response = _call_perplexity_api("sonar", request)

            logger.info("Response received from Perplexity API")

            # Return JSON response directly
            return json.dumps(response, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error in perplexity_sonar: {e}")
            return json.dumps({"error": str(e)}, indent=2)

    @local_mcp_instance.tool()
    def perplexity_sonar_pro(request: str) -> str:
        """
        Advanced search with enhanced search results using Perplexity Sonar Pro.

        An advanced search model designed for complex queries, delivering deeper content
        understanding with enhanced search result accuracy and 2x more search results
        than standard Sonar.

        Features:
        - Non-reasoning model
        - 200K context length
        - Advanced information retrieval architecture
        - 2x more search results than standard Sonar
        - Real-time web search with comprehensive results
        - No training on customer data

        Real-world use cases:
        - Complex research questions requiring depth
        - Comparative analysis across multiple sources
        - Information synthesis and detailed reporting

        Parameters:
            request (str): Your search query or question (can be complex)

        Returns:
            str: Formatted response with file path, citations, search results, and content preview

        Example:
            perplexity_sonar_pro(request="Analyze the competitive positioning of AI search engines")
        """
        logger.info(f"perplexity_sonar_pro invoked with request: {request[:100]}...")

        try:
            # Call Perplexity API
            response = _call_perplexity_api("sonar-pro", request)

            logger.info("Response received from Perplexity API")

            # Return JSON response directly
            return json.dumps(response, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error in perplexity_sonar_pro: {e}")
            return json.dumps({"error": str(e)}, indent=2)

    @local_mcp_instance.tool()
    def perplexity_sonar_reasoning(request: str) -> str:
        """
        Quick reasoning with real-time search using Perplexity Sonar Reasoning.

        A reasoning-focused model that applies Chain-of-Thought (CoT) reasoning for quick
        problem-solving and structured analysis with real-time web search.

        Features:
        - Reasoning model with Chain-of-Thought (CoT) reasoning
        - 128K context length
        - Designed for quick reasoning-based tasks
        - Real-time web search with detailed search results
        - No training on customer data

        Real-world use cases:
        - Multi-step problem solving
        - Logical analysis and structured reasoning
        - Strategic planning and decision making

        Parameters:
            request (str): Your query requiring reasoning and analysis

        Returns:
            str: Formatted response with file path, citations, search results, and reasoning content

        Note:
            Image input with structured response format is not supported in reasoning models.

        Example:
            perplexity_sonar_reasoning(
                request="Analyze the impact of AI on global job markets over the next decade"
            )
        """
        logger.info(f"perplexity_sonar_reasoning invoked with request: {request[:100]}...")

        try:
            # Call Perplexity API
            response = _call_perplexity_api("sonar-reasoning", request)

            logger.info("Response received from Perplexity API")

            # Return JSON response directly
            return json.dumps(response, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error in perplexity_sonar_reasoning: {e}")
            return json.dumps({"error": str(e)}, indent=2)

    @local_mcp_instance.tool()
    def perplexity_sonar_reasoning_pro(request: str) -> str:
        """
        Advanced reasoning with enhanced multi-step analysis using Perplexity Sonar Reasoning Pro.

        A high-performance reasoning model leveraging advanced multi-step Chain-of-Thought (CoT)
        reasoning and enhanced information retrieval for complex problem-solving.

        Features:
        - Advanced reasoning model with enhanced CoT reasoning
        - 128K context length
        - Best for complex multi-step reasoning tasks
        - 2x more search results than Sonar Reasoning
        - No training on customer data

        Real-world use cases:
        - Complex multi-step analysis and reasoning
        - Advanced research with deep reasoning
        - Strategic decision making with comprehensive analysis

        Parameters:
            request (str): Your query requiring advanced reasoning and deep analysis

        Returns:
            str: Formatted response with file path, citations, search results, and reasoning content

        Note:
            - Image input with structured response format is not supported in reasoning models
            - This model outputs a <think> section with reasoning tokens before the main response
            - The saved JSON preserves the full response including reasoning tokens

        Example:
            perplexity_sonar_reasoning_pro(
                request="Analyze the feasibility of fusion energy becoming mainstream by 2040"
            )
        """
        logger.info(f"perplexity_sonar_reasoning_pro invoked with request: {request[:100]}...")

        try:
            # Call Perplexity API
            response = _call_perplexity_api("sonar-reasoning-pro", request)

            logger.info("Response received from Perplexity API")

            # Return JSON response directly
            return json.dumps(response, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error in perplexity_sonar_reasoning_pro: {e}")
            return json.dumps({"error": str(e)}, indent=2)

    @local_mcp_instance.tool()
    def perplexity_sonar_deep_research(
        request: str,
        reasoning_effort: str = "medium"
    ) -> str:
        """
        Exhaustive research with expert-level insights using Perplexity Sonar Deep Research.

        A powerful research model capable of conducting exhaustive searches across hundreds
        of sources, synthesizing expert-level insights, and generating detailed reports
        with comprehensive analysis.

        Features:
        - Deep research / Reasoning model
        - Exhaustive research across hundreds of sources
        - 128K context length
        - Expert-level subject analysis
        - Detailed report generation with comprehensive citations
        - No training on customer data

        Real-world use cases:
        - Academic research and comprehensive reports
        - Market analysis and competitive intelligence
        - Due diligence and investigative research

        Parameters:
            request (str): Your research query (should be comprehensive and detailed)
            reasoning_effort (str): Computational effort level - controls speed vs thoroughness
                - "low": Faster, simpler answers with reduced token usage
                - "medium": Balanced approach (default)
                - "high": Deeper, more thorough responses with increased token usage

        Returns:
            str: Formatted response with file path, citations, search results, and detailed analysis

        Example:
            perplexity_sonar_deep_research(
                request="Conduct comprehensive analysis of quantum computing industry through 2035",
                reasoning_effort="high"
            )
        """
        logger.info(f"perplexity_sonar_deep_research invoked with request: {request[:100]}...")
        logger.info(f"Reasoning effort: {reasoning_effort}")

        # Validate reasoning_effort parameter
        if reasoning_effort not in ["low", "medium", "high"]:
            return json.dumps({"error": f"reasoning_effort must be 'low', 'medium', or 'high', got '{reasoning_effort}'"}, indent=2)

        try:
            # Call Perplexity API with reasoning_effort parameter
            response = _call_perplexity_api("sonar-deep-research", request, reasoning_effort)

            logger.info("Response received from Perplexity API")

            # Return JSON response directly
            return json.dumps(response, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error in perplexity_sonar_deep_research: {e}")
            return json.dumps({"error": str(e)}, indent=2)
