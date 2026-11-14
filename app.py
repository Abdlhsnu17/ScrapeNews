"""
Web UI untuk Scraper Berita Online Indonesia.
Jalankan:  python app.py   lalu buka http://127.0.0.1:5000
"""
from flask import Flask, request, render_template_string, send_from_directory, abort
from datetime import datetime
import os

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
<meta name="theme-color" content="#101d19">
<title>Ruang Berita — News Intelligence</title>
<style>
  :root { color-scheme:light; --ink:#18211e; --muted:#75807b; --line:#e7eae7; --paper:#fff; --canvas:#f4f5f2; --green:#25694e; --green-dark:#1c563f; --mint:#eaf3ed; --orange:#fff1df; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--canvas); color:var(--ink); font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; font-size:14px; line-height:1.5; }
  .topbar { height:72px; background:#13221c; color:#fff; display:flex; align-items:center; }
  .topbar-inner,.wrap { width:min(1260px,calc(100% - 64px)); margin:0 auto; }
  .topbar-inner { display:flex; align-items:center; justify-content:space-between; }
  .brand { display:flex; align-items:center; gap:11px; font-weight:760; letter-spacing:-.04em; font-size:16px; }
  .brand-mark { display:grid; place-items:center; width:35px; height:35px; border-radius:11px; color:#173326; background:#c3dfc9; font-size:17px; font-family:Georgia,serif; }
  .nav-right { display:flex; align-items:center; gap:22px; color:#c2d0c8; font-size:11px; }
  .clock-display { text-align:right; line-height:1.35; }
  .clock-display strong { display:block; color:#f4f7f4; font-size:11px; font-weight:650; letter-spacing:.02em; }
  .clock-display small { color:#9eafa4; font-size:9px; letter-spacing:.04em; }
  .nav-status { display:flex; align-items:center; gap:7px; padding:7px 10px; border:1px solid #405148; border-radius:99px; color:#e2ede6; }
  .nav-status i { width:6px; height:6px; border-radius:50%; background:#7dc396; box-shadow:0 0 0 3px #294536; }
  .hero { position:relative; display:flex; align-items:flex-end; justify-content:space-between; gap:30px; overflow:hidden; margin:28px 0 22px; padding:36px 42px; border-radius:18px; color:#f8fbf8; background:radial-gradient(ellipse at 80% 0%,rgba(111,153,125,.24),transparent 36%),linear-gradient(115deg,#172720,#233a2e 70%,#1e3329); }
  .hero:after { content:""; position:absolute; width:300px; height:300px; right:4%; top:-210px; border:1px solid rgba(224,240,226,.13); border-radius:50%; box-shadow:0 0 0 35px rgba(224,240,226,.025),0 0 0 70px rgba(224,240,226,.025); }
  .hero-copy { position:relative; z-index:1; max-width:690px; }
  .eyebrow { display:flex; align-items:center; gap:8px; color:#c3dfc9; font-size:10px; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }
  .eyebrow:before { content:""; width:19px; height:1px; background:#9bc5a5; }
  h1 { margin:12px 0 9px; font-family:Georgia,"Times New Roman",serif; font-size:clamp(34px,4.4vw,52px); line-height:1.02; letter-spacing:-.045em; font-weight:400; }
  .hero p { max-width:570px; margin:0; color:#c3cec7; font-size:13px; }
  .hero-index { position:relative; z-index:1; align-self:flex-end; min-width:130px; padding-left:18px; border-left:1px solid #65786c; color:#d1ddd4; font:11px/1.7 ui-monospace,SFMono-Regular,Menlo,monospace; }
  .hero-index strong { display:block; color:#fff; font:500 24px/1.2 Georgia,serif; }
  .layout { display:grid; grid-template-columns:minmax(0,1fr) 300px; gap:18px; align-items:start; padding-bottom:50px; }
  .card { background:var(--paper); border:1px solid var(--line); border-radius:13px; box-shadow:0 5px 18px rgba(22,38,29,.025); }
  .form-card { padding:24px 26px; }
  .section-heading { display:flex; align-items:flex-start; gap:13px; margin-bottom:22px; }
  .step { display:grid; place-items:center; flex:0 0 31px; height:31px; border-radius:9px; background:#1d3328; color:#d1e6d5; font-weight:700; font-size:10px; letter-spacing:.05em; }
  h2 { margin:0; font-size:16px; letter-spacing:-.025em; }
  .section-heading p { margin:3px 0 0; color:var(--muted); font-size:12px; }
  .grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:17px 14px; }
  label.field { display:block; color:#34433b; font-size:12px; font-weight:700; }
  input[type=text],input[type=date],input[type=number] { display:block; width:100%; height:44px; margin-top:7px; padding:0 12px; border:1px solid #dce3dd; border-radius:9px; background:#fff; color:var(--ink); font:inherit; outline:none; transition:border-color .15s,box-shadow .15s; }
  input:focus { border-color:#69a482; box-shadow:0 0 0 3px rgba(50,125,82,.12); }
  .divider { height:1px; background:var(--line); margin:25px 0 21px; }
  .site-heading { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:12px; }
  .site-heading strong { font-size:13px; }
  .site-heading span { color:var(--muted); font-size:11px; }
  .sites { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:9px; }
  .site-chip { display:flex; align-items:center; gap:9px; min-height:49px; padding:9px 11px; border:1px solid var(--line); border-radius:8px; background:#fff; cursor:pointer; user-select:none; transition:.15s ease; }
  .site-chip:hover { border-color:#aac8b4; background:#fbfdfb; }
  .site-chip:has(input:checked) { border-color:#83b296; background:#f4faf5; box-shadow:inset 0 0 0 1px #cce0d1; }
  .site-chip input { accent-color:var(--green); margin:0; }
  .site-name { flex:1; font-size:12px; font-weight:650; }
  .badge { padding:3px 6px; border-radius:5px; font-size:8px; line-height:1; letter-spacing:.04em; font-weight:800; }
  .badge.statis { background:var(--mint); color:var(--green); }
  .badge.browser { background:var(--orange); color:#9a5b12; }
  .hint { margin:11px 0 0; color:var(--muted); font-size:11px; }
  .form-footer { display:flex; align-items:center; justify-content:space-between; gap:15px; margin-top:23px; }
  .secure-note { display:flex; align-items:center; gap:7px; color:var(--muted); font-size:11px; }
  button { display:inline-flex; align-items:center; justify-content:center; gap:9px; min-height:44px; padding:0 18px; border:0; border-radius:9px; background:var(--green); color:#fff; font:inherit; font-weight:700; cursor:pointer; transition:background .15s,transform .15s; }
  button:hover { background:var(--green-dark); transform:translateY(-1px); }
  .side-card { padding:21px; }
  .side-card h3 { margin:0 0 15px; font-size:13px; }
  .side-kicker { margin-bottom:7px; color:var(--green); font-size:9px; font-weight:800; letter-spacing:.13em; text-transform:uppercase; }
  .side-list { display:grid; gap:14px; }
  .side-item { display:flex; align-items:flex-start; gap:10px; }
  .side-icon { display:grid; place-items:center; flex:0 0 29px; height:29px; border-radius:9px; background:#f1f5f1; color:var(--green); font-size:13px; }
  .side-item strong { display:block; font-size:11px; }
  .side-item small { display:block; margin-top:2px; color:var(--muted); font-size:10px; line-height:1.4; }
  .side-rule { height:1px; background:var(--line); margin:18px 0 14px; }
  .side-foot { color:var(--muted); font-size:10px; line-height:1.55; }
  .results-card { grid-column:1/-1; overflow:hidden; }
  .results-head { display:flex; align-items:center; justify-content:space-between; gap:16px; padding:21px 24px; border-bottom:1px solid var(--line); }
  .results-title { display:flex; align-items:center; gap:12px; }
  .results-title h2 { font-size:16px; }
  .results-title p { margin:3px 0 0; color:var(--muted); font-size:11px; }
  .total { min-width:46px; padding:7px 9px; border-radius:8px; background:var(--mint); color:var(--green); text-align:center; font-size:12px; font-weight:800; }
  .downloads { display:flex; gap:8px; }
  .dl { display:inline-flex; align-items:center; gap:7px; min-height:36px; padding:0 12px; border:1px solid var(--line); border-radius:8px; color:#34433b; text-decoration:none; font-size:11px; font-weight:700; }
  .dl:hover { border-color:#9cbea7; background:#f8fbf8; }
  .platform-stats { display:flex; flex-wrap:wrap; gap:7px; padding:13px 24px 2px; }
  .stat { padding:5px 9px; border:1px solid var(--line); border-radius:7px; color:#526158; font-size:10px; }
  .table-scroll { overflow-x:auto; padding:14px 20px 20px; }
  table { width:100%; border-collapse:collapse; font-size:12px; }
  th,td { padding:12px 11px; border-bottom:1px solid #edf0ed; text-align:left; vertical-align:middle; }
  th { color:#7a857e; font-size:9px; letter-spacing:.1em; text-transform:uppercase; }
  td.number,td.date,td.score { color:var(--muted); white-space:nowrap; }
  td.title { min-width:250px; max-width:520px; font-weight:650; }
  .platform-tag { display:inline-block; padding:4px 7px; border-radius:6px; background:#f2f5f2; color:#435249; font-size:10px; white-space:nowrap; }
  .article-link { color:var(--green); font-weight:700; text-decoration:none; white-space:nowrap; }
  .article-link:hover { text-decoration:underline; }
  .empty { padding:44px 20px; color:var(--muted); text-align:center; }
  .empty-mark { display:grid; place-items:center; width:42px; height:42px; margin:0 auto 11px; border-radius:14px; background:#f1f5f1; color:var(--green); font-size:18px; }
  .empty strong { display:block; margin-bottom:4px; color:var(--ink); font-size:13px; }
  footer { display:flex; justify-content:space-between; padding:0 0 24px; color:#859088; font-size:10px; }
  @media(max-width:820px) { .layout { grid-template-columns:1fr; } .side-card { order:2; } .results-card { grid-column:auto; } }
  @media(max-width:900px) { .layout { grid-template-columns:1fr; } .side-card { order:2; } .results-card { grid-column:auto; } }
  @media(max-width:560px) { .topbar-inner,.wrap { width:min(100% - 30px,1260px); } .nav-right { gap:12px; } .nav-right>span:first-child { display:none; } .clock-display small { display:none; } .hero { align-items:flex-start; margin-top:18px; padding:28px 23px; } .hero-index { display:none; } .form-card { padding:19px; } .grid { grid-template-columns:1fr; gap:13px; } .sites { grid-template-columns:1fr; } .form-footer,.results-head { align-items:stretch; flex-direction:column; } .form-footer button { width:100%; } .downloads { flex-wrap:wrap; } .results-head { padding:18px; } .platform-stats { padding-left:18px; padding-right:18px; } .table-scroll { padding:10px 12px 16px; } footer { gap:12px; flex-direction:column; } }
</style>
</head>
<body>
<nav class="topbar"><div class="topbar-inner"><div class="brand"><span class="brand-mark">R.</span> ruang berita</div><div class="nav-right"><span>MONITORING MEDIA INDONESIA</span><div class="clock-display"><strong id="current-time">--:--:-- WIB</strong><small id="current-date">Memuat tanggal…</small></div><span class="nav-status"><i></i> Workspace aktif</span></div></div></nav>
<main class="wrap">
  <section class="hero"><div class="hero-copy"><div class="eyebrow">Media intelligence · Indonesia</div><h1>Perspektif dimulai<br>dari pencarian yang tepat.</h1><p>Telusuri percakapan media dari berbagai portal berita. Tetapkan fokus, pilih sumber, lalu rangkum temuan dalam satu alur kerja.</p></div><div class="hero-index"><strong>01 / 07</strong>SUMBER TERKURASI</div></section>
  <div class="layout">
    <form method="post" action="/scrape" class="card form-card">
      <div class="section-heading"><span class="step">01</span><div><h2>Bangun pencarian</h2><p>Tentukan parameter untuk menemukan liputan yang relevan.</p></div></div>
      <div class="grid">
        <label class="field">Kata kunci<input type="text" name="keyword" value="{{ form.keyword or '' }}" placeholder="Contoh: ekonomi digital" required></label>
        <label class="field">Artikel per portal<input type="number" name="max_articles" value="{{ form.max_articles or 20 }}" min="1" max="200"></label>
        <label class="field">Tanggal mulai<input type="date" name="start_date" value="{{ form.start_date or '' }}" required></label>
        <label class="field">Tanggal akhir<input type="date" name="end_date" value="{{ form.end_date or '' }}" required></label>
      </div>
      <div class="divider"></div>
      <div class="site-heading"><strong>Pilih sumber berita</strong><span>7 sumber tersedia</span></div>
      <div class="sites">
        {% for key, label, _m, tipe in sites %}
        <label class="site-chip"><input type="checkbox" name="site" value="{{ key }}" {{ 'checked' if key in selected else '' }}><span class="site-name">{{ label }}</span><span class="badge {{ tipe }}">{{ 'CEPAT' if tipe=='statis' else 'BROWSER' }}</span></label>
        {% endfor %}
      </div>
      <p class="hint">Sumber browser memakai Selenium dan mungkin perlu waktu lebih lama untuk memuat halaman.</p>
      <div class="form-footer"><span class="secure-note"><span>◷</span> Proses dapat berlangsung beberapa saat</span><button type="submit">Mulai pencarian <span aria-hidden="true">→</span></button></div>
    </form>
    <aside class="card side-card"><div class="side-kicker">Panduan singkat</div><h3>Mulai dengan fokus yang jelas.</h3><div class="side-list">
      <div class="side-item"><span class="side-icon">⌕</span><div><strong>Tentukan topik</strong><small>Gunakan kata atau frasa yang spesifik.</small></div></div>
      <div class="side-item"><span class="side-icon">▦</span><div><strong>Pilih periode</strong><small>Atur tanggal untuk mempersempit hasil.</small></div></div>
      <div class="side-item"><span class="side-icon">↗</span><div><strong>Ekspor temuan</strong><small>Unduh hasil sebagai file CSV atau Excel.</small></div></div>
    </div><div class="side-rule"></div><div class="side-foot">Hasil dikumpulkan dari portal berita yang dipilih. Ketersediaan artikel bergantung pada akses dan struktur masing-masing situs.</div></aside>
    {% if did_run %}
    <section class="card results-card">
      <div class="results-head"><div class="results-title"><span class="total">{{ results|length }}</span><div><h2>Hasil pencarian</h2><p>Artikel yang cocok untuk “{{ form.keyword }}”</p></div></div>
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
    selected = set(request.form.getlist('site'))
    try:
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
    except (ValueError, KeyError):
        abort(400, "Format tanggal tidak valid.")
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
    if scraper.data:
        scraper.save_to_csv(keyword.replace(' ', '_') or 'hasil')
        files = sorted(os.listdir(scraper.output_dir))
        csvs = [f for f in files if f.endswith('.csv')]
        xlsxs = [f for f in files if f.endswith('.xlsx')]
        if csvs:
            csv_name = csvs[-1]
        if xlsxs:
            xlsx_name = xlsxs[-1]

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
    directory = os.path.abspath('scraped_media_data')
    return send_from_directory(directory, filename, as_attachment=True)


if __name__ == '__main__':
    # Catatan: di macOS port 5000 sering dipakai AirPlay, jadi default 5050.
    debug = os.environ.get('FLASK_DEBUG', '1') != '0'
    app.run(debug=debug, port=int(os.environ.get('PORT', 5050)))
