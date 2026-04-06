"""
ChiroCandy Google PPC Campaign Builder
Reads a client JSON file and generates a Google Ads Editor CSV.

Usage:
    python build_campaign.py <client_data.json> <output_path.csv>

The template CSV must be at: ../assets/template.csv (relative to this script)
"""

import csv
import json
import sys
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, '..', 'assets', 'template.csv')

# Standard landing page path slugs per ad group
LANDING_PAGE_SLUGS = {
    "Back/Neck Pain":       "back-and-neck-pain",
    "Sciatic Nerve Pain":   "sciatica",
    "Chiropractic Near Me": "chiropractor-near-me",
    "Headaches/Migraines":  "headaches",
}
# Office Branding slug is derived from office name


def slugify(text):
    """Convert office name to URL slug: 'Davis Chiropractic' -> 'davis-chiropractic'"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text


# Matches common US phone formats: (555) 867-5309, 555-867-5309, 5558675309, +15558675309, etc.
PHONE_PATTERN = re.compile(
    r'(\+?1[\s.-]?)?'
    r'(\(?\d{3}\)?[\s.-]?)'
    r'\d{3}[\s.-]?\d{4}'
)


def strip_phone_numbers(text):
    """Remove any phone numbers from ad copy — including them is a Google Ads policy violation.
    Replaces detected phone numbers with 'Call Us Today' so the ad still has a CTA.
    """
    if not text:
        return text
    cleaned = PHONE_PATTERN.sub('Call Us Today', text)
    if cleaned != text:
        print(f"  ⚠️  Phone number removed from ad copy: {repr(text)} → {repr(cleaned)}")
    return cleaned


def build_landing_url(base_domain, ad_group, office_name):
    """Derive the full landing page URL for a given ad group."""
    base = base_domain.rstrip('/')
    if not base.startswith('http'):
        base = 'https://' + base
    slug = LANDING_PAGE_SLUGS.get(ad_group) or slugify(office_name)
    return f"{base}/{slug}"


def replace_text(text, c):
    """Apply all client-data substitutions to a string."""
    if not text:
        return text

    replacements = [
        # Campaign name
        ("CC Chiropractic TEMPLATE", c['campaign_name']),
        # Ad group names (strip TEMPLATE suffix)
        ("Back/Neck Pain TEMPLATE",        "Back/Neck Pain"),
        ("Sciatic Nerve Pain TEMPLATE",    "Sciatic Nerve Pain"),
        ("Chiropractic Near Me TEMPLATE",  "Chiropractic Near Me"),
        ("Headaches/Migraines TEMPLATE",   "Headaches/Migraines"),
        ("Office Branding TEMPLATE",       "Office Branding"),
        # Doctor name (order: longer patterns first)
        ("Dr. First Last Name",     c['doctor_name']),
        ("Dr. First Last",          c['doctor_name']),
        ("Dr. First and Last Name", c['doctor_name']),
        # Office name
        ("Office Name",             c['office_name']),
        # Location (more specific first)
        ("in Office, Location",     f"in {c['city_state']}"),
        ("in Office Location",      f"in {c['city_state']}"),
        ("Office, Location",        c['city_state']),
        ("Office Location",         c['city_state']),
        # Offer price
        ("$$",                      c['offer_price']),
        # Budget
        ("20.00",                   c['daily_budget']),
        # Website
        ("https://chirocandy.com",  c['website']),
        # Office Branding keywords
        ("office name office location", f"{slugify(c['office_name'])} {c['city'].lower()}"),
        ("dr first last chiropractic",  f"dr {c['doctor_first'].lower()} {c['doctor_last'].lower()} chiropractic"),
        ("office name",                 slugify(c['office_name']).replace('-', ' ')),
        ("dr first last",               f"dr {c['doctor_first'].lower()} {c['doctor_last'].lower()}"),
        # URL display paths
        ("Officelocation", c['city']),
        ("officelocation", c['city'].lower()),
        ("Officename",     c['office_short']),
        ("officename",     c['office_short'].lower()),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def build_sitelink_rows(c, headers):
    """Generate 4 sitelink asset rows from the client's website navigation."""
    sitelinks = c.get('sitelinks', [])
    rows = []
    for sl in sitelinks[:4]:
        row = {k: '' for k in headers}
        row['Campaign'] = c['campaign_name']
        row['Ad Group'] = ''
        # Google Ads Editor sitelink columns
        row['Ad type'] = 'Sitelink'
        row['Headline 1'] = sl['text']
        row['Description 1'] = sl.get('desc1', '')
        row['Description 2'] = sl.get('desc2', '')
        row['Final URL'] = sl['url']
        row['Campaign Status'] = 'Paused'
        row['Status'] = 'Enabled'
        rows.append(row)
    return rows


def build_callout_rows(c, headers):
    """Generate callout asset rows."""
    callouts = c.get('callouts', [])
    rows = []
    for text in callouts[:8]:
        row = {k: '' for k in headers}
        row['Campaign'] = c['campaign_name']
        row['Ad type'] = 'Callout'
        row['Headline 1'] = text
        row['Campaign Status'] = 'Paused'
        row['Status'] = 'Enabled'
        rows.append(row)
    return rows


def build_structured_snippet_rows(c, headers):
    """Generate structured snippet asset rows."""
    snippets = c.get('structured_snippets', [])
    rows = []
    for snippet in snippets:
        row = {k: '' for k in headers}
        row['Campaign'] = c['campaign_name']
        row['Ad type'] = 'Structured snippet'
        row['Headline 1'] = snippet['header']
        row['Description 1'] = '; '.join(snippet['values'])
        row['Campaign Status'] = 'Paused'
        row['Status'] = 'Enabled'
        rows.append(row)
    return rows


def build_call_rows(c, headers):
    """Generate call asset row."""
    if not c.get('phone'):
        return []
    row = {k: '' for k in headers}
    row['Campaign'] = c['campaign_name']
    row['Ad type'] = 'Call'
    row['Headline 1'] = c['phone']
    row['Description 1'] = 'US'
    row['Campaign Status'] = 'Paused'
    row['Status'] = 'Enabled'
    return [row]


def build_image_rows(c, headers):
    """Generate image asset rows from scraped image URLs."""
    images = c.get('image_urls', [])
    rows = []
    for i, url in enumerate(images[:3]):
        row = {k: '' for k in headers}
        row['Campaign'] = c['campaign_name']
        row['Ad type'] = 'Image'
        row['Headline 1'] = f"{c['office_name']} Image {i+1}"
        row['Final URL'] = url
        row['Campaign Status'] = 'Paused'
        row['Status'] = 'Enabled'
        rows.append(row)
    return rows


def main(client_json_path, output_path):
    # Load client data
    with open(client_json_path) as f:
        c = json.load(f)

    # Derive helper fields
    name_parts = c['doctor_name'].replace('Dr. ', '').replace('Dr.', '').strip().split()
    c['doctor_first'] = name_parts[0] if name_parts else ''
    c['doctor_last'] = name_parts[-1] if len(name_parts) > 1 else ''
    c['city'] = c['city_state'].split(',')[0].strip()
    c['office_short'] = c['office_name'].split()[0]  # e.g. "Davis" from "Davis Chiropractic"
    c['campaign_name'] = c['office_name']

    # Load template
    with open(TEMPLATE_PATH, encoding='utf-16') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
        rows = list(reader)

    # Ad copy fields where phone numbers are never allowed (Google Ads policy violation)
    AD_COPY_FIELDS = [f'Headline {i}' for i in range(1, 16)] + [f'Description {i}' for i in range(1, 5)]

    # Apply text replacements to all rows, then strip phone numbers from ad copy fields
    new_rows = []
    for row in rows:
        new_row = {k: replace_text(v, c) for k, v in row.items()}
        # Only scrub ad copy fields on actual ad rows, not call asset rows
        if new_row.get('Ad type', '') not in ('Call',):
            for field in AD_COPY_FIELDS:
                if field in new_row:
                    new_row[field] = strip_phone_numbers(new_row[field])
        new_rows.append(new_row)

    # Set per-ad-group landing page URLs
    base_domain = c.get('landing_page_domain', '')
    if base_domain:
        for row in new_rows:
            ag = row.get('Ad Group', '')
            if row.get('Ad type') == 'Responsive search ad' and ag:
                row['Final URL'] = build_landing_url(base_domain, ag, c['office_name'])

    # Append asset rows
    new_rows += build_call_rows(c, headers)
    new_rows += build_sitelink_rows(c, headers)
    new_rows += build_callout_rows(c, headers)
    new_rows += build_structured_snippet_rows(c, headers)
    new_rows += build_image_rows(c, headers)

    # Write output
    with open(output_path, 'w', encoding='utf-16', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers, delimiter='\t', extrasaction='ignore')
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"✅ Campaign CSV written to: {output_path}")
    print(f"   Rows: {len(new_rows)} ({len(rows)} campaign + {len(new_rows)-len(rows)} asset rows)")
    location_radius = c.get('location_radius', '')
    if location_radius:
        print(f"\n📍 LOCATION TARGETING REMINDER:")
        print(f"   After importing, set location targeting to: {location_radius}")
        print(f"   In Google Ads: Campaign Settings → Locations → Advanced Search → Radius")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python build_campaign.py <client_data.json> <output.csv>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
