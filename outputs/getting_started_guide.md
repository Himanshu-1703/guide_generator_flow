# Getting Started with n8n — Beginner-Friendly Guide (Markdown)

> Friendly note: This guide is written for absolute beginners. It defines terms before use, shows step-by-step setup (cloud + local), includes complete working examples, points out common pitfalls, and has troubleshooting tips. If anything is unclear, you can pause and test each node as described — small tests are key to building confidence.

---

## Table of contents

- Introduction
- Quick glossary (terms defined before use)
- Why learn n8n (use cases & benefits)
- What you'll learn
- Prerequisites (system & software)
- Installation & setup
  - Option A — n8n Cloud (fastest)
  - Option B — Self-host with Docker (local)
- Core concepts (simple analogies + short practical notes)
- Your first project: RSS → LLM Summary → Discord (complete, step-by-step)
  - Pre-setup checklist
  - Full node-by-node instructions
  - Example: HTTP Request to OpenAI (complete example)
  - Testing & limiting results
- Common patterns & use cases
- Troubleshooting (top errors and fixes)
- Next steps (learning path & production tips)
- Additional resources
- Summary of changes made to this guide

---

## Introduction

n8n (pronounced "n-eight-n") is an open-source workflow automation tool. You build workflows visually by connecting "nodes", and n8n runs those steps for you automatically.

Why learn it?
- Automate repetitive manual tasks.
- Connect APIs and apps without writing boilerplate glue code.
- Combine data processing, webhooks, schedules, and AI models into repeatable workflows.
- Great for prototyping, small business automation, and personal productivity.

What you'll learn in this guide:
- Core n8n concepts with clear definitions.
- How to run n8n (cloud + local Docker).
- How to build and test a full practical example: RSS → LLM summary → Discord.
- How to use expressions safely and troubleshoot common problems.

---

## Quick glossary (you'll see these words often — definitions first)

- Workflow: A sequence of steps (nodes) that n8n executes. Analogy: a recipe.
- Node: A single step in a workflow that performs an action (read RSS, call an API, send a message, run code).
- Trigger: A node that starts a workflow (e.g., schedule, webhook, RSS).
- Credential: Stored secret info (API key, token). Analogy: keys to locked doors.
- Expression: A small snippet/template used inside node fields to compute dynamic values, wrapped in {{ }}.
- LLM: Large Language Model — AI models that generate or process text (e.g., OpenAI).
- JSON: JavaScript Object Notation — a structured text format used for data interchange.
- Merge / Split: Nodes that combine/split streams of items (be careful with different counts).
- Pinning (n8n UI): Storing a value in the editor so it isn't re-sent to an LLM repeatedly (saves tokens).

(Every technical term used later will be defined beforehand or when first referenced.)

---

## Prerequisites

Who this guide assumes you are:
- A beginner with no prior n8n experience. Basic comfort using a web browser and optionally a terminal/shell is enough.

System requirements (self-hosted/local):
- OS: Linux, macOS, or Windows (WSL recommended on Windows).
- CPU: 2+ cores recommended.
- RAM: 2GB+ (4GB+ recommended for heavy use).
- Disk: 10GB+ free.
- Docker Desktop (Windows/macOS) or Docker Engine (Linux) if self-hosting.

Software you may install:
- Option A (recommended for beginners): n8n Cloud — no local install required.
- Option B (local): Docker (and optionally Docker Compose).
- Optional: VS Code (for viewing JSON exports), a terminal for Docker commands.

Note about webhooks and testing locally:
- If you plan to use webhooks locally, you'll need a public URL. For testing, tools like ngrok (https://ngrok.com) are very helpful.

Emoji note: ✅ Use n8n Cloud for the fastest start. Use Docker when you want local control.

---

## Installation & Setup

Two recommended ways to start:

### Option A — n8n Cloud (fastest, best for beginners)
1. Visit https://n8n.io and click "Get started" or "Try n8n Cloud".
2. Create an account (email + password) and verify your email.
3. Open the n8n Editor from the dashboard.

How to verify:
- You should see the n8n canvas with a "Create Workflow" or "Start from Scratch" button.
- Click "Create Workflow" and the editor opens — success!

Basic notes:
- Credentials are managed in the editor (Menu → Credentials).
- No local Docker installation required.
- Recommended for trying examples quickly.

---

### Option B — Self-host with Docker (local, for more control)

We give a minimal Docker Compose setup for a development environment. For production, follow the official n8n deployment docs.

1. Install Docker Desktop (macOS/Windows) or Docker Engine (Linux).
2. Make a folder for n8n:
```bash
mkdir -p ~/n8n
cd ~/n8n
```

3. Create a `.env` file in the folder (safer than hardcoding secrets in compose):
```bash
# File: .env
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=youruser
N8N_BASIC_AUTH_PASSWORD=yourstrongpassword
# Optional: PUBLIC_URL used for webhooks if accessible externally, e.g. via ngrok/tunnel
# N8N_PUBLIC_URL=https://yourdomain.example
```

4. Create a `docker-compose.yml` file:
```yaml
version: '3.7'

services:
  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=${N8N_BASIC_AUTH_ACTIVE}
      - N8N_BASIC_AUTH_USER=${N8N_BASIC_AUTH_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_BASIC_AUTH_PASSWORD}
      # Uncomment and set if you expose to internet
      # - N8N_HOST=yourdomain.example
      # - N8N_PORT=5678
      # - WEBHOOK_URL=${N8N_PUBLIC_URL}
    volumes:
      - ~/.n8n:/home/node/.n8n
```

5. Start n8n:
```bash
docker-compose up -d
```

6. Verify:
- Open http://localhost:5678 in your browser.
- Log in using the username/password from the `.env` file.
- You should see the editor canvas.

Helpful dev commands:
- View logs: docker-compose logs -f n8n
- Stop: docker-compose down

Security note 🔒:
- For public exposure, use HTTPS and stronger auth (reverse proxy + TLS). Do NOT expose the editor to the open internet with default credentials.

---

## Core Concepts (with simple analogies & quick practical notes)

1. Workflow
   - Definition: Full pipeline of nodes executed by n8n.
   - Analogy: A recipe with ordered steps.
   - Practical: Save workflows, name them, and version control by export/import.

2. Node
   - Definition: One step in the workflow (trigger, API call, transformation).
   - Analogy: A single instruction in a recipe.
   - Practical: Nodes receive and output arrays of JSON items.

3. Trigger
   - Definition: Node that starts the workflow automatically.
   - Examples: Manual Trigger (start by clicking), Schedule Trigger (time-based), Webhook Trigger (HTTP event), RSS Trigger (new feed item).
   - Practical: Only triggers can start automatic runs; others are action nodes.

4. Credential
   - Definition: Stored secret (API key/token) used by nodes.
   - Practical: Create credentials once and reuse them. Use the "Credentials" area in the editor.

5. Expression & JSON
   - Expression: Small inline JavaScript-like code in {{ }} used to compute values dynamically inside node fields.
   - JSON: Data format used to pass information between nodes. Inspect node output to learn field names.
   - Practical: Use expressions to insert titles, links, or LLM outputs into messages.

Extra terms:
- Merge: Join multiple inputs — careful with different numbers of items.
- Split: Break multi-item payloads into individual executions.
- Pinning: In UI, pin values so they are not re-sent (useful to save LLM tokens).

---

## Your First Project — RSS → LLM Summary → Discord

Goal: Read RSS items, summarize each using an LLM, and post summaries to Discord.

High-level flow:
RSS Read (trigger or node) → LLM (OpenAI via HTTP Request or built-in OpenAI node) → Set (format message) → Discord (webhook)

Before you start — Pre-setup checklist
- Discord: Create a webhook for your channel (Server Settings → Integrations → Webhooks) and copy the webhook URL.
- OpenAI: Create an API key in your OpenAI account and copy it as a credential (or store as a credential/secret in n8n).
- If self-hosting and testing webhooks, ensure your local instance is accessible or use ngrok.

Step-by-step (n8n Editor):

1) Create a new workflow
- In the editor click "Create Workflow".
- Give it a name like "RSS -> LLM -> Discord".
- Save the workflow early to avoid losing work.

2) Add RSS Read node
- Add a node: search for "RSS" → choose "RSS Read".
- Set field "URL" to an RSS feed, for example: https://krebsonsecurity.com/feed/
- Optional: set "Limit" to a number (e.g., 5) to avoid fetching too many items during testing.
- Click "Execute Node" to fetch items.
- Inspect the OUTPUT panel: each item will show fields such as `title`, `link`, `content`, `pubDate`.

Tip: If the RSS node returns an array, n8n normally runs downstream nodes once per item (this is usually what you want).

3) Add an LLM node — two recommended approaches

Option A — Use the built-in OpenAI node (if available)
- Add "OpenAI" node.
- Create a credential with your OpenAI API key in the node's credential dropdown.
- Configure:
  - Operation: "Chat completion" (if supported)
  - Model: gpt-3.5-turbo (or another available model)
  - Messages: Use a single message with role "user" and content like:
    ```
    Please summarize the following article into two concise sentences.

    {{$json["content"]}}
    ```
- Execute the node (connect it to the RSS node first and run the workflow), inspect output. The summary text will usually be at `choices[0].message.content`.

Option B — Use an HTTP Request node to call OpenAI Chat Completions API (complete example)

This option always works and shows exactly what the API returns. Replace `YOUR_OPENAI_KEY` with the credential value (use n8n credentials in production).

- Add "HTTP Request" node.
- Set:
  - HTTP Method: POST
  - URL: https://api.openai.com/v1/chat/completions
  - Authentication: None (we'll set the Authorization header)
  - Headers (JSON):
    - Authorization: Bearer {{ $credentials.openaiApiKey.value }}  <-- example if you stored as credential
    - Content-Type: application/json
  - Body Content Type: JSON
  - Body Parameters (raw JSON): (use expression mode to include the RSS article content)
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "user",
      "content": "Please summarize the following article into two concise sentences.\n\n{{$json[\"content\"]}}"
    }
  ],
  "temperature": 0.2,
  "max_tokens": 200
}
```
Notes:
- In n8n, to put the expression inside the JSON body, ensure the node allows expressions (there will be a toggle or an icon to switch value to expression mode). The expression above inserts the RSS article content.
- The response JSON will contain `choices[0].message.content` — use that in the next node.

Why HTTP Request? It's explicit and helpful to learn what the API returns. But using the dedicated OpenAI node is simpler if available.

4) Add Set node to format the Discord message
- Add "Set" node (this node creates/renames fields in the item).
- Create a new field:
  - Name: message
  - Value (use expression; example uses Chat Completion response path):
```text
Hey — here is a short summary:

Title: {{$json["title"]}}

Summary: {{$json["choices"] && $json["choices"][0] && $json["choices"][0].message && $json["choices"][0].message.content || $json["response"] || $json["summary"]}}

Link: {{$json["link"]}}
```
Explanation:
- We attempt several possible keys for the LLM output because different nodes / APIs return different structures. The most common for OpenAI Chat is `choices[0].message.content`.
- After running the LLM node once, inspect the output and update this expression to use the exact path found in the LLM node's output.

5) Add Discord node (Webhook)
- Add "Discord" node if available, or use "HTTP Request" to POST to the webhook URL.
Option A — Discord Node:
  - Operation: "Send message"
  - Credential: (if a credential type exists for Discord webhooks enter the webhook URL)
  - Message content: use expression `{{ $json["message"] }}`

Option B — HTTP Request to Discord webhook (simple and universal)
- Add "HTTP Request" node:
  - HTTP Method: POST
  - URL: (paste your Discord webhook URL)
  - Body Content Type: JSON
  - Body Parameters:
```json
{
  "content": "{{$json[\"message\"]}}"
}
```
- Execute the node; one message per input item should appear in your Discord channel.

6) Wire the nodes together:
- RSS Read → LLM (OpenAI/HTTP Request) → Set → Discord

7) Test the workflow
- Click "Execute Workflow" (this runs the entire flow).
- Inspect outputs at each node.
- Check Discord for posted messages.

Important testing pointers:
- During early experiments, set a low "Limit" on RSS and set "Execute Node" to test nodes individually.
- If you see multiple messages and want just one digest, aggregate items before sending (see "Testing & limiting results" below).

---

### Example: cURL test for OpenAI (useful to debug outside n8n)

From your terminal (replace OPENAI_KEY and paste a short article text):
```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_KEY" \
  -d '{
    "model":"gpt-3.5-turbo",
    "messages":[{"role":"user","content":"Please summarize this article into two sentences:\n\n<article text here>"}],
    "temperature":0.2
  }'
```
The response will include `choices[0].message.content` which contains the summary.

---

### Testing & limiting results (common needs)
- If RSS returns many items and you only want recent ones:
  - Use the "Limit" field in the RSS node.
  - Or add an "If" node after RSS with a JavaScript expression to filter by `pubDate`. Example expression (in an If node Expression field):
```javascript
// Returns true if item is within last 3 days
{{$json["pubDate"] ? (new Date($json["pubDate"]).getTime() >= Date.now() - 3*24*60*60*1000) : false}}
```
- To create a single digest message for multiple items:
  - Use a "Merge" or a small Code node to aggregate item fields (e.g., build a string of summaries). Then post that one message to Discord.

---

## Common patterns and use cases

1. Schedule-triggered reports:
   - Schedule Trigger → Fetch data → Transform → Email/Slack/Discord.
   - Use for automatic daily/weekly digests.

2. Event-driven webhook flows:
   - Webhook Trigger → Validate → Store in database → Notify.
   - Use for form submissions, Stripe events, or CI notifications.

3. Pull-process-publish:
   - RSS → LLM Analysis → Combine → Post to Slack/Discord or update a website.
   - Useful for news monitoring, security feeds, content curation.

---

## Troubleshooting (top beginner errors & fixes)

1. Invalid credentials / Authentication failed
   - Symptoms: 401/403 errors or node shows authentication error.
   - Fix:
     - Recreate credentials in the editor, paste full keys (no extra spaces).
     - Check that the service (OpenAI, Discord) key hasn't expired or been revoked.
     - For OpenAI, ensure the account has access and billing is set up.

2. Node returns empty output
   - Symptoms: OUTPUT panel shows zero items.
   - Fix:
     - Execute the upstream node alone (e.g., RSS) and inspect its output.
     - Confirm the feed URL is correct and accessible from your instance.
     - For webhooks, ensure the external system actually sent a request.

3. Duplicate or many messages posted
   - Symptoms: Many repeated posts in Discord.
   - Explanation: n8n executes downstream nodes once per input item by default.
   - Fix:
     - Limit items in RSS node.
     - Aggregate into one message when you want a digest.
     - Use filters to only process new items.

4. LLM summaries truncated or low-quality
   - Symptoms: Summaries missing parts or repetitive.
   - Fix:
     - Local LLMs may have small context windows — chunk articles or use remote models.
     - Improve prompts with clear instructions and examples.
     - Pin static prompt parts to save tokens.

5. Merge node mismatches
   - Symptoms: After merging, fields misaligned or missing.
   - Fix:
     - Avoid merging streams with differing counts unless you intentionally want pairing behavior.
     - Collect arrays first and then merge intentionally (use Code node to join arrays).

General debugging tips:
- Use "Execute Node" to test a single node.
- Inspect the "Executions" panel to replay and view past runs.
- Add "Set" nodes with sample data to develop downstream nodes.

---

## Next steps (learning plan)

1. Expressions deep-dive
   - Learn $json, $items, and how expressions evaluate values.
2. Aggregation & data transformations
   - Learn Merge, Split, and Code nodes where needed.
3. Production readiness
   - Deploy behind HTTPS, use environment variables, backups, and monitor runs.
4. Advanced AI integrations
   - Learn few-shot prompts, instruction tuning, and token-efficiency tricks.

Recommended order:
1) Official quickstart (you’ve already started).
2) Expressions practice.
3) Build 3 small automations.
4) Export/import workflows (JSON templates).
5) Explore community templates.

---

## Additional resources

- Official n8n docs: https://docs.n8n.io/
- First workflow tutorial: https://docs.n8n.io/try-it-out/tutorial-first-workflow/
- Community forum: https://community.n8n.io/
- Stack Overflow: https://stackoverflow.com/questions/tagged/n8n
- Templates: https://n8n.io/workflows
- ngrok for local webhook testing: https://ngrok.com

---

## Final encouragement

You completed a practical end-to-end example. Celebrate small wins: "first workflow executed", "first Discord message sent", "first LLM summary produced". Automation is iterative — build small, test frequently, and gradually add complexity.

If you want, I can:
- Create an exportable n8n workflow JSON for the RSS→LLM→Discord example.
- Produce a checklist for deploying n8n with Docker Compose and HTTPS.
- Help refine prompts for better summarization.

Happy automating! 🚀

---

## Summary of changes made to this guide

- Reorganized structure for clearer learning progression (glossary before use, checklist before steps).
- Defined all technical jargon before first use and included analogies that assist rather than confuse.
- Improved Docker Compose instructions (use .env for credentials; safer practice).
- Provided two practical, complete ways to call LLMs:
  - Using OpenAI node (simpler).
  - Using an explicit, working HTTP Request example (complete JSON body) — includes where to find the summary in the response (`choices[0].message.content`).
- Fixed and clarified expression examples and gave safer JS expressions for date filtering.
- Made troubleshooting more explicit with direct symptoms and step-by-step fixes.
- Added concrete testing tips (Execute Node, limit RSS results, ngrok for local webhooks).
- Improved tone to be encouraging and beginner-focused.
- Ensured code blocks are complete and ready to use (Docker Compose, cURL).
- Added security notes and production hints so beginners avoid common exposure mistakes.
- Shortened/clarified sections that were previously overly technical without explanation.

---

If you'd like, I can also:
- Generate the actual n8n JSON export of the RSS → OpenAI → Discord workflow so you can import it directly into your instance.
- Create a one-page printable checklist for running n8n locally or on the cloud.

Would you like the importable workflow JSON next?