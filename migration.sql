-- MULTI-CLIENT MIGRATION — Run once on PostgreSQL
CREATE TABLE IF NOT EXISTS ks_clients (
  id SERIAL PRIMARY KEY,
  client_id TEXT UNIQUE NOT NULL,
  firebase_uid TEXT,
  business_name TEXT NOT NULL,
  tagline TEXT, established_year TEXT, location TEXT,
  brand_category TEXT DEFAULT 'electronics', brand_positioning TEXT,
  phone_primary TEXT NOT NULL, phone_display TEXT,
  wa_phone_id TEXT NOT NULL, wa_token TEXT NOT NULL,
  fb_page_id TEXT, fb_access_token TEXT,
  ig_node_id TEXT, ig_credential_id TEXT,
  kie_api_key TEXT, imgbb_api_key TEXT,
  openrouter_api_key TEXT, serp_api_key TEXT, calendarific_api_key TEXT,
  brand_colors JSONB DEFAULT '{"primary":"#1A3A6B","secondary":"#C8972A","accent":"#E8621A","background":"#FAFAF7"}',
  -- System Prompts (all configurable from web)
  prompt_poster TEXT,    -- Master poster generation prompt
  prompt_enhance TEXT,   -- Prompt enhancer system message
  prompt_planner TEXT,   -- Content planner system message
  prompt_morning TEXT,   -- Morning WhatsApp message template
  prompt_welcome TEXT,   -- Welcome message template
  daily_cron TEXT DEFAULT '0 12 * * 1-6',
  timezone TEXT DEFAULT 'Asia/Kolkata',
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE ks_sessions ADD COLUMN IF NOT EXISTS client_id TEXT;

-- Auto-migrate Kapoor & Sons
INSERT INTO ks_clients (
  client_id, business_name, tagline, established_year, location, brand_category, brand_positioning,
  phone_primary, phone_display, wa_phone_id, wa_token,
  fb_page_id, fb_access_token, ig_node_id, ig_credential_id,
  kie_api_key, imgbb_api_key, openrouter_api_key, calendarific_api_key
) VALUES (
  'kapoor_sons', 'Kapoor & Sons', 'A Trusted Name Since 1977', '1977', 'Betul, Madhya Pradesh',
  'electronics', 'Betul ka Sabse Trusted Electronics Store. Premium Electronics & Appliance Showroom.',
  '919203580338', '7697551111', '1054458951093025',
  'EAARHnoiO6GcBRfHJZAatAnI2x13ldiUwOHhzL0ssyBJ4k5WJk11YSKFig6Q3Lvloje9dlZCvZCPFm03IURgzk37NfTe6AlhVOYIcnYyVifLRQ6cS9ZBxhCxPZBHrYZBp0H4Lcl1BuUOn9AZCEp6zmKRJM2ate4Gd5LxzoeKHZBPISeuCKlzwoIBz4kkHylT8udPjRwZDZD',
  '971861779351791',
  'EAAXNCSO50WkBRePAplWuVpddAt0vwF0TZAZCyZA8yvWBQArhm86NswmXKzdbhfX4M60aopSZCLQZAFXY01VUD5HO26zA3bylxlCQOkGFBg9lnTAHEp6Jjus2sdt7AXBXCZBTKlTQJkmIaMTXkKA7wIjyMYbuJ9XBKCVzVTOXC8QnV6ffbhkgStGicQs5YTpV6bcl8h702M',
  '17841453240936127', '7MwIGchVTqOxa9K3',
  'f52d9b265c5ebb349db57853d1d66f56', 'a2f4498b52bcf401b672deae374e0bfe',
  'YOUR_OPENROUTER_KEY',
  'PEILsPlx6c3g0mYVBhj700U38i9ySwWJ'
) ON CONFLICT (client_id) DO NOTHING;

UPDATE ks_sessions SET client_id = 'kapoor_sons' WHERE client_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_clients_phone ON ks_clients(phone_primary);
CREATE INDEX IF NOT EXISTS idx_sessions_client ON ks_sessions(client_id);
