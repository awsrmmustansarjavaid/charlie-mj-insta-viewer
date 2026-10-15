// Purpose: Render a profile detail page using the configured frontend data adapter.
import { Link, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { api } from "../services/api";
import type { Profile as ProfileType, Post, Reel, Story } from "../types/models";
import { PostCard } from "../components/PostCard";
import { formatDateTime } from "../utils/dates";

export function Profile() {
  const { username = "" } = useParams();
  const [profile, setProfile] = useState<ProfileType | null>(null);
  const [stories, setStories] = useState<Story[]>([]);
  const [posts, setPosts] = useState<Post[]>([]);
  const [reels, setReels] = useState<Reel[]>([]);

  useEffect(() => {
    api.getProfile(username).then(setProfile);
    api.getStories(username).then(setStories);
    api.getPosts(username).then(setPosts);
    api.getReels(username).then(setReels);
  }, [username]);

  if (!profile) return <div className="py-20 text-center text-zinc-400">Profile not found in demo data.</div>;

  return (
    <div className="space-y-8">
      <section className="glass rounded-3xl p-6">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-center">
          <img src={profile.avatar} className="h-28 w-28 rounded-full object-cover ring-2 ring-violet-400/50" />
          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-2xl font-black">@{profile.username}</h1>
              {profile.isVerified && <span className="rounded-full bg-sky-400/15 px-2 py-1 text-xs text-sky-300">Verified demo</span>}
            </div>
            <p className="mt-2 max-w-xl text-zinc-400">{profile.bio}</p>
            <div className="mt-4 flex gap-5 text-sm text-zinc-300">
              <span><b>{profile.postsCount}</b> posts</span>
              <span><b>{profile.followers.toLocaleString()}</b> followers</span>
              <span><b>{profile.following}</b> following</span>
            </div>
          </div>
          <Link to={`/stories/${profile.username}`} className="rounded-xl bg-white px-4 py-2 text-center font-semibold text-zinc-950">Stories</Link>
        </div>
      </section>

      <section>
        <div className="mb-4 flex items-center justify-between"><h2 className="text-xl font-bold">Story archive</h2><span className="text-xs text-zinc-500">Exact metadata only when supplied</span></div>
        <div className="grid gap-4 sm:grid-cols-3">
          {stories.map((story) => (
            <Link key={story.id} to={`/inspector/${story.id}`} className="glass rounded-2xl p-4">
              <img src={story.mediaUrl} className="mb-3 aspect-[4/5] rounded-xl object-cover" />
              <div className="font-semibold">{story.title}</div>
              <div className="text-xs text-zinc-500">{formatDateTime(story.postedAt)}</div>
              <div className="mt-2 text-xs text-violet-300">{story.archived ? "Archived while available" : "Currently available"}</div>
            </Link>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-xl font-bold">Posts</h2>
        <div className="grid gap-5 md:grid-cols-2">{posts.map((post) => <PostCard key={post.id} post={post} />)}</div>
      </section>

      <section>
        <h2 className="mb-4 text-xl font-bold">Reels</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {reels.map((reel) => <div key={reel.id} className="glass overflow-hidden rounded-3xl"><img src={reel.mediaUrl} className="aspect-[3/4] w-full object-cover" /><div className="p-4"><p>{reel.caption}</p><p className="mt-2 text-xs text-zinc-500">{reel.views.toLocaleString()} demo views</p></div></div>)}
        </div>
      </section>
    </div>
  );
}