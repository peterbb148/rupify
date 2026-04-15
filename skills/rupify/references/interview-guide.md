# Rupify Interview Guide

Use grouped questions instead of a single prompt dump.

## Prompting Rules

- keep each round short
- prefer 2 to 4 prompts per round
- always give a compact answer template when asking for several fields
- avoid asking the user to fill large inline scoring matrices
- delay UCP scoring until the discovery baseline is stable

## 1. Problem Framing

- What problem is the system solving
- Who experiences the problem
- What system boundary should Rupify assume

## 2. Outcomes

- What business goals matter most
- What would count as success
- What constraints matter for scope, timing, or compliance

## 3. Actors

- Which humans interact with the system
- Which external systems interact with it
- How sophisticated or automated are those interactions

## 4. Use Cases

- What are the main user goals
- What is the primary actor for each goal
- What is the normal flow
- What exceptions or alternative flows matter

## 5. Requirements

- What must the system do
- What quality attributes or constraints matter

## 6. UCP Inputs

- actor complexity in a compact list
- use-case complexity in a compact list
- technical factors in one or two small groups
- environmental factors in one small group

If the answers are too vague to score defensibly, stop and list the unresolved questions.

## Recommended Answer Shapes

Use lightweight copy-paste templates such as:

```text
Idea:
Problem:
Users:
In scope:
Out of scope:
```

```text
Actors:
Use cases:
Integrations:
```

```text
Technical:
distributed system:
response time:
...
```

Prefer these small answer shapes over long mixed prose plus inline classifications.
