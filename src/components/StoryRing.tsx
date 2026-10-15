// Purpose: Render a profile's Story preview ring and navigation link.
import type { Story } from "../types/models";
import { Link } from "react-router-dom";

export function StoryRing({ story }: { story: Story }) {
  return (
    <Link to={`/stories/${story.username}`} className="group flex w-24 flex-col items-center gap-2">
      <div className="rounded-full bg-gradient-to-tr from-violet-500 via-fuchsia-500 to-sky-400 p-[3px]">
        <img src={story.mediaUrl} className="h-16 w-16 rounded-full border-2 border-zinc-950 object-cover" />
      </div>
      <span className="w-full truncate text-center text-xs text-zinc-300">{story.title}</span>
    </Link>
  );
}