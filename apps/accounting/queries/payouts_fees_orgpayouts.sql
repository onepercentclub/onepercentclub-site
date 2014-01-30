-- Organization payouts versus payouts versus calculated fees
WITH payouts AS (
  -- Completed payouts
  SELECT
    completed AS date,
    amount_raised,
    organization_fee,
    amount_payable
  FROM
    payouts_payout AS payouts
  WHERE
    payouts.status = 'completed'
), psp_fees AS (
  -- PSP fees for paid, chargeback and refunded payments
  SELECT
    payments.fee,
    donations.ready AS date
  FROM
    public.cowry_payment payments
  JOIN
    public.fund_donation donations ON payments.order_id = donations.order_id
  WHERE
    payments.status IN ('paid', 'chargedback', 'refunded')
), bank_mutations AS (
  -- Bank mutations
  SELECT
    book_date,
    CASE
      WHEN credit_debit = 'D' THEN amount
      WHEN credit_debit = 'C' THEN -amount
    END AS mutation
  FROM
    public.accounting_banktransaction
  ORDER BY book_date
), docdata_bank_in AS (
  -- Incoming money from Docdata
  SELECT
    amount, book_date
  FROM
    public.accounting_banktransaction
  WHERE
    credit_debit = 'C' AND
    counter_name LIKE '%DOCDATA%'
), docdata_out AS (
  -- Money going out from Docdata, should match incoming money
  SELECT
    end_date, total
  FROM
    public.accounting_docdatapayout
)
