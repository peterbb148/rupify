"""Executable interview harness for the SpecOps interview flow."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any


def _normalize_key(value: str) -> str:
    """Normalize a human label into a snake_case key.

    Args:
        value: Source label.

    Returns:
        Normalized key.
    """
    normalized = []
    for char in value.strip().lower():
        if char.isalnum():
            normalized.append(char)
        else:
            normalized.append("_")
    result = "".join(normalized).strip("_")
    while "__" in result:
        result = result.replace("__", "_")
    return result


def _parse_block_answer(text: str) -> dict[str, Any]:
    """Parse a simple key/value interview answer block.

    Supports:
    - `Key: value`
    - bullet lines under a previous key

    Args:
        text: Raw answer text.

    Returns:
        Parsed answer mapping.
    """
    parsed: dict[str, Any] = {}
    current_key: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if ":" in line and not line.startswith("- "):
            label, value = line.split(":", 1)
            current_key = _normalize_key(label)
            stripped_value = value.strip()
            if stripped_value:
                parsed[current_key] = stripped_value
            else:
                parsed[current_key] = []
            continue

        if line.startswith("- ") and current_key:
            if not isinstance(parsed[current_key], list):
                parsed[current_key] = [parsed[current_key]]
            parsed[current_key].append(line[2:].strip())
            continue

        if current_key:
            current_value = parsed[current_key]
            if isinstance(current_value, list):
                current_value.append(line)
            elif current_value:
                parsed[current_key] = f"{current_value} {line}".strip()
            else:
                parsed[current_key] = line

    return parsed


@dataclass(frozen=True)
class InterviewQuestion:
    """Definition of one question within an interview round."""

    key: str
    label: str
    prompt: str


@dataclass(frozen=True)
class InterviewRound:
    """Definition of a SpecOps interview round."""

    number: int
    title: str
    prompt: str
    template: str
    questions: tuple[InterviewQuestion, ...]


ROUND_DEFINITIONS: list[InterviewRound] = [
    InterviewRound(
        number=1,
        title="Problem and Scope",
        prompt=(
            "Capture the software idea, the core problem, who it is for, and the first-release "
            "scope boundary."
        ),
        template=(
            "Idea:\nProblem:\nUsers:\nIn scope:\nOut of scope:\n"
        ),
        questions=(
            InterviewQuestion("idea", "Idea", "What software idea are we talking about?"),
            InterviewQuestion("problem", "Problem", "What problem does it solve?"),
            InterviewQuestion("users", "Users", "Who is it for?"),
            InterviewQuestion("in_scope", "In scope", "What is in scope for the first version?"),
            InterviewQuestion(
                "out_of_scope",
                "Out of scope",
                "What is explicitly out of scope for the first version?",
            ),
        ),
    ),
    InterviewRound(
        number=2,
        title="Outcomes and Constraints",
        prompt=(
            "Capture business outcomes, success criteria, required data, and important constraints."
        ),
        template=(
            "Outcomes:\nSuccess criteria:\nRequired data:\nConstraints:\n"
        ),
        questions=(
            InterviewQuestion("outcomes", "Outcomes", "What business outcomes do you want?"),
            InterviewQuestion(
                "success_criteria",
                "Success criteria",
                "How will you know this system is successful?",
            ),
            InterviewQuestion(
                "required_data",
                "Required data",
                "What data must be tracked?",
            ),
            InterviewQuestion(
                "constraints",
                "Constraints",
                "What important constraints already exist?",
            ),
        ),
    ),
    InterviewRound(
        number=3,
        title="Actors and Use Cases",
        prompt="Capture the main actors, top use cases, and key integrations.",
        template="Actors:\nUse cases:\nIntegrations:\n",
        questions=(
            InterviewQuestion("actors", "Actors", "Who uses or interacts with the system?"),
            InterviewQuestion("use_cases", "Use cases", "What are the main things they need to do?"),
            InterviewQuestion(
                "integrations",
                "Integrations",
                "What external systems or integrations matter in V1?",
            ),
        ),
    ),
    InterviewRound(
        number=4,
        title="Requirements",
        prompt=(
            "Capture workflow scope, key metadata fields, and non-functional requirements."
        ),
        template="Workflow scope:\nMetadata fields:\nNon-functional requirements:\n",
        questions=(
            InterviewQuestion(
                "workflow_scope",
                "Workflow scope",
                "What workflow actions must V1 support?",
            ),
            InterviewQuestion(
                "metadata_fields",
                "Metadata fields",
                "What metadata fields are most important per system?",
            ),
            InterviewQuestion(
                "non_functional_requirements",
                "Non-functional requirements",
                "What key non-functional requirements apply?",
            ),
        ),
    ),
    InterviewRound(
        number=5,
        title="UCP Actor Complexity",
        prompt=(
            "Capture actor complexity using simple/average/complex after discovery is stable."
        ),
        template="Actor complexity:\n- Actor A: simple/average/complex\n",
        questions=(
            InterviewQuestion(
                "actor_complexity",
                "Actor complexity",
                "How should each actor be classified for UCP?",
            ),
        ),
    ),
    InterviewRound(
        number=6,
        title="UCP Use-Case Complexity",
        prompt="Capture use-case complexity using simple/average/complex.",
        template="Use-case complexity:\n- Use case A: simple/average/complex\n",
        questions=(
            InterviewQuestion(
                "use_case_complexity",
                "Use-case complexity",
                "How should each use case be classified for UCP?",
            ),
        ),
    ),
    InterviewRound(
        number=7,
        title="UCP Technical Factors",
        prompt="Capture the technical 0-5 influence scores in a compact block.",
        template=(
            "Technical:\n"
            "distributed system:\nresponse time:\nend-user efficiency:\n"
            "complex internal processing:\nreusability:\nease of installation:\n"
        ),
        questions=(
            InterviewQuestion(
                "technical",
                "Technical",
                "What technical 0-5 influence scores apply?",
            ),
        ),
    ),
    InterviewRound(
        number=8,
        title="UCP Environmental Factors",
        prompt="Capture the environmental 0-5 influence scores in a compact block.",
        template=(
            "Environmental:\nteam familiarity:\napplication experience:\n"
            "architecture experience:\nanalyst capability:\nmotivation:\n"
        ),
        questions=(
            InterviewQuestion(
                "environmental",
                "Environmental",
                "What environmental 0-5 scores apply?",
            ),
        ),
    ),
]


def get_round(number: int) -> InterviewRound:
    """Return a round definition.

    Args:
        number: Round number.

    Returns:
        Interview round definition.

    Raises:
        ValueError: If the round number does not exist.
    """
    for round_definition in ROUND_DEFINITIONS:
        if round_definition.number == number:
            return round_definition
    raise ValueError(f"Unknown interview round: {number}")


def next_round(number: int) -> InterviewRound | None:
    """Return the next round definition if one exists."""
    if number >= len(ROUND_DEFINITIONS):
        return None
    return get_round(number + 1)


def _round_payload(round_definition: InterviewRound) -> dict[str, Any]:
    """Serialize a round definition for CLI output."""
    return {
        "number": round_definition.number,
        "title": round_definition.title,
        "prompt": round_definition.prompt,
        "template": round_definition.template,
        "questions": [
            {
                "key": question.key,
                "label": question.label,
                "prompt": question.prompt,
            }
            for question in round_definition.questions
        ],
    }


def _stringify_response_value(value: Any) -> str:
    """Render a response value into text for replay and parsing."""
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value)
    return str(value).strip()


def _coerce_round_answer(number: int, item: dict[str, Any]) -> tuple[str, list[dict[str, str]]]:
    """Convert replay input into canonical answer text and response items."""
    if "responses" in item:
        round_definition = get_round(number)
        keyed_values: dict[str, Any] = {}

        for response in item["responses"]:
            key = response.get("key")
            label = response.get("label")
            if key is None and label is None:
                raise ValueError("Each response must include either `key` or `label`.")
            normalized_key = key or _normalize_key(str(label))
            keyed_values[normalized_key] = response.get("answer", "")

        response_items: list[dict[str, str]] = []
        lines: list[str] = []

        for question in round_definition.questions:
            if question.key not in keyed_values:
                continue
            rendered_value = _stringify_response_value(keyed_values[question.key])
            response_items.append(
                {
                    "key": question.key,
                    "label": question.label,
                    "prompt": question.prompt,
                    "answer": rendered_value,
                }
            )
            if "\n" in rendered_value:
                lines.append(f"{question.label}:")
                lines.extend(rendered_value.splitlines())
            else:
                lines.append(f"{question.label}: {rendered_value}")

        return "\n".join(lines).strip() + "\n", response_items

    answer_text = str(item.get("answer", ""))
    parsed_answers = _parse_block_answer(answer_text)
    response_items = []
    for question in get_round(number).questions:
        if question.key in parsed_answers:
            response_items.append(
                {
                    "key": question.key,
                    "label": question.label,
                    "prompt": question.prompt,
                    "answer": _stringify_response_value(parsed_answers[question.key]),
                }
            )
    return answer_text, response_items


def process_round(number: int, answer_text: str) -> dict[str, Any]:
    """Process one round answer and prepare the next prompt.

    Args:
        number: Current round number.
        answer_text: Raw answer text.

    Returns:
        Structured round result.
    """
    round_definition = get_round(number)
    parsed_answers = _parse_block_answer(answer_text)
    following_round = next_round(number)
    response_items = []
    for question in round_definition.questions:
        if question.key in parsed_answers:
            response_items.append(
                {
                    "key": question.key,
                    "label": question.label,
                    "prompt": question.prompt,
                    "answer": _stringify_response_value(parsed_answers[question.key]),
                }
            )

    return {
        "round": _round_payload(round_definition),
        "raw_answer": answer_text,
        "responses": response_items,
        "parsed_answers": parsed_answers,
        "next_round": None
        if following_round is None
        else _round_payload(following_round),
    }


def replay_session(round_inputs: list[dict[str, Any]]) -> dict[str, Any]:
    """Replay a sequence of interview rounds.

    Args:
        round_inputs: List of round input dictionaries with `round` and `answer`.

    Returns:
        Structured replay summary.
    """
    transcript = []
    merged_answers: dict[str, Any] = {}

    for item in round_inputs:
        round_number = int(item["round"])
        answer_text, response_items = _coerce_round_answer(round_number, item)
        result = process_round(round_number, answer_text)
        if response_items:
            result["responses"] = response_items
        transcript.append(result)
        merged_answers[f"round_{round_number}"] = result["parsed_answers"]

    return {
        "transcript": transcript,
        "merged_answers": merged_answers,
        "last_round": transcript[-1]["round"]["number"] if transcript else None,
        "next_round": transcript[-1]["next_round"] if transcript else None,
    }


def to_json(data: dict[str, Any]) -> str:
    """Render JSON output for CLI use."""
    return json.dumps(data, indent=2)
