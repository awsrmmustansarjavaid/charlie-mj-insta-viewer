// Purpose: Supply demonstration-only profile, Story, Post, Reel, Repost and comment data.
// Warning: These records are fixtures and must never be presented as live Instagram results.
import type { Comment, Post, Profile, Reel, Repost, Story } from "../types/models";

export const profiles: Profile[] = [
  {
    username: "charliemj",
    displayName: "Charlie MJ",
    bio: "Public-content viewer demo profile.",
    avatar: "https://i.pravatar.cc/240?img=12",
    followers: 128400,
    following: 318,
    postsCount: 84,
    isVerified: true
  },
  {
    username: "alexdev",
    displayName: "Alex Dev",
    bio: "Cloud, code and coffee.",
    avatar: "https://i.pravatar.cc/240?img=33",
    followers: 18200,
    following: 511,
    postsCount: 132
  }
];

export const stories: Story[] = [
  {
    id: "story-1",
    username: "charliemj",
    title: "Morning build",
    mediaUrl: "https://picsum.photos/seed/story1/900/1400",
    postedAt: "2026-08-12T20:04:17+05:00",
    exactTimeAvailable: true,
    mentions: ["@alexdev", "@cloudlab"],
    location: "Islamabad",
    music: "Demo track",
    archived: true
  },
  {
    id: "story-2",
    username: "charliemj",
    title: "Workspace",
    mediaUrl: "https://picsum.photos/seed/story2/900/1400",
    postedAt: "2026-08-12T20:27:29+05:00",
    exactTimeAvailable: true,
    mentions: [],
    archived: true
  },
  {
    id: "story-3",
    username: "alexdev",
    title: "Kubernetes lab",
    mediaUrl: "https://picsum.photos/seed/story3/900/1400",
    postedAt: "2026-08-13T10:15:00+05:00",
    exactTimeAvailable: true,
    mentions: ["@charliemj"],
    archived: false
  }
];

export const posts: Post[] = [
  {
    id: "post-1",
    username: "charliemj",
    mediaUrl: "https://picsum.photos/seed/post1/1200/900",
    caption: "Building a clean DevOps lab one component at a time.",
    postedAt: "2026-08-12T16:30:00+05:00",
    likes: 824,
    comments: 41
  },
  {
    id: "post-2",
    username: "alexdev",
    mediaUrl: "https://picsum.photos/seed/post2/1200/900",
    caption: "Local Kubernetes experiments today.",
    postedAt: "2026-08-13T11:20:00+05:00",
    likes: 231,
    comments: 19
  }
];

export const reels: Reel[] = [
  {
    id: "reel-1",
    username: "charliemj",
    mediaUrl: "https://picsum.photos/seed/reel1/900/1200",
    caption: "A quick tour of the lab architecture.",
    postedAt: "2026-08-11T19:40:00+05:00",
    views: 42000
  }
];

export const reposts: Repost[] = [
  {
    id: "repost-1",
    repostedBy: "charliemj",
    originalCreator: "alexdev",
    originalPostId: "post-2",
    postedAt: "2026-08-13T18:37:00+05:00",
    originalUrl: "https://www.instagram.com/"
  }
];

export const comments: Comment[] = [
  {
    id: "comment-1",
    username: "alexdev",
    text: "Amazing work!",
    likes: 14,
    postedAt: "2h ago",
    replies: [
      {
        id: "reply-1",
        username: "charliemj",
        text: "Thank you!",
        likes: 4,
        postedAt: "1h ago"
      }
    ]
  },
  {
    id: "comment-2",
    username: "fatima",
    text: "Beautiful setup.",
    likes: 8,
    postedAt: "3h ago"
  }
];