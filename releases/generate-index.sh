#!/bin/bash

# Generate releases directory index with simple file listing
# Usage: ./generate-index.sh

RELEASES_DIR="/home/joels/Current/lispbm.com/releases"
OUTPUT_FILE="$RELEASES_DIR/index.html"

cd "$RELEASES_DIR"

# Start building the HTML file
cat > "$OUTPUT_FILE" << 'EOF'
<!DOCTYPE html>
<html lang="en-US">
<head>
  <meta charset="UTF-8">
  <meta name="description" content="LispBM Release Changelogs - Browse all version release notes and changelogs">
  <meta name="keywords" content="lispbm, releases, changelog, version history, release notes">
  <meta name="author" content="Bo Joel Svensson">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <title>LispBM Releases - Changelog Directory</title>

  <!-- SEO Meta Tags -->
  <link rel="canonical" href="https://www.lispbm.com/releases/" />
  <meta name="robots" content="index, follow">

  <link rel="stylesheet" href="../styles.css">

  <style>
    .release-list {
      background: white;
      padding: 30px;
      border-radius: 5px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .release-list ul {
      list-style-type: none;
      padding: 0;
    }

    .release-list li {
      margin: 10px 0;
      padding: 10px;
      border-bottom: 1px solid #eee;
    }

    .release-list li:last-child {
      border-bottom: none;
    }

    .release-list a {
      color: #0056b3;
      text-decoration: none;
      font-size: 1.1em;
      display: block;
    }

    .release-list a:hover {
      color: #003d82;
      text-decoration: underline;
    }

    h1 {
      color: #333;
      border-bottom: 2px solid #0056b3;
      padding-bottom: 10px;
    }

    .intro-text {
      color: #666;
      margin-bottom: 30px;
      line-height: 1.6;
    }
  </style>
</head>

<body class="with-background">
  <div class="container">
    <div class="nav-menu">
      <a href="https://www.lispbm.com/" class="back-link">← Back to LispBM Home</a>
    </div>

    <h1>LispBM Release Changelogs</h1>

    <div class="intro-text">
      <p>For the latest release information and test reports, see the <a href="https://www.lispbm.com/#testlogs">Testing section</a>.</p>
    </div>

    <div class="release-list">
      <ul>
EOF

# Find all release-*.html files, sort them in reverse version order (newest first)
# Extract version numbers for proper sorting
for file in release-*.html; do
  # Extract version number (e.g., "0.34.1" from "release-0.34.1.html")
  version=$(echo "$file" | sed 's/release-//;s/.html//')
  echo "$version $file"
done | sort -t. -k1,1nr -k2,2nr -k3,3nr | while read version file; do
  # Create display name from filename
  display_name=$(echo "$file" | sed 's/.html$//' | sed 's/release-/Version /')

  # Add list item
  echo "        <li><a href=\"$file\">$display_name</a></li>" >> "$OUTPUT_FILE"
done

# Close the HTML
cat >> "$OUTPUT_FILE" << 'EOF'
      </ul>
    </div>

    <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
      <p>&copy; 2025 Bo Joel Svensson. LispBM Project.</p>
    </footer>
  </div>
</body>
</html>
EOF

echo "Generated $OUTPUT_FILE with $(grep -c '<li>' "$OUTPUT_FILE") releases"
