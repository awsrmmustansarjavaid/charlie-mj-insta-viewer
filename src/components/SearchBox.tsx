import { Search } from "lucide-react";
import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { addHistory } from "../store/storage";

export function SearchBox() {
  const [value, setValue] = useState("");
  const navigate = useNavigate();

  function submit(event: FormEvent) {
    event.preventDefault();
    const username = value.replace("@", "").trim();
    if (!username) return;
    addHistory(username);
    navigate(`/profile/${username}`);
  }

  return (
    <form onSubmit={submit} className="mx-auto flex max-w-2xl items-center gap-2 rounded-2xl border border-white/10 bg-white/[0.06] p-2 shadow-glow">
      <Search className="ml-2 text-zinc-500" size={20} />
      <input
        value={value}
        onChange={(event) => setValue(event.target.value)}
        className="w-full bg-transparent px-2 py-3 outline-none placeholder:text-zinc-600"
        placeholder="Search Instagram username"
        aria-label="Instagram username"
      />
      <button className="rounded-xl bg-white px-4 py-2 font-semibold text-zinc-950">Search</button>
    </form>
  );
}