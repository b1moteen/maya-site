const rows = document.querySelector('#rows');
const performances = Array.from(rows.querySelectorAll('.row'), (row) => {
  const time = row.querySelector('time');
  return { row, datetime: time.dateTime, start: Date.parse(time.dateTime) };
}).sort((first, second) => first.start - second.start);

const dateFormatter = new Intl.DateTimeFormat('ru-RU', {
  timeZone: 'Europe/Moscow',
  day: 'numeric',
  month: 'long',
  hour: '2-digit',
  minute: '2-digit',
});
const nextShow = document.querySelector('#next-show');
const nextShowTime = nextShow.querySelector('time');
const nextShowLabel = nextShow.querySelector('span');
const scheduleNote = document.querySelector('#schedule-note');
const showCta = document.querySelector('#show-cta');
const ticketPrice = document.querySelector('#ticket-price');
const activeScheduleNote = scheduleNote.textContent;
let scheduleTimer;

function refreshSchedule() {
  clearTimeout(scheduleTimer);
  const now = Date.now();
  const upcoming = performances.filter(({ row, start }) => {
    row.hidden = !(start > now);
    return !row.hidden;
  });
  const next = upcoming[0];
  rows.hidden = !next;
  nextShowTime.hidden = !next;
  nextShowLabel.textContent = next ? 'Ближайший показ' : 'Актуальные даты в IceTickets';
  ticketPrice.hidden = !next || !ticketPrice.textContent.trim();
  scheduleNote.textContent = next
    ? activeScheduleNote
    : 'Ближайшие даты уточняйте в афише IceTickets.';
  showCta.textContent = next ? 'Выбрать дату' : 'Смотреть афишу';

  if (next) {
    nextShowTime.dateTime = next.datetime;
    nextShowTime.textContent = dateFormatter.format(next.start);
    scheduleTimer = setTimeout(refreshSchedule, Math.min(next.start - now, 2_147_483_647));
  }
}

refreshSchedule();
window.addEventListener('pageshow', refreshSchedule);
document.addEventListener('visibilitychange', () => {
  if (!document.hidden) refreshSchedule();
});

const photoDialog = document.querySelector('#photo-dialog');
const dialogImage = document.querySelector('#dialog-image');
const photoCaption = document.querySelector('#photo-caption');
let activePhotoLink;

if (typeof photoDialog.showModal === 'function') {
  document.querySelectorAll('[data-photo]').forEach((link) => {
    link.addEventListener('click', (event) => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      activePhotoLink = link;
      dialogImage.src = link.href;
      photoCaption.textContent = link.dataset.photo;
      photoDialog.showModal();
    });
  });
  photoDialog.querySelector('.dialog-close').addEventListener('click', () => photoDialog.close());
  photoDialog.addEventListener('click', (event) => {
    if (event.target === photoDialog) photoDialog.close();
  });
  photoDialog.addEventListener('close', () => activePhotoLink.focus());
}

const heroVideo = document.querySelector('#bg');
const motionControl = document.querySelector('#motion-control');
const motionAllowed = matchMedia('(min-width: 901px) and (prefers-reduced-motion: no-preference)');
let videoPaused = false;

function updateHeroVideo() {
  if (!motionAllowed.matches || navigator.connection?.saveData) {
    heroVideo.pause();
    motionControl.hidden = true;
    return;
  }

  if (!heroVideo.hasAttribute('src')) heroVideo.src = heroVideo.dataset.src;
  if (!videoPaused) {
    heroVideo.play().then(() => {
      motionControl.hidden = !motionAllowed.matches;
    }).catch(() => {
      motionControl.hidden = true;
    });
  } else {
    heroVideo.pause();
    motionControl.hidden = false;
  }
  motionControl.textContent = videoPaused ? 'Включить фоновое видео' : 'Пауза фонового видео';
}

window.addEventListener('load', () => {
  setTimeout(updateHeroVideo, 1000);
  motionAllowed.addEventListener?.('change', updateHeroVideo);
}, { once: true });
motionControl.addEventListener('click', () => {
  videoPaused = !videoPaused;
  updateHeroVideo();
});
