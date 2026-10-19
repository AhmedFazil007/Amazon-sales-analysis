# Reproducing the order analysis

The workbook is supplied as `data/Amazon Sale Report.xlsb`. The Python script reads it with `pandas` and `pyxlsb`, standardizes commonly used column names, exports CSV summaries and builds a SQLite database.

```bash
pip install pandas pyxlsb
python python/analyze_amazon.py
```

If the first worksheet is not the order data, run `python python/analyze_amazon.py --sheet "Sheet Name"`. The script prints source columns and the mapping it chose. Adjust the alias dictionary if needed.

**Important:** This script has been added as reproducible source code but has **not yet been executed against the 24 MB XLSB workbook in this environment**. Outputs will be generated only after it is run successfully. A row may be an order line, not a unique order; reported amounts should not be described as realized or net sales without checking the source's cancellation and return rules.

After running the script, open `analysis/amazon_orders.sqlite` in a SQLite client and run `sql/operations_analysis.sql`. Queries using optional fields need those fields to exist in the workbook.
