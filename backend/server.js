require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');
const admin = require('firebase-admin');

// Initialize Firebase Admin — use env vars on production, fallback to JSON file locally
if (process.env.FIREBASE_PROJECT_ID) {
  admin.initializeApp({
    credential: admin.credential.cert({
      projectId: process.env.FIREBASE_PROJECT_ID,
      clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
      privateKey: (process.env.FIREBASE_PRIVATE_KEY || '').replace(/\\n/g, '\n'),
    })
  });
} else {
  const serviceAccount = require('./social-media-images-agent-firebase-adminsdk-fbsvc-823df3cf6c.json');
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
  });
}

// Initialize Postgres
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

const app = express();
app.use(cors());
app.use(express.json());

// Auth Middleware
async function verifyToken(req, res, next) {
  const token = req.headers.authorization?.split('Bearer ')[1];
  if (!token) return res.status(401).json({ success: false, message: 'No token provided' });
  try {
    const decodedToken = await admin.auth().verifyIdToken(token);
    req.user = decodedToken;
    next();
  } catch (error) {
    res.status(401).json({ success: false, message: 'Invalid token', error: error.message });
  }
}

app.use(verifyToken);

// List Clients
app.get('/api/clients', async (req, res) => {
  try {
    const { rows } = await pool.query('SELECT * FROM ks_clients ORDER BY created_at DESC');
    res.json({ success: true, clients: rows });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// Create Client
app.post('/api/clients', async (req, res) => {
  const b = req.body;
  const cid = b.client_id || (b.business_name || 'c').toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '') + '_' + Date.now().toString(36);
  
  const query = `
    INSERT INTO ks_clients (
      client_id, firebase_uid, business_name, tagline, established_year, location, brand_category, brand_positioning, 
      phone_primary, phone_display, wa_phone_id, wa_token, fb_page_id, fb_access_token, ig_node_id, ig_credential_id, 
      kie_api_key, imgbb_api_key, serp_api_key, calendarific_api_key, daily_cron, 
      timezone, prompt_poster, prompt_enhance, prompt_planner, prompt_morning, prompt_welcome
    ) VALUES (
      $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26, $27
    )
  `;
  const values = [
    cid, req.user.uid, b.business_name, b.tagline, b.established_year, b.location, b.brand_category, b.brand_positioning,
    b.phone_primary, b.phone_display, b.wa_phone_id, b.wa_token, b.fb_page_id, b.fb_access_token, b.ig_node_id, b.ig_credential_id,
    b.kie_api_key, b.imgbb_api_key, b.serp_api_key, b.calendarific_api_key, b.daily_cron || '0 12 * * 1-6',
    b.timezone || 'Asia/Kolkata', b.prompt_poster, b.prompt_enhance, b.prompt_planner, b.prompt_morning, b.prompt_welcome
  ];

  try {
    await pool.query(query, values);
    res.json({ success: true, message: 'Registered', client_id: cid });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// Update Client
app.put('/api/clients', async (req, res) => {
  const b = req.body;
  const query = `
    UPDATE ks_clients SET 
      business_name=$1, tagline=$2, established_year=$3, location=$4, brand_category=$5, brand_positioning=$6, 
      phone_primary=$7, phone_display=$8, wa_phone_id=$9, wa_token=$10, fb_page_id=$11, fb_access_token=$12, 
      ig_node_id=$13, ig_credential_id=$14, kie_api_key=$15, imgbb_api_key=$16, 
      serp_api_key=$17, calendarific_api_key=$18, daily_cron=$19, timezone=$20, 
      prompt_poster=$21, prompt_enhance=$22, prompt_planner=$23, prompt_morning=$24, prompt_welcome=$25, updated_at=NOW()
    WHERE client_id=$26
  `;
  const values = [
    b.business_name, b.tagline, b.established_year, b.location, b.brand_category, b.brand_positioning,
    b.phone_primary, b.phone_display, b.wa_phone_id, b.wa_token, b.fb_page_id, b.fb_access_token,
    b.ig_node_id, b.ig_credential_id, b.kie_api_key, b.imgbb_api_key,
    b.serp_api_key, b.calendarific_api_key, b.daily_cron, b.timezone,
    b.prompt_poster, b.prompt_enhance, b.prompt_planner, b.prompt_morning, b.prompt_welcome, b.client_id
  ];

  try {
    await pool.query(query, values);
    res.json({ success: true, message: 'Updated' });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// Toggle Client Status
app.patch('/api/clients/:id/toggle', async (req, res) => {
  try {
    await pool.query('UPDATE ks_clients SET is_active=$1, updated_at=NOW() WHERE client_id=$2', [req.body.is_active, req.params.id]);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// Delete Client
app.delete('/api/clients/:id', async (req, res) => {
  const cid = req.params.id;
  try {
    await pool.query('BEGIN');
    await pool.query('DELETE FROM ks_offers WHERE session_id IN (SELECT session_id FROM ks_sessions WHERE client_id=$1)', [cid]);
    await pool.query('DELETE FROM ks_sessions WHERE client_id=$1', [cid]);
    await pool.query('DELETE FROM ks_clients WHERE client_id=$1', [cid]);
    await pool.query('COMMIT');
    res.json({ success: true });
  } catch (err) {
    await pool.query('ROLLBACK');
    res.status(500).json({ success: false, message: err.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Backend server running on port ${PORT}`);
});
