// Purpose: Render a post preview card and its local save interaction.
import { Bookmark, Heart, MessageCircle } from "lucide-react";
import { useState } from "react";
import type { Post } from "../types/models";
import { formatDateTime } from "../utils/dates";
import { toggleSaved, readSaved } from "../store/storage";

export function PostCard({ post }: { post: Post }) {
  const [saved, setSaved] = useState(readSaved().includes(post.id));

  function save() {
    const next = toggleSaved(post.id);
    setSaved(next.includes(post.id));
  }

  return (
    <article className="glass overflow-hidden rounded-3xl">
      <img src={post.mediaUrl} className="aspect-[4/3] w-full object-cover" />
      <div className="p-4">
        <div className="mb-3 flex items-center justify-between">
          <span className="font-semibold">@{post.username}</span>
          <span className="text-xs text-zinc-500">{formatDateTime(post.postedAt)}</span>
        </div>
        <p className="text-zinc-300">{post.caption}</p>
        <div className="mt-4 flex items-center gap-4 text-sm text-zinc-400">
          <span className="flex items-center gap-1"><Heart size={16} /> {post.likes}</span>
          <span className="flex items-center gap-1"><MessageCircle size={16} /> {post.comments}</span>
          <button onClick={save} className="ml-auto"><Bookmark size={18} fill={saved ? "currentColor" : "none"} /></button>
        </div>
      </div>
    </article>
  );
}