// Purpose: Build canonical Instagram profile URLs from normalized usernames.
export function profileUrl(username: string): string {
  return `https://www.instagram.com/${username.replace("@", "")}/`;
}