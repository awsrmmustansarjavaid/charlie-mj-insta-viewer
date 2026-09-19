import { Link } from "react-router-dom";
import { comments, posts, reels, reposts, stories } from "../data/mockData";
import { PostCard } from "../components/PostCard";
import { formatDateTime } from "../utils/dates";

export function Posts() { return <section><h1 className="mb-5 text-3xl font-black">Posts</h1><div className="grid gap-5 md:grid-cols-2">{posts.map(p => <PostCard key={p.id} post={p}/>)}</div></section>; }

export function Reels() { return <section><h1 className="mb-5 text-3xl font-black">Reels</h1><div className="grid gap-5 sm:grid-cols-2 md:grid-cols-3">{reels.map(r => <article key={r.id} className="glass overflow-hidden rounded-3xl"><img src={r.mediaUrl} className="aspect-[3/4] w-full object-cover"/><div className="p-4"><b>@{r.username}</b><p className="mt-2 text-zinc-300">{r.caption}</p><p className="mt-2 text-xs text-zinc-500">{r.views.toLocaleString()} demo views</p></div></article>)}</div></section>; }

export function Reposts() { return <section><h1 className="mb-5 text-3xl font-black">Reposts</h1><div className="space-y-4">{reposts.map(r => <article key={r.id} className="glass rounded-2xl p-5"><div className="text-sm text-zinc-400">Reposted by</div><div className="font-bold">@{r.repostedBy}</div><div className="mt-3 text-sm text-zinc-400">Original creator</div><div className="font-semibold">@{r.originalCreator}</div><div className="mt-3 text-sm text-zinc-500">{formatDateTime(r.postedAt)}</div><a href={r.originalUrl} target="_blank" rel="noreferrer" className="mt-4 inline-block text-violet-300">Open original →</a></article>)}</div></section>; }

export function Comments() { return <section><h1 className="mb-5 text-3xl font-black">Comment Explorer</h1><div className="space-y-4">{comments.map(c => <article key={c.id} className="glass rounded-2xl p-5"><b>@{c.username}</b><p className="mt-2 text-zinc-300">{c.text}</p><p className="mt-2 text-xs text-zinc-500">♥ {c.likes} · {c.postedAt}</p>{c.replies?.map(r => <div key={r.id} className="mt-4 ml-6 border-l border-white/10 pl-4 text-sm"><b>@{r.username}</b><p>{r.text}</p></div>)}</article>)}</div></section>; }

export function Highlights() { return <section><h1 className="mb-5 text-3xl font-black">Highlights</h1><div className="grid gap-4 sm:grid-cols-3">{["Builds","Travel","Labs"].map((x,i)=><div key={x} className="glass rounded-3xl p-6"><div className="mb-4 h-24 rounded-2xl bg-gradient-to-br from-violet-500/30 to-sky-500/20"/><b>{x}</b><p className="mt-1 text-xs text-zinc-500">{i+2} demo items</p></div>)}</div></section>; }

export function Timeline() { return <section><h1 className="mb-5 text-3xl font-black">Content Timeline</h1><div className="space-y-3">{[...stories,...posts,...reels].map((item:any)=><div key={item.id} className="glass rounded-2xl p-4"><span className="text-xs text-violet-300">{item.id}</span><div className="font-semibold">@{item.username}</div><div className="text-sm text-zinc-500">{formatDateTime(item.postedAt)}</div></div>)}</div></section>; }

export function Calendar() { return <section><h1 className="mb-5 text-3xl font-black">Story Calendar</h1><div className="grid gap-4 sm:grid-cols-3">{stories.map(s=><Link key={s.id} to={`/inspector/${s.id}`} className="glass rounded-2xl p-5"><div className="text-xs text-zinc-500">{formatDateTime(s.postedAt)}</div><div className="mt-2 font-bold">{s.title}</div></Link>)}</div></section>; }