// Purpose: Define shared TypeScript data contracts for profiles and Instagram-style media.
export interface Profile {
  username: string;
  displayName: string;
  bio: string;
  avatar: string;
  followers: number;
  following: number;
  postsCount: number;
  isVerified?: boolean;
}

export interface Story {
  id: string;
  username: string;
  title: string;
  mediaUrl: string;
  postedAt?: string;
  exactTimeAvailable: boolean;
  mentions: string[];
  location?: string;
  music?: string;
  link?: string;
  archived: boolean;
}

export interface Post {
  id: string;
  username: string;
  mediaUrl: string;
  caption: string;
  postedAt?: string;
  likes: number;
  comments: number;
  carousel?: string[];
}

export interface Reel {
  id: string;
  username: string;
  mediaUrl: string;
  caption: string;
  postedAt?: string;
  views: number;
}

export interface Repost {
  id: string;
  repostedBy: string;
  originalCreator: string;
  originalPostId: string;
  postedAt?: string;
  originalUrl: string;
}

export interface Comment {
  id: string;
  username: string;
  text: string;
  likes: number;
  postedAt: string;
  replies?: Comment[];
}

export interface AppSettings {
  darkMode: boolean;
  language: "en";
  apiBaseUrl: string;
}