// Fallback gallery data (used when CSV loading fails)
const fallbackGalleryImages = [
  {
    src: 'images/collage/rad_rod.png',
    filename: 'rad_rod.png',
    title: 'Rad Rod AWD',
    description: 'Razor Ground Force Rad Rod AWD. VESC\u00ae based controllers at 8KW',
    attribution: 'https://www.youtube.com/watch?v=NEgMkoUbaqs'
  },
  {
    src: 'images/collage/DemiLama.png',
    filename: 'DemiLama.png',
    title: 'DemiLama',
    description: 'Creative artwork featuring our beloved LispBM mascot',
    attribution: 'https://www.instagram.com/pixiladyart/'
  },
  {
    src: 'images/collage/cat_holiday_03.png',
    filename: 'cat_holiday_03.png',
    title: 'Holiday Cat Animation',
    description: 'Screenshot from a festive LispBM holiday animation',
    attribution: 'https://github.com/laxsjo/'
  },
  {
    src: 'images/collage/lbm-holiday-animation_04.png',
    filename: 'lbm-holiday-animation_04.png',
    title: 'LispBM Holiday Animation',
    description: 'Frame from a LispBM-powered holiday animation project',
    attribution: 'https://github.com/r3n33'
  },
  {
    src: 'images/collage/lispbm.jpeg',
    filename: 'lispbm.jpeg',
    title: 'LispBM Logo',
    description: 'Official LispBM project logo and branding',
    attribution: 'https://www.instagram.com/pixiladyart/'
  },
  {
    src: 'images/collage/lispbm_llama.png',
    filename: 'lispbm_llama.png',
    title: 'Lispy the Llama',
    description: 'Our mascot Lispy the llama in all their glory',
    attribution: 'https://www.instagram.com/pixiladyart/'
  },
  {
    src: 'images/collage/lisprunners.png',
    filename: 'lisprunners.png',
    title: 'Lisp Runners',
    description: 'Dynamic visualization of Lisp processes in action',
    attribution: 'LispBM Project'
  },
  {
    src: 'images/collage/lispwizaard.png',
    filename: 'lispwizaard.png',
    title: 'Lisp Wizard',
    description: 'The mystical Lisp Wizard conjuring code magic',
    attribution: 'LispBM Project'
  },
  {
    src: 'images/collage/llamacouldron.jpg',
    filename: 'llamacouldron.jpg',
    title: 'Llama Cauldron',
    description: 'Brewing up some LispBM magic in the llama cauldron',
    attribution: 'https://www.instagram.com/pixiladyart/'
  },
  {
    src: 'images/collage/xmas_lisp-2024-12-20_11.39.26_04.png',
    filename: 'xmas_lisp-2024-12-20_11.39.26_04.png',
    title: 'Christmas Lisp 2024',
    description: 'Holiday-themed LispBM project from December 2024',
    attribution: 'https://github.com/svenssonjoel/'
  }
];

// Global variable to store gallery data from CSV
let galleryImages = [];

// Function to parse CSV line properly (handles commas in quoted fields)
function parseCSVLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];

    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      result.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current.trim());
  return result;
}

// Function to format attribution (make URLs clickable)
function formatAttribution(attribution) {
  if (attribution.startsWith('http://') || attribution.startsWith('https://')) {
    return `<a href="${attribution}" target="_blank" rel="noopener noreferrer" style="color: #007bff; text-decoration: none;">${attribution}</a>`;
  }
  return attribution;
}

// Function to load and parse CSV data
async function loadGalleryData(noticeElementId) {
  let usingFallback = false;

  try {
    const response = await fetch('image_credits.csv');
    const csvText = await response.text();
    const lines = csvText.trim().split('\n');

    // Skip header row and parse each line
    for (let i = 1; i < lines.length; i++) {
      const [filename, title, description, attribution] = parseCSVLine(lines[i]);
      if (filename && title && description && attribution) {
        galleryImages.push({
          src: `images/collage/${filename}`,
          filename: filename,
          title: title,
          description: description,
          attribution: attribution
        });
      }
    }
  } catch (error) {
    console.log('Could not load CSV data, using fallback:', error);
    galleryImages = [...fallbackGalleryImages];
    usingFallback = true;
  }

  // If no items loaded, use fallback
  if (galleryImages.length === 0) {
    galleryImages = [...fallbackGalleryImages];
    usingFallback = true;
  }

  // Show notice if using fallback data
  if (noticeElementId) {
    const notice = document.getElementById(noticeElementId);
    if (notice) {
      notice.style.display = usingFallback ? 'block' : 'none';
    }
  }
}
