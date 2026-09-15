# C - Provenance & recontextualisation

## C1. Recontextualisation (reverse image search)
The instructor gives you ONE real photo (a public-domain image from Wikimedia Commons, chosen the day before)
with a FALSE caption: `recontext/claim.txt`. Your job: find the first occurrence online (date, place, author),
and write the graded verdict. Tools: Google Lens, Yandex Images, TinEye (sort by oldest), Bing Visual Search.

Instructor: pick an image with a documented upload history, save it as `recontext/photo.jpg`, strip its EXIF
(`exiftool -all= photo.jpg`), and write a caption placing it in another city and year.

## C2. Content Credentials (C2PA)
Public test files with valid, tampered and missing manifests:
  https://c2pa.org/public-testfiles/image/
Verify them with https://contentcredentials.org/verify or the CLI `c2patool file.jpg`.
Questions: which file has a valid manifest? which one was edited after signing? what does the ABSENCE of a
manifest prove (slide 23)?
