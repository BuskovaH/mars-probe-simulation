/* Shared theme + language handling for all pages.
   Load in <head> (applies theme immediately), then call App.init(...) at the end of <body>.
   Preferences are stored in localStorage and also passed in the URL of the
   navigation links (data-nav), so they carry over even when opened from file://. */
(function () {
  const KEY_THEME = 'app-theme', KEY_LANG = 'app-lang';
  const params = new URLSearchParams(location.search);
  const read = k => { try { return localStorage.getItem(k); } catch (e) { return null; } };
  const write = (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} };

  const COMMON = {
    en: { back: '← Menu' },
    cs: { back: '← Menu' }
  };

  const App = window.App = { lang: 'en', theme: 'dark', dict: {}, _cb: null };

  function pick(param, key, valid, fallback) {
    const a = params.get(param), b = read(key);
    if (valid.includes(a)) return a;
    if (valid.includes(b)) return b;
    return fallback();
  }

  App.theme = pick('theme', KEY_THEME, ['light', 'dark'],
    () => (window.matchMedia && matchMedia('(prefers-color-scheme: light)').matches) ? 'light' : 'dark');
  App.lang = pick('lang', KEY_LANG, ['en', 'cs'],
    () => (navigator.language || 'en').toLowerCase().startsWith('cs') ? 'cs' : 'en');

  document.documentElement.setAttribute('data-theme', App.theme);

  App.t = key => (App.dict[App.lang] && App.dict[App.lang][key]) ?? key;

  function updateLinks() {
    document.querySelectorAll('a[data-nav]').forEach(a => {
      if (!a.dataset.base) a.dataset.base = a.getAttribute('href');
      a.href = a.dataset.base + '?lang=' + App.lang + '&theme=' + App.theme;
    });
  }

  function applyText() {
    document.documentElement.lang = App.lang;
    document.querySelectorAll('[data-i18n]').forEach(n => { n.textContent = App.t(n.dataset.i18n); });
    const title = App.t('docTitle');
    if (title !== 'docTitle') document.title = title;
    document.querySelectorAll('[data-lang]').forEach(b => b.classList.toggle('active', b.dataset.lang === App.lang));
    document.querySelectorAll('[data-theme]').forEach(b => b.classList.toggle('active', b.dataset.theme === App.theme));
    updateLinks();
  }

  App.setLang = lang => {
    App.lang = lang; write(KEY_LANG, lang);
    applyText();
    if (App._cb) App._cb(lang);
  };
  App.setTheme = theme => {
    App.theme = theme; write(KEY_THEME, theme);
    document.documentElement.setAttribute('data-theme', theme);
    applyText();
  };

  /* translations: {en:{...}, cs:{...}}; onLang(lang) is called after every (incl. the first) language apply */
  App.init = function (translations, onLang) {
    App.dict = {
      en: Object.assign({}, COMMON.en, translations.en),
      cs: Object.assign({}, COMMON.cs, translations.cs)
    };
    App._cb = onLang || null;

    const host = document.getElementById('switches');
    if (host) {
      host.innerHTML =
        '<div class="switch-group">' +
        '<div class="lang-switch"><button type="button" data-lang="en">EN</button><button type="button" data-lang="cs">CS</button></div>' +
        '<div class="theme-switch"><button type="button" data-theme="light" aria-label="Light">☀</button>' +
        '<button type="button" data-theme="dark" aria-label="Dark">☾</button></div></div>';
      host.querySelectorAll('[data-lang]').forEach(b => b.addEventListener('click', () => App.setLang(b.dataset.lang)));
      host.querySelectorAll('[data-theme]').forEach(b => b.addEventListener('click', () => App.setTheme(b.dataset.theme)));
    }
    write(KEY_LANG, App.lang); write(KEY_THEME, App.theme);
    applyText();
    if (App._cb) App._cb(App.lang);
  };
})();
