-- Monthly aggregate of donations versus payouts

-- List of months, pending/paid donations and completed payouts over 2014.

-- Fields:
-- - month: month a donation was 'ready'/closed / payout was set to completed
-- - donation_count: total number of paid/pending donations
-- - donations: total amount of donations received (paid/pending)
-- - payouts_count: amount of payouts in the month
-- - payouts_amount_raised: amount of donations when the payout was set in progress (bank transfer initiated)
-- - payouts_organization_fee: organization fee calculated from payouts_amount_raised according to payout_rule
-- - payouts_amount_paid: payable amount after substracting organization_fee from amount_raised
-- - amount_payable: donations - amount_raised
-- - running_amount_payable: difference of amount_payable running over months

WITH payment_methods AS (
    SELECT DISTINCT
      order_id, payment_method_id AS payment_method
    FROM public.cowry_payment AS payments
), donations AS (
    SELECT
      date_trunc('month', donations.ready)::date AS month,
      COUNT(donations.id),
      SUM(donations.amount/100.0)::numeric(12,2) AS amount
    FROM
      fund_donation AS donations
    JOIN
      projects_project AS projects ON projects.id = donations.project_id
    LEFT JOIN
      payment_methods ON payment_methods.order_id = donations.order_id
    WHERE
      donations.status IN ('paid', 'pending')
    GROUP BY month
    ORDER BY month
), payouts AS (
    SELECT
      date_trunc('month', completed)::date AS month,
      COUNT(id),
      SUM(amount_raised) AS amount_raised,
      SUM(organization_fee) AS organization_fee,
      SUM(amount_payable) AS amount_payable
    FROM
      payouts_payout AS payouts
    WHERE status = 'completed'
    GROUP BY month
    ORDER BY month
)
SELECT
  donations.month,
  donations.count AS donation_count,
  donations.amount AS donations_amount,
  payouts.count AS payouts_amount_count,
  payouts.amount_raised AS payouts_amount_raised,
  payouts.organization_fee AS payouts_organization_fee,
  payouts.amount_payable AS payouts_amount_paid,
  donations.amount - coalesce(payouts.amount_raised, 0.0) AS amount_payable,
  SUM(donations.amount - coalesce(payouts.amount_raised, 0.0)) OVER(ORDER BY donations.month) as running_payable
FROM donations
LEFT JOIN
  payouts ON payouts.month = donations.month
WHERE donations.month BETWEEN '2013-01-01' AND '2014-01-01'
