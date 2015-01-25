from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django import forms

from bluebottle.payments.models import OrderPayment
from bluebottle.donations.models import Donation

from apps.accounting.models import BankTransaction, RemoteDocdataPayment, RemoteDocdataPayout
from apps.payouts.models import ProjectPayout


class PeriodForm(forms.Form):
    start = forms.DateField()
    stop = forms.DateField()

    def clean(self):
        cleaned_data = super(PeriodForm, self).clean()

        start = cleaned_data.get('start')
        stop = cleaned_data.get('stop')

        if start > stop:
            raise forms.ValidationError(_('Start date cannot be before stop date.'))

        return cleaned_data

    def get_start(self):
        start = self.cleaned_data['start']
        return timezone.datetime(start.year, start.month, start.day, 0, 0, 0, tzinfo=timezone.utc)

    def get_stop(self):
        stop = self.cleaned_data['stop']
        return timezone.datetime(stop.year, stop.month, stop.day, 12, 59, 59, tzinfo=timezone.utc)


class AccountingOverviewView(FormView):
    template_name = 'admin/accounting/overview.html'
    form_class = PeriodForm

    def form_valid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        form = kwargs.get('form')

        statistics = {}
        pending = {}

        if form and form.is_valid():
            start = form.get_start()
            stop = form.get_stop()

            order_payments = OrderPayment.objects.filter(created__gte=start, created__lte=stop, status='settled')
            bank_transactions = BankTransaction.objects.filter(book_date__gte=start, book_date__lte=stop)
            remote_docdata_payments = RemoteDocdataPayment.objects.filter(local_payment__created__gte=start, local_payment__created__lte=stop, local_payment__status='settled')
            remote_docdata_payouts = RemoteDocdataPayout.objects.filter(payout_date__gte=start, payout_date__lte=stop)
            project_payouts = ProjectPayout.objects.filter(created__gte=start, created__lte=stop, status='settled') #
            donations = Donation.objects.filter(created__gte=start, created__lte=stop, order__status='success')

            bank_credit = bank_transactions.filter(credit_debit='C').aggregate(Sum('amount'))['amount__sum']
            bank_debit = bank_transactions.filter(credit_debit='D').aggregate(Sum('amount'))['amount__sum']

            statistics.update({
                'orders': {
                    'total_amount': order_payments.aggregate(Sum('amount'))['amount__sum'],
                    'transaction_fee': order_payments.aggregate(Sum('transaction_fee'))['transaction_fee__sum'],
                    'count': order_payments.count(),
                },
                'donations': {
                    'total_amount': donations.aggregate(Sum('amount'))['amount__sum'],
                    'count': donations.count(),
                },
                'bank': {
                    'credit': bank_credit,  # in
                    'debit': bank_debit,    # out
                    'balance': bank_credit - bank_debit,
                    'count': bank_transactions.count(),
                },
                'docdata_payments': {
                    'total_amount': remote_docdata_payments.aggregate(Sum('amount_collected'))['amount_collected__sum'],
                    'docdata_fee': remote_docdata_payments.aggregate(Sum('docdata_fee'))['docdata_fee__sum'],
                    'count': remote_docdata_payments.count()
                },
                'docdata_payouts': {
                    'total_amount': remote_docdata_payouts.aggregate(Sum('payout_amount'))['payout_amount__sum'],
                    'count': remote_docdata_payouts.count()
                },
                'project_payouts': {
                    'raised': project_payouts.aggregate(Sum('amount_raised'))['amount_raised__sum'],
                    'paid': project_payouts.aggregate(Sum('amount_payable'))['amount_payable__sum'],
                    'organization_fee': project_payouts.aggregate(Sum('organization_fee'))['organization_fee__sum'],
                    'count': project_payouts.count()
                },
            })

            pending.update({
                # Balance (saldo) of pending (to be paid) projects (all orders minus all payments to projects)
                'project': {
                    'total_order': statistics['orders']['total_amount'],
                    'total_payment': 0,
                    'balance': 0
                },
                # Balance (saldo) of pending (to be paid) orders (pending or paid orders not yet processed by Docdata)
                'orders': {
                    'total_order': 0,
                    'total_docdata': 0,
                    'balance': 0,
                },
                # Balance (saldo) of pending (to be paid) service fees to Docdata
                'fees_docdata': {
                },
                # Balance (saldo) of pending (to be paid) service fees to 1%Club
                'fees_organization': {
                },
                # Balance (saldo) of pending (to be paid) by Docdata to 1%Club (not yet processed/recieved by Bank)
                'docdata_payouts': {
                }
            })

        context = super(AccountingOverviewView, self).get_context_data(**kwargs)
        context.update({
             'app_label': 'accounting',
             'title': _('Accountancy Overview'),
             'statistics': statistics,
             'pending': pending,
        })
        return context
