// Purpose: Expose the frontend data-provider adapter used by page components.
// Current implementation: Mock data only; a live provider is not implemented here.
import { profiles, stories, posts, reels, reposts, comments } from "../data/mockData";
import type { Comment, Post, Profile, Reel, Repost, Story } from "../types/models";

// This adapter is deliberately provider-agnostic.
// Replace the mock implementation with a legitimate API integration later.
export interface DataProvider {
  getProfile(username: string): Promise<Profile | null>;
  getStories(username: string): Promise<Story[]>;
  getPosts(username: string): Promise<Post[]>;
  getReels(username: string): Promise<Reel[]>;
  getReposts(username: string): Promise<Repost[]>;
  getComments(postId: string): Promise<Comment[]>;
}

const mockProvider: DataProvider = {
  async getProfile(username) {
    return profiles.find((profile) => profile.username === username.replace("@", "")) ?? null;
  },
  async getStories(username) {
    return stories.filter((story) => story.username === username.replace("@", ""));
  },
  async getPosts(username) {
    return posts.filter((post) => post.username === username.replace("@", ""));
  },
  async getReels(username) {
    return reels.filter((reel) => reel.username === username.replace("@", ""));
  },
  async getReposts(username) {
    return reposts.filter((repost) => repost.repostedBy === username.replace("@", ""));
  },
  async getComments() {
    return comments;
  }
};

// VITE_API_BASE_URL can later point to a legitimate HTTPS API.
// The demo stays on mock data when no endpoint is configured.
export const api: DataProvider = mockProvider;