import { useParams, Link } from "react-router-dom";
import { stories } from "../data/mockData";
import { formatDateTime } from "../utils/dates";

export function Stories() {
  const { username = "charliemj" } = useParams();
  const items = stories.filter((s) => s.username === username);
  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between"><div><h1 className="text-3xl font-black">Stories</h1><p className="text-zinc-400">@{username}</p></div><Link to={`/inspector/${items[0]?.id}`} className="rounded-xl bg-white px-4 py-2 text-sm font-semibold text-zinc-950">Story Inspector</Link></div>
      <div className="grid gap-5 md:grid-cols-3">
        {items.map((story) => <Link key={story.id} to={`/inspector/${story.id}`} className="glass overflow-hidden rounded-3xl"><img src={story.mediaUrl} className="aspect-[4/5] w-full object-cover" /><div className="p-4"><div className="font-bold">{story.title}</div><div className="mt-1 text-xs text-zinc-500">{formatDateTime(story.postedAt)}</div></div></Link>)}
      </div>
    </div>
  );
}