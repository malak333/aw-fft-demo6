# Final Fantasy Tactics - PlayStation Website

A fan-made informational website about **Final Fantasy Tactics** for the Sony PlayStation (1997).

## Features

- Comprehensive overview of the game including story, gameplay, job system, music, and legacy
- Responsive design that works on desktop, tablet, and mobile
- Accessible semantic HTML with proper heading structure, ARIA labels, and keyboard navigation
- Smooth scrolling navigation
- No external dependencies — works offline

## Files

- `index.html` — Main website page
- `styles.css` — Styling and responsive layout
- `script.js` — Smooth scroll navigation behavior
- `test_website.py` — Automated test suite (HTML structure, accessibility, content, CSS, JS)
- `README.md` — This file

## How to View

1. Open `index.html` in any modern web browser.
2. No build step or server required.

Alternatively, you can serve the files locally:

```bash
# Using Python 3
python -m http.server 8000

# Using Node.js (if available)
npx serve .

# Using PHP
php -S localhost:8000
```

Then navigate to `http://localhost:8000` in your browser.

## Running Tests

This project includes an automated test suite written in Python that validates:

- **File existence** — All required project files are present
- **HTML structure** — DOCTYPE, lang attribute, charset, viewport, semantic elements
- **Accessibility** — ARIA labels, heading hierarchy, focus indicators, no empty links/images
- **Content accuracy** — Required sections, character names, game facts, release dates
- **CSS quality** — Responsive media queries, box-sizing reset, print styles
- **JavaScript quality** — DOM-ready wrapper, no alert/confirm, no inline handlers
- **Best practices** — No deprecated tags, no inline styles, no javascript: URIs

```bash
# Run all tests (requires Python 3)
python test_website.py
```

Run the tests and verify they pass. If any fail, review the error output for details.

## About the Game

Final Fantasy Tactics was developed by Square for the PlayStation. Square published the Japanese release, and Sony Computer Entertainment published the North American release. It was released in Japan on June 20, 1997, and in North America on January 28, 1998. The game is a tactical RPG set in the world of Ivalice, featuring a complex political narrative, a deep job system, and turn-based grid combat.

## License

This is a fan-made informational website. Final Fantasy Tactics is a trademark of Square Enix Co., Ltd. All game-related content belongs to their respective owners.
