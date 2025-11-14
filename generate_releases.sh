#!/bin/bash

# Script to generate release HTML pages from LispBM changelog
# Usage: ./generate_releases.sh

VERSION_FILE="../lispbm/include/lbm_version.h"
RELEASES_DIR="./releases"
CURRENT_YEAR=$(date +%Y)

# Check if version file exists
if [ ! -f "$VERSION_FILE" ]; then
    echo "Error: Cannot find $VERSION_FILE"
    exit 1
fi

# Create releases directory if it doesn't exist
mkdir -p "$RELEASES_DIR"

# Extract changelog entries from version file
# Format: "Oct 28 2025: Version 0.34.1" or "APR 14 2025: VERSION 0.32.0"
grep -A 500 '/\*! \\page changelog Changelog' "$VERSION_FILE" | \
    grep -iE ': [Vv][Ee][Rr][Ss][Ii][Oo][Nn] [0-9]+\.[0-9]+\.[0-9]+' | \
    while IFS=':' read -r date_part rest; do
        # date_part now contains everything before the colon (the date)
        # Extract version number from the rest
        version=$(echo "$rest" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')

        # Skip if version extraction failed
        if [ -z "$version" ]; then
            continue
        fi

        echo "Generating release page for version $version..."

        # Check if GitHub release exists
        github_url="https://github.com/svenssonjoel/lispBM/releases/tag/$version"
        if curl -s -o /dev/null -w "%{http_code}" "$github_url" | grep -q "200"; then
            github_link="      <p>
        <a href=\"$github_url\" target=\"_blank\" rel=\"noopener noreferrer\">
          View on GitHub →
        </a>
      </p>"
            echo "  - GitHub release found"
        else
            github_link=""
            echo "  - No GitHub release found (skipping link)"
        fi

        # Extract changelog for this version
        # Get all indented lines after this version until we hit a line with 0 indentation
        changelog=$(awk -v ver="$version" '
            $0 ~ ver && /[Vv][Ee][Rr][Ss][Ii][Oo][Nn]/ {
                found=1
                next
            }
            found && /^[^ \t]/ { exit }
            found && /^[ \t]+/ {
                line = $0
                gsub(/^[ \t]+/, "", line)
                if (line ~ /^-/) {
                    gsub(/^- */, "", line)
                    if (in_item) print "</li>"
                    print "      <li>" line
                    in_item=1
                } else if (line != "") {
                    print " " line
                }
            }
            END { if (in_item) print "</li>" }
        ' "$VERSION_FILE")

        # Create HTML file
        cat > "$RELEASES_DIR/release-$version.html" << EOF
<!DOCTYPE html>
<html lang="en-US">

<head>
  <meta charset="UTF-8">
  <meta name="description" content="LispBM version $version release notes and changelog">
  <meta name="keywords" content="lispbm, lisp, release, version $version, changelog">
  <meta name="author" content="Bo Joel Svensson">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <title>LispBM $version Release</title>

  <!-- SEO Meta Tags -->
  <link rel="canonical" href="https://www.lispbm.com/releases/release-$version.html">
  <meta name="robots" content="index, follow">

  <!-- Open Graph Meta Tags -->
  <meta property="og:title" content="LispBM $version Release">
  <meta property="og:description" content="Release notes and changelog for LispBM version $version">
  <meta property="og:image" content="https://www.lispbm.com/images/lispbm_llama_small.png">
  <meta property="og:url" content="https://www.lispbm.com/releases/release-$version.html">
  <meta property="og:type" content="article">

  <link rel="apple-touch-icon" sizes="180x180" href="../ico/apple-touch-icon.png">
  <link rel="icon" type="image/png" sizes="32x32" href="../ico/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="../ico/favicon-16x16.png">
  <link rel="shortcut icon" href="../ico/favicon.ico">

  <link rel="stylesheet" href="../styles.css">
</head>

<body>
  <div id="wrapper">
    <div id="header">
      <h1>LispBM $version</h1>
    </div>

    <div id="content">
      <p><strong>Released:</strong> $date_part</p>

$github_link

      <h2>Changelog</h2>
      <ul>
$changelog
      </ul>

      <hr>

      <p>
        <a href="https://www.lispbm.com/">← Back to LispBM Home</a> |
        <a href="https://github.com/svenssonjoel/lispBM">GitHub Repository</a>
      </p>
    </div>

    <div id="footer">
      <p>&copy; $CURRENT_YEAR Bo Joel Svensson</p>
    </div>
  </div>
</body>
</html>
EOF

        echo "Created $RELEASES_DIR/release-$version.html"
    done

echo ""
echo "Release page generation complete!"
echo "Files created in $RELEASES_DIR/"
