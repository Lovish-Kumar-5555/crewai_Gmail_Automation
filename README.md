# AI-Powered Gmail Automation with Safety Guardrails

**A multi-agent CrewAI system that automates inbox triage and actions while enforcing production-style safety policies before any Gmail or Slack operation is executed.**

## 🚀 Project Overview
Modern inboxes are high-volume and high-risk: automation can save time, but unsafe actions (especially deletion) can cause irreversible loss.

This project solves that by combining **LLM-driven email decisioning** with a **centralized guardrails engine** that validates every sensitive action before execution. Instead of trusting agent output blindly, actions are policy-checked and blocked when conditions are not met.

What makes this implementation different:
- Multi-agent workflow for categorization, organization, response drafting, notifications, and cleanup
- Centralized policy validation reused across Gmail/Slack tools
- Fail-closed safety behavior for unknown, missing, or uncertain inputs

## 💡 Key Highlights
- Built a **multi-agent email automation pipeline** using CrewAI with sequential task orchestration.
- Designed a **centralized guardrails engine** (`validate_action`) used by all action tools.
- Implemented **fail-closed policy enforcement** for unknown actions/categories/priorities and missing critical metadata.
- Added **destructive-action controls**: delete is allowed only when strict policy conditions pass.
- Integrated **Gmail IMAP automation** (fetch, organize, draft, delete, empty trash) and **Slack webhook notifications**.
- Added **unit-tested policy validation** with positive and negative scenarios for safety-critical decisions.

## 🛡️ Guardrails System (Core Differentiator)
AI agents can misclassify, hallucinate fields, or produce inconsistent actions. In production, that means risk. This system treats guardrails as a first-class safety layer.

How safety is enforced:
- Every actionable tool call (e.g., `delete`, `archive`, `notify`, `draft_reply`, `label`, `empty_trash`) is validated through the same policy engine.
- Inputs are normalized (aliases for actions/categories), then evaluated against explicit policy config.
- Unknown or missing critical fields are blocked by default (fail-closed), not silently accepted.

Examples of enforced rules:
- **No delete for protected categories**: `PERSONAL`, `INVOICE`, `RECEIPTS_INVOICES`
- **Delete only if all conditions pass**: LOW priority + valid age + age threshold met (default: >= 30 days)
- **Archive constraints**: only allowed categories and MEDIUM/LOW priorities
- **High-priority actions (`notify`, `draft_reply`)**: only for HIGH priority and allowed categories

Fail-closed behavior:
- Missing `requested_action` -> blocked
- Unknown category/priority/action -> blocked
- Missing/invalid `age_days` for delete -> blocked
- Sensitive personal/invoice signal + uncertain classification -> blocked

## ⚙️ Tech Stack
- Python
- CrewAI
- Gmail IMAP integration (Gmail account + App Password)
- Slack Webhooks
- Pydantic models/validation
- `unittest`

## 🧠 System Architecture
```text
Unread Emails (Gmail)
        |
        v
Categorizer Agent -> category + priority + required_action
        |
        v
Organizer / Draft / Notify / Cleanup Decision
        |
        v
Central Guardrails Engine (validate_action)
        |
        +--> Allowed  -> Execute tool action (Gmail/Slack)
        |
        +--> Blocked  -> Return structured denial + reasons (no unsafe action)
```

## 📂 Project Structure
```text
crewai-gmail-automation/
|-- src/gmail_crew_ai/
|   |-- crew.py
|   |-- main.py
|   |-- models.py
|   |-- config/
|   |   |-- agents.yaml
|   |   `-- tasks.yaml
|   |-- guardrails/
|   |   |-- config.py
|   |   |-- engine.py
|   |   |-- models.py
|   |   `-- policy.py
|   `-- tools/
|       |-- gmail_tools.py
|       |-- slack_tool.py
|       `-- date_tools.py
|-- tests/
|   `-- test_guardrails_engine.py
|-- knowledge/
|-- assets/
|-- output/
|-- .env_example
|-- pyproject.toml
`-- uv.lock
```

## 🧪 Testing & Validation
Safety logic is validated with unit tests in `tests/test_guardrails_engine.py`.

Covered validation scenarios include:
- Delete allowed for low-priority, old promotional email
- Delete blocked for high-priority emails
- Delete blocked for protected categories (invoice/personal)
- Delete blocked when `age_days` is missing
- Archive allowed for valid category + priority
- Unknown action/category/priority blocked

This test suite reinforces a **safety-first, policy-driven design** for AI automation.

## ▶️ How to Run
### 1) Setup environment
```bash
cp .env_example .env
# Fill in OPENAI_API_KEY, EMAIL_ADDRESS, APP_PASSWORD, SLACK_WEBHOOK_URL
```

### 2) Install dependencies
```bash
uv sync
```

Alternative (if not using uv):
```bash
pip install -e .
```

### 3) Run the project
```bash
python -m gmail_crew_ai.main
```

### 4) Run tests
```bash
python -m unittest tests/test_guardrails_engine.py -v
```

## 📊 Example Outputs
### Blocked Example
```json
{
  "action": "delete",
  "category": "invoice",
  "priority": "low",
  "allowed": false,
  "reason": "Protected category"
}
```

### Allowed Example
```json
{
  "action": "archive",
  "category": "newsletter",
  "priority": "medium",
  "allowed": true
}
```

## 🎯 Why This Project Matters
- Demonstrates **real-world automation engineering** across LLM orchestration, external APIs, and workflow design.
- Shows **safe AI system design** by separating decision generation from policy enforcement.
- Reflects **production readiness thinking**: structured validation, explicit policies, logging payloads, and fail-closed defaults.
- Highlights **agent-based architecture skills** with specialized roles and sequential task dependencies.
- Maps directly to industry needs in AI operations, workflow automation, and reliability engineering.

## 🚀 Future Improvements
- Expand strict schema contracts for every intermediate artifact and tool payload
- Add human-in-the-loop approval gates for destructive or ambiguous actions
- Add global dry-run/simulation mode for safe policy tuning
- Build a lightweight UI/dashboard for policy visibility, blocked-action review, and audit trails

## 👨‍💻 Author
Lovish Kumar  
GitHub: [https://github.com/Lovish-Kumar-5555](https://github.com/Lovish-Kumar-5555)
