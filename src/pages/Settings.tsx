import { useEffect, useState } from "react";
import { readSettings, saveSettings } from "../store/storage";

export function Settings() {
  const [settings, setSettings] = useState(readSettings());

  useEffect(() => {
    document.documentElement.classList.toggle("dark", settings.darkMode);
    saveSettings(settings);
  }, [settings]);

  return <section className="mx-auto max-w-2xl space-y-6">
    <div><h1 className="text-3xl font-black">Settings</h1><p className="mt-2 text-zinc-400">Local browser settings for the demo.</p></div>
    <div className="glass rounded-3xl p-6 space-y-6">
      <label className="flex items-center justify-between gap-4"><span>Dark mode</span><input type="checkbox" checked={settings.darkMode} onChange={e=>setSettings({...settings,darkMode:e.target.checked})}/></label>
      <label className="block"><span className="text-sm text-zinc-400">Future API base URL</span><input value={settings.apiBaseUrl} onChange={e=>setSettings({...settings,apiBaseUrl:e.target.value})} placeholder="https://api.example.com" className="mt-2 w-full rounded-xl border border-white/10 bg-black/30 p-3 outline-none"/></label>
      <p className="text-xs text-zinc-500">Do not put private credentials, cookies or secret tokens in a browser-side API URL.</p>
    </div>
  </section>;
}