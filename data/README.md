# Data dictionary

All files are synthetic and were generated for this hackathon. They contain no real people, sites or permits. Every name is a fictional first name with an initial.

| File | Rows | One row per |
|---|---:|---|
| [`sites.csv`](sites.csv) | 6 | Site |
| [`permit_types.csv`](permit_types.csv) | 6 | Permit type |
| [`roles.csv`](roles.csv) | 4 | Role |
| [`users.csv`](users.csv) | 24 | User |
| [`sample_requests.csv`](sample_requests.csv) | 20 | Permit request to try in your app |

Every file is a UTF-8, comma-separated CSV with a header row. A list inside one value, such as a user's roles, is separated by pipes (`|`).

## sites.csv

| Column | Type | Example | Notes |
|---|---|---|---|
| `site_id` | Text | `GC-01` | Unique key. |
| `site_name` | Text | `Gathering Centre 01` | Fictional. |
| `area` | Text | `North Field` | The operating area the site belongs to. |
| `hazardous_zone` | Text | `ZONE_1` | `ZONE_1`, `ZONE_2` or `NON_HAZARDOUS`, from most to least likely to have flammable gas present. Not used by the checks. |

## permit_types.csv

| Column | Type | Example | Notes |
|---|---|---|---|
| `permit_type_id` | Text | `HOT_WORK` | Unique key. |
| `name` | Text | `Hot work` | |
| `risk_level` | Text | `HIGH` | `HIGH` or `MEDIUM`. Not used by the checks. |
| `requires_hse_approval` | `Y` or `N` | `Y` | `Y` means that, on a real site, an HSE officer also approves this kind of work. Not used by the checks. |
| `requires_gas_test` | `Y` or `N` | `Y` | `Y` means that, on a real site, a gas test must pass before this kind of work starts. Not used by the checks. |
| `max_validity_hours` | Integer | `8` | The longest a permit of this type can last, from `valid_from` to `valid_to`. Not used by the checks. |
| `description` | Text | `Welding, cutting, grinding or any other work that can ignite flammable gas.` | What the type covers. |

On a real site, the permit types and their limits come from the site's safety management system. The values here are illustrative.

## roles.csv

| Column | Type | Example | Notes |
|---|---|---|---|
| `role_id` | Text | `AREA_AUTHORITY` | `REQUESTER`, `AREA_AUTHORITY`, `HSE_OFFICER` or `VIEWER`. |
| `name` | Text | `Area authority` | |
| `description` | Text | `Controls a site. Approves and closes permits at their sites.` | What the role does. |

## users.csv

| Column | Type | Example | Notes |
|---|---|---|---|
| `user_id` | Text | `U-004` | Unique key. |
| `display_name` | Text | `Noura M.` | Fictional first name and initial. |
| `roles` | Text, pipe-separated | `REQUESTER\|AREA_AUTHORITY` | One or more role IDs from `roles.csv`. See [Things to know](#things-to-know). |
| `sites` | Text, pipe-separated | `GC-01\|GC-02` | The sites where the user can act, or `ALL` for every site. |
| `active` | `Y` or `N` | `Y` | `N` means the user has left or is on long leave. Used by `ROLE_REQUIRED`: inactive users can't act. |

## sample_requests.csv

| Column | Type | Example | Notes |
|---|---|---|---|
| `request_ref` | Text | `REQ-002` | Identifies the sample request. Your app gives each permit its own ID. |
| `requested_by` | Text | `U-001` | The user who submits the request. Joins to `users.csv`. |
| `site_id` | Text | `GC-01` | Joins to `sites.csv`. |
| `permit_type_id` | Text | `HOT_WORK` | Joins to `permit_types.csv`, with an exception. See [Things to know](#things-to-know). |
| `work_description` | Text | `Weld a new pipe support on the inlet manifold` | The work the crew will do. |
| `valid_from` | ISO 8601 date and time with offset | `2026-11-15T07:30:00+03:00` | When the permit starts. Kuwait time (UTC+03:00, no daylight saving time). |
| `valid_to` | ISO 8601 date and time with offset | `2026-11-15T14:30:00+03:00` | When the permit ends. |
| `hazards` | Text | `Flammable gas; sparks; hot surfaces` | The main hazards, separated by semicolons. |
| `controls` | Text | `Gas test; fire watch; fire blanket; extinguisher at the work area` | The main controls, separated by semicolons. |

The sample requests aren't permits yet. Submit them through your app, and use them in your tests and your demo.

## Things to know

Real permit records are messy, so these are too. The users and sample requests deliberately contain a small number of:

- **Users with more than one role:** for example, a user who can both request and approve permits at the same site.
- **Inactive users:** some users have `active` = `N`, including area authorities. One site has no active area authority at all.
- **`ALL` sites:** some users, such as HSE officers, have `ALL` instead of a list of site IDs.
- **Inconsistent role formatting:** a role ID in lower case with an extra space.
- **Sample requests with problems:** one request ends before it starts, one permit type isn't in `permit_types.csv` and one requester isn't assigned to the site.

These issues can change who can do what. Decide how your app handles each one, record the decision in your plan, and test it.

All times are Kuwait time (UTC+03:00, no daylight saving time). Some permits run overnight, so compare full dates and times, not just times of day.
