-- Paid out (Docdata payout exports) versus received (bank statements) funds
--
-- Fields:
-- - month: month of bank's book date resp. end of Docdata's payout period
-- - amount_out: monthly total transferred to bank account according to Docdata
-- - amount_in: monthly total of incoming bank transactions from Docdata according to bank statements
-- - difference: amount_out - amount_in
-- - running_difference: difference running over months

WITH docdata_bank_in AS (
  -- Incoming money from Docdata
  SELECT
    date_trunc('month', book_date)::date AS month,
    SUM(amount) AS amount
  FROM
    public.accounting_banktransaction
  WHERE
    credit_debit = 'C' AND
    counter_name ILIKE '%docdata%'
  GROUP BY month
  ORDER BY month
), docdata_import_out AS (
  -- Money going out from Docdata, should match incoming money
  SELECT
    date_trunc('month', end_date)::date AS month,
    SUM(total) AS amount
  FROM
    public.accounting_docdatapayout
  GROUP BY month
  ORDER BY month
)

SELECT
  docdata_import_out.month,
  docdata_import_out.amount AS amount_out,
  docdata_bank_in.amount AS amount_in,
  docdata_import_out.amount - docdata_bank_in.amount AS difference,
  SUM(docdata_import_out.amount - docdata_bank_in.amount) OVER(ORDER BY docdata_import_out.month) as running_difference
FROM docdata_import_out
LEFT JOIN
  docdata_bank_in ON docdata_bank_in.month = docdata_import_out.month
