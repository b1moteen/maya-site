const counterId = Number(document.querySelector('meta[name="metrika-id"]')?.content);

if (Number.isSafeInteger(counterId) && counterId > 0) {
  const metrika = window.ym = window.ym || function (...args) {
    (metrika.a ||= []).push(args);
  };
  metrika.l ||= Date.now();
  const tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://mc.yandex.ru/metrika/tag.js';
  document.head.append(tag);

  metrika(counterId, 'init', {
    clickmap: false,
    trackLinks: false,
    webvisor: false,
    disableYtm: true,
  });

  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[data-buy], a[data-corporate]');
    if (!link) return;
    if (link.hasAttribute('data-buy')) {
      const details = link.dataset.showDate ? { date: link.dataset.showDate } : {};
      metrika(counterId, 'reachGoal', 'ticket_click', details);
    } else {
      const format = link.dataset.format;
      const details = format ? { format } : {};
      metrika(counterId, 'reachGoal', 'corporate_' + link.dataset.corporate, details);
    }
  });
}
