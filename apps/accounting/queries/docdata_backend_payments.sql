-- Show Docdata payments and fees and corresponding backend data

-- List of Docdata payment as exported from their backend with matching payment information from the backend system, sorted by the date the payment was set to pending or paid (ready).

-- Fields:
--  - merchant_reference: payment reference
--  - payment_type: action can be paid, chargedback etc. - for chargebacks expect a 'paid' first with positive amount and 'chargedback' with negative amount with additional costs later
--  - donation_ready: date when payment was set to pending or paid
--  - docdata_tpci: Docdata third party costs
--  - docdata_fee: fee taken by Docdata
--  - docdata_fee_total: docdata_tpci + docdata_fee
--  - backend_fee: fee as registered by the backend
--  - fee_difference: docdata_fee - backend_fee
--  - docdata_amount: payment amount as registered by docdata
--  - backend_amount: amount as registered by backend
--  - amount_difference: docdata_amount - backend_amount

-- Note: these are *all* payments done corresponding to the *new* Docdata account.
-- Hence legacy donations are not in this dataset.

SELECT
  accounting_docdatapayment.merchant_reference,
  accounting_docdatapayment.payment_type,
  DATE(donations.ready) AS donation_ready,
  coalesce(accounting_docdatapayment.tpci, 0) AS docdata_tpci,
  coalesce(accounting_docdatapayment.docdata_fee, 0) AS docdata_fee,
  coalesce(accounting_docdatapayment.tpci, 0) + coalesce(accounting_docdatapayment.docdata_fee, 0) AS docdata_fee_total,
  (cowry_payment.fee/100.0)::numeric(12,2) AS backend_fee,
  coalesce(accounting_docdatapayment.tpci, 0) + coalesce(accounting_docdatapayment.docdata_fee, 0) - (cowry_payment.fee/100.0)::numeric(12,2) AS fee_difference,
  accounting_docdatapayment.amount_collected AS docdata_amount,
  (cowry_payment.amount/100.0)::numeric(12,2) AS backend_amount,
  accounting_docdatapayment.amount_collected - (cowry_payment.amount/100.0)::numeric(12,2) AS amount_difference
FROM
  public.accounting_docdatapayment,
  public.cowry_docdata_docdatapaymentorder,
  public.cowry_payment,
  public.fund_donation AS donations
WHERE
  cowry_docdata_docdatapaymentorder.merchant_order_reference = accounting_docdatapayment.merchant_reference AND
  cowry_payment.id = cowry_docdata_docdatapaymentorder.payment_ptr_id AND
  donations.order_id = cowry_payment.order_id
ORDER BY
  donations.ready
