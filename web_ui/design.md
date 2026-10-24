# Design: NSY Projects

The shared public-site system, also mirrored in the self-contained DEM login template. Other backend app interfaces are outside this system's scope.

## System

- Genre: editorial. Theme: retained NSY Projects brand. Vibe: a warm workshop for practical software.
- Home: short split introduction and abstract paper sculpture, original maker introduction, colophon.
- About: short split introduction, education/experience/building-interest sections, personal close.
- Login: the same 1120px header, nav, footer and 5:7 layout as Home; large Georgia introduction on the left, native 440px form on the right. Stack below 800px. No marketing artwork.
- One centered 1120px public container; 24px side gutters above 768px, 16px below.
- Hero columns 5:7 above 800px; all main biography and hero layouts stack below 800px.

## Tokens

`tokens.css` is the public source of truth. Login mirrors the same values inline so styles work before authentication and without a cross-origin dependency.

- Paper `#f7f5ef`; surface `#fffcf6`; soft surface `#e9eeea`.
- Ink `#252820`; secondary text `#62675c`; rules `#d8ddd3`.
- Accent/focus `#23594f`; pressed accent `#19443c`; accent ink `#fffcf6`.
- Display: Georgia, Times New Roman, Songti SC, SimSun, serif; weight 400.
- Body: platform system sans; weight 400; controls 600; item headings 500.
- Display 44–68px; section 44px (36px mobile); item 20–28px; body 16px; lead 20px; labels 14px.
- Space steps: 4, 8, 12, 16, 24, 32, 48, 80px. Control radius 6px; image/surface radius 8px.

## Controls and motion

- One green filled primary action; 48px buttons/inputs; 44px minimum navigation targets.
- Instant 3px keyboard focus outline. Input borders have 3:1 contrast.
- Only brief color transitions; no reveals, scroll choreography, or layout animation. Reduced motion removes transitions.
- Content and native login submission work without JavaScript. Successful authentication redirects; no simulated success state.

## Recorded layout exceptions

The user explicitly requested a compact portfolio, retained brand and directory compatibility. Gates 1 (directory item titles), 44c/79 (short Banner), 59 (compact section spacing), 77 (content-driven length and biography sections), and 78 (retained heading scale) are documented house choices. They do not waive contrast, focus, overflow, truthfulness, or functionality. About copy preserves the owner's facts rather than imposing a marketing word budget.

## Exports

`tokens.css`, `base.css`, and `styles.css` serve the public site. The inline login export lives in `projects/dem-claim/app/auth_gate.py` and must be kept in sync for future palette/font changes.

## Copy revision

The owner requested the original wording on Home and About after reviewing the redesign. Preserve Project Lab, its original supporting sentence, the original home descriptions, and the original biography prose. Layout and visual styling remain redesigned. The owner selected an abstract paper sculpture: ivory folded and curved surfaces with one forest-green element and soft natural shadows. Home must not show app interfaces or list individual projects. Keep Explore Projects as the gateway to the existing Projects directory. The decorative artwork has no caption, text, or interface content. This explicit owner-selected visual replaces Hallmark’s default preference for product imagery.
