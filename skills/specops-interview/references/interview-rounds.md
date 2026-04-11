# Interview Rounds

Use these rounds in order. Do not collapse them into one long message unless the user explicitly
asks for that style.

## Round 1: Problem and Scope

Ask at most 4 short prompts.

Preferred answer shape:

```text
Idea:
Problem:
Users:
In scope:
Out of scope:
```

Collect:

- what the system is
- what problem it solves
- who it is for
- what is in and out of the first release

## Round 2: Outcomes and Constraints

Ask at most 4 short prompts.

Preferred answer shape:

```text
Outcomes:
Success criteria:
Required data:
Constraints:
```

Collect:

- business outcomes
- success criteria
- must-have data categories
- important constraints

## Round 3: Actors and Use Cases

Ask at most 3 prompts.

Preferred answer shape:

```text
Actors:
Use cases:
Integrations:
```

Collect:

- user roles
- system actors
- top use cases
- external integrations

## Round 4: Requirements

Ask at most 3 prompts.

Preferred answer shape:

```text
Workflow scope:
Metadata fields:
Non-functional requirements:
```

Collect:

- workflow actions vs inventory/reporting only
- core metadata fields
- non-functional requirements

## Round 5: UCP Actor Complexity

Do not ask for all UCP inputs in one block.

Explain the scale first:

- `simple`: system/API actor
- `average`: human with simpler interaction
- `complex`: human with richer interactive UI

Ask for actor complexity in a short list only.

Preferred answer shape:

```text
Actor complexity:
- Actor A: simple/average/complex
- Actor B: simple/average/complex
```

## Round 6: UCP Use-Case Complexity

Explain the scale first:

- `simple`: few transactions
- `average`: moderate flow
- `complex`: longer flow, more rules, more branching or approvals

Ask only for the main use cases already identified.

Preferred answer shape:

```text
Use-case complexity:
- Use case A: simple/average/complex
- Use case B: simple/average/complex
```

## Round 7: UCP Technical Factors

Explain the influence scale briefly:

- `0`: not relevant
- `3`: moderate influence
- `5`: very high influence

Ask the technical factors in 2 smaller groups if needed instead of one giant block.

Preferred answer shape:

```text
Technical:
distributed system:
response time:
end-user efficiency:
complex internal processing:
...
```

## Round 8: UCP Environmental Factors

Use the same `0-5` influence explanation, but state clearly that:

- higher is better for familiarity, capability, motivation, and stability
- higher is worse for part-time staffing and platform difficulty

Preferred answer shape:

```text
Environmental:
team familiarity:
application experience:
architecture experience:
analyst capability:
...
```

## Stopping Rule

If the user cannot answer a round comfortably, do one of these:

- ask a smaller clarifying question
- record a provisional assumption clearly
- stop and surface the missing points explicitly

Do not force completion through an unreadable scoring wall.
