## 1. The act marker does not print

- **Type:** code
- **Depends on:** — (native Fountain already saves the act break as `# X`)
- **Decided (Rafael, 2026-10-26):** an act is a **marker only**: the
  existing Act break element, shown in the editor and saved in the
  `.fountain`, never printed (study/1, Decision).
- **Contract:**
  - In: a script with Act break elements
  - Requires: the PDF (`Screenplay.generatePML`, which Print also uses)
    leaves out every Act break line, and the text after it moves up into
    its place; **pagination does not change**, so a page holds the same
    lines on screen and in the PDF (the page just ends a little short);
    the editor still shows the marker in every view mode; the Fountain
    file is unchanged (`# X`)
  - Delivers: the act break no longer printed
- **Pre-work:** —
- **Out of scope:** RTF, FDX, HTML and text exports (they keep the act
  break as today); pagination that gives the marker's space back; the old
  File → Export → Fountain writer (`>X<`)
- **Tests:** an act break's text is not in the PDF's page ops; the lines
  around it are; page breaks are the same with and without the act break
  in the PDF; the screen's page (forPDF false) still holds it
