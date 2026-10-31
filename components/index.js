const search = document.querySelector('[data-component-search]');
if (search) {
  const cards = [...document.querySelectorAll('[data-component-card]')];
  const status = document.querySelector('[data-filter-status]');
  const empty = document.querySelector('[data-filter-empty]');
  const filter = () => {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    for (const card of cards) {
      const matches = card.dataset.search.includes(query);
      card.hidden = !matches;
      if (matches) count++;
    }
    empty.hidden = count !== 0;
    status.textContent = query ? `${count} ${count === 1 ? 'component' : 'components'} found.` : '';
  };
  search.addEventListener('input', filter);
}
for (const frame of document.querySelectorAll('[data-embed-url]')) {
  const button = frame.querySelector('[data-embed-toggle]');
  const slot = frame.querySelector('[data-embed-slot]');
  button.addEventListener('click', () => {
    if (button.getAttribute('aria-expanded') === 'true') {
      slot.replaceChildren();
      button.setAttribute('aria-expanded', 'false');
      button.textContent = 'Load desktop specimen';
    } else {
      const iframe = document.createElement('iframe');
      iframe.src = frame.dataset.embedUrl;
      iframe.title = frame.dataset.embedTitle;
      slot.append(iframe);
      button.setAttribute('aria-expanded', 'true');
      button.textContent = 'Close desktop specimen';
    }
  });
}
