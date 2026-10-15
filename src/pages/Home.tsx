// Purpose: Render the frontend demonstration home dashboard and content previews.
import { Link } from "react-router-dom";
import { SearchBox } from "../components/SearchBox";
import { StoryRing } from "../components/StoryRing";
import { PostCard } from "../components/PostCard";
import { posts, profiles, stories } from "../data/mockData";

export function Home() {
  return (
    <div className="space-y-10">
      <section className="py-10 text-center">
        <p className="mb-3 text-sm uppercase tracking-[0.3em] text-violet-300">Independent public content viewer</p>
        <h1 className="text-4xl font-black sm:text-6xl"><span className="gradient-text">Explore Public Profiles</span></h1>
        <p className="mx-auto mt-4 max-w-2xl text-zinc-400">Search profiles, inspect demo Stories, browse posts and save items locally.</p>
        <div className="mt-8"><SearchBox /></div>
      </section>

      <section>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-bold">Stories</h2>
          <Link to="/stories/charliemj" className="text-sm text-violet-300">Open viewer →</Link>
        </div>
        <div className="flex gap-3 overflow-x-auto pb-2">
          {stories.map((story) => <StoryRing key={story.id} story={story} />)}
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-xl font-bold">Demo profiles</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {profiles.map((profile) => (
            <Link key={profile.username} to={`/profile/${profile.username}`} className="glass rounded-3xl p-5 transition hover:-translate-y-1 hover:bg-white/[0.07]">
              <div className="flex items-center gap-4">
                <img src={profile.avatar} className="h-16 w-16 rounded-full object-cover" />
                <div>
                  <div className="font-bold">@{profile.username}</div>
                  <div className="text-sm text-zinc-400">{profile.displayName}</div>
                  <div className="mt-1 text-xs text-zinc-500">{profile.followers.toLocaleString()} followers</div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-xl font-bold">Recent posts</h2>
        <div className="grid gap-5 md:grid-cols-2">{posts.map((post) => <PostCard key={post.id} post={post} />)}</div>
      </section>
    </div>
  );
}