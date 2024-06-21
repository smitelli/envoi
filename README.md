Envoi
=====

Converts YAML invoice data into reasonably well-formatted PDFs.

by [Scott Smitelli](mailto:scott@smitelli.com)

The Quick Bits
--------------

```bash
python -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install --editable .[dev]

.venv/bin/envoi
```

"Source" File Definition
------------------------

The base name of the source file will be used to name the output file. As an
example, `sources/240601-01.yaml` will generate `output/240601-01.pdf` when
it is processed. If the source file has its `paid` flag set, the output file
is slightly modified to `output/240601-01.paid.pdf`

```yaml
# String containing the base name (without `.yaml`) of the payer file in the
# `payers/` directory to pull unchanging information from. The example payer
# file will be in `payers/example.yaml`.
payer: example

# Mark this invoice as paid. Produces a PDF with a red "PAID" overlay and
# adds a `paid` tag to the output filename (this prevents overwriting the
# original PDF that was originally sent.) Defaults false.
paid: false

# Date this invoice was generated. Affects the invoice number, and the
# invoice/due dates shown in the box.
invoice_date: 2024-06-01

# Integer sequence number identifying this invoice within a single date. Only
# incremented when more than one invoice is produced on a single
# `invoice_date` -- usually this stays at 1.
invoice_seq: 1

# Integer number of days. This is added to `invoice_date` to produce the due
# date shown at the top of the PDF. If this date falls on a weekend, it is
# adjusted ahead to the following Monday.
days_due_in: 30

# Optional floating point adjustments value. Added if positive, subtracted if
# negative. Changes the final total of the invoice without introducing a
# specific ledger line to account for it. Explain it in `notes`! Defaults 0.
adjustments: 0.00

# Optional string of text to show in a notes box at the end of the PDF.
# Defaults empty.
notes: Thank you for your business.

# Optional floating point value. If this is set and any item in `ledger` does
# not have a `rate`, this value will be used for that item's rate. Has no
# default -- if this is not set and something in `ledger` needs it, the PDF
# will not be built.
default_rate: 100.00

# List of maps, each element representing one line of ledger data to show on
# the invoice. All of the ledger lines are printed in the order defined, and
# their totals are summed together to produce the total amount due.
ledger:
    - date: 2024-05-03  # The date when this item was incurred.
      qty: 1            # The number of units purchased/utilized.
      rate: 99.99       # The price for one unit.
      description: One  # Freeform text to display in the description box.

    - date: 2024-05-10  # Second item. This uses the global `default_rate`.
      qty: 1.5
      description: One and a half hours!
```

"Payer" File Definition
-----------------------

The payer file is designed to hold default values that never change between
invoices. For example, the "bill to" address likely has the same content for
the duration of the business relationship, so it can be pulled in by
reference via the payer file.

Any top-level key supported in a source file can be given here, with the
exception of `payer`.

```yaml
# List of strings to display as the address in the header on page one of the
# PDF. Each list element is separated with a bullet and laid out on one line.
header_address:
    - Element 1
    - Element 2

# List of strings to display as the footer on page one of the PDF. Formatted
# similarly to `header_address`.
footer_address:
    - Element 1
    - Element 2

# List of strings to use in the "BILL TO" box.
bill_to_address:
    - Line 1
    - Line 2

# Optional area. Any key:value allowed in a source file (except for `payer`)
# can be given here, and will take effect in any instance where a source file
# does not have that top-level key set.
days_due_in: 60  # In this example, the source file no longer needs this now.
```
