// =============================================
//   WISANG BRAT API v1.0 - Super Clean Edition
//   Author: Wisang | All in one, no bloat
// =============================================

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const { chromium } = require('playwright');

const app = express();
const PORT = process.env.PORT || 3000;
const URL = process.env.BRAT_URL || 'https://brat.ngau.org';

// Middleware
app.use(cors());
app.use(express.json());
app.use('/api', rateLimit({ windowMs: 60_000, max: 10, message: 'Wisang bilang: Too fast!' }));

// Helper: Screenshot element → base64
const snap = async (el) => `data:image/png;base64,${(await el.screenshot()).toString('base64')}`;

// Core: Generate BRAT image
const generate = async (text) => {
  const browser = await chromium.launch({ headless: process.env.HEADLESS !== 'false' });
  const page = await browser.newPage();
  
  try {
    await page.goto(URL, { waitUntil: 'networkidle' });
    await page.fill('textarea, input[type="text"]', text);
    await page.click('button, [onclick], [type="submit"]');
    await page.waitForSelector('img, canvas, .output', { timeout: 15000 });
    
    const img = await page.$('img, canvas');
    return img ? await snap(img) : 'No image found';
  } finally {
    await browser.close();
  }
};

// API Route
app.get('/api', async (req, res) => {
  const text = (req.query.text || '').trim();
  
  if (!text) return res.status(400).json({ error: 'Wisang minta: ?text= wajib!' });
  if (text.length > 500) return res.status(400).json({ error: 'Max 500 huruf, Wisang ga suka panjang!' });

  console.log(`[Wisang] Generating: "${text}"`);
  
  try {
    const image = await generate(text);
    res.json({ 
      success: true, 
      image, 
      by: 'Wisang',
      tip: 'Jangan lupa kasih bintang di GitHub ya!' 
    });
  } catch (err) {
    res.status(500).json({ error: 'Wisang gagal: ' + err.message });
  }
});

// Health
app.get('/', (req, res) => res.send(`<h1>Wisang BRAT API</h1><p>/api?text=Halo Wisang</p>`));

app.listen(PORT, () => {
  console.log(`\n Wisang BRAT API jalan di http://localhost:${PORT}`);
  console.log(` Coba: http://localhost:${PORT}/api?text=Wisang+Ganteng\n`);
});
