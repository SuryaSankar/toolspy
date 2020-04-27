from __future__ import absolute_import
import csv
import xlsxwriter


def split_csv_into_columns(csvfilepath):
    cols = {}
    with open(csvfilepath) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for k, v in row.items():
                if k not in cols:
                    cols[k] = []
                cols[k].append(v)
    return cols


def write_xlsx_sheet(xlsx_file, rows=[], cols=[]):
    """
    If cols is mentioned, then each entry in rows should be of format
    {
        "Name": "Surya", "Email": "Surya@inkmonk.com"
    }
    If cols is not given, then each entry in row should be a list of values
    ["Surya", "Surya@inkmonk.com"]
    """
    workbook = xlsxwriter.Workbook(xlsx_file)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': 1})
    text_wrap = workbook.add_format({'text_wrap': 1})
    if len(cols) > 0:
        for col, heading in enumerate(cols):
            worksheet.write(0, col, heading, bold)
        for row_index, row in enumerate(rows):
            for col_index, col_name in enumerate(cols):
                worksheet.write(
                    row_index + 1, col_index, row.get(col_name, ""), text_wrap)
    else:
        for row_index, row_cells in enumerate(rows):
            for col, cell in enumerate(row_cells):
                worksheet.write(row_index, col, cell, text_wrap)
    workbook.close()


def write_csv_file(csvfile, rows, cols):
    if isinstance(csvfile, str):
        with open(csvfile, 'w') as file:
            write_csv_file(file, rows, cols)
    else:
        writer = csv.DictWriter(csvfile, fieldnames=cols)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
