// Purpose: Declare the React application routes and connect page components.
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Home } from "./pages/Home";
import { Search } from "./pages/Search";
import { Profile } from "./pages/Profile";
import { Stories } from "./pages/Stories";
import { StoryInspector } from "./pages/StoryInspector";
import { Posts, Reels, Reposts, Comments, Highlights, Timeline, Calendar } from "./pages/ContentPages";
import { Saved, History, About, Privacy, Terms } from "./pages/LocalPages";
import { Settings } from "./pages/Settings";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<Search />} />
          <Route path="/profile/:username" element={<Profile />} />
          <Route path="/stories/:username" element={<Stories />} />
          <Route path="/inspector/:id" element={<StoryInspector />} />
          <Route path="/posts" element={<Posts />} />
          <Route path="/reels" element={<Reels />} />
          <Route path="/reposts" element={<Reposts />} />
          <Route path="/comments" element={<Comments />} />
          <Route path="/highlights" element={<Highlights />} />
          <Route path="/timeline" element={<Timeline />} />
          <Route path="/calendar" element={<Calendar />} />
          <Route path="/saved" element={<Saved />} />
          <Route path="/history" element={<History />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/about" element={<About />} />
          <Route path="/privacy" element={<Privacy />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="*" element={<Home />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}