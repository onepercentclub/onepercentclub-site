Registering payments
--------------------

Donation: The amount of the Order can be divided among one or more projects, a donation. Let's say project A gets a donation of EUR 25 (amount=25) and project B gets a donation of EUR 20 (amount=20).

Order: The donations are part of an Order, in this case of EUR 45 (status=success, amount=45).

OrderPayment: Stores the payment method, transaction fee (amount=45, status=settled). This model is somewhat artificial and redudent in the case of 1 payment provider.

(Docdata)Payment: Each OrderPayment is paid via a payment provider, and in our case this is Docdata (total_gross_amount=4500 # in cents).
(DocdataDirectDebit)Payment: Same as above, except!

Import
------

RemoteDocdataPayout: Imported weekly CSV file metadata (payout_reference=pop...). Each line is saved as a RemoteDocdataPayment.

RemoteDocdataPayment: Imported entries from Docdata CSV files (triple_deal_reference=pid..., remote_payout=<RemoteDocdataPayout>, local_payment=<(Docdata)Payment>, amount_collected=45, type=paid, docdata_fee=0.15).

BankTransaction: Imported entries from the bank CSV files.

Admin
-----

1. Import Remote Docdata Payments (exports from Docdata): /admin/accounting/remotedocdatapayment/import/
2. Import Bank Transactions (exports from Rabobank): /admin/accounting/banktransaction/import/
3. Select all Bank Transactions, and perform "Try to match with Payouts."
