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
