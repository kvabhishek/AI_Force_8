# Default API conventions

Good defaults for a JSON HTTP API. Change any of them to suit your team, and record the ones you use in `.github/copilot-instructions.md`.

## Paths and methods

| Action | Method and path | Success response |
|---|---|---|
| List | `GET /orders` | `200` with a page of items |
| Get one | `GET /orders/{order_id}` | `200` with the item |
| Create | `POST /orders` | `201` with the new item |
| Change | `PATCH /orders/{order_id}` | `200` with the changed item |
| Delete | `DELETE /orders/{order_id}` | `204` with no body |
| Take an action | `POST /orders/{order_id}/cancel` | `200` with the changed item |

- Name paths after things, using plural nouns in lower case with hyphens, such as `/purchase-orders`. Use an action path, such as `/cancel` or `/approve`, only for a state change that isn't a simple edit.
- Put filters, sorting and paging in the query string, such as `?status=OPEN&sort=-created_at&limit=50&offset=0`.

## Data

- Send and receive JSON. Use the same field names as your data, such as `order_id`.
- Return a list as `{"items": [...], "total": 120, "limit": 50, "offset": 0}`, so the front end can page through it.
- Write dates and times in ISO 8601 with the offset, such as `2026-11-15T07:00:00+03:00`.
- Send money as a string with fixed decimal places, such as `"1250.000"`, so no precision is lost.
- When a business rule produces a result, include the rule and the values it used, so the front end can explain the result.

## Errors

Use one format for every error:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "The request has 2 invalid fields.",
    "details": [
      {"field": "quantity", "problem": "Must be 1 or more.", "value": 0},
      {"field": "customer_id", "problem": "Required."}
    ]
  }
}
```

| Status | When |
|---|---|
| `400` | The input is invalid, such as a missing field or a value out of range |
| `401` | The caller isn't signed in |
| `403` | The caller isn't allowed to do this |
| `404` | The item doesn't exist |
| `409` | The request conflicts with the current state, such as cancelling an order that has shipped |
| `500` | Something unexpected failed. Log the details, and return only a general message. |

Never return a stack trace, a SQL error or a secret in a response.
