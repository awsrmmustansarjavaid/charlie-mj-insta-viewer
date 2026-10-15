// Purpose: Encapsulate browser localStorage operations for saved items, history and settings.
// Desktop migration note: Replace or adapt this storage boundary when SQLite is introduced.
const SAVED_KEY = "cmj_saved_items";
const HISTORY_KEY = "cmj_search_history";
const SETTINGS_KEY = "cmj_settings";

export function readSaved(): string[] {
  return JSON.parse(localStorage.getItem(SAVED_KEY) ?? "[]");
}

export function toggleSaved(id: string): string[] {
  const current = readSaved();
  const next = current.includes(id) ? current.filter((item) => item !== id) : [...current, id];
  localStorage.setItem(SAVED_KEY, JSON.stringify(next));
  return next;
}

export function readHistory(): string[] {
  return JSON.parse(localStorage.getItem(HISTORY_KEY) ?? "[]");
}

export function addHistory(username: string): string[] {
  const normalized = username.replace("@", "").trim();
  const next = [normalized, ...readHistory().filter((item) => item !== normalized)].slice(0, 20);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(next));
  return next;
}

export function clearHistory(): void {
  localStorage.removeItem(HISTORY_KEY);
}

export interface StoredSettings {
  darkMode: boolean;
  language: "en";
  apiBaseUrl: string;
}

export function readSettings(): StoredSettings {
  return JSON.parse(
    localStorage.getItem(SETTINGS_KEY) ??
      JSON.stringify({ darkMode: true, language: "en", apiBaseUrl: "" })
  );
}

export function saveSettings(settings: StoredSettings): void {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}