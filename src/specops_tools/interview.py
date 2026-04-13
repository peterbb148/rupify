"""Executable interview harness for the SpecOps interview flow."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from .readiness import evaluate_readiness, identify_stale_artifacts


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
    guidance: tuple[str, ...] = ()
    example: str | None = None


@dataclass(frozen=True)
class InterviewRound:
    """Definition of a SpecOps interview round."""

    number: int
    title: str
    prompt: str
    template: str
    questions: tuple[InterviewQuestion, ...]
    guidance: tuple[str, ...] = ()


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
        title="Domain Model",
        prompt=(
            "Capture the core domain concepts, important relationships, and key business rules that "
            "shape the logical view."
        ),
        template="Domain entities:\nRelationships:\nBusiness rules:\n",
        guidance=(
            "Focus on the important nouns, relationships, and rules, not implementation classes.",
            "If a relationship or rule is unclear, record the ambiguity instead of inventing detail.",
        ),
        questions=(
            InterviewQuestion(
                "domain_entities",
                "Domain entities",
                "What are the core business entities or concepts?",
                guidance=(
                    "Prefer domain concepts such as System, Lifecycle, Approval, Contract, or Risk.",
                    "Avoid technical table or API naming unless it already matters to the business.",
                ),
                example="- System\n- Capability\n- Contract\n- Lifecycle state",
            ),
            InterviewQuestion(
                "relationships",
                "Relationships",
                "How do the important entities relate to each other?",
                guidance=(
                    "Capture business relationships such as ownership, dependency, approval, or containment.",
                ),
                example="- A System has one Business Owner\n- A System supports many Capabilities",
            ),
            InterviewQuestion(
                "business_rules",
                "Business rules",
                "What key rules or constraints govern these entities?",
                guidance=(
                    "Include rules that shape lifecycle transitions, approvals, ownership, or data validity.",
                ),
                example="- A deprecation request requires at least one approver\n- Contract end date cannot precede go-live date",
            ),
        ),
    ),
    InterviewRound(
        number=6,
        title="State and Workflow Model",
        prompt=(
            "Capture the important lifecycle states, transitions, and triggers that shape the "
            "process view."
        ),
        template="State entities:\nStates and transitions:\nTriggers and approvals:\n",
        guidance=(
            "Focus on business lifecycle behavior, approvals, and transitions, not implementation events.",
            "If a process is unclear, capture the uncertainty instead of forcing a complete state machine.",
        ),
        questions=(
            InterviewQuestion(
                "state_entities",
                "State entities",
                "Which entities or workflows have meaningful states or lifecycle behavior?",
                guidance=(
                    "Typical examples are System, Approval Request, Contract, Case, or Application Lifecycle.",
                ),
                example="- System lifecycle\n- Deprecation request\n- Approval request",
            ),
            InterviewQuestion(
                "states_and_transitions",
                "States and transitions",
                "What are the key states and allowed transitions?",
                guidance=(
                    "Capture the main states and the transitions stakeholders care about.",
                ),
                example="- Proposed -> Active -> Sunset -> Decommissioned\n- Submitted -> Approved or Rejected",
            ),
            InterviewQuestion(
                "triggers_and_approvals",
                "Triggers and approvals",
                "What triggers transitions, and where are approvals or exceptions required?",
                guidance=(
                    "Include approvals, validations, time-based triggers, and exception paths where relevant.",
                ),
                example="- Deprecation requires governance approval\n- Missing metadata blocks promotion to Active",
            ),
        ),
    ),
    InterviewRound(
        number=7,
        title="UCP Actor Complexity",
        prompt=(
            "Capture actor complexity using simple/average/complex after discovery is stable."
        ),
        template="Actor complexity:\n- Actor A: simple/average/complex\n",
        guidance=(
            "Use standard UCP semantics, not general product complexity intuition.",
            "System or API actors are usually simpler than humans using a rich UI.",
            "If a classification is uncertain, state the assumption instead of forcing false precision.",
        ),
        questions=(
            InterviewQuestion(
                "actor_complexity",
                "Actor complexity",
                "How should each actor be classified for UCP?",
                guidance=(
                    "`simple` usually means a system or API actor.",
                    "`average` usually means a human with a simpler interaction pattern.",
                    "`complex` usually means a human using a richer interactive UI.",
                    "A human actor is often more complex than an API actor in UCP.",
                ),
                example="- Downstream reporting API: simple\n- Enterprise architect: complex",
            ),
        ),
    ),
    InterviewRound(
        number=8,
        title="UCP Use-Case Complexity",
        prompt="Capture use-case complexity using simple/average/complex.",
        template="Use-case complexity:\n- Use case A: simple/average/complex\n",
        guidance=(
            "Classify the use case based on transaction count, branching, rules, and approvals.",
            "Do not rate a use case as complex just because the business topic feels important.",
        ),
        questions=(
            InterviewQuestion(
                "use_case_complexity",
                "Use-case complexity",
                "How should each use case be classified for UCP?",
                guidance=(
                    "`simple` means few transactions and little branching.",
                    "`average` means a moderate flow.",
                    "`complex` means longer flows, more branching, more rules, or approvals.",
                ),
                example="- Edit metadata: average\n- Approve deprecation: complex",
            ),
        ),
    ),
    InterviewRound(
        number=9,
        title="UCP Technical Factors",
        prompt="Capture the technical 0-5 influence scores in a compact block.",
        template=(
            "Technical:\n"
            "distributed system:\nresponse time:\nend-user efficiency:\n"
            "complex internal processing:\nreusability:\nease of installation:\n"
        ),
        guidance=(
            "Use a 0-5 influence scale, not a good-versus-bad scale.",
            "`0` means not relevant, `3` means moderate influence, and `5` means very high influence.",
            "Score how strongly the factor shapes the system, not whether the team is performing well.",
        ),
        questions=(
            InterviewQuestion(
                "technical",
                "Technical",
                "What technical 0-5 influence scores apply?",
                guidance=(
                    "Security and third-party access are often high for internal enterprise systems.",
                    "Response time should reflect business importance, not an arbitrary SLA guess.",
                ),
                example="security: 5\nthird-party access: 4\nease of change: 4",
            ),
        ),
    ),
    InterviewRound(
        number=10,
        title="UCP Environmental Factors",
        prompt="Capture the environmental 0-5 influence scores in a compact block.",
        template=(
            "Environmental:\nteam familiarity:\napplication experience:\n"
            "architecture experience:\nanalyst capability:\nmotivation:\n"
        ),
        guidance=(
            "Use the same 0-5 influence scale, but note that some factors are positive and some are drag.",
            "Higher is better for familiarity, experience, capability, motivation, and stability.",
            "Higher is worse for part-time staffing and platform difficulty.",
        ),
        questions=(
            InterviewQuestion(
                "environmental",
                "Environmental",
                "What environmental 0-5 scores apply?",
                guidance=(
                    "If requirements are volatile, keep requirements stability low.",
                    "If the team is split or part-time, part-time staffing should be scored higher.",
                ),
                example="team familiarity: 3\nteam motivation: 4\npart-time staffing: 2",
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


def _resolve_round_number(number: int, item: dict[str, Any]) -> int:
    """Resolve a round number, including compatibility with legacy replay fixtures."""
    candidate_keys: set[str] = set()

    if "responses" in item:
        for response in item["responses"]:
            key = response.get("key")
            label = response.get("label")
            if key is None and label is None:
                continue
            candidate_keys.add(key or _normalize_key(str(label)))
    else:
        candidate_keys.update(_parse_block_answer(str(item.get("answer", ""))).keys())

    if candidate_keys:
        matching_rounds = []
        for round_definition in ROUND_DEFINITIONS:
            round_keys = {question.key for question in round_definition.questions}
            if candidate_keys <= round_keys:
                matching_rounds.append(round_definition.number)

        if len(matching_rounds) == 1:
            return matching_rounds[0]
        if number in matching_rounds:
            return number

    return number


def _round_payload(round_definition: InterviewRound) -> dict[str, Any]:
    """Serialize a round definition for CLI output."""
    return {
        "number": round_definition.number,
        "title": round_definition.title,
        "prompt": round_definition.prompt,
        "template": round_definition.template,
        "guidance": list(round_definition.guidance),
        "questions": [
            {
                "key": question.key,
                "label": question.label,
                "prompt": question.prompt,
                "guidance": list(question.guidance),
                "example": question.example,
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
    number = _resolve_round_number(number, item)
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


def _normalize_round_item(item: dict[str, Any]) -> dict[str, Any]:
    """Normalize one round input into a response-based shape.

    Args:
        item: Raw round input.

    Returns:
        Normalized round item with canonical response entries.
    """
    round_number = _resolve_round_number(int(item["round"]), item)
    answer_text, response_items = _coerce_round_answer(round_number, item)
    normalized_item: dict[str, Any] = {
        "round": round_number,
        "responses": response_items,
    }
    if answer_text.strip():
        normalized_item["answer"] = answer_text
    return normalized_item


def merge_round_inputs(
    round_inputs: list[dict[str, Any]],
    updates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Merge targeted updates into an existing replay session.

    Round number acts as the stable round identifier. Within a round, question key acts as the
    stable response identifier when responses are provided.

    Args:
        round_inputs: Existing replay rounds.
        updates: Update items to apply.

    Returns:
        Merged round inputs ordered by round number.
    """
    merged_by_round: dict[int, dict[str, Any]] = {
        int(item["round"]): _normalize_round_item(item)
        for item in round_inputs
    }

    for update in updates:
        round_number = int(update["round"])
        normalized_update = _normalize_round_item(update)

        if "responses" in update:
            existing = merged_by_round.get(round_number, {"round": round_number, "responses": []})
            existing_by_key = {
                response["key"]: response
                for response in existing.get("responses", [])
            }
            for response in normalized_update["responses"]:
                existing_by_key[response["key"]] = response

            merged_responses = []
            for question in get_round(round_number).questions:
                if question.key in existing_by_key:
                    merged_responses.append(existing_by_key[question.key])

            merged_by_round[round_number] = {
                "round": round_number,
                "responses": merged_responses,
            }
            continue

        merged_by_round[round_number] = normalized_update

    return [merged_by_round[number] for number in sorted(merged_by_round)]


def process_round(number: int, answer_text: str) -> dict[str, Any]:
    """Process one round answer and prepare the next prompt.

    Args:
        number: Current round number.
        answer_text: Raw answer text.

    Returns:
        Structured round result.
    """
    number = _resolve_round_number(number, {"round": number, "answer": answer_text})
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
    normalized_round_inputs = [_normalize_round_item(item) for item in round_inputs]

    for item in normalized_round_inputs:
        round_number = _resolve_round_number(int(item["round"]), item)
        answer_text, response_items = _coerce_round_answer(round_number, item)
        result = process_round(round_number, answer_text)
        if response_items:
            result["responses"] = response_items
        transcript.append(result)
        merged_answers[f"round_{result['round']['number']}"] = result["parsed_answers"]

    return {
        "transcript": transcript,
        "merged_answers": merged_answers,
        "last_round": transcript[-1]["round"]["number"] if transcript else None,
        "next_round": transcript[-1]["next_round"] if transcript else None,
        "readiness": evaluate_readiness(normalized_round_inputs),
        "stale_artifacts": [],
    }


def replay_session_with_updates(
    round_inputs: list[dict[str, Any]],
    updates: list[dict[str, Any]],
) -> dict[str, Any]:
    """Replay a session after applying targeted updates.

    Args:
        round_inputs: Existing replay rounds.
        updates: Round updates to merge into the existing session.

    Returns:
        Structured replay summary including the merged session input.
    """
    merged_rounds = merge_round_inputs(round_inputs, updates)
    replay = replay_session(merged_rounds)
    replay["merged_round_inputs"] = merged_rounds
    replay["stale_artifacts"] = identify_stale_artifacts(updates)
    return replay


def to_json(data: dict[str, Any]) -> str:
    """Render JSON output for CLI use."""
    return json.dumps(data, indent=2)
