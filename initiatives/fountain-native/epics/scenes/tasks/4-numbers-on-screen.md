## 4. Numbers on screen, in the PDF and in Go to scene; the click warning

- **Type:** code
- **Depends on:** 2, 3
- **Contract:**
  - In: a script with numbered and not yet numbered scenes
  - Requires:
    - the editor shows each heading's number left of it, in every view
      mode; a scene not numbered yet shows the number it will get in
      parentheses (`(12.A)`), and `?` when there is no room;
    - the PDF, when "show scene numbers" is on, prints the permanent
      number (both sides, as now), also in the table of contents; the
      scene report uses it too;
    - Go to scene takes a permanent number (`12.A`);
    - a click on the number shows a warning that numbers are permanent
      and do not change, with **"do not show this again for the next 5
      clicks"**; the counter lasts while the program runs;
    - the number is never put into the heading's text.
  - Delivers: the screen and PDF numbers, Go to scene, the warning (its
    counter without wx, tested)
- **Pre-work:** —
- **Out of scope:** editing a number (never allowed)
- **Tests:** the PDF's page ops hold the permanent numbers, and the
  provisional one in parentheses; Go to scene's list; the 5-click counter
