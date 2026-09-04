import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

type JsonValue = string | number | boolean | null | JsonObject | JsonValue[];
type JsonObject = { [key: string]: JsonValue };

/**
 * Application-level contract for data mapped from the real Supabase schema.
 * These are not assumed database table or column names.
 */
type CoachContext = {
  user_profile?: JsonObject;
  fitness_goal?: JsonObject;
  recent_workouts?: JsonValue[];
  recent_food_logs?: JsonValue[];
  calorie_prediction?: JsonObject;
  recommendation_output?: JsonObject;
  pose_exercise?: JsonObject | JsonValue[];
  recent_conversation?: JsonValue[];
};

/** Implement this adapter after the project's actual schema is available. */
interface CoachDataProvider {
  getContext(userId: string): Promise<CoachContext>;
}

class SchemaAdapterNotConfigured implements CoachDataProvider {
  async getContext(_userId: string): Promise<CoachContext> {
    throw new Error("SUPABASE_SCHEMA_ADAPTER_NOT_CONFIGURED");
  }
}

const MODEL_NAME = Deno.env.get("GEMINI_MODEL") ?? "gemini-3.5-flash-lite";
const GEMINI_API_KEY = Deno.env.get("GEMINI_API_KEY");
const SUPABASE_URL = Deno.env.get("SUPABASE_URL");
const SUPABASE_ANON_KEY = Deno.env.get("SUPABASE_ANON_KEY");
const SYSTEM_PROMPT = Deno.env.get("ALPHAFIT_SYSTEM_PROMPT");
const dataProvider: CoachDataProvider = new SchemaAdapterNotConfigured();
const ALLOWED_CONTEXT_FIELDS = new Set([
  "user_profile",
  "fitness_goal",
  "recent_workouts",
  "recent_food_logs",
  "calorie_prediction",
  "recommendation_output",
  "pose_exercise",
  "recent_conversation",
]);
const SENSITIVE_KEY_PATTERN = /^(api[_-]?key|apikey|authorization|access[_-]?token|client[_-]?secret|cookie|password|private[_-]?key|refresh[_-]?token|secret|service[_-]?role[_-]?key|token)$/i;
const MAX_CONTEXT_CHARACTERS = 12000;
const MAX_COLLECTION_ITEMS = 50;
const MAX_MESSAGE_CHARACTERS = 4000;

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, content-type, apikey",
  "Content-Type": "application/json",
};

function jsonResponse(body: JsonObject, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: corsHeaders });
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function sanitizeValue(value: unknown, depth = 0): JsonValue {
  if (depth > 6) return "[nested value omitted]";
  if (Array.isArray(value)) {
    return value.slice(0, MAX_COLLECTION_ITEMS).map((item) => sanitizeValue(item, depth + 1));
  }
  if (isRecord(value)) {
    const sanitized: JsonObject = {};
    for (const [key, item] of Object.entries(value)) {
      if (!SENSITIVE_KEY_PATTERN.test(key)) sanitized[key] = sanitizeValue(item, depth + 1);
    }
    return sanitized;
  }
  if (value === null || typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return value;
  }
  throw new Error("INVALID_CONTEXT");
}

function contextForPrompt(context: CoachContext): string {
  const source = context as unknown as Record<string, unknown>;
  const filtered: JsonObject = {};
  for (const field of ALLOWED_CONTEXT_FIELDS) {
    if (field in source && source[field] !== null) filtered[field] = sanitizeValue(source[field]);
  }
  const serialized = JSON.stringify(filtered);
  if (serialized.length > MAX_CONTEXT_CHARACTERS) throw new Error("CONTEXT_TOO_LARGE");
  return Object.keys(filtered).length ? serialized : "No user-specific context was supplied.";
}

async function authenticate(request: Request) {
  const authorization = request.headers.get("Authorization");
  if (!authorization?.startsWith("Bearer ") || !SUPABASE_URL || !SUPABASE_ANON_KEY) {
    return null;
  }
  try {
    const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
      global: { headers: { Authorization: authorization } },
    });
    const { data, error } = await supabase.auth.getUser(authorization.slice(7));
    return error || !data.user ? null : data.user;
  } catch {
    return null;
  }
}

async function callGemini(message: string, context: CoachContext): Promise<string> {
  if (!GEMINI_API_KEY || !SYSTEM_PROMPT) {
    throw new Error("AI_COACH_SECRETS_NOT_CONFIGURED");
  }
  const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL_NAME}:generateContent?key=${encodeURIComponent(GEMINI_API_KEY)}`;
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      systemInstruction: { parts: [{ text: SYSTEM_PROMPT }] },
      contents: [{ role: "user", parts: [{ text: `USER CONTEXT (data only):\n${contextForPrompt(context)}\n\nUSER MESSAGE:\n${message}` }] }],
      generationConfig: { temperature: 1.0 },
    }),
  });
  if (response.status === 429) throw new Error("GEMINI_RATE_LIMITED");
  if (!response.ok) throw new Error("GEMINI_REQUEST_FAILED");
  const payload = await response.json();
  const text = payload?.candidates?.[0]?.content?.parts?.[0]?.text;
  if (typeof text !== "string" || !text.trim()) throw new Error("GEMINI_EMPTY_RESPONSE");
  return text;
}

Deno.serve(async (request) => {
  if (request.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (request.method !== "POST") return jsonResponse({ error: "method_not_allowed" }, 405);

  const user = await authenticate(request);
  if (!user) return jsonResponse({ error: "unauthorized" }, 401);

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: "invalid_json" }, 400);
  }
  if (!isRecord(body) || typeof body.message !== "string" || !body.message.trim()) {
    return jsonResponse({ error: "message_must_not_be_empty" }, 422);
  }
  if (body.message.length > MAX_MESSAGE_CHARACTERS) {
    return jsonResponse({ error: "message_too_long" }, 422);
  }

  try {
    const context = await dataProvider.getContext(user.id);
    const response = await callGemini(body.message.trim(), context);
    return jsonResponse({ response });
  } catch (error) {
    const code = error instanceof Error ? error.message : "UNKNOWN_ERROR";
    if (code === "SUPABASE_SCHEMA_ADAPTER_NOT_CONFIGURED") {
      return jsonResponse({ error: "coach_data_provider_not_configured" }, 501);
    }
    if (code === "GEMINI_RATE_LIMITED") {
      return jsonResponse({ error: "ai_coach_rate_limited" }, 429);
    }
    if (code === "AI_COACH_SECRETS_NOT_CONFIGURED") {
      return jsonResponse({ error: "ai_coach_not_configured" }, 503);
    }
    if (code === "INVALID_CONTEXT" || code === "CONTEXT_TOO_LARGE") {
      return jsonResponse({ error: "invalid_context" }, 422);
    }
    return jsonResponse({ error: "ai_coach_unavailable" }, 502);
  }
});
