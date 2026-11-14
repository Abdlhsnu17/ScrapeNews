const searchForm = document.getElementById('search-form');
  const sourceChecks = [...searchForm.querySelectorAll('input[name="site"]')];
  const selectedCount = document.getElementById('selected-count');
  const submitButton = document.getElementById('submit-button');
  const searchProgress = document.getElementById('search-progress');
  const updateSelectedCount = () => { selectedCount.textContent = `${sourceChecks.filter(item => item.checked).length} dari ${sourceChecks.length} dipilih`; };
  sourceChecks.forEach(item => item.addEventListener('change', updateSelectedCount));

  const workspaceTabs = [...document.querySelectorAll('[role="tab"]')];
  const activateTab = tab => {
    workspaceTabs.forEach(item => {
      const active = item === tab;
      item.setAttribute('aria-selected', String(active));
      item.tabIndex = active ? 0 : -1;
      document.getElementById(item.getAttribute('aria-controls')).hidden = !active;
    });
  };
  workspaceTabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activateTab(tab));
    tab.addEventListener('keydown', event => {
      let nextIndex = index;
      if (event.key === 'ArrowRight') nextIndex = (index + 1) % workspaceTabs.length;
      else if (event.key === 'ArrowLeft') nextIndex = (index - 1 + workspaceTabs.length) % workspaceTabs.length;
      else if (event.key === 'Home') nextIndex = 0;
      else if (event.key === 'End') nextIndex = workspaceTabs.length - 1;
      else return;
      event.preventDefault();
      workspaceTabs[nextIndex].focus();
      activateTab(workspaceTabs[nextIndex]);
    });
  });

  searchForm.addEventListener('submit', event => {
    if (!sourceChecks.some(item => item.checked)) {
      event.preventDefault();
      alert('Pilih minimal satu sumber berita.');
      return;
    }
    submitButton.disabled = true;
    submitButton.setAttribute('aria-label', 'Pencarian sedang berjalan');
    submitButton.innerHTML = '<span class="spinner spinner-button" aria-hidden="true"></span><span class="button-label">Sedang mencari</span>';
    searchProgress.hidden = false;
    searchForm.setAttribute('aria-busy', 'true');
  });

  const timeNode = document.getElementById('current-time');
  const dateNode = document.getElementById('current-date');
  const jakartaTime = new Intl.DateTimeFormat('id-ID', {
    timeZone: 'Asia/Jakarta', hour: '2-digit', minute: '2-digit', hour12: false
  });
  const jakartaDate = new Intl.DateTimeFormat('id-ID', {
    timeZone: 'Asia/Jakarta', weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
  });
  const updateJakartaClock = () => {
    const now = new Date();
    timeNode.textContent = `${jakartaTime.format(now)} WIB`;
    dateNode.textContent = jakartaDate.format(now);
  };
  updateJakartaClock();
  window.setInterval(updateJakartaClock, 60_000);

  const resultRows = [...document.querySelectorAll('.result-row')];
  const paginationBar = document.getElementById('results-pagination');
  const paginationSummary = document.getElementById('pagination-summary');
  const paginationControls = document.getElementById('pagination-controls');
  const pageSize = 10;
  const visiblePageCount = 4;
  if (paginationBar && resultRows.length > pageSize) {
    const pageTotal = Math.ceil(resultRows.length / pageSize);
    let currentPage = 1;

    const renderPage = () => {
      const firstIndex = (currentPage - 1) * pageSize;
      resultRows.forEach((row, index) => {
        row.hidden = index < firstIndex || index >= firstIndex + pageSize;
      });
      paginationSummary.textContent = `Menampilkan ${firstIndex + 1}–${Math.min(firstIndex + pageSize, resultRows.length)} dari ${resultRows.length} artikel`;

      const firstPage = Math.floor((currentPage - 1) / visiblePageCount) * visiblePageCount + 1;
      const lastPage = Math.min(firstPage + visiblePageCount - 1, pageTotal);
      const buttons = [
        `<button class="page-control" type="button" data-page="${currentPage - 1}" aria-label="Halaman sebelumnya" ${currentPage === 1 ? 'disabled' : ''}>‹</button>`
      ];
      for (let page = firstPage; page <= lastPage; page += 1) {
        buttons.push(`<button class="page-number" type="button" data-page="${page}" aria-label="Halaman ${page}" ${page === currentPage ? 'aria-current="page"' : ''}>${page}</button>`);
      }
      buttons.push(`<button class="page-control" type="button" data-page="${currentPage + 1}" aria-label="Halaman berikutnya" ${currentPage === pageTotal ? 'disabled' : ''}>›</button>`);
      paginationControls.innerHTML = buttons.join('');
      paginationControls.querySelectorAll('button:not(:disabled)').forEach(button => {
        button.addEventListener('click', () => {
          currentPage = Number(button.dataset.page);
          renderPage();
        });
      });
    };

    paginationBar.hidden = false;
    renderPage();
  }
