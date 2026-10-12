# Digital marketing course demo (source)

Not published: Jekyll skips folders starting with `_`. The page is `../digital-marketing-course/index.html`.

- `en.json` is the original text; `hi`, `ta`, `te`, `ml` are machine translations, not yet reviewed by native speakers.
- `python3 check.py` checks that each translation keeps the English structure, answers, minutes, every number and the
  exact legal quote. `python3 build.py` builds the page.
- `PWCORE=<playwright-core> CHROME=<chrome> node test_page.mjs` loads every language, checks a lesson, a quiz, paging,
  no sideways scroll at 375 px, and fails on any request that leaves the site.
