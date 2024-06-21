from datetime import datetime
from importlib.metadata import version
from math import atan2, degrees
from pathlib import Path
from fpdf import FPDF
from fpdf.fonts import FontFace

ROOT_DIR = Path(__file__).resolve().parents[1]
BULLET = '\u2022'
SILCROW = '\u00a7'


def format_date(val):
    return f'{val.month}/{val.day}/{val:%Y}'


def format_price(val):
    abs_formatted = f'${abs(val):,.02f}'
    if val < 0:
        abs_formatted = f'-{abs_formatted}'
    return abs_formatted


class Invoice(FPDF):
    MARKDOWN_LINK_UNDERLINE = False

    def __init__(self, data):
        self.data = data
        self.accent_color = '#0a3678'
        self.logo_file = ROOT_DIR / 'assets/Logo.svg'
        self.logo_aspect = 5.656

        super().__init__(orientation='portrait', unit='in', format='letter')
        self.set_margins(left=1.25, top=0.5, right=1.25)  # 6 x 10 effective
        self.set_auto_page_break(auto=True, margin=self.t_margin)

        self.add_font(family='Roboto Black', fname=ROOT_DIR / 'assets/Roboto-Black.ttf')
        self.add_font(family='Roboto Medium', fname=ROOT_DIR / 'assets/Roboto-Medium.ttf')
        self.add_font(family='Roboto Light', fname=ROOT_DIR / 'assets/Roboto-Light.ttf')

        self.set_font(family='Roboto Light', size=11)
        self.head_style = FontFace(color=255, fill_color=self.accent_color)
        self.bold_style = FontFace(family='Roboto Medium')

        self.set_title(f'[{SILCROW}] Invoice {self.data.invoice_number}')
        self.set_author('Scott Smitelli')
        self.set_creator(f'{__package__} {version(__package__)}')
        self.set_producer(f'fpdf2 {version("fpdf2")}')
        self.set_creation_date(datetime.now())

    def header(self):
        logo_w = self.epw / 2
        logo_h = logo_w / self.logo_aspect
        bar_h = self.t_margin + logo_h + self.t_margin

        if self.page_no() == 1:
            bar_h += (self.t_margin / 2)

        with self.local_context(fill_color=self.accent_color):
            self.rect(x=0, y=0, w=self.w, h=bar_h, style='F')
            self.image(
                name=self.logo_file, x=self.l_margin, y=self.t_margin, w=logo_w,
                alt_text=f'[{SILCROW}] Scott Smitelli')

        with self.local_context(font_size=14, text_color=255):
            with self.local_context(font_size=(logo_h / 1.2) * self.k):
                self.cell(w=self.epw, align='R', new_x='LMARGIN', new_y='NEXT', text='INVOICE')

            with self.use_font_face(self.bold_style):
                self.cell(
                    w=self.epw, align='R', new_x='LMARGIN', new_y='NEXT',
                    text=self.data.invoice_number)

            if self.page_no() == 1:
                self.ln()
                ht = f'  {BULLET}  '.join(self.data.header_address)
                self.cell(w=self.epw, align='C', text=ht, markdown=True)

        self.set_y(bar_h)
        self.ln()

    def footer(self):
        self.set_y(-self.t_margin)

        if self.page_no() == 1:
            ft = f'   {BULLET}   '.join(self.data.footer_address)
        else:
            ft = f'{self.page_no()} of {{nb}}'

        with self.local_context(font_size=14, text_color=96):
            self.cell(w=self.epw, align='C', text=ft, markdown=True)

        if self.data.paid:
            self.stamp_paid()

    def stamp_paid(self):
        fs = self.w_pt / 2.4
        fs_unit = fs / self.k
        rot = degrees(atan2(self.h, self.w))
        halfw = self.w / 2
        halfh = self.h / 2

        self.set_xy(0, halfh - (fs_unit / 2.25))

        with (
            self.rotation(rot, halfw, halfh),
            self.local_context(text_mode='CLIP', font_family='Roboto Black', font_size=fs)
        ):
            self.cell(w=self.w, align='C', text='PAID')
            y = 0
            while y < self.h:
                with self.local_context(line_width=0.01, draw_color='#f00'):
                    self.line(0, y, self.w, y)
                y += 0.05

    def format_page(self):
        self.add_page()

        l_start = self.y
        self.data_box('BILL TO', '\n'.join(self.data.bill_to_address), 'L', 3.9)
        l_end = self.y

        self.set_y(l_start)
        self.data_box('INVOICE DATE', format_date(self.data.invoice_date), 'R', 1.9)
        self.data_box('TOTAL DUE', format_price(self.data.total), 'R', 1.9)
        self.data_box('DUE DATE', format_date(self.data.due_date), 'R', 1.9)
        self.set_y(max(l_end, self.y))

        self.data_table()

        if self.data.notes:
            self.data_box('NOTES', self.data.notes, 'L', 3.9)

    def data_box(self, t1, t2, align, width):
        with self.local_context(draw_color=self.accent_color), self.table(
            align=align, width=width, headings_style=self.head_style,
            padding=(0.1, 0.05), line_height=1.5 * self.font_size
        ) as table:
            table.row([t1])
            table.row([t2], style=self.bold_style)

        self.ln()

    def data_table(self):
        with self.local_context(draw_color=self.accent_color), self.table(
            col_widths=(2, 6, 1, 2, 2), text_align=('L', 'L', 'R', 'R', 'R'),
            v_align='T', borders_layout='NONE', headings_style=self.head_style,
            padding=(0.1, 0.05), line_height=1.5 * self.font_size
        ) as table:
            table.get_cell_border = self._cell_border_control

            table.row(['DATE', 'ITEM DESCRIPTION', 'QTY', 'PRICE', 'AMOUNT'])

            for line in self.data.ledger:
                row = table.row()
                row.cell(format_date(line['date']))
                row.cell(line['description'])
                row.cell(str(line['qty']))
                row.cell(format_price(line['rate']))
                row.cell(format_price(line['qty'] * line['rate']), style=self.bold_style)

            row = table.row()
            row.cell(None, rowspan=2, colspan=2)
            row.cell('ADJUSTMENTS', colspan=2, style=self.head_style)
            row.cell(format_price(self.data.adjustments), style=self.bold_style)

            row = table.row()
            row.cell('TOTAL', colspan=2, style=self.head_style)
            row.cell(format_price(self.data.total), style=self.bold_style)

        self.ln()

    @staticmethod
    def _cell_border_control(i, j, cell):
        if cell.text is None:
            return ''
        return 'LRTB'
