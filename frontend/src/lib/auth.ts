const SESSION_TOKEN_KEY = "aegis_session_token";
const SESSION_CHANGE_EVENT = "aegis-session-change";
const AUTH_API_PREFIX = "/api/v1/auth";

type SafeUser = {
  user_id: number;
  full_name: string;
  email: string;
  role: string;
};

type LoginResponse = {
  access_token: string;
  token_type: "bearer";
  expires_at: string;
  user: SafeUser;
};

type ApiErrorResponse = {
  error?: {
    code?: unknown;
    message?: unknown;
  };
};

function getApiBaseUrl(): string {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (!baseUrl) {
    throw new Error("API is not configured. Set NEXT_PUBLIC_API_BASE_URL in frontend/.env.local.");
  }
  return baseUrl.replace(/\/+$/, "");
}

function getApiErrorMessage(payload: unknown, status: number): string {
  if (typeof payload === "object" && payload !== null && "error" in payload) {
    const message = (payload as ApiErrorResponse).error?.message;
    if (typeof message === "string" && message.trim()) {
      return message;
    }
  }
  return `The API request failed (${status}). Please try again.`;
}

function getRegistrationErrorMessage(payload: unknown, status: number): string {
  if (typeof payload === "object" && payload !== null && "error" in payload) {
    const code = (payload as ApiErrorResponse).error?.code;
    if (code === "EMAIL_ALREADY_REGISTERED" || status === 409) {
      return "An account with this email already exists. Try signing in instead.";
    }
  }

  if (status === 422) {
    return "Please check the name, email, and password requirements and try again.";
  }
  if (status >= 500) {
    return "The registration service is unavailable right now. Please try again later.";
  }
  return "We could not create your account. Check your details and try again.";
}

async function post(
  path: string,
  options: { body?: object; token?: string } = {},
  getErrorMessage = getApiErrorMessage,
): Promise<Response> {
  getApiBaseUrl();

  const headers = new Headers({ Accept: "application/json" });
  if (options.body) {
    headers.set("Content-Type", "application/json");
  }
  if (options.token) {
    headers.set("Authorization", `Bearer ${options.token}`);
  }

  let response: Response;
  try {
    response = await fetch(path, {
      method: "POST",
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    throw new Error("Could not reach the AEGIS API. Check the backend connection and API URL.");
  }

  if (!response.ok) {
    let payload: unknown;
    try {
      payload = await response.json();
    } catch {
      payload = undefined;
    }
    throw new Error(getErrorMessage(payload, response.status));
  }

  return response;
}

export async function registerAccount(
  fullName: string,
  email: string,
  password: string,
): Promise<void> {
  await post(
    `${AUTH_API_PREFIX}/register`,
    { body: { full_name: fullName, email, password } },
    getRegistrationErrorMessage,
  );
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await post(`${AUTH_API_PREFIX}/login`, {
    body: { email, password },
  });

  let result: unknown;
  try {
    result = await response.json();
  } catch {
    throw new Error("The API returned an unreadable login response.");
  }

  if (
    typeof result !== "object" ||
    result === null ||
    !("access_token" in result) ||
    typeof result.access_token !== "string" ||
    !result.access_token ||
    !("token_type" in result) ||
    typeof result.token_type !== "string" ||
    result.token_type.toLowerCase() !== "bearer" ||
    !("expires_at" in result) ||
    typeof result.expires_at !== "string" ||
    !("user" in result) ||
    typeof result.user !== "object" ||
    result.user === null
  ) {
    throw new Error("The API returned an invalid login response.");
  }

  const user = result.user;
  if (
    !("user_id" in user) ||
    typeof user.user_id !== "number" ||
    !("full_name" in user) ||
    typeof user.full_name !== "string" ||
    !("email" in user) ||
    typeof user.email !== "string" ||
    !("role" in user) ||
    typeof user.role !== "string"
  ) {
    throw new Error("The API returned an invalid login response.");
  }

  return {
    access_token: result.access_token,
    token_type: "bearer",
    expires_at: result.expires_at,
    user: {
      user_id: user.user_id,
      full_name: user.full_name,
      email: user.email,
      role: user.role,
    },
  };
}

export async function logout(token: string): Promise<void> {
  await post(`${AUTH_API_PREFIX}/logout`, { token });
}

export function getSessionToken(): string | null {
  return window.sessionStorage.getItem(SESSION_TOKEN_KEY);
}

export function hasActiveSession(): boolean {
  return Boolean(getSessionToken());
}

export function subscribeToSession(listener: () => void): () => void {
  window.addEventListener(SESSION_CHANGE_EVENT, listener);
  return () => window.removeEventListener(SESSION_CHANGE_EVENT, listener);
}

export function saveSessionToken(token: string): void {
  window.sessionStorage.setItem(SESSION_TOKEN_KEY, token);
  window.dispatchEvent(new Event(SESSION_CHANGE_EVENT));
}

export function clearSessionToken(): void {
  window.sessionStorage.removeItem(SESSION_TOKEN_KEY);
  window.dispatchEvent(new Event(SESSION_CHANGE_EVENT));
}
