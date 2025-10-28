// =============================================
//   WISANG BRAT API v1.0 
//   Author: Wisang | Full metadata + hit counter
// =============================================

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const os = require('os');
const { chromium } = require('playwright');

const app = express();
const PORT = process.env.PORT || 7860;
const URL = process.env.BRAT_URL || 'https://brat.ngau.org';

// Hit counter (simpan di memory)
let hitCounter = 0;

// Runtime info
const getRuntime = () => {
  const totalMem = os.totalmem() / 1024 / 1024;
  const freeMem = os.freemem() / 1024 / 1024;
  const usedMem = totalMem - freeMem;
  return {
    os: os.type(),
    platform: os.platform(),
    architecture: os.arch(),
    cpuCount: os.cpus().length,
    uptime: `${os.uptime().toFixed(1)} seconds`,
    memoryUsage: `${Math.round(usedMem)} MB used of ${Math.round(totalMem)} MB`
  };
};

// Middleware
app.use(cors());
app.use(express.json());

// Helper: Screenshot
const snap = async (el) => `data:image/png;base64,${(await el.screenshot()).toString('base64')}`;

// Generate BRAT
const generate = async (text) => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    await page.goto(URL, { waitUntil: 'networkidle' });
    await page.fill('textarea, input[type="text"]', text);
    await page.click('button, [onclick], [type="submit"]');
    await page.waitForSelector('img, canvas, .output', { timeout: 15000 });
    
    const img = await page.$('img, canvas');
    return img ? await snap(img) : null;
  } finally {
    await browser.close();
  }
};

// API Route
app.get('/api', async (req, res) => {
  hitCounter++;
  const text = (req.query.text || '').trim();

  const baseResponse = {
    author: "Wisang (JustWisang)",
    repository: { github: "https://github.com/W154N9/wisang-brat-api" },
    hit: hitCounter,
    runtime: getRuntime()
  };

  if (!text) {
    return res.json({
      ...baseResponse,
      message: "Parameter `text` diperlukan"
    });
  }

  if (text.length > 500) {
    return res.json({
      ...baseResponse,
      message: "Max 500 karakter"
    });
  }

  try {
    const image = await generate(text);
    if (!image) {
      return res.json({
        ...baseResponse,
        message: "Gagal generate gambar"
      });
    }

    res.json({
      ...baseResponse,
      message: "Success",
      image
    });
  } catch (err) {
    res.status(500).json({
      ...baseResponse,
      message: `Error: ${err.message}`
    });
  }
});

// Health
app.get('/', (req, res) => {
  res.send(`
    <h1>Wisang BRAT API</h1>
    <p>/api?text=Wisang Ganteng</p>
    <pre>${JSON.stringify({
      author: "Wisang (JustWisang)",
      repository: { github: "https://github.com/W154N9/wisang-brat-api" },
      hit: hitCounter,
      runtime: getRuntime()
    }, null, 2)}</pre>
  `);
});

app.listen(PORT, () => {
  console.log(`Wisang BRAT API jalan di port ${PORT}`);
});
