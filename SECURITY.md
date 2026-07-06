# Security & Privacy for Jamalek

Jamalek is a beauty assistant, so it handles two kinds of sensitive data: **selfies** and a
**beauty profile** (undertone, product inventory, skin sensitivities, and history). Because
that's personal, privacy is treated as a design constraint, not an afterthought, in line
with the Concierge track's requirement to keep personal information safe.

## Data handling principles

1. **Selfies are ephemeral.** Uploaded photos are processed entirely in memory for a single
   analysis pass and are **never written to disk**. Only the derived, non-identifying result
   (for example `undertone: warm`, `concern: dryness`) is saved to your profile. The image itself
   is discarded once the turn completes.
2. **Minimize what persists.** The profile stores derived attributes and product inventory,
   not raw biometric or image data. A leaked profile reveals "warm undertone, owns two
   foundations, fragrance-sensitive," not a face.
3. **Consent before writing.** When Jamalek extracts a new fact about you mid-conversation,
   it asks for permission before saving it to your profile (the **consent gate**). It
   proposes; you decide.
4. **You own your data.** You can wipe your entire profile at any time by typing
   **`delete my profile`**.

## What is stored vs. discarded

| Data | Persisted? | Where | Notes |
|---|---|---|---|
| Raw selfie / uploaded image | **No** | (none) | In memory only, discarded after analysis |
| Derived undertone / skin concerns | Yes | Beauty profile | Non-identifying; consent-gated |
| Product inventory | Yes | Beauty profile | Editable / removable by the user |
| Sensitivities & reaction history | Yes | Beauty profile | Used to avoid recommending irritants |
| Session conversation state | Ephemeral | ADK session state | Cleared per session lifecycle |
| API keys / credentials | **Never committed** | Environment variables | See "Secrets" below |

## Consent gate & user control

- **Consent gate:** before any new fact is written to the long-term profile, Jamalek
  confirms it with the user.
- **Deletion:** `delete my profile` removes the stored profile entirely.
- **Inspection:** the user can ask what Jamalek currently remembers about them.

## Secrets management

- `GEMINI_API_KEY` and `GOOGLE_API_KEY` are read from **environment variables at runtime**,
  never hard-coded, never committed.
- Local profile stores and any `.env` files are excluded from version control.
- On Cloud Run, keys are injected as runtime environment variables via `--set-env-vars`,
  never baked into the container image.

## MCP data-source boundary

Product lookups run through a **read-only Stdio MCP server** exposing a narrow tool over a
local `products.json` catalog. The agent cannot issue arbitrary queries or reach beyond the
catalog, which both prevents hallucinated recommendations and limits blast radius if a
prompt-injection attempt tries to steer a tool call.

## Threat model (brief)

| Threat | Mitigation |
|---|---|
| Face / biometric data leak | Selfies never persisted; only derived labels stored |
| Profile data exposure | Stored data is minimized, non-identifying derived attributes |
| Unwanted data collection | Consent gate before any profile write; `delete my profile` to wipe |
| Credential leakage via source control | Keys in env vars only; excluded from version control |
| Prompt injection steering tool calls | Narrow, read-only MCP surface over a local catalog |

---

*This is a hackathon capstone project. The posture above reflects the design as built; a
production deployment would add authenticated per-user isolation, encryption at rest for the
profile store, and audit logging.*
