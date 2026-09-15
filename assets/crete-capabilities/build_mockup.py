# /// script
# dependencies = ["pyyaml"]
# ///
"""Rebuild the standalone mock-up from the user-downloaded METR TH 1.1 YAML.
Run: UV_CACHE_DIR=/tmp/crete-uv uv run assets/crete-capabilities/build_mockup.py
Source: https://metr.org/time-horizons/ (inspected 2026-09-12).
Horizon values are MINUTES of human expert time, not agent runtime.
"""
import json
import re
from pathlib import Path
import yaml


def main():
    here = Path(__file__).resolve().parent
    raw = yaml.safe_load((here / 'benchmark_results_1_1.yaml').read_text())
    points = [dict(id=k, date=str(v['release_date']), **v['metrics'])
              for k, v in raw['results'].items()]
    html = (here / 'mockup_template.html').read_text().replace('__DATA__', json.dumps(points))
    (here.parent.parent / '2609_FORTH_Crete/capabilities_mockup.html').write_text(html)
    chart = re.sub(r'<section id="questions".*?</section>', '', html, flags=re.S)
    chart = re.sub(r'<section id="cases".*?</section>', '', chart, flags=re.S)
    chart = re.sub(r'<footer>.*?</footer>', '', chart, flags=re.S)
    chart = chart.replace('<section id="measurement">', '<section id="measurement" class="active">')
    chart = chart.replace('</style>', """main{max-width:none;padding:0 18px}section{min-height:0}#measurement .eyebrow,#measurement h1{display:none}#measurement .sub{font-size:23px;margin:0 0 8px}#measurement button{font-size:17px;padding:8px 16px}#measurement #detail{font-size:16px;min-height:24px}#measurement .note,#measurement #forecast-note{font-size:16px}summary{cursor:pointer}#measurement .chart{width:auto;max-width:100%;max-height:none;height:calc(100vh - 95px);min-height:0;margin:0 auto}</style>""")
    (here / 'chart.html').write_text(chart)


if __name__ == '__main__':
    main()
