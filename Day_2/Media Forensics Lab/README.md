# Media Forensics Lab — Operation Riverbank (Day 2 afternoon, 3h)

| File | Audience | Content |
|---|---|---|
| `MediaForensics_Lab.md` / `.pdf` | students (EN) | workshops A-E (metadata, ELA/shadows, provenance & C2PA, video, CIB) + verification note + grading |
| `WriteUp_FR_MediaForensics_Lab.md` | instructor (FR) | why a synthetic dataset, every planted answer, measured results, pitfalls |
| `scripts/make_dataset.py` | instructor | generates `dataset/` and `instructor/ground_truth.json` (seeded) |
| `scripts/ela.py` | students | Error Level Analysis + embedded thumbnail extraction |
| `templates/verification_note.md` | students | the deliverable |
| `dataset/` | students | pre-generated with seed 42 (A_metadata, B_signal, C_provenance, D_video, E_cib) |
| `instructor_private/` | instructor | `ground_truth.json` + untouched original. **Move out of the shared folder before class.** |

Regenerate (the day before):

```bash
cd scripts && pip install pillow pandas numpy networkx imageio-ffmpeg
python3 make_dataset.py --out ../dataset --seed 42 && mv ../dataset/instructor ../instructor_private
```
Then add the C1 image (public-domain photo + false caption) in `dataset/C_provenance/recontext/`.
