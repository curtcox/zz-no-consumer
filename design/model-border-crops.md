# Reviewed model border crops

On 2026-09-09, inspected the reader-selected artwork using `panelart.pick`,
including automatically selected candidates. A scan of only `status: chosen`
misses the older Flux images. Of 31 reader-selected Flux WebP images, 22 had
textured off-white outer frames. Reviewed all 22 crops in the browser, including
all three model images on page 010. The other nine lacked a surrounding white frame.

Converted temporary copies with macOS `sips -s format png SOURCE --out TEMP.png`
for the standard-library PNG analyzer. `image_crop.py inspect TEMP.png --white-border
--ocr off` detects the paper margins. Its output is a suggestion: an eight-pixel
allowance clears irregular edges, then the largest centered 3:2 rectangle fits
the reader. Three crops instead anchor at the top left to preserve edge labels.
Internal split-panel dividers, caption backgrounds and black composition bars
are retained. Source WebP bytes are embedded unchanged in new `panel-fit` SVG
versions; adjacent JSON receipts record source hashes and reviewed coordinates.
Controlled lettering is applied after the crop by the existing builder.

| Panel | Original source | Crop [left, top, right, bottom] | Selected version |
| --- | --- | --- | --- |
| 002-01 | assets/art/panels/002-01/v01-flux2-klein-4b-1001.webp | [63, 46, 1143, 766] | v04 |
| 002-03 | assets/art/panels/002-03/v01-flux2-klein-4b-1001.webp | [45, 32, 1155, 772] | v04 |
| 002-04 | assets/art/panels/002-04/v01-flux2-klein-4b-1001.webp | [28, 24, 1159, 778] | v04 |
| 003-01 | assets/art/panels/003-01/v05-flux2-klein-4b-1001.webp | [60, 47, 1143, 769] | v08 |
| 003-05 | assets/art/panels/003-05/v01-flux2-klein-4b-1001.webp | [52, 34, 1153, 768] | v03 |
| 004-01 | assets/art/panels/004-01/v01-flux2-klein-4b-1001.webp | [50, 33, 1154, 769] | v04 |
| 004-02 | assets/art/panels/004-02/v02-flux2-klein-4b-1001.webp | [59, 47, 1142, 769] | v05 |
| 010-01 | assets/art/panels/010-01/v01-flux2-klein-4b-1001.webp | [52, 36, 1150, 768] | v04 |
| 010-03 | assets/art/panels/010-03/v02-flux2-klein-4b-1001.webp | [40, 29, 1165, 779] | v05 |
| 010-04 | assets/art/panels/010-04/v02-flux2-klein-4b-1001.webp | [63, 47, 1143, 767] | v05 |
| 014-01 | assets/art/panels/014-01/v01-flux2-klein-4b-1001.webp | [43, 30, 1159, 774] | v04 |
| 014-04 | assets/art/panels/014-04/v01-flux2-klein-4b-1001.webp | [31, 19, 1171, 779] | v04 |
| 014-05 | assets/art/panels/014-05/v01-flux2-klein-4b-1001.webp | [46, 32, 1156, 772] | v04 |
| 016-05 | assets/art/panels/016-05/v05-flux2-klein-4b-1001.webp | [63, 48, 1140, 766] | v08 |
| 025-01 | assets/art/panels/025-01/v01-flux2-klein-4b-1001.webp | [51, 35, 1152, 769] | v04 |
| 025-04 | assets/art/panels/025-04/v02-flux2-klein-4b-1001.webp | [61, 46, 1144, 768] | v05 |
| 034-01 | assets/art/panels/034-01/v05-flux2-klein-4b-1001.webp | [41, 38, 1148, 776] | v08 |
| 034-04 | assets/art/panels/034-04/v01-flux2-klein-4b-1001.webp | [50, 34, 1154, 770] | v04 |
| 042-01 | assets/art/panels/042-01/v02-flux2-klein-4b-1001.webp | [29, 28, 1151, 776] | v05 |
| 042-05 | assets/art/panels/042-05/v02-flux2-klein-4b-1001.webp | [51, 35, 1152, 769] | v05 |
| 050-05 | assets/art/panels/050-05/v02-flux2-klein-4b-1001.webp | [61, 47, 1144, 769] | v05 |
| 055-04 | assets/art/panels/055-04/v01-flux2-klein-4b-1001.webp | [45, 30, 1158, 772] | v04 |
