#!/usr/bin/env python3
"""Check Gathering 34 bytes, records, scope and offline gallery structure."""
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess

from check_delivery import Gallery, jpeg_dimensions, png_dimensions


def main():
    wall_path = Path('artifacts/gathering/wall-v14.png')
    wall = wall_path.read_bytes()
    assert wall == Path('artifacts/gathering/wall.png').read_bytes()
    assert png_dimensions(wall) == (1254, 1254)
    assert wall[24:26] == bytes((8, 2)), 'need 8-bit RGB PNG'
    digest = hashlib.sha256(wall).hexdigest()
    jpeg = Path('dist/gathering/34.jpg').read_bytes()
    assert jpeg_dimensions(jpeg) == (512, 512) and len(jpeg) < 100000
    record = json.loads(Path('dist/gathering/34.json').read_text())
    assert set(record) == {'name', 'image', 'attributes'}
    assert record['image'] == 'https://api.imd.fun/artifacts/' + digest
    attributes = {item['trait_type']: item['value'] for item in record['attributes']}
    assert len(attributes) == len(record['attributes']) == 6
    assert set(attributes) == {'Cave', 'Wall', 'Number', 'Left behind', 'Meaning', 'One thing'}
    assert attributes['Cave'] == 'Ice' and attributes['Wall'] == 'Gathering'
    assert type(attributes['Number']) is int and attributes['Number'] == 34
    assert attributes['One thing'] == 'Gathering'
    goals = [{'line': n, 'goal': Path(f'line-{n}/GOAL.md').read_text().strip()}
             for n in range(1, 5)]
    assert json.loads(Path('dist/goals.json').read_text()) == goals

    content = Path('dist/index.html').read_text()
    gallery = Gallery(content)
    sources = sorted(Path('dist').glob('*/[0-9][0-9].json'))
    expected = {p.relative_to('dist').as_posix() for p in sources}
    assert len(content.encode()) < 100000
    assert len(gallery.records) == len(expected) == 170
    assert set(gallery.records) == expected
    assert len(gallery.images) == 70
    assert all(re.fullmatch(r'data:image/jpeg;base64,[A-Za-z0-9+/=]+', src)
               for src in gallery.images)
    assert not set(gallery.tags) & {'script', 'iframe', 'link'}
    assert len(base64.b64decode(gallery.images[0].split(',', 1)[1])) > 100
    for href in gallery.links:
        if href.startswith('#'):
            assert f'id="{href[1:]}"' in content
        elif not href.startswith('https://'):
            assert (Path('dist') / href).is_file(), href
    for wall_name in ('gathering', 'line-1', 'line-2', 'line-3', 'line-4'):
        keys = [key for key in gallery.records if key.startswith(wall_name + '/')]
        for unpainted in (False, True):
            subset = [key for key in keys if
                      (json.loads(Path('dist', key).read_text())['name'] == 'Not painted yet') == unpainted]
            assert subset == sorted(subset, reverse=True)
        for number in range(2, 22):
            source = Path('dist', wall_name, f'{number:02}.json')
            assert json.loads(source.read_text()) == {
                'name': 'Not painted yet',
                'image': 'https://api.imd.fun/artifacts/b5e794cb2c70bd232230e389707698c69c2080786d606a13b39f9315c9a90799',
                'attributes': [{'trait_type': 'Cave', 'value': 'Ice'}]}
            assert not source.with_suffix('.jpg').exists()

    assert Path('line-1/tools/payload-lens/payload_lens.py').read_bytes() == \
           Path('shared/http-evidence/payload_lens.py').read_bytes()
    adapted = Path('line-2/tools/csv-duplicates/duplicates.py').read_text().replace(
        "Path(__file__).resolve().parents[1] / 'csv-reconcile' / 'reconcile.py'",
        "Path(__file__).resolve().parent / 'reconcile.py'")
    assert adapted == Path('shared/http-evidence/duplicates.py').read_text()

    image = json.loads(Path('gathering/image-checks34.json').read_text())
    assert image['png']['sha256'] == digest
    assert image['png']['format'] == 'PNG' and image['png']['dimensions'] == [1254, 1254]
    assert image['jpeg']['format'] == 'JPEG' and image['jpeg']['dimensions'] == [512, 512]
    assert image['preservation']['changed_pixels'] > 0
    assert image['preservation']['outside_rectangle_changed_pixels'] == 0
    assert image['visual_review_completed'] and image['unmet_visual_requirements'] == []
    tests = json.loads(Path('gathering/test-runs34.json').read_text())
    assert tests['ok'] and tests['line_tests'] == 535 and tests['shared_tests'] == 97
    assert tests['gathering_tests'] == 8
    for name in ('integration-checks34', 'inherited-new-tool-checks34', 'new-tool-checks34'):
        assert json.loads(Path(f'gathering/{name}.json').read_text())['ok']
    assert not subprocess.run(['git', 'diff', 'HEAD', '--', 'line-1', 'line-2', 'line-3', 'line-4', 'dist/line-1', 'dist/line-2', 'dist/line-3', 'dist/line-4'], capture_output=True, check=True).stdout
    baseline = json.loads(Path('gathering/scope-before34.json').read_text())
    actual = {p.as_posix() for n in range(1, 5)
              for root in (Path(f'line-{n}'), Path(f'dist/line-{n}'))
              for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    assert actual == set(baseline), 'line paths added or removed'
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == digest
               for p, digest in baseline.items()), 'line bytes changed'
    for root in ('gathering', 'shared', 'dist'):
        for path in Path(root).rglob('*'):
            if path.is_file() and path.stat().st_size >= 100000:
                assert path.as_posix() in baseline, path
    assert Path('shared/http-evidence/framing_lens.py').read_bytes() == \
           Path('line-1/tools/framing-lens/framing_lens.py').read_bytes()
    expected_slice = Path('line-2/tools/csv-slice/slice.py').read_text().replace(
        "Path(__file__).resolve().parents[1] / 'csv-reconcile' / 'reconcile.py'",
        "Path(__file__).resolve().parent / 'reconcile.py'")
    assert Path('shared/http-evidence/review_slice.py').read_text() == expected_slice
    assert json.loads(Path('gathering/round32-checks34.json').read_text())['ok']
    adapted_age = Path('line-1/tools/freshness-lens/freshness_lens.py').read_text().replace("Path(__file__).resolve().parent.parent /\n    'payload-lens' / 'payload_lens.py'", "Path(__file__).resolve().parent / 'payload_lens.py'")
    assert adapted_age == Path('shared/http-evidence/freshness_lens.py').read_text()
    adapted_summary = Path('line-2/tools/csv-summary/summary.py').read_text().replace("Path(__file__).resolve().parents[1] / 'csv-reconcile' / 'reconcile.py'", "Path(__file__).resolve().parent / 'reconcile.py'")
    assert adapted_summary == Path('shared/http-evidence/change_summary.py').read_text()
    assert Path('gathering/COINS.md').read_text().splitlines()[0] == 'none'
    result = {'ok': True, 'png': {'format': 'PNG', 'mode': 'RGB',
              'dimensions': [1254, 1254], 'bytes': len(wall), 'sha256': digest},
              'jpeg': {'format': 'JPEG', 'dimensions': [512, 512], 'bytes': len(jpeg)},
              'gallery_records': 170, 'painted_previews': 70,
              'placeholders': 100, 'gallery_bytes': len(content.encode()),
              'line_paths_unchanged': True, 'unmet_visual_requirements': []}
    Path('gathering/delivery-checks34.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
