"""
Web UI untuk Scraper Berita Online Indonesia.
Jalankan:  python app.py   lalu buka http://127.0.0.1:5050
"""
from flask import Flask, request, render_template, send_from_directory, abort
from datetime import datetime
import os
import re
import glob
from pathlib import Path

from .scraper import OnlineMediaScraper

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "scraped_media_data"
app = Flask(__name__)

# Definisi situs: key -> (label, nama_method, tipe)
SITES = [
    ('detik',    'Detik.com',        'scrape_detik',    'statis'),
    ('kompas',   'Kompas.com',       'scrape_kompas',   'statis'),
    ('viva',     'Viva.co.id',       'scrape_viva',     'statis'),
    ('antara',   'AntaraNews.com',   'scrape_antara',   'statis'),
    ('cnn',      'CNNIndonesia.com', 'scrape_cnn',      'browser'),
    ('liputan6', 'Liputan6.com',     'scrape_liputan6', 'browser'),
    ('tempo',    'Tempo.co',         'scrape_tempo',    'browser'),
]


@app.route('/')
def index():
    default_selected = {'detik', 'kompas', 'viva', 'antara'}
    return render_template("index.html", sites=SITES, selected=default_selected,
                                  did_run=False, form={}, results=[], per_platform={},
                                  csv_name=None, xlsx_name=None)


@app.route('/scrape', methods=['POST'])
def scrape():
    keyword = (request.form.get('keyword') or '').strip()
    selected = set(request.form.getlist('site')) & {site[0] for site in SITES}
    if not keyword:
        abort(400, "Kata kunci wajib diisi.")
    if not selected:
        abort(400, "Pilih minimal satu sumber berita.")
    try:
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
    except (ValueError, KeyError):
        abort(400, "Format tanggal tidak valid.")
    if start_date > end_date:
        abort(400, "Tanggal mulai tidak boleh melewati tanggal akhir.")
    try:
        max_articles = max(1, min(200, int(request.form.get('max_articles', 20))))
    except ValueError:
        max_articles = 20

    scraper = OnlineMediaScraper()
    try:
        for key, label, method_name, _tipe in SITES:
            if key in selected:
                getattr(scraper, method_name)(keyword, start_date, end_date, max_articles)
    finally:
        scraper.close()

    csv_name = None
    xlsx_name = None
    safe_prefix = re.sub(r'[^\w-]+', '_', keyword, flags=re.UNICODE).strip('_')[:60] or 'hasil'
    files_before = set(glob.glob(os.path.join(scraper.output_dir, f"{safe_prefix}_*")))
    scraper.save_to_csv(safe_prefix)
    created_files = set(glob.glob(os.path.join(scraper.output_dir, f"{safe_prefix}_*"))) - files_before
    csv_files = sorted(path for path in created_files if path.endswith('.csv'))
    xlsx_files = sorted(path for path in created_files if path.endswith('.xlsx'))
    if csv_files:
        csv_name = os.path.basename(csv_files[0])
    if xlsx_files:
        xlsx_name = os.path.basename(xlsx_files[0])

    per_platform = {}
    for a in scraper.data:
        per_platform[a['platform']] = per_platform.get(a['platform'], 0) + 1

    form = {'keyword': keyword, 'start_date': str(start_date),
            'end_date': str(end_date), 'max_articles': max_articles}
    return render_template("index.html", sites=SITES, selected=selected, did_run=True,
                                  form=form, results=scraper.data, per_platform=per_platform,
                                  csv_name=csv_name, xlsx_name=xlsx_name)


@app.route('/download/<path:filename>')
def download(filename):
    output_dir = str(OUTPUT_DIR)
    allowed = {name for name in os.listdir(output_dir) if name.endswith(('.csv', '.xlsx'))} if os.path.isdir(output_dir) else set()
    if filename not in allowed:
        abort(404)
    return send_from_directory(output_dir, filename, as_attachment=True)


