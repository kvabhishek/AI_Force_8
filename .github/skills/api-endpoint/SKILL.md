---
# Example skill. Copilot loads it when you ask it to add or change an API
# endpoint, or you can type /api-endpoint in Copilot Chat.
# It has one supporting file: a reference that Copilot reads when it needs it.
# How skills fit with instructions and agents: docs/copilot-customization.md
name: api-endpoint
description: Adds or changes an HTTP API endpoint so it follows the project's API conventions. Writes the contract first, then builds, tests and checks the endpoint against it. Use when adding, changing or fixing an API endpoint, or when the front end needs new data from the back end.
---

# API endpoint

Follow these steps for each endpoint you add or change.

## 1. Check the conventions

Use the API conventions in `.github/copilot-instructions.md`. If there aren't any, suggest a short set based on [the default conventions](references/api-conventions.md), and ask the team to add them to that file before you continue. Then every endpoint follows the same rules.

## 2. Write the contract

Before you write any code, add the endpoint to `docs/api.md` in this format:

```markdown
### GET /orders/{order_id}

Returns one order with its items.

- **Request:** no body
- **Response 200:** `{"order_id": "O-1001", "status": "OPEN", "total": "125.500"}`
- **Errors:** `404` if the order doesn't exist
```

Show the contract and wait for approval. Whoever builds the front end can start from it straight away.

## 3. Build it

- Keep the route handler thin: validate the input, call the back end and shape the response. Business rules belong in the back end, where tests can reach them without HTTP.
- Validate every input, and report all the problems at once in the error format.
- If the endpoint changes data or depends on who's calling, check permissions on the server, never only in the front end.
- Use parameterized queries. Never build SQL by joining strings.

## 4. Test it

Test at least a success, invalid input and something that doesn't exist. Use your team's test skill if you have one. Test business rules in the back end, and test the endpoint for status codes and the shape of the response.

## 5. Check it

Run the app, call the endpoint, for example with `curl`, and compare the response with `docs/api.md`. Fix whichever one is wrong. For a second opinion, select the **Reviewer** agent and ask it to review the endpoint.
