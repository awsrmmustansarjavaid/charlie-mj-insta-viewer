# Frontend Design Guide

## 1. Visual direction

Use a modern desktop-first dark interface with a restrained violet/blue accent system. Provide a light theme as an option. Prioritize readable density, predictable navigation and consistent interaction patterns over decorative effects.

See `../assets/charlie-mj-insta-viewer-banner.png` for the concept artwork. It is a visual direction mockup, not a screenshot of a completed application.

## 2. Main layout

- Left sidebar: grouped navigation.
- Top bar: global search, monitoring state, notifications and quick-add action.
- Main canvas: responsive cards, tables, grids and detail pages.
- Optional right inspector: metadata for selected media.

## 3. Suggested navigation groups

### Main
- Dashboard
- Profile Search
- Monitored Profiles
- Favorites

### Instagram Content
- Stories
- Story Calendar
- Story Inspector
- Highlights
- Posts
- Reels
- Reposts
- Profile Pictures
- Followers & Following (only when provider-supported)

### Automation
- Monitoring Bot
- Schedule
- Visibility Tracker
- Mention Tracker
- Notifications

### Media
- Download Manager
- Saved Library
- Collections
- Download History

### Activity
- Activity Timeline
- Search History
- Daily Reports
- Weekly Reports
- Monthly Reports

### Application
- Settings
- Backup & Restore
- About
- Help

## 4. Grid behavior

- Responsive column count based on available width.
- Compact, standard and large card density.
- Grid and list modes.
- Consistent thumbnail aspect ratios.
- Keyboard-accessible focus and actions.
- Hover states must not be the only way to reveal controls.
- Loading skeletons and empty states.
- Clear provider/source indicators.

## 5. Story Inspector

Recommended split layout:
- Large media viewer on the left.
- Metadata panel on the right.
- Header with profile and media identity.
- Separate publication, detection and download timestamps.
- Mention/tag list with source labels.
- Download, save and open-source actions.

## 6. Accessibility and usability

- Maintain sufficient contrast.
- Use descriptive button labels and tooltips.
- Support keyboard navigation.
- Respect reduced-motion preferences.
- Use confirmation for destructive actions.
- Distinguish disabled, unavailable and loading states.
- Do not use color as the only status indicator.
