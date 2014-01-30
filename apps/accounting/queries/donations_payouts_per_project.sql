-- Per project aggregate of donations versus payouts

-- List of projects, pending/paid donations and completed payouts in 2014.

-- Fields:
-- - id: project id
-- - title: project title
-- - last_donation: 'ready'/closed date of last paid/pending donation
-- - donation_count: total number of paid/pending donations
-- - donations: total amount of donations received (paid/pending)
-- - payout_date: date associated payout was completed
-- - payout_rule: payout rule used for calculating fees
-- - payouts_amount_raised: amount of donations when the payout was set in progress (bank transfer initiated)
-- - payouts_organization_fee: organization fee calculated from payouts_amount_raised according to payout_rule
-- - payouts_amount_paid: payable amount after substracting organization_fee from amount_raised
-- - amount_payable: donations - amount_raised

WITH payment_methods AS (
    SELECT DISTINCT
      order_id, payment_method_id AS payment_method
    FROM public.cowry_payment AS payments
), donations AS (
    SELECT
      project_id,
      MAX(donations.ready::date) AS last_donation,
      COUNT(donations.id),
      SUM(amount/100.0)::numeric(12,2) AS amount
    FROM
      fund_donation AS donations
    JOIN
      projects_project AS projects ON projects.id = donations.project_id
    LEFT JOIN
      payment_methods ON payment_methods.order_id = donations.order_id
    WHERE
      status IN ('paid', 'pending') AND
      donations.ready BETWEEN '2013-01-01' AND '2014-01-01'
    GROUP BY project_id
    ORDER BY project_id
)
SELECT
  projects.id,
  projects.title,
  donations.last_donation,
  donations.count AS donation_count,
  donations.amount AS donations,
  payouts.completed AS payout_date,
  payouts.payout_rule AS payout_rule,
  payouts.amount_raised AS payouts_amount_raised,
  payouts.organization_fee AS payouts_organization_fee,
  payouts.amount_payable AS payouts_amount_paid,
  donations.amount - coalesce(payouts.amount_raised, 0.0) AS amount_payable
FROM
  donations
LEFT JOIN payouts_payout AS payouts
  ON payouts.project_id = donations.project_id AND
     payouts.status = 'completed'
JOIN projects_project AS projects
  ON donations.project_id = projects.id
