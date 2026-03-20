import pathlib
import requests
import json
import logging
import os
import threading
import time
import uuid
from typing import Any, Dict, Optional

from request_logger import log_request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory store for async deep-research jobs
_jobs: Dict[str, Dict[str, Any]] = {}
_jobs_lock = threading.Lock()

# Auto-expire jobs older than 2 hours
_JOB_TTL_SECONDS = 7200


def _call_perplexity_api(
    model: str,
    request: str,
    reasoning_effort: Optional[str] = None,
    timeout: int = 120
) -> Dict[str, Any]:
    """
    Call Perplexity API with the specified model and request.

    Args:
        model: Perplexity model name (e.g., "sonar", "sonar-pro")
        request: User query/prompt
        reasoning_effort: Optional reasoning effort level for deep-research models
        timeout: Request timeout in seconds (default 120, use higher for deep-research)

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
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
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


def _run_deep_research_job(
    job_id: str,
    request: str,
    reasoning_effort: str,
    requests_dir: pathlib.Path,
    requester: str
) -> None:
    """Background thread worker for async deep research jobs."""
    try:
        response = _call_perplexity_api("sonar-deep-research", request, reasoning_effort, timeout=600)

        choices = response.get("choices", [])
        content = choices[0].get("message", {}).get("content", "") if choices else ""
        reasoning = choices[0].get("message", {}).get("reasoning", "") if choices else ""
        logger.info(
            f"[job={job_id}] Response received from Perplexity API: "
            f"keys={list(response.keys())}, "
            f"choices={len(choices)}, "
            f"content_len={len(content)}, "
            f"reasoning_len={len(reasoning) if reasoning else 0}, "
            f"citations={len(response.get('citations', []))}, "
            f"search_results={len(response.get('search_results', []))}, "
            f"usage={response.get('usage', {})}"
        )

        result = json.dumps(response, indent=2, ensure_ascii=False)
        logger.info(f"[job={job_id}] Result payload size: {len(result)} chars")

        log_request(
            requests_dir=requests_dir,
            requester=requester,
            tool_name="perplexity_sonar_deep_research",
            input_params={"request": request, "reasoning_effort": reasoning_effort},
            output_result=result
        )

        with _jobs_lock:
            _jobs[job_id]["status"] = "done"
            _jobs[job_id]["result"] = result
            _jobs[job_id]["finished_at"] = time.time()

    except Exception as e:
        logger.error(f"[job={job_id}] Error: {e}")
        error_result = json.dumps({"error": str(e)}, indent=2)

        log_request(
            requests_dir=requests_dir,
            requester=requester,
            tool_name="perplexity_sonar_deep_research",
            input_params={"request": request, "reasoning_effort": reasoning_effort},
            output_result=error_result
        )

        with _jobs_lock:
            _jobs[job_id]["status"] = "error"
            _jobs[job_id]["error"] = str(e)
            _jobs[job_id]["finished_at"] = time.time()


def register_perplexity_tools(local_mcp_instance, json_dir: pathlib.Path, requests_dir: pathlib.Path):
    """Register all Perplexity search and research tools"""

    @local_mcp_instance.tool()
    def perplexity_sonar(request: str, requester: str = "unknown") -> str:
        """
        Fast answers with reliable search results using Perplexity Sonar.

        A lightweight, cost-effective search model optimized for quick, grounded answers
        with real-time web search. Ideal for quick searches and straightforward Q&A tasks.
        Typical response time: 5-15 seconds.

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
            requester (str): Optional identifier of who is calling this tool (e.g., 'trading-agent', 'user-alex').
                Used for request logging and audit purposes.

        Returns:
            str: JSON response with citations, search results, and content

        Example:
            perplexity_sonar(request="What is the latest news in AI research?", requester="my-agent")
        """
        logger.info(f"perplexity_sonar invoked by {requester} with request ({len(request)} chars): {request[:200]}...")

        try:
            # Call Perplexity API
            response = _call_perplexity_api("sonar", request)

            # Log response structure for debugging
            choices = response.get("choices", [])
            content = choices[0].get("message", {}).get("content", "") if choices else ""
            logger.info(
                f"Response received from Perplexity API: "
                f"keys={list(response.keys())}, "
                f"choices={len(choices)}, "
                f"content_len={len(content)}, "
                f"citations={len(response.get('citations', []))}, "
                f"usage={response.get('usage', {})}"
            )

            # Return JSON response directly
            result = json.dumps(response, indent=2, ensure_ascii=False)
            logger.info(f"Result payload size: {len(result)} chars")

            # Log the request
            log_request(
                requests_dir=requests_dir,
                requester=requester,
                tool_name="perplexity_sonar",
                input_params={"request": request},
                output_result=result
            )

            return result

        except Exception as e:
            logger.error(f"Error in perplexity_sonar: {e}")
            error_result = json.dumps({"error": str(e)}, indent=2)

            # Log error requests too
            log_request(
                requests_dir=requests_dir,
                requester=requester,
                tool_name="perplexity_sonar",
                input_params={"request": request},
                output_result=error_result
            )

            return error_result

    @local_mcp_instance.tool()
    def perplexity_sonar_pro(request: str, requester: str = "unknown") -> str:
        """
        Advanced search with enhanced search results using Perplexity Sonar Pro.

        An advanced search model designed for complex queries, delivering deeper content
        understanding with enhanced search result accuracy and 2x more search results
        than standard Sonar. Typical response time: 10-30 seconds.

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
            requester (str): Optional identifier of who is calling this tool (e.g., 'trading-agent', 'user-alex').
                Used for request logging and audit purposes.

        Returns:
            str: JSON response with citations, search results, and content

        Example:
            perplexity_sonar_pro(request="Analyze the competitive positioning of AI search engines", requester="my-agent")
        """
        logger.info(f"perplexity_sonar_pro invoked by {requester} with request ({len(request)} chars): {request[:200]}...")

        try:
            # Call Perplexity API
            response = _call_perplexity_api("sonar-pro", request)

            # Log response structure for debugging
            choices = response.get("choices", [])
            content = choices[0].get("message", {}).get("content", "") if choices else ""
            logger.info(
                f"Response received from Perplexity API: "
                f"keys={list(response.keys())}, "
                f"choices={len(choices)}, "
                f"content_len={len(content)}, "
                f"citations={len(response.get('citations', []))}, "
                f"usage={response.get('usage', {})}"
            )

            # Return JSON response directly
            result = json.dumps(response, indent=2, ensure_ascii=False)
            logger.info(f"Result payload size: {len(result)} chars")

            # Log the request
            log_request(
                requests_dir=requests_dir,
                requester=requester,
                tool_name="perplexity_sonar_pro",
                input_params={"request": request},
                output_result=result
            )

            return result

        except Exception as e:
            logger.error(f"Error in perplexity_sonar_pro: {e}")
            error_result = json.dumps({"error": str(e)}, indent=2)

            # Log error requests too
            log_request(
                requests_dir=requests_dir,
                requester=requester,
                tool_name="perplexity_sonar_pro",
                input_params={"request": request},
                output_result=error_result
            )

            return error_result

    @local_mcp_instance.tool()
    def perplexity_sonar_deep_research(
        request: str,
        requester: str = "unknown",
        reasoning_effort: str = "medium"
    ) -> str:
        """
        Start exhaustive deep research using Perplexity Sonar Deep Research (ASYNC).

        This tool returns IMMEDIATELY with a job_id. The research runs in the background
        and typically takes 3-10 minutes. Use get_research_result(job_id) to poll for
        completion every 30 seconds.

        IMPORTANT: This tool is async by design to avoid MCP client timeouts. Do NOT
        wait for it to return results — call get_research_result() after submitting.

        Workflow:
            1. Call perplexity_sonar_deep_research(...) → get job_id
            2. Wait ~30 seconds
            3. Call get_research_result(job_id=...) → check status
            4. Repeat step 3 until status == "done"

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
            requester (str): Optional identifier of who is calling this tool.
                Used for request logging and audit purposes.
            reasoning_effort (str): Computational effort level - controls speed vs thoroughness
                - "low": Faster, simpler answers with reduced token usage
                - "medium": Balanced approach (default)
                - "high": Deeper, more thorough responses with increased token usage

        Returns:
            str: JSON with job_id and status "running". Use get_research_result(job_id) to fetch results.

        Example:
            # Step 1: start research
            perplexity_sonar_deep_research(
                request="Conduct comprehensive analysis of quantum computing industry through 2035",
                reasoning_effort="high"
            )
            # Returns: {"job_id": "a1b2c3d4", "status": "running", ...}

            # Step 2: poll after ~30s
            get_research_result(job_id="a1b2c3d4")
        """
        logger.info(
            f"perplexity_sonar_deep_research invoked by {requester} with request "
            f"({len(request)} chars): {request[:200]}..."
        )
        logger.info(f"Reasoning effort: {reasoning_effort}")

        # Validate reasoning_effort parameter
        if reasoning_effort not in ["low", "medium", "high"]:
            error_result = json.dumps({"error": f"reasoning_effort must be 'low', 'medium', or 'high', got '{reasoning_effort}'"}, indent=2)

            log_request(
                requests_dir=requests_dir,
                requester=requester,
                tool_name="perplexity_sonar_deep_research",
                input_params={"request": request, "reasoning_effort": reasoning_effort},
                output_result=error_result
            )

            return error_result

        # Generate a short unique job ID
        job_id = uuid.uuid4().hex[:8]

        with _jobs_lock:
            _jobs[job_id] = {
                "status": "running",
                "started_at": time.time(),
                "requester": requester,
                "reasoning_effort": reasoning_effort,
                "request_preview": request[:100],
            }

        # Start background thread
        thread = threading.Thread(
            target=_run_deep_research_job,
            args=(job_id, request, reasoning_effort, requests_dir, requester),
            daemon=True,
        )
        thread.start()

        logger.info(f"[job={job_id}] Background thread started")

        return json.dumps({
            "job_id": job_id,
            "status": "running",
            "message": (
                f"Deep research started (reasoning_effort={reasoning_effort}). "
                f"Typical completion: 3-10 minutes. "
                f"Poll with get_research_result(job_id='{job_id}') every 30 seconds."
            ),
            "request_preview": request[:100],
        }, indent=2)

    @local_mcp_instance.tool()
    def get_research_result(job_id: str) -> str:
        """
        Poll for the result of an async deep research job.

        Use this tool after calling perplexity_sonar_deep_research(). Returns the full
        research result when complete, or status information if still running.

        Job results are kept in memory for 2 hours after completion, then auto-expired.

        Parameters:
            job_id (str): The job ID returned by perplexity_sonar_deep_research()

        Returns:
            str: JSON with one of:
                - status "running": {"job_id", "status", "elapsed_seconds", "message"}
                - status "done": Full Perplexity API response JSON (same format as sonar/sonar-pro)
                - status "error": {"job_id", "status", "error"}
                - not found: {"error": "Job not found..."}

        Example:
            get_research_result(job_id="a1b2c3d4")
        """
        now = time.time()

        with _jobs_lock:
            # Clean up expired jobs
            expired = [
                jid for jid, j in _jobs.items()
                if now - j.get("started_at", now) > _JOB_TTL_SECONDS
            ]
            for jid in expired:
                logger.info(f"[job={jid}] Expired, removing from store")
                del _jobs[jid]

            job = _jobs.get(job_id)

        if job is None:
            return json.dumps({
                "error": f"Job '{job_id}' not found. It may have expired (TTL: {_JOB_TTL_SECONDS // 3600}h) or never existed."
            }, indent=2)

        status = job["status"]
        elapsed = int(now - job["started_at"])

        if status == "running":
            logger.info(f"[job={job_id}] Still running ({elapsed}s elapsed)")
            return json.dumps({
                "job_id": job_id,
                "status": "running",
                "elapsed_seconds": elapsed,
                "message": f"Still running ({elapsed}s elapsed). Check back in 30 seconds.",
                "request_preview": job.get("request_preview", ""),
            }, indent=2)

        if status == "done":
            logger.info(f"[job={job_id}] Done, returning result (elapsed={elapsed}s)")
            return job["result"]  # Already serialized JSON string

        # status == "error"
        logger.info(f"[job={job_id}] Returning error result")
        return json.dumps({
            "job_id": job_id,
            "status": "error",
            "error": job.get("error", "Unknown error"),
            "elapsed_seconds": elapsed,
        }, indent=2)
