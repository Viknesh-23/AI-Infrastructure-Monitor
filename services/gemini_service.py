"""Gemini-powered recommendations with dependable local rule-based fallback."""

import json
import os


def _fallback(values):
    causes = []
    steps = []
    if values["cpu_usage"] >= 80:
        causes.append("sustained CPU saturation")
        steps.append("Inspect running processes and identify CPU-intensive applications.")
    if values["memory_usage"] >= 80:
        causes.append("memory pressure or a possible memory leak")
        steps.append("Review memory consumers and restart only the affected memory-intensive service.")
    if values["disk_usage"] >= 85:
        causes.append("low free disk capacity")
        steps.append("Clean unneeded files, rotate logs, and investigate unexpected disk growth.")
    if values["network_latency"] >= 150 or values["response_time"] >= 900:
        causes.append("network congestion or a slow downstream dependency")
        steps.append("Check connectivity, DNS, packet loss, and latency to dependent services.")
    if values["error_rate"] >= 3:
        causes.append("elevated application or API errors")
        steps.append("Review recent application logs, error traces, and recent deployments.")
    if not causes:
        causes.append("an unusual performance pattern")
        steps.append("Compare the metric trend with recent deployments and scheduled jobs.")
    return {
        "root_cause": "Probable cause: " + "; ".join(causes) + ".",
        "recommendation": " ".join(steps)
        + " Prevent recurrence by setting capacity and latency alerts before warning thresholds are reached.",
    }


def get_ai_analysis(server, values, risk, severity):
    """Ask Gemini when configured; otherwise return useful deterministic guidance."""
    fallback = _fallback(values)
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return fallback

    try:
        from google import genai

        prompt = f"""You are an SRE assistant. Analyse this simulated server incident.
Server: {server.name} ({server.operating_system}, {server.environment})
Severity: {severity}; failure risk: {risk}%
Metrics: CPU {values['cpu_usage']}%, memory {values['memory_usage']}%, disk {values['disk_usage']}%, latency {values['network_latency']}ms, error rate {values['error_rate']}%, response time {values['response_time']}ms.
Return only a JSON object with exactly these string keys: "root_cause" and "recommendation". Give concise, safe diagnostic steps and do not claim certainty."""
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        text = (response.text or "").strip()
        if not text:
            return fallback
        # Some proxies wrap JSON in a Markdown fence despite the MIME hint.
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        data = json.loads(text)
        root_cause = str(data.get("root_cause", "")).strip()
        recommendation = str(data.get("recommendation", "")).strip()
        if not root_cause or not recommendation:
            return fallback
        return {"root_cause": root_cause, "recommendation": recommendation}
    except Exception:
        return fallback
