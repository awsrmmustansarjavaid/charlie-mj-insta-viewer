import { useState } from "react";
import { Link } from "react-router-dom";
import { clearHistory, readHistory, readSaved } from "../store/storage";

export function Saved() {
  const [saved] = useState(readSaved());
  return <section><h1 className="text-3xl font-black">Saved Library</h1><p className="mt-2 text-zinc-400">Saved item IDs stored locally in your browser.</p><div className="mt-6 space-y-3">{saved.length ? saved.map(id=><div key={id} className="glass rounded-xl p-4">{id}</div>) : <div className="glass mt-6 rounded-2xl p-6">Nothing saved yet. Use the bookmark button on a post.</div>}</div></section>;
}

export function History() {
  const [history, setHistory] = useState(readHistory());
  return <section><div className="flex items-center justify-between"><div><h1 className="text-3xl font-black">Search History</h1><p className="mt-2 text-zinc-400">Stored locally; never sent by this demo.</p></div>{history.length>0 && <button onClick={()=>{clearHistory();setHistory([])}} className="rounded-xl border border-white/10 px-4 py-2 text-sm">Clear</button>}</div><div className="mt-6 space-y-3">{history.map(x=><Link key={x} to={`/profile/${x}`} className="glass block rounded-xl p-4">@{x}</Link>)}</div></section>;
}

export function About() { return <section className="prose prose-invert max-w-3xl"><h1>About</h1><p>Charlie MJ Insta is an independent frontend demonstration for browsing public-content data through a replaceable provider layer.</p><p>It is not affiliated with or endorsed by Instagram or Meta.</p></section>; }
export function Privacy() { return <section className="max-w-3xl space-y-4"><h1 className="text-3xl font-black">Privacy</h1><p className="text-zinc-400">This demo stores saved IDs, search history and settings in your browser localStorage. It does not request Instagram passwords or session cookies.</p></section>; }
export function Terms() { return <section className="max-w-3xl space-y-4"><h1 className="text-3xl font-black">Terms</h1><p className="text-zinc-400">Use this project only with data and media you are authorized to access and retain. The demo contains sample data for development.</p></section>; }