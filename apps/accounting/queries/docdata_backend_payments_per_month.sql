-- Monthly aggregation of docdata_backend_payments

WITH docdata_payments AS (
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
)

SELECT
  date_trunc('month', donation_ready)::date AS month,
  SUM(docdata_fee_total) AS docdata_fee_total,
  SUM(backend_fee) AS backend_fee,
  SUM(docdata_fee_total) - SUM(backend_fee) AS fee_difference,
  SUM(docdata_amount) AS docdata_amount,
  SUM(backend_amount) AS backend_amount,
  SUM(docdata_amount) - SUM(backend_amount) AS amount_difference
FROM docdata_payments
GROUP BY month
ORDER BY month
