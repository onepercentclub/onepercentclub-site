from django.db.models import Sum, Count
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

        if form and form.is_valid():
            start = form.get_start()
            stop = form.get_stop()

            order_payments = OrderPayment.objects.filter(created__gte=start, created__lte=stop, status='settled')
            order_payments_aggregated = order_payments.aggregate(Sum('amount'), Sum('transaction_fee'))

            bank_transactions = BankTransaction.objects.filter(book_date__gte=start, book_date__lte=stop)
            bank_credit = bank_transactions.filter(credit_debit='C').aggregate(Sum('amount'))['amount__sum']
            bank_debit = bank_transactions.filter(credit_debit='D').aggregate(Sum('amount'))['amount__sum']

            bank_cp = bank_transactions.filter(category_id=1)
            bank_cp_credit = bank_cp.filter(credit_debit='C').aggregate(Sum('amount'))['amount__sum']
            bank_cp_debit = bank_cp.filter(credit_debit='D').aggregate(Sum('amount'))['amount__sum']

            remote_docdata_payments = RemoteDocdataPayment.objects.filter(remote_payout__payout_date__gte=start, remote_payout__payout_date__lte=stop)
            remote_docdata_payments_aggregated = remote_docdata_payments.aggregate(Sum('amount_collected'), Sum('docdata_fee'), Sum('tpci'))

            remote_docdata_payouts = RemoteDocdataPayout.objects.filter(payout_date__gte=start, payout_date__lte=stop)
            remote_docdata_payouts_aggregated = remote_docdata_payouts.aggregate(Sum('payout_amount'))

            project_payouts = ProjectPayout.objects.filter(created__gte=start, created__lte=stop, status='settled') #
            project_payouts_aggregated = project_payouts.aggregate(Sum('amount_raised'), Sum('amount_payable'), Sum('organization_fee'))

            donations = Donation.objects.filter(created__gte=start, created__lte=stop, order__status='success')

            statistics.update({
                'orders': {
                    'total_amount': order_payments_aggregated['amount__sum'],
                    'transaction_fee': order_payments_aggregated['transaction_fee__sum'],
                    'count': order_payments.count(),
                },
                'donations': {
                    'total_amount': donations.aggregate(Sum('amount'))['amount__sum'],
                    'count': donations.count(),
                },
                'bank': {
                    'campaign_payout': {
                        'credit': bank_cp_credit,  # in
                        'debit': bank_cp_debit,    # out
                        'balance': bank_cp_credit - bank_cp_debit,
                        'count': bank_cp.count(),
                    },
                    'credit': bank_credit,  # in
                    'debit': bank_debit,    # out
                    'balance': bank_credit - bank_debit,
                    'count': bank_transactions.count(),
                },
                'docdata': {
                    'payment': {
                        'total_amount': remote_docdata_payments_aggregated['amount_collected__sum'],
                        'docdata_fee': remote_docdata_payments_aggregated['docdata_fee__sum'],
                        'third_party': remote_docdata_payments_aggregated['tpci__sum'],
                        'count': remote_docdata_payments.count()
                    },
                    'payout': {
                        'total_amount': remote_docdata_payouts_aggregated['payout_amount__sum'],
                        'count': remote_docdata_payouts.count()
                    },
                },
                'project_payouts': {
                    'per_payout_rule': project_payouts.order_by('payout_rule').values('payout_rule').annotate(
                        raised=Sum('amount_raised'),
                        payable=Sum('amount_payable'),
                        organization_fee=Sum('organization_fee'),
                        count=Count('payout_rule'),
                    ),
                    'raised': project_payouts_aggregated['amount_raised__sum'],
                    'payable': project_payouts_aggregated['amount_payable__sum'],
                    'organization_fee': project_payouts_aggregated['organization_fee__sum'],
                    'count': project_payouts.count()
                },
            })

            # Tpci (third party costs)
            # Tdf (docdata fee)

            statistics['docdata']['pending_orders'] = \
                statistics['orders']['total_amount'] - \
                statistics['docdata']['payout']['total_amount']

            statistics['docdata']['payout']['other_costs'] = \
                statistics['docdata']['payment']['total_amount'] - \
                statistics['docdata']['payment']['docdata_fee'] - \
                statistics['docdata']['payment']['third_party'] - \
                statistics['docdata']['payout']['total_amount']


        context = super(AccountingOverviewView, self).get_context_data(**kwargs)
        context.update({
             'app_label': 'accounting',
             'title': _('Accountancy Overview'),
             'statistics': statistics,
        })
        return context