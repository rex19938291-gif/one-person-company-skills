"""相容入口；實際互動版由 scripts/interactive/build.py 產生。"""
import argparse
from interactive.build import build

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('config');build(p.parse_args().config)
