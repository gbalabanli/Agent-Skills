from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPCookieProcessor, Request, build_opener, urlopen


OVERALL_URL = "https://api.aidetector.com/api/v1/detect/overall"
SENTENCE_STREAM_URL = "https://api.aidetector.com/api/v1/detect/sentences/stream"
SITE_ORIGIN = "https://aidetector.com"
SITE_REFERER = "https://aidetector.com/"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/145.0.0.0 Safari/537.36"
)
QUILLBOT_ORIGIN = "https://quillbot.com"
QUILLBOT_PAGE_URL = "https://quillbot.com/ai-content-detector"
QUILLBOT_SPAM_CHECK_URL = "https://quillbot.com/api/auth/spam-check"
QUILLBOT_SCORE_URL = "https://quillbot.com/api/ai-detector/score"
SCRIBBR_ORIGIN = "https://quillbot.scribbr.com"
SCRIBBR_PAGE_URL = (
    "https://quillbot.scribbr.com/ai-content-detector"
    "?independentTool=true&language=en&partnerCompany=scribbr"
    "&initialInputLanguage=en&enableUpsell=true&fullScreen=true&hideCautionBox=true"
)
SCRIBBR_SPAM_CHECK_URL = "https://quillbot.scribbr.com/api/auth/spam-check"
SCRIBBR_SCORE_URL = "https://quillbot.scribbr.com/api/ai-detector/score"

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
WORD_RE = re.compile(r"\b[\w'-]+\b")


class AnalysisError(RuntimeError):
    """Raised when the remote detector cannot be queried successfully."""


@dataclass
class ApiResponse:
    data: dict[str, Any]
    headers: dict[str, str]


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _split_sentences(text: str) -> list[str]:
    cleaned = _normalize_text(text)
    if not cleaned:
        return []
    return [sentence.strip() for sentence in SENTENCE_SPLIT.split(cleaned) if sentence.strip()]


def _verdict(score: float) -> str:
    if score >= 70:
        return "Likely AI"
    if score >= 40:
        return "Mixed"
    return "Likely Human"


def _confidence_score(label: str) -> int:
    mapping = {
        "high": 85,
        "medium": 60,
        "low": 35,
    }
    return mapping.get(label.lower(), 0)


def _request_headers(accept: str) -> dict[str, str]:
    return {
        "Origin": SITE_ORIGIN,
        "Referer": SITE_REFERER,
        "Accept": accept,
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }


def _quillbot_headers(origin: str, referer: str, accept: str) -> dict[str, str]:
    return {
        "Origin": origin,
        "Referer": referer,
        "Accept": accept,
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }


def _post_json(url: str, payload: dict[str, Any], accept: str) -> ApiResponse:
    body = json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers=_request_headers(accept), method="POST")

    try:
        with urlopen(request, timeout=25) as response:
            raw = response.read().decode("utf-8")
            headers = {key.lower(): value for key, value in response.headers.items()}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise AnalysisError(f"AiDetector request failed with status {exc.code}: {detail}") from exc
    except URLError as exc:
        raise AnalysisError(f"AiDetector request failed: {exc.reason}") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AnalysisError("AiDetector returned invalid JSON.") from exc

    return ApiResponse(data=data, headers=headers)


def _quillbot_detector_score(
    text: str,
    source_name: str,
    origin: str,
    page_url: str,
    spam_check_url: str,
    score_url: str,
) -> dict[str, Any]:
    opener = build_opener(HTTPCookieProcessor())
    page_request = Request(
        page_url,
        headers={"User-Agent": USER_AGENT, "Referer": page_url, "Origin": origin},
        method="GET",
    )
    spam_request = Request(
        spam_check_url,
        headers={"User-Agent": USER_AGENT, "Referer": page_url, "Origin": origin},
        method="GET",
    )

    try:
        with opener.open(page_request, timeout=25):
            pass
        with opener.open(spam_request, timeout=25):
            pass

        payload = json.dumps({"text": text, "language": "en", "explain": False}).encode("utf-8")
        score_request = Request(
            score_url,
            data=payload,
            headers=_quillbot_headers(origin, page_url, "application/json"),
            method="POST",
        )
        with opener.open(score_request, timeout=25) as response:
            raw = response.read().decode("utf-8")
            headers = {key.lower(): value for key, value in response.headers.items()}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise AnalysisError(f"{source_name} request failed with status {exc.code}: {detail}") from exc
    except URLError as exc:
        raise AnalysisError(f"{source_name} request failed: {exc.reason}") from exc

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AnalysisError(f"{source_name} returned invalid JSON.") from exc

    value = parsed.get("data", {}).get("value", {})
    chunks = value.get("chunks", [])
    ai_score = round(float(value.get("aiScore", 0.0)) * 100, 1)
    human_paraphrased = round(float(value.get("humanParaphrasedScore", 0.0)) * 100, 1)
    ai_paraphrased = round(float(value.get("aiParaphrasedScore", 0.0)) * 100, 1)

    return {
        "score": ai_score,
        "human_paraphrased_score": human_paraphrased,
        "ai_paraphrased_score": ai_paraphrased,
        "verdict": _verdict(ai_score),
        "model_version": value.get("modelVersion"),
        "model_id": value.get("modelID"),
        "report_id": value.get("id"),
        "timed_out": bool(parsed.get("data", {}).get("timedOut", False)),
        "rate_limit_remaining": headers.get("x-retry-remaining"),
        "chunks": [
            {
                "text": chunk.get("text", ""),
                "type": chunk.get("type", ""),
                "ai_probability": round(float(chunk.get("aiScore", 0.0)) * 100, 1),
                "human_paraphrased_probability": round(float(chunk.get("humanParaphrasedScore", 0.0)) * 100, 1),
                "ai_paraphrased_probability": round(float(chunk.get("aiParaphrasedScore", 0.0)) * 100, 1),
                "is_failed": bool(chunk.get("isFailed", False)),
            }
            for chunk in chunks
        ],
    }


def _quillbot_score(text: str) -> dict[str, Any]:
    return _quillbot_detector_score(
        text=text,
        source_name="QuillBot",
        origin=QUILLBOT_ORIGIN,
        page_url=QUILLBOT_PAGE_URL,
        spam_check_url=QUILLBOT_SPAM_CHECK_URL,
        score_url=QUILLBOT_SCORE_URL,
    )


def _scribbr_score(text: str) -> dict[str, Any]:
    return _quillbot_detector_score(
        text=text,
        source_name="Scribbr",
        origin=SCRIBBR_ORIGIN,
        page_url=SCRIBBR_PAGE_URL,
        spam_check_url=SCRIBBR_SPAM_CHECK_URL,
        score_url=SCRIBBR_SCORE_URL,
    )


def _post_sse(url: str, payload: dict[str, Any]) -> ApiResponse:
    body = json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers=_request_headers("text/event-stream"), method="POST")

    try:
        with urlopen(request, timeout=25) as response:
            raw = response.read().decode("utf-8")
            headers = {key.lower(): value for key, value in response.headers.items()}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise AnalysisError(f"AiDetector sentence request failed with status {exc.code}: {detail}") from exc
    except URLError as exc:
        raise AnalysisError(f"AiDetector sentence request failed: {exc.reason}") from exc

    return ApiResponse(data={"stream": raw}, headers=headers)


def _parse_sentence_stream(raw_stream: str) -> list[dict[str, Any]]:
    sentences: list[dict[str, Any]] = []
    current_event = ""

    for line in raw_stream.splitlines():
        if not line:
            continue
        if line.startswith("event:"):
            current_event = line.partition(":")[2].strip()
            continue
        if not line.startswith("data:"):
            continue

        payload = line.partition(":")[2].strip()
        if current_event != "sentence" or payload == "{}":
            continue

        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            continue

        ai_probability = float(parsed.get("ai_probability", 0.0))
        sentences.append(
            {
                "index": int(parsed.get("index", len(sentences))),
                "text": parsed.get("text", ""),
                "ai_probability": round(ai_probability, 1),
                "verdict": _verdict(ai_probability),
                "reason": parsed.get("reason", ""),
            }
        )

    return sentences


def analyze_text(text: str, include_partners: bool = True) -> dict[str, Any]:
    normalized = _normalize_text(text)
    sentences = _split_sentences(normalized)
    word_count = len(WORD_RE.findall(normalized))

    if word_count == 0:
        return {
            "source": "AiDetector.com",
            "score": 0,
            "human_score": 0,
            "verdict": "No text",
            "confidence_label": "None",
            "confidence_score": 0,
            "word_count": 0,
            "sentence_count": 0,
            "summary": "Paste text to fetch a live score from AiDetector.com.",
            "notes": ["No text submitted."],
            "sentences": [],
            "report_id": None,
            "expires_at": None,
            "model_used": None,
            "rate_limit_remaining": None,
            "quillbot": None,
            "scribbr": None,
        }

    payload = {"text": normalized}

    try:
        overall_response = _post_json(OVERALL_URL, payload, "application/json")
        sentence_response = _post_sse(SENTENCE_STREAM_URL, payload)
    except AnalysisError as exc:
        return {
            "source": "AiDetector.com",
            "score": 0,
            "human_score": 0,
            "verdict": "Unavailable",
            "confidence_label": "Unavailable",
            "confidence_score": 0,
            "word_count": word_count,
            "sentence_count": len(sentences),
            "summary": "Live detector request failed.",
            "notes": [str(exc)],
            "sentences": [],
            "report_id": None,
            "expires_at": None,
            "model_used": None,
            "rate_limit_remaining": None,
            "quillbot": None,
            "scribbr": None,
        }

    result = overall_response.data.get("result", {})
    meta = overall_response.data.get("meta", {})
    ai_probability = round(float(result.get("ai_probability", 0.0)), 1)
    human_probability = round(float(result.get("human_probability", 0.0)), 1)
    confidence_label = str(result.get("confidence_level", "Unknown"))
    sentence_rows = _parse_sentence_stream(sentence_response.data.get("stream", ""))

    notes = [
        "Live result fetched from AiDetector.com public web endpoint.",
        "This reflects the external detector's model output, not a local heuristic.",
    ]

    rate_limit_remaining = overall_response.headers.get("x-ratelimit-remaining")
    if rate_limit_remaining:
        notes.append(f"AiDetector rate-limit remaining for this session: {rate_limit_remaining}.")

    quillbot_result = None
    scribbr_result = None
    if include_partners:
        try:
            quillbot_result = _quillbot_score(normalized)
            if quillbot_result.get("rate_limit_remaining"):
                notes.append(
                    "QuillBot rate-limit remaining for this session: "
                    f"{quillbot_result['rate_limit_remaining']}."
                )
        except AnalysisError as exc:
            notes.append(str(exc))

        try:
            scribbr_result = _scribbr_score(normalized)
            if scribbr_result.get("rate_limit_remaining"):
                notes.append(
                    "Scribbr rate-limit remaining for this session: "
                    f"{scribbr_result['rate_limit_remaining']}."
                )
        except AnalysisError as exc:
            notes.append(str(exc))

    return {
        "source": "AiDetector.com",
        "score": ai_probability,
        "human_score": human_probability,
        "verdict": _verdict(ai_probability),
        "confidence_label": confidence_label,
        "confidence_score": _confidence_score(confidence_label),
        "word_count": word_count,
        "sentence_count": len(sentences),
        "summary": result.get("analysis_summary", "No summary returned."),
        "notes": notes,
        "sentences": sentence_rows,
        "report_id": meta.get("report_id"),
        "expires_at": meta.get("expires_at"),
        "model_used": meta.get("model_used"),
        "rate_limit_remaining": rate_limit_remaining,
        "quillbot": quillbot_result,
        "scribbr": scribbr_result,
    }


if __name__ == "__main__":
    import sys

    sample = sys.stdin.read()
    print(json.dumps(analyze_text(sample), indent=2))
