/* Shared by the local display, published viewer, and browser regression fixtures. */
window.auditPanelFit = async function (root = document, {allowLegacy = false} = {}) {
  const errors = [];
  const pages = [...root.querySelectorAll('.page-art')];
  if (!pages.length) return [{problem: 'no panel pages'}];
  for (const page of pages) {

    const expected = Number(page.dataset.panels);
    const images = [...page.querySelectorAll(':scope > img')];
    const report = (problem, extra = {}) => errors.push({problem, expected, ...extra});
    if (!Number.isInteger(expected) || expected < 1) report('invalid panel count');
    if (images.length !== expected) report('panel count mismatch', {actual: images.length});
    const modern = page.dataset.panelLayout === '2';
    if (!modern && !allowLegacy) report('legacy panel layout');
    const bounds = page.getBoundingClientRect();
    if (!bounds.width || !bounds.height) report('zero-sized page');
    const rects = [];
    for (const [index, img] of images.entries()) {
      const r = img.getBoundingClientRect(), css = getComputedStyle(img);
      rects.push(r);
      const detail = {panel: index + 1, src: (img.getAttribute('src') || '').startsWith('data:') ? 'embedded image' : img.getAttribute('src')};
      if (!r.width || !r.height || css.display === 'none' || css.visibility === 'hidden' || Number(css.opacity) === 0) report('invisible panel', detail);
      if (!img.complete || !img.naturalWidth) report('image not loaded', detail);
      if (modern && !['left','top','width','height'].every(k => img.style[k])) report('missing panel coordinates', detail);
      if (r.left < bounds.left - 1 || r.top < bounds.top - 1 || r.right > bounds.right + 1 || r.bottom > bounds.bottom + 1) report('panel outside page', detail);
      for (let ancestor = img.parentElement; ancestor && ancestor !== document.body; ancestor = ancestor.parentElement) {
        const s = getComputedStyle(ancestor), a = ancestor.getBoundingClientRect();
        if ((['hidden','clip'].includes(s.overflowX) && (r.left < a.left - 1 || r.right > a.right + 1)) || (['hidden','clip'].includes(s.overflowY) && (r.top < a.top - 1 || r.bottom > a.bottom + 1))) {
          report('panel clipped by ancestor', detail); break;
        }
      }
      if (modern && img.naturalWidth && Math.abs(r.width - r.height * img.naturalWidth / img.naturalHeight) > 0.5) report('aspect mismatch', detail);
      // Sample the visible part only; scrolling offscreen is not a missing panel.
      const left = Math.max(r.left, 0), right = Math.min(r.right, innerWidth);
      const top = Math.max(r.top, 0), bottom = Math.min(r.bottom, innerHeight);
      if (right > left && bottom > top) {
        const hit = document.elementsFromPoint((left + right) / 2, (top + bottom) / 2)
          .find(el => el.closest('.page-art') === page && el !== page);
        if (hit && hit !== img && !img.contains(hit)) report('panel obscured inside page', detail);
      }
    }
    for (let i = 0; i < rects.length; i++) for (let j = i + 1; j < rects.length; j++) {
      const a = rects[i], b = rects[j];
      if (Math.min(a.right,b.right) - Math.max(a.left,b.left) > 1 && Math.min(a.bottom,b.bottom) - Math.max(a.top,b.top) > 1) report('panels overlap', {panels: [i + 1,j + 1]});
    }
  }
  return errors;
};
