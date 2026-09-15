# Hunchly - case checklist

## Before browsing
- [ ] Hunchly dashboard open, **new case** created named `<CASE-ID>` (never the target's real name in the case title)
- [ ] Case is **active** in the extension and capture is ON (green icon)
- [ ] Browser profile = the persona profile (not your personal Chrome)
- [ ] Selectors added: target handle, email, phone, wallet, company name, aliases
- [ ] Network exit verified (opsec_check GO) BEFORE the first page load

## While browsing
- [ ] Let Hunchly capture: every page you visit is saved (URL, timestamp, hash, full-page screenshot)
- [ ] Highlighted selectors = confirmation that the page mentions your entity
- [ ] Add a **note** on every page that matters (why it matters, confidence level)
- [ ] Add **tags** (identity / infra / finance / social / to-verify)
- [ ] Attach photos to the case when you download media (Photos tab) - keep the originals

## At the end of the session
- [ ] Export the report (Word / HTML) into `/workspace/exports/` of the case
- [ ] Verify the export contains hashes + timestamps for each page
- [ ] Note the Hunchly export hash in the case log (`sha256sum report.docx`)
- [ ] Pause the case (capture OFF) before doing anything personal

## Never
- Never browse personal sites with capture ON (it becomes part of the case)
- Never rename/modify a captured page - add a note instead (chain of custody)
- Never share the raw Hunchly case folder: export a report instead
