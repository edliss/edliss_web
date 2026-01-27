# Edliss Website - HTML Version

Your PHP website has been converted to pure HTML and is ready to deploy to GitHub Pages!

## What Changed

- **index.php** → **index.html** (with embedded header/footer)
- **privacy.php** → **privacy.html** (with embedded header/footer)
- **kurkum.php** → **kurkum.html** (with embedded header/footer)
- PHP includes removed - all header/footer content is now directly in each HTML file
- Dynamic year (2026) hardcoded in footer
- Link to privacy updated from `/privacy` to `/privacy.html`
- All assets (CSS, fonts, images) copied and ready to use

## Files Included

```
edliss-html/
├── index.html          # Main homepage
├── privacy.html        # Privacy policy page
├── kurkum.html         # Kurkum app page
├── favicon.ico         # Site favicon
├── assets/
│   ├── styles.css      # Main stylesheet
│   ├── kurkum_styles.css  # Kurkum page styles
│   └── fonts/          # All font files
└── README.md           # This file
```

## Deploy to GitHub Pages

### Option 1: New Repository (Easiest)

1. Go to https://github.com/new
2. Name your repository (e.g., `username.github.io` or `edliss-site`)
3. Make it public
4. Don't initialize with README
5. Click "Create repository"

6. In your terminal, navigate to this folder and run:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/username/repository-name.git
git push -u origin main
```

7. Go to repository Settings → Pages
8. Under "Source", select "Deploy from branch"
9. Select "main" branch and "/ (root)" folder
10. Click Save

Your site will be live at: `https://username.github.io/repository-name/`

### Option 2: Using Existing Repository

If you already have a repository, just copy these files into it and push:

```bash
git add .
git commit -m "Convert to static HTML"
git push
```

## Other Free Hosting Options

### Netlify
1. Go to https://app.netlify.com/drop
2. Drag and drop the `edliss-html` folder
3. Done! You get a free URL instantly

### Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. In this folder, run: `vercel`
3. Follow the prompts

### Cloudflare Pages
1. Go to https://pages.cloudflare.com/
2. Connect your GitHub repository or upload directly
3. Deploy

## Future Updates

When you need to update header/footer:
1. Use Find & Replace in your text editor across all HTML files
2. Example: To update the email, search for `ed@edliss.com` and replace all

## Notes

- The copyright year is hardcoded as 2026 (was dynamic PHP)
- Bootstrap JS is included in kurkum.html (you mentioned no JavaScript, but this was in your original file - you can remove it if you don't need Bootstrap features)
- All internal links now point to `.html` files

Good luck with your deployment! 🚀
