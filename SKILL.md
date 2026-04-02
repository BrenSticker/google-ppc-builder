---
name: google-ppc-builder
description: >
  Use this skill whenever Brenden uploads a chiropractic client intake form PDF and wants Google PPC Search Ads built.
  Triggers on phrases like "build the ads", "generate the campaign", "here's the intake form", or any time a new
  intake PDF is dropped into the conversation. Automates the full workflow: extract client data → scrape website
  for assets → ask for landing page domain → generate a ready-to-import Google Ads Editor CSV with campaign,
  ad groups, keywords, responsive search ads, sitelinks, callouts, structured snippets, call asset, and image assets.
---

# Google PPC Campaign Builder — ChiroCandy

This skill automates building a complete Google Ads Search campaign from a chiropractic client intake form PDF.
The output is a single Google Ads Editor CSV, ready to import — no manual steps needed.

## What Gets Built

- **1 Search campaign** (Manual CPC, Google search only)
- **5 ad groups**: Back/Neck Pain · Sciatic Nerve Pain · Chiropractic Near Me · Headaches/Migraines · Office Branding
- **27 keywords** (Exact + Phrase match)
- **15 responsive search ads** (3 per ad group, all unique headline variations)
- **Per-ad-group landing pages** from the client's `newpatientspecial.co` domain
- **Assets**: Call · Sitelinks (4) · Callouts · Structured Snippets · Images

---

## Step-by-Step Workflow

### Step 1 — Extract data from the intake PDF

Read the uploaded PDF and extract these fields:

| Field | Where to find it |
|---|---|
| `doctor_name` | "Doctor's Name" — format as "Dr. First Last" |
| `office_name` | "Office Name" |
| `city_state` | From office address — e.g. "Omaha, NE" |
| `website` | "Website" field |
| `phone` | "Office Phone Number" |
| `offer_price` | "Offer Price" — format as "$47" |
| `daily_budget` | "Daily Ad Spend Budget" — format as "30.00" |

### Step 2 — Scrape the client's website for assets

Use WebFetch on the client's `website` URL. Extract:

**For sitelinks (pick 4 most relevant service/condition pages):**
- Page name → becomes sitelink text (max 25 chars)
- Page URL
- Write a short 1-line description for each (35 chars max)

Good sitelink picks: conditions treated pages (Back Pain, Sciatica, Headaches), Contact Us, About. Avoid homepage and generic service pages.

**For callouts (6–8 short phrases, max 25 chars each):**
Pull from services, credentials, or differentiators on the site. Examples based on what the site says:
- "25 Years of Experience"
- "Family Chiropractic Care"
- "Same-Day Appointments"
- "Accepting New Patients"
- "Pediatric Chiropractic"
- "Prenatal Chiropractic"
- "Gentle Adjustments"
- "Advanced Nerve Scanning"

**For structured snippets (1–2 headers with 3–5 values each):**
Common headers: "Services", "Conditions Treated". Pull values from the site's service/condition lists.

**For images (up to 3 direct image URLs):**
Look for hero images, doctor photos, or office photos. These need to be direct `.jpg` or `.png` URLs (not CSS backgrounds or lazy-loaded). Prefer landscape images ≥ 1200×628px. If you can't find direct image URLs, skip and note it.

**For call asset:**
Use the phone number from the landing page (not the main website) — it's the tracking number. If only one number is available, use that.

### Step 3 — Ask for the landing page domain

Say: "What's the landing page domain for [Client Name]? (e.g. `clientname.newpatientspecial.co`)"

The domain structure is always: `[clientslug].newpatientspecial.co`

Landing page URLs are derived automatically per ad group:
- Back/Neck Pain → `/back-and-neck-pain`
- Sciatic Nerve Pain → `/sciatica`
- Chiropractic Near Me → `/chiropractor-near-me`
- Headaches/Migraines → `/headaches`
- Office Branding → `/[office-name-as-slug]` (e.g. `davis-chiropractic`)

You can also scrape the landing page to pull a more accurate phone number for the call asset (landing pages often have a tracking number different from the main website).

### Step 4 — Build the client data JSON and run the script

Once you have all the data, write it to a JSON file and run the builder script.

**JSON format** (`/tmp/client_data.json`):
```json
{
  "doctor_name": "Dr. Matthew Davis",
  "office_name": "Davis Chiropractic",
  "city_state": "Omaha, NE",
  "website": "https://davischiropracticomaha.com/",
  "phone": "(402) 964-2930",
  "offer_price": "$47",
  "daily_budget": "30.00",
  "landing_page_domain": "davischirone.newpatientspecial.co",
  "sitelinks": [
    {"text": "Back Pain", "desc1": "Get relief for chronic back pain.", "desc2": "Request an appointment today.", "url": "https://davischiropracticomaha.com/services/back-pain/"},
    {"text": "Sciatica", "desc1": "Find relief for sciatic nerve pain.", "desc2": "Chiropractic care that works.", "url": "https://davischiropracticomaha.com/services/sciatica/"},
    {"text": "Headaches & Migraines", "desc1": "Stop suffering from headaches.", "desc2": "Natural chiropractic relief.", "url": "https://davischiropracticomaha.com/services/headaches-migraines/"},
    {"text": "Contact Us", "desc1": "Schedule your appointment today.", "desc2": "Serving Omaha, NE.", "url": "https://davischiropracticomaha.com/contact-us/"}
  ],
  "callouts": [
    "25 Years of Experience",
    "Family Chiropractic Care",
    "Accepting New Patients",
    "Pediatric Chiropractic",
    "Prenatal Chiropractic",
    "Advanced Nerve Scanning",
    "Gentle Adjustments",
    "Same-Day Appointments"
  ],
  "structured_snippets": [
    {
      "header": "Services",
      "values": ["Family Care", "Pediatric Chiro", "Prenatal Chiro", "Massage Therapy", "Wellness Programs"]
    },
    {
      "header": "Conditions Treated",
      "values": ["Back Pain", "Sciatica", "Headaches", "Neck Pain", "Shoulder Pain"]
    }
  ],
  "image_urls": [
    "https://example.com/image1.jpg"
  ]
}
```

**Run the script:**
```bash
python /path/to/skill/scripts/build_campaign.py /tmp/client_data.json /sessions/amazing-zen-einstein/mnt/outputs/[OfficeName]-Google-Ads.csv
```

The script path is relative to where the skill was installed. Use the path shown when the skill was packaged.

### Step 5 — Deliver the file

Share the CSV file link with the user using a `computer://` link. Include a brief summary:
- Campaign name
- Budget
- Number of ad groups, keywords, ads
- Assets included (call, sitelinks, callouts, snippets, images)
- Any notes (e.g., if image URLs couldn't be found and need manual upload)

---

## Important Notes

**Character limits (Google Ads):**
- Headlines: max 30 characters
- Descriptions: max 90 characters
- Sitelink text: max 25 characters
- Callout text: max 25 characters
- Structured snippet values: max 25 characters each

Always check these before writing the JSON. If a callout or sitelink is over the limit, shorten it.

**Offer price formatting:** Always include the dollar sign — `$47` not `47`.

**Doctor name formatting:** Always include the title — `Dr. Matthew Davis` not `Matthew Davis`.

**Landing page domain:** Only the domain is needed (no `https://`, no trailing slash). The script adds these automatically.

**Phone number:** Prefer the number on the landing page over the main website — it's usually a call tracking number.

**Images:** If direct image URLs are unavailable (many sites use lazy loading or CDN obfuscation), skip the image asset rows and add a note to the user that images need to be uploaded manually in Google Ads.

**Budget field:** Always format as `"30.00"` (two decimal places, no dollar sign).
