# Render both presenter transcripts to PDF

Date: 30 October 2026, Vietnam time (UTC+7). Reporting only; research remains stopped.

The owner requested PDF exports of the existing English and Vietnamese Markdown transcripts. Rendered both retained files without changing scientific content, slide data, PowerPoint, HPC payloads or submission ZIP. Each output has 89 A4 portrait pages. Every slide begins on a new page with its hardware reminder, quick brief and embedded slide image; explanations continue below. A clickable contents list and PDF outline support navigation.

The renderer embeds DejaVu Sans fonts for Vietnamese and preserves selectable text. Slide images are encoded for embedding at high JPEG quality without modifying original images, reducing each output from roughly 27 MB to about 6.9 MiB. The source renderer and pinned package versions are retained for reproduction on a replacement machine; the temporary Python environment is not part of the backup.

Validation checks source and PDF hashes, all 40 slide start pages, all 40 complete quick briefs in extracted text, embedded fonts/images, working internal navigation, no blank pages and no text outside the page. PyMuPDF reports ReportLab Fit destinations as one-based named-page links; validation handles that representation. Initial visual inspection found a previous-slide running header; the final edition uses a consistent document header to avoid misattribution. Introductory, result and scatter pages were reviewed visually.

The [Vietnamese PDF](../../../ai-final-report-20261030/TRANSCRIPT_VI.pdf), [English PDF](../../../ai-final-report-20261030/TRANSCRIPT_EN.pdf) and [validation](../../../ai-final-report-20261030/transcript-pdf-validation.json) are linked from the persistent notes. Capture and push this coherent rendering checkpoint. Large PDF bytes belong to the sibling artifact store under existing archive policy; GitHub contains recovery metadata rather than those external bytes. No new research, authentication, scheduling or organiser upload occurs.
