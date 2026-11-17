# API contract

### POST /api/permits/{permit_id}/review

Allows an active `HSE_OFFICER` assigned to the permit site to mark a requested permit as reviewed or reject it before Area Authority approval. A `REVIEWED` permit proceeds to Area Authority approval; `REJECT` is terminal.

- **Request:**

  ```json
  {
    "user_id": "U-010",
    "decision": "REVIEWED",
    "comment": "Work scope and safety controls reviewed."
  }
  ```

  `decision` must be `REVIEWED` or `REJECT`. `user_id` and `decision` are required. `comment` is optional for `REVIEWED` and required for `REJECT`.

- **Response 200:** `{"success": true, "permit": {...}}`; the permit status is `REVIEWED` or `REJECTED`, according to the decision. A `REVIEWED` permit may then be approved by an eligible Area Authority.
- **Errors:** `400` for invalid input, unauthorized role, site assignment failure, or invalid transition; `404` if the permit does not exist. Refusals use `{"ok": false, "error": {"code": "CHECK_ID", "message": "..."}}`.
