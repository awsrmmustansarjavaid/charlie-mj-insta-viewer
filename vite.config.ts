import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages needs the repository name as the Vite base path.
// Change this if you rename the GitHub repository.
export default defineConfig({
  plugins: [react()],
  base: "/charlie-mj-insta-viewer/",
});