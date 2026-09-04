# AlphaFit AI Coach

AlphaFit is a fitness and nutrition assistant for the AlphaFit FYP. The AI Coach is a hosted Gemini LLM integration, not a separately trained ML model.

## Current Status

The local Python implementation is usable and tested. The Supabase Edge Function boundary is implemented, but its data provider is intentionally not connected because this workspace contains no Supabase schema, credentials, or existing ML output contracts. No database table names or fake model outputs are assumed.

## Architecture

### Local development and testing

```text
Client or test
    -> FastAPI (api/main.py)
    -> Google Gemini API
    -> AI Coach response
```

FastAPI is a development/testing layer only. It is not the final production path.

### Production target

```text
React Native
    -> Supabase Edge Function (supabase/functions/ai-coach)
    -> Supabase Auth and user-scoped data provider
    -> Context builder
    -> Google Gemini API
    -> React Native
```

The production Edge Function authenticates the caller before requesting context. Its provider interface must map the real schema into the application contract; RLS and the authenticated user identity must prevent cross-user access.

## Gemini

- Model: `gemini-3.5-flash-lite` by default; set `GEMINI_MODEL` to an available model for your Google AI account.
- Python package: `google-genai==2.20.0`
- Python SDK style: `genai.Client(api_key=...)`
- The Gemini API key is loaded server-side and is never returned to clients.

## Python Setup

From the project root:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` locally:

```text
GEMINI_API_KEY=your_key_here
```

Do not commit `.env`.

## Local FastAPI API

Start the API:

```powershell
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Health check:

```text
GET http://127.0.0.1:8000/health
```

```json
{"status":"ok"}
```

Chat request:

```text
POST http://127.0.0.1:8000/chat
Content-Type: application/json
```

```json
{
  "session_id": "local-user-1",
  "message": "Why am I not losing weight?",
  "context": {
    "user_profile": {},
    "fitness_goal": {},
    "recent_workouts": [],
    "recent_food_logs": [],
    "calorie_prediction": {},
    "recommendation_output": {}
  }
}
```

`context` is optional. The Python builder only forwards the seven agreed fields, redacts secret-like keys, bounds collections, and rejects unsupported or oversized values. Unknown raw database fields are ignored.

A `session_id` reuses one bounded in-memory Gemini chat. Omitting it creates an isolated session. Local sessions are capped at 100 and are lost when the process stops. Production conversation persistence belongs in Supabase.

PowerShell examples:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/chat -ContentType "application/json" -Body '{"session_id":"local-user-1","message":"Give me a beginner workout."}'
```

## Context and ML Integration

The Python contract is in `context/builder.py` and uses these application-level categories:

- `user_profile`
- `fitness_goal`
- `recent_workouts`
- `recent_food_logs`
- `calorie_prediction`
- `recommendation_output`
- `pose_exercise`
- `recent_conversation`

The calorie prediction and recommendation engine outputs are accepted as supplied data only. Their real shapes are not available in this workspace, so no production fields or calculations have been invented. The future Supabase provider must map actual outputs into the contract.

## Supabase Edge Function

The function is in `supabase/functions/ai-coach/index.ts`. It:

1. Requires a bearer access token and validates it with Supabase Auth.
2. Uses the authenticated user's ID when requesting context.
3. Calls a schema-neutral `CoachDataProvider` interface.
4. Sends only the mapped context and message to Gemini.
5. Keeps `GEMINI_API_KEY` and the system prompt server-side.
6. Returns clean errors for unauthorized, invalid, rate-limited, unavailable, and unconfigured states.

Required Edge Function secrets/environment values:

- `GEMINI_API_KEY`
- `GEMINI_MODEL` (optional; defaults to `gemini-3.5-flash-lite`)
- `ALPHAFIT_SYSTEM_PROMPT`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

The provider currently returns `501 coach_data_provider_not_configured`. This is intentional until the actual schema is inspected. The function has not been deployed or remotely tested because no Supabase project connection is present.

## Testing

Run mock-based tests without consuming Gemini quota:

```powershell
.venv\Scripts\python.exe -m pytest tests -q
```

Compile Python files:

```powershell
.venv\Scripts\python.exe -m py_compile app.py api/main.py context/builder.py context/__init__.py
```

Run a small real Gemini integration test through the local API by starting Uvicorn and posting to `/chat`. Keep real requests limited to development checks.

The original terminal chatbot remains available:

```powershell
.venv\Scripts\python.exe app.py
```

## Safety

The system prompt keeps the assistant within general fitness and nutrition coaching. It prohibits diagnosis, medication advice, unsafe extreme weight loss, exercising through significant pain, and fabricated user data. Serious symptoms and urgent injuries are directed to qualified medical or emergency care.

## Proposal Alignment

- Chat-based conversational interface: **COMPLETE locally; production pending deployment**
- Free-text fitness and nutrition questions: **COMPLETE locally**
- Hosted LLM API: **COMPLETE**
- Supabase Edge Function orchestration: **PARTIALLY COMPLETE; provider/deployment pending schema access**
- Prompted with recent user logs: **PARTIALLY COMPLETE; local contract exists, real schema mapping pending**
- Calorie-estimation outputs: **PARTIALLY COMPLETE; interface exists, actual output format unavailable**
- Recommendation-engine outputs: **PARTIALLY COMPLETE; interface exists, actual output format unavailable**
- Grounded, contextually relevant responses: **COMPLETE for supplied local context; production data access pending**
- Pose estimation, calorie, and recommendation ML components: **NOT IMPLEMENTED in this repository; not duplicated or modified**

## Next Required Step

Obtain the Supabase schema and actual calorie/recommendation output formats. Then implement the `CoachDataProvider` mapping, conversation persistence, RLS-aware queries, Edge Function deployment configuration, and integration tests against a non-production Supabase project.
