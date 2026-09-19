import { SearchBox } from "../components/SearchBox";
import { profiles } from "../data/mockData";
import { Link } from "react-router-dom";

export function Search() {
  return (
    <div className="space-y-8">
      <div><h1 className="text-3xl font-black">Search</h1><p className="mt-2 text-zinc-400">Try one of the built-in demo profiles.</p></div>
      <SearchBox />
      <div className="grid gap-4 sm:grid-cols-2">
        {profiles.map((p) => <Link key={p.username} to={`/profile/${p.username}`} className="glass rounded-2xl p-5 hover:bg-white/[0.07]">@{p.username} — {p.displayName}</Link>)}
      </div>
    </div>
  );
}