const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function apiGet<T>(path: string, fallback?: T): Promise<{ data: T; fallbackUsed: boolean }> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    return { data: (await response.json()) as T, fallbackUsed: false };
  } catch (error) {
    if (fallback !== undefined) {
      console.warn("API failed, fallback to mock:", path, error);
      return { data: fallback, fallbackUsed: true };
    }
    throw error;
  }
}

export function shouldForceMock() {
  return process.env.NEXT_PUBLIC_USE_MOCK === "true";
}
