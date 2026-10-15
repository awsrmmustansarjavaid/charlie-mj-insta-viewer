// Purpose: Display the available demonstration metadata for a selected Story.
import { Link, useParams } from "react-router-dom";
import { stories } from "../data/mockData";
import { formatDate, formatDateTime } from "../utils/dates";

export function StoryInspector() {
  const { id = "" } = useParams();
  const story = stories.find((item) => item.id === id);
  if (!story) return <div className="py-20 text-center">Story not found.</div>;

  return (
    <div className="mx-auto grid max-w-5xl gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
      <div className="overflow-hidden rounded-3xl bg-black"><img src={story.mediaUrl} className="mx-auto max-h-[75vh] w-full object-contain" /></div>
      <aside className="glass rounded-3xl p-6">
        <div className="text-xs uppercase tracking-widest text-violet-300">Story Inspector</div>
        <h1 className="mt-2 text-2xl font-black">@{story.username}</h1>
        <p className="mt-6 text-sm text-zinc-500">Posted</p>
        <p className="font-semibold">{formatDate(story.postedAt)}</p>
        <p className="mt-4 text-sm text-zinc-500">Exact time</p>
        <p className="font-semibold">{story.exactTimeAvailable ? formatDateTime(story.postedAt) : "Unavailable"}</p>
        <p className="mt-4 text-sm text-zinc-500">Mentions</p>
        <p>{story.mentions.length ? story.mentions.join(", ") : "None provided"}</p>
        <p className="mt-4 text-sm text-zinc-500">Location</p>
        <p>{story.location ?? "Unavailable"}</p>
        <p className="mt-4 text-sm text-zinc-500">Music</p>
        <p>{story.music ?? "Unavailable"}</p>
        <p className="mt-4 text-sm text-zinc-500">Link</p>
        <p>{story.link ?? "Unavailable"}</p>
        <div className="mt-6 rounded-xl bg-violet-400/10 p-3 text-xs text-violet-200">Archived metadata is shown only because this demo story contains a captured timestamp and metadata.</div>
        <Link to={`/profile/${story.username}`} className="mt-5 inline-block text-sm text-violet-300">← Back to profile</Link>
      </aside>
    </div>
  );
}