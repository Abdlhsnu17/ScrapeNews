"""
Web UI untuk Scraper Berita Online Indonesia.
Jalankan:  python app.py   lalu buka http://127.0.0.1:5000
"""
from flask import Flask, request, render_template_string, send_from_directory, abort
from datetime import datetime
import os
import re
import glob

from main import OnlineMediaScraper

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

TEMPLATE = """
<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#f4f6f8">
<title>Ruang Berita | Pencarian Media</title>
<style>
  :root { color-scheme:light; --ink:#17212b; --muted:#65717d; --line:#dfe5eb; --paper:#fff; --canvas:#f4f6f8; --accent:#245b8f; --accent-dark:#19466f; --accent-soft:#edf4fa; --amber:#fff4df; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--canvas); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; font-size:14px; line-height:1.5; }
  .topbar { height:62px; background:#fff; border-bottom:1px solid var(--line); display:flex; align-items:center; }
  .topbar-inner,.wrap { width:min(1180px,calc(100% - 48px)); margin:0 auto; }
  .topbar-inner { display:flex; align-items:center; justify-content:space-between; }
  .brand { display:flex; align-items:center; gap:10px; font-weight:700; letter-spacing:-.02em; font-size:15px; }
  .brand-mark { display:grid; place-items:center; width:30px; height:30px; border-radius:7px; color:#fff; background:#244c70; font-size:14px; font-weight:700; }
  .nav-right { display:flex; align-items:center; gap:18px; color:var(--muted); font-size:11px; }
  .clock-display { text-align:right; line-height:1.35; }
  .clock-display strong { display:block; color:var(--ink); font-size:11px; font-weight:650; }
  .clock-display small { color:var(--muted); font-size:9px; }
  .nav-status { display:flex; align-items:center; gap:7px; padding:6px 9px; border:1px solid var(--line); border-radius:6px; color:#46535f; }
  .nav-status i { width:6px; height:6px; border-radius:50%; background:#4b9b6b; }
  .page-head { display:flex; justify-content:space-between; align-items:flex-end; gap:20px; margin:30px 0 20px; }
  .eyebrow { margin-bottom:6px; color:var(--accent); font-size:10px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
  h1 { margin:0; font-size:26px; line-height:1.2; letter-spacing:-.035em; font-weight:650; }
  .page-head p { margin:6px 0 0; color:var(--muted); font-size:13px; }
  .head-meta { color:var(--muted); font-size:11px; white-space:nowrap; }
  .layout { display:grid; grid-template-columns:minmax(0,1fr) 280px; gap:16px; align-items:start; padding-bottom:42px; }
  .card { background:var(--paper); border:1px solid var(--line); border-radius:9px; box-shadow:0 1px 2px rgba(16,36,54,.03); }
  .form-card { padding:22px; }
  .section-heading { display:flex; align-items:flex-start; gap:11px; margin-bottom:20px; }
  .step { display:grid; place-items:center; flex:0 0 26px; height:26px; border-radius:6px; background:var(--accent-soft); color:var(--accent); font-weight:700; font-size:11px; }
  h2 { margin:0; font-size:15px; letter-spacing:-.015em; }
  .section-heading p { margin:3px 0 0; color:var(--muted); font-size:12px; }
  .grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:15px 14px; }
  label.field { display:block; color:#35424e; font-size:12px; font-weight:600; }
  input[type=text],input[type=date],input[type=number] { display:block; width:100%; height:40px; margin-top:6px; padding:0 10px; border:1px solid #d5dde5; border-radius:6px; background:#fff; color:var(--ink); font:inherit; outline:none; transition:border-color .15s,box-shadow .15s; }
  input:focus { border-color:#5f8eb5; box-shadow:0 0 0 3px rgba(36,91,143,.11); }
  .divider { height:1px; background:var(--line); margin:22px 0 18px; }
  .site-heading { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:10px; }
  .site-heading strong { font-size:12px; }
  .site-heading span { color:var(--muted); font-size:11px; }
  .sites { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }
  .site-chip { display:flex; align-items:center; gap:9px; min-height:45px; padding:8px 10px; border:1px solid var(--line); border-radius:6px; background:#fff; cursor:pointer; user-select:none; transition:border-color .15s,background .15s; }
  .site-chip:hover { border-color:#9bb4c9; background:#fbfdff; }
  .site-chip:has(input:checked) { border-color:#81a3bf; background:#f5f9fc; }
  .site-chip input { accent-color:var(--accent); margin:0; }
  .site-name { flex:1; font-size:12px; font-weight:600; }
  .badge { padding:3px 5px; border-radius:4px; font-size:8px; line-height:1; letter-spacing:.03em; font-weight:700; }
  .badge.statis { background:#eaf4ee; color:#34704e; }
  .badge.browser { background:var(--amber); color:#8b611d; }
  .hint { margin:10px 0 0; color:var(--muted); font-size:11px; }
  .form-footer { display:flex; align-items:center; justify-content:space-between; gap:15px; margin-top:20px; }
  .secure-note { display:flex; align-items:center; gap:7px; color:var(--muted); font-size:11px; }
  button { display:inline-flex; align-items:center; justify-content:center; gap:9px; min-height:40px; padding:0 15px; border:0; border-radius:6px; background:var(--accent); color:#fff; font:inherit; font-weight:650; cursor:pointer; transition:background .15s; }
  button:hover { background:var(--accent-dark); }
  button:focus-visible,.dl:focus-visible,.article-link:focus-visible { outline:3px solid rgba(36,91,143,.25); outline-offset:2px; }
  .side-card { padding:19px; }
  .side-card h3 { margin:0 0 14px; font-size:13px; }
  .side-kicker { margin-bottom:6px; color:var(--accent); font-size:9px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
  .side-list { display:grid; gap:13px; }
  .side-item { display:flex; align-items:flex-start; gap:9px; }
  .side-icon { display:grid; place-items:center; flex:0 0 27px; height:27px; border:1px solid var(--line); border-radius:6px; color:var(--accent); font-size:12px; }
  .side-item strong { display:block; font-size:11px; }
  .side-item small { display:block; margin-top:2px; color:var(--muted); font-size:10px; line-height:1.45; }
  .side-rule { height:1px; background:var(--line); margin:16px 0 12px; }
  .side-foot { color:var(--muted); font-size:10px; line-height:1.55; }
  .results-card { grid-column:1/-1; overflow:hidden; }
  .results-head { display:flex; align-items:center; justify-content:space-between; gap:16px; padding:18px 20px; border-bottom:1px solid var(--line); }
  .results-title { display:flex; align-items:center; gap:11px; }
  .results-title h2 { font-size:15px; }
  .results-title p { margin:3px 0 0; color:var(--muted); font-size:11px; }
  .total { min-width:42px; padding:6px 8px; border-radius:6px; background:var(--accent-soft); color:var(--accent); text-align:center; font-size:12px; font-weight:700; }
  .downloads { display:flex; gap:7px; }
  .dl { display:inline-flex; align-items:center; gap:7px; min-height:34px; padding:0 10px; border:1px solid #d5dde5; border-radius:6px; color:#35424e; text-decoration:none; font-size:11px; font-weight:600; }
  .dl:hover { border-color:#9bb4c9; background:#f7fafc; }
  .platform-stats { display:flex; flex-wrap:wrap; gap:6px; padding:12px 20px 0; }
  .stat { padding:4px 8px; border:1px solid var(--line); border-radius:5px; color:#52606c; font-size:10px; }
  .table-scroll { overflow-x:auto; padding:12px 14px 16px; }
  table { width:100%; border-collapse:collapse; font-size:12px; }
  th,td { padding:11px 10px; border-bottom:1px solid #edf0f3; text-align:left; vertical-align:middle; }
  th { color:#697783; font-size:9px; letter-spacing:.07em; text-transform:uppercase; }
  tbody tr:hover { background:#fafcfd; }
  td.number,td.date,td.score { color:var(--muted); white-space:nowrap; }
  td.title { min-width:250px; max-width:520px; font-weight:600; }
  .platform-tag { display:inline-block; padding:4px 7px; border-radius:5px; background:#f1f4f6; color:#43515d; font-size:10px; white-space:nowrap; }
  .article-link { color:var(--accent); font-weight:650; text-decoration:none; white-space:nowrap; }
  .article-link:hover { text-decoration:underline; }
  .empty { padding:38px 20px; color:var(--muted); text-align:center; }
  .empty-mark { display:grid; place-items:center; width:38px; height:38px; margin:0 auto 10px; border:1px solid var(--line); border-radius:10px; background:#f7f9fa; color:var(--accent); font-size:17px; }
  .empty strong { display:block; margin-bottom:4px; color:var(--ink); font-size:13px; }
  footer { display:flex; justify-content:space-between; padding:0 0 22px; color:#7b8792; font-size:10px; }
  @media(max-width:860px) { .layout { grid-template-columns:1fr; } .side-card { order:2; } .results-card { grid-column:auto; } }
  @media(max-width:560px) { .topbar-inner,.wrap { width:calc(100% - 30px); } .nav-right { gap:10px; } .nav-right>span:first-child { display:none; } .clock-display small { display:none; } .page-head { align-items:flex-start; flex-direction:column; margin-top:22px; } .head-meta { display:none; } h1 { font-size:23px; } .form-card { padding:17px; } .grid { grid-template-columns:1fr; gap:12px; } .sites { grid-template-columns:1fr; } .form-footer,.results-head { align-items:stretch; flex-direction:column; } .form-footer button { width:100%; } .downloads { flex-wrap:wrap; } .results-head { padding:16px; } .platform-stats { padding-left:16px; padding-right:16px; } .table-scroll { padding:8px 10px 14px; } footer { gap:8px; flex-direction:column; } }
</style>
</head>
<body>
<nav class="topbar"><div class="topbar-inner"><div class="brand"><span class="brand-mark">RB</span> Ruang Berita</div><div class="nav-right"><span>MONITORING MEDIA</span><div class="clock-display"><strong id="current-time">--:--:-- WIB</strong><small id="current-date">Memuat tanggal…</small></div><span class="nav-status"><i></i> Siap digunakan</span></div></div></nav>
<main class="wrap">
  <section class="page-head"><div><div class="eyebrow">Pencarian berita</div><h1>Temukan liputan yang relevan</h1><p>Atur topik, periode, dan sumber untuk mengumpulkan artikel berita.</p></div><div class="head-meta">7 portal berita tersedia</div></section>
  <div class="layout">
    <form method="post" action="/scrape" class="card form-card" id="search-form">
      <div class="section-heading"><span class="step">01</span><div><h2>Bangun pencarian</h2><p>Tentukan parameter untuk menemukan liputan yang relevan.</p></div></div>
      <div class="grid">
        <label class="field">Kata kunci<input type="text" name="keyword" value="{{ form.keyword or '' }}" placeholder="Contoh: ekonomi digital" maxlength="120" required></label>
        <label class="field">Artikel per portal<input type="number" name="max_articles" value="{{ form.max_articles if form.max_articles is defined else 20 }}" min="1" max="200" required></label>
        <label class="field">Tanggal mulai<input type="date" name="start_date" value="{{ form.start_date or '' }}" required></label>
        <label class="field">Tanggal akhir<input type="date" name="end_date" value="{{ form.end_date or '' }}" required></label>
      </div>
      <div class="divider"></div>
      <div class="site-heading"><strong>Pilih sumber berita</strong><span id="selected-count">{{ selected|length }} dari 7 dipilih</span></div>
      <div class="sites">
        {% for key, label, _m, tipe in sites %}
        <label class="site-chip"><input type="checkbox" name="site" value="{{ key }}" {{ 'checked' if key in selected else '' }}><span class="site-name">{{ label }}</span><span class="badge {{ tipe }}">{{ 'CEPAT' if tipe=='statis' else 'BROWSER' }}</span></label>
        {% endfor %}
      </div>
      <p class="hint">Sumber browser memakai Selenium dan mungkin perlu waktu lebih lama untuk memuat halaman.</p>
      <div class="form-footer"><span class="secure-note"><span>◷</span> Proses berjalan sesuai sumber pilihan</span><button type="submit" id="submit-button">Mulai pencarian <span aria-hidden="true">→</span></button></div>
    </form>
    <aside class="card side-card"><div class="side-kicker">Panduan singkat</div><h3>Mulai dengan fokus yang jelas.</h3><div class="side-list">
      <div class="side-item"><span class="side-icon">⌕</span><div><strong>Tentukan topik</strong><small>Gunakan kata atau frasa yang spesifik.</small></div></div>
      <div class="side-item"><span class="side-icon">▦</span><div><strong>Pilih periode</strong><small>Atur tanggal untuk mempersempit hasil.</small></div></div>
      <div class="side-item"><span class="side-icon">↗</span><div><strong>Ekspor temuan</strong><small>Unduh hasil sebagai file CSV atau Excel.</small></div></div>
    </div><div class="side-rule"></div><div class="side-foot">Hasil dikumpulkan dari portal berita yang dipilih. Ketersediaan artikel bergantung pada akses dan struktur masing-masing situs.</div></aside>
    {% if did_run %}
    <section class="card results-card">
      <div class="results-head"><div class="results-title"><span class="total">{{ results|length }}</span><div><h2>Hasil pencarian</h2><p>Artikel yang cocok untuk “{{ form.keyword }}” · {{ form.start_date }} — {{ form.end_date }}</p></div></div>
        {% if csv_name or xlsx_name %}<div class="downloads">{% if xlsx_name %}<a class="dl" href="/download/{{ xlsx_name }}">↓ Excel</a>{% endif %}{% if csv_name %}<a class="dl" href="/download/{{ csv_name }}">↓ CSV</a>{% endif %}</div>{% endif %}
      </div>
      {% if per_platform %}<div class="platform-stats">{% for plat, n in per_platform.items() %}<span class="stat">{{ plat }} · {{ n }}</span>{% endfor %}</div>{% endif %}
      {% if results %}<div class="table-scroll"><table><thead><tr><th>#</th><th>Sumber</th><th>Tanggal</th><th>Judul artikel</th><th>Relevansi</th><th></th></tr></thead><tbody>
      {% for a in results %}<tr><td class="number">{{ loop.index }}</td><td><span class="platform-tag">{{ a.platform }}</span></td><td class="date">{{ a.date }}</td><td class="title">{{ a.title }}</td><td class="score">{{ '%d%%' | format((a.relevance * 100) | round | int) if a.relevance is defined else '—' }}</td><td><a class="article-link" href="{{ a.url }}" target="_blank" rel="noopener">Buka ↗</a></td></tr>{% endfor %}
      </tbody></table></div>{% else %}<div class="empty"><div class="empty-mark">⌕</div><strong>Belum ada artikel yang cocok</strong>Coba kata kunci lain atau rentang tanggal yang lebih luas.</div>{% endif %}
    </section>
    {% endif %}
  </div>
  <footer><span>RUANG BERITA · MEDIA INTELLIGENCE</span><span>Untuk riset informasi publik</span></footer>
</main>
<script>
  const searchForm = document.getElementById('search-form');
  const sourceChecks = [...searchForm.querySelectorAll('input[name="site"]')];
  const selectedCount = document.getElementById('selected-count');
  const submitButton = document.getElementById('submit-button');
  const updateSelectedCount = () => { selectedCount.textContent = `${sourceChecks.filter(item => item.checked).length} dari ${sourceChecks.length} dipilih`; };
  sourceChecks.forEach(item => item.addEventListener('change', updateSelectedCount));
  searchForm.addEventListener('submit', event => {
    if (!sourceChecks.some(item => item.checked)) {
      event.preventDefault();
      alert('Pilih minimal satu sumber berita.');
      return;
    }
    submitButton.disabled = true;
    submitButton.textContent = 'Pencarian berjalan…';
  });
  (() => {
    const timeNode = document.getElementById('current-time');
    const dateNode = document.getElementById('current-date');
    const jakarta = new Intl.DateTimeFormat('id-ID', {
      timeZone: 'Asia/Jakarta', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
    });
    const dateFormat = new Intl.DateTimeFormat('id-ID', {
      timeZone: 'Asia/Jakarta', weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
    });
    const updateClock = () => {
      const now = new Date();
      timeNode.textContent = `${jakarta.format(now)} WIB`;
      dateNode.textContent = dateFormat.format(now);
    };
    updateClock();
    window.setInterval(updateClock, 1000);
  })();
</script>
</body>
</html>
"""


@app.route('/')
def index():
    default_selected = {'detik', 'kompas', 'viva', 'antara'}
    return render_template_string(TEMPLATE, sites=SITES, selected=default_selected,
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
    return render_template_string(TEMPLATE, sites=SITES, selected=selected, did_run=True,
                                  form=form, results=scraper.data, per_platform=per_platform,
                                  csv_name=csv_name, xlsx_name=xlsx_name)


@app.route('/download/<path:filename>')
def download(filename):
    output_dir = os.path.abspath('scraped_media_data')
    allowed = {name for name in os.listdir(output_dir) if name.endswith(('.csv', '.xlsx'))} if os.path.isdir(output_dir) else set()
    if filename not in allowed:
        abort(404)
    return send_from_directory(output_dir, filename, as_attachment=True)


if __name__ == '__main__':
    # Catatan: di macOS port 5000 sering dipakai AirPlay, jadi default 5050.
    debug = os.environ.get('FLASK_DEBUG', '1') != '0'
    app.run(debug=debug, port=int(os.environ.get('PORT', 5050)))
