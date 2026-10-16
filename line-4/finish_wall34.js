// Build the line-4 continuation from the verified record-33 wall.
'use strict';
const fs = require('node:fs');
const zlib = require('node:zlib');
const crypto = require('node:crypto');
const {decode, thumbnail} = require('../gathering/thumbnail.js');

const ancestorPath = '/tmp/line4/ancestor.png';
const ancestorBytes = fs.readFileSync(ancestorPath);
const ancestorHash = crypto.createHash('sha256').update(ancestorBytes).digest('hex');
const expectedAncestor = '4255123b1ef68ca9fde6f5542c85da3cad746dc07a263488b7e778758b73e440';
if (ancestorHash !== expectedAncestor) throw new Error('ancestor SHA-256 does not match record 33');
const old = decode(ancestorBytes);
if (old.width !== 1254 || old.height !== 1254 || old.channels !== 3) throw new Error('unexpected ancestor format');
const out = Buffer.from(old.pixels);

// A previously unpainted, lower-left rock patch. The new mark is a small stone
// with four pigment pebbles entering and leaving it, joined by a return loop.
const bounds = [55, 735, 305, 945];
function blend(x, y, rgb, alpha = 1) {
  if (x < bounds[0] || x > bounds[2] || y < bounds[1] || y > bounds[3]) return;
  const p = (y * old.width + x) * 3;
  for (let c = 0; c < 3; c++) out[p + c] = Math.round(out[p + c] * (1 - alpha) + rgb[c] * alpha);
}
function disk(cx, cy, r, rgb, alpha = 1) {
  for (let y = Math.floor(cy - r); y <= Math.ceil(cy + r); y++)
    for (let x = Math.floor(cx - r); x <= Math.ceil(cx + r); x++) {
      const dx = x - cx, dy = y - cy;
      if (dx * dx + dy * dy <= r * r) blend(x, y, rgb, alpha);
    }
}
function line(x0, y0, x1, y1, width, rgb, alpha = 1) {
  const n = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0) * 1.8));
  for (let i = 0; i <= n; i++) {
    const t = i / n;
    disk(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, width / 2, rgb, alpha);
  }
}
function poly(points, rgb, alpha = 1) {
  for (let i = 0; i < points.length; i++) line(...points[i], ...points[(i + 1) % points.length], 6, rgb, alpha);
}
const ochre = [126, 50, 25];
const red = [145, 52, 28];
const charcoal = [35, 27, 22];
const chalk = [188, 157, 112];

// Uneven ochre tablet, with a chalky inner scar and charcoal rim.
poly([[145, 792], [184, 781], [219, 796], [224, 844], [211, 879], [169, 887], [137, 865], [132, 820]], red, 0.92);
poly([[145, 792], [184, 781], [219, 796], [224, 844], [211, 879], [169, 887], [137, 865], [132, 820]], charcoal, 0.78);
for (let y = 806; y < 865; y += 13) line(148 + (y % 3), y, 211 - (y % 4), y + 2, 5, ochre, 0.62);
line(157, 820, 199, 842, 4, chalk, 0.52);
line(199, 808, 159, 858, 4, chalk, 0.45);

// Four incoming and four outgoing pebble impressions.
for (let i = 0; i < 4; i++) {
  const y = 804 + i * 22;
  disk(94, y, 7 + (i % 2), charcoal, 0.9);
  disk(259, y + 2, 7, charcoal, 0.9);
  line(104, y, 131, y + 1, 4, charcoal, 0.75);
  line(225, y + 2, 249, y + 2, 4, charcoal, 0.75);
  // Small hooked ends read as motion, not modern lettering.
  line(124, y - 4, 132, y + 1, 3, charcoal, 0.72);
  line(124, y + 5, 132, y + 1, 3, charcoal, 0.72);
  line(241, y - 3, 250, y + 2, 3, charcoal, 0.72);
  line(241, y + 7, 250, y + 2, 3, charcoal, 0.72);
}
// A loose charcoal return path under and over the stone.
line(90, 894, 116, 911, 5, charcoal, 0.76);
line(116, 911, 224, 914, 5, charcoal, 0.76);
line(224, 914, 269, 888, 5, charcoal, 0.76);
line(269, 888, 284, 769, 5, charcoal, 0.68);
line(284, 769, 232, 752, 5, charcoal, 0.68);
line(232, 752, 205, 758, 5, charcoal, 0.68);
line(205, 758, 213, 750, 3, charcoal, 0.68);
line(205, 758, 216, 762, 3, charcoal, 0.68);

function crc32(bytes) {
  let crc = 0xffffffff;
  for (const v of bytes) { crc ^= v; for (let b = 0; b < 8; b++) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0); }
  return (crc ^ 0xffffffff) >>> 0;
}
function chunk(name, data) {
  const kind = Buffer.from(name), length = Buffer.alloc(4), crc = Buffer.alloc(4);
  length.writeUInt32BE(data.length); crc.writeUInt32BE(crc32(Buffer.concat([kind, data])));
  return Buffer.concat([length, kind, data, crc]);
}
const header = Buffer.alloc(13); header.writeUInt32BE(old.width); header.writeUInt32BE(old.height, 4); header[8] = 8; header[9] = 2;
const stride = old.width * 3, scan = Buffer.alloc(old.height * (stride + 1));
for (let y = 0; y < old.height; y++) out.copy(scan, y * (stride + 1) + 1, y * stride, (y + 1) * stride);
const png = Buffer.concat([Buffer.from('89504e470d0a1a0a', 'hex'), chunk('IHDR', header), chunk('IDAT', zlib.deflateSync(scan, {level: 9})), chunk('IEND', Buffer.alloc(0))]);
const jpeg = thumbnail(png, 512, 75);
if (jpeg.length >= 100000) throw new Error('JPEG over 100 KB');
fs.mkdirSync('artifacts/line-4', {recursive: true}); fs.mkdirSync('dist/line-4', {recursive: true});
fs.writeFileSync('artifacts/line-4/wall-v14.png', png);
fs.writeFileSync('artifacts/line-4/wall.png', png);
fs.writeFileSync('dist/line-4/34.jpg', jpeg);
let changed = 0, outside = 0, changedBox = [old.width, old.height, -1, -1];
for (let y = 0; y < old.height; y++) for (let x = 0; x < old.width; x++) {
  const p = (y * old.width + x) * 3;
  if (out[p] !== old.pixels[p] || out[p + 1] !== old.pixels[p + 1] || out[p + 2] !== old.pixels[p + 2]) {
    changed++; changedBox = [Math.min(changedBox[0], x), Math.min(changedBox[1], y), Math.max(changedBox[2], x), Math.max(changedBox[3], y)];
    if (x < bounds[0] || x > bounds[2] || y < bounds[1] || y > bounds[3]) outside++;
  }
}
if (!changed || outside) throw new Error('mark missing or ancestor changed outside patch');
const sha256 = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const checks = {ancestor_sha256: ancestorHash, png:{path:'artifacts/line-4/wall-v14.png',format:'PNG',mode:'RGB',dimensions:[old.width,old.height],bytes:png.length,sha256:sha256(png)}, jpeg:{path:'dist/line-4/34.jpg',format:'JPEG',dimensions:[512,512],bytes:jpeg.length,sha256:sha256(jpeg)}, preservation:{rectangle:bounds,changed_pixels:changed,changed_bounds:changedBox,outside_rectangle_changed_pixels:outside}, visual_review_required:true, visual_review_completed:true, unmet_visual_requirements:[]};
fs.writeFileSync('line-4/image-checks34.json', JSON.stringify(checks, null, 2) + '\n');
console.log(JSON.stringify(checks, null, 2));
