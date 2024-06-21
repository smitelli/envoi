import sys
import yaml
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from envoi.invoice import Invoice

ROOT_DIR = Path(__file__).resolve().parents[1]
SOURCES_DIR = ROOT_DIR / 'sources'
PAYERS_DIR = ROOT_DIR / 'payers'
OUTPUT_DIR = ROOT_DIR / 'output'


@dataclass
class Data:
    header_address: list[str]
    footer_address: list[str]
    bill_to_address: list[str]
    invoice_date: date
    invoice_seq: int
    days_due_in: int
    ledger: list[dict]
    adjustments: float = 0.0
    notes: str = ''
    paid: bool = False

    @property
    def invoice_number(self):
        return f'{self.invoice_date.strftime("%y%m%d")}-{self.invoice_seq:02}'

    @property
    def total(self):
        return sum(e['qty'] * e['rate'] for e in self.ledger) + self.adjustments

    @property
    def due_date(self):
        dt = self.invoice_date + timedelta(days=self.days_due_in)
        while dt.weekday() >= 5:
            dt += timedelta(days=1)
        return dt


def die(message):
    print(f'{sys.argv[0]}: {message}', file=sys.stderr)
    sys.exit(1)


def build_file(data_dict, output_file):
    if default_rate := data_dict.pop('default_rate', None):
        for entry in data_dict['ledger']:
            entry.setdefault('rate', default_rate)

    data_obj = Data(**data_dict)

    inv = Invoice(data_obj)
    inv.format_page()

    output_file.parent.mkdir(parents=True, exist_ok=True)
    inv.output(output_file)


def build_sources():
    for source_file in SOURCES_DIR.rglob('*'):
        with source_file.open(mode='r') as f:
            source_data = yaml.safe_load(f)
            payer_name = source_data.pop('payer')

        payer_file = PAYERS_DIR / f'{payer_name}.yaml'
        with payer_file.open(mode='r') as f:
            payer_data = yaml.safe_load(f)

        if 'payer' in payer_data:
            die(f'Payer file {payer_file} should not have a `payer` value')

        source_data = payer_data | source_data

        tag = '.paid' if source_data.get('paid') else ''
        output_file = OUTPUT_DIR / f'{source_file.stem}{tag}.pdf'

        try:
            t = output_file.stat().st_mtime
            if t >= source_file.stat().st_mtime and t >= payer_file.stat().st_mtime:
                continue
        except FileNotFoundError:
            pass

        print(f'Building {output_file}...', end='', flush=True)
        build_file(source_data, output_file)
        print(' done.')
