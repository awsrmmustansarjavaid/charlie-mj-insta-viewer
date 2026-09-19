export function profileUrl(username: string): string {
  return `https://www.instagram.com/${username.replace("@", "")}/`;
}