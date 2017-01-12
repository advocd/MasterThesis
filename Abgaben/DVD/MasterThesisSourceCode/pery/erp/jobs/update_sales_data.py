from django.db.models import Sum, Max

from erp.models import Partner, Invoice
from pery_batch.job import PeryJob

import datetime

class UpdateSalesData(PeryJob):
    '''
    This Job will used to gather and aggregate the context sensitve data.
    The intervall of the executing for this job could be configured into the
    Jobs-Settings in Pery
    '''

    def run(self):

        # gather data from the db (reverse by the Invoice) and create dictonaries ordered by Partner ID
        partners_total_turnovers = Invoice.objects.filter(is_released=True).values('partner__id').annotate(total_turnover=Sum('grand_total_without_tax') ).order_by('partner')
        partners_total_turnovers = {x['partner__id']: {'total_turnover': x['total_turnover']} for x in partners_total_turnovers}

        # get datetime from last year
        d = datetime.datetime.now() - datetime.timedelta(days=365)
        partners_last_year_turnovers = Invoice.objects.filter(is_released=True, date__gte=d).values('partner__id').annotate(last_year_turnover=Sum('grand_total_without_tax') ).order_by('partner')
        partners_last_year_turnovers = {x['partner__id']: {'last_year_turnover': x['last_year_turnover']} for x in partners_last_year_turnovers}

        partner_last_invoice = Invoice.objects.filter(is_released=True).values('partner__id').annotate(last_invoice=Max('date')).order_by('partner')
        partner_last_invoice = {x['partner__id']: {'last_invoice': x['last_invoice']} for x in partner_last_invoice}

        for partner in Partner.objects.all():

            has_changed = False

            temp_total_turnover = partners_total_turnovers.get(partner.pk, {'total_turnover': None}).get('total_turnover')
            temp_last_year_turnover = partners_last_year_turnovers.get(partner.pk, {'last_year_turnover': None}).get('last_year_turnover')
            temp_last_invoice = partner_last_invoice.get(partner.pk, {'last_invoice': None}).get('last_invoice')

            if temp_total_turnover:
                if temp_total_turnover != partner.sales_total_turnover:
                    partner.sales_total_turnover = temp_total_turnover
                    has_changed = True

            if temp_last_year_turnover:
                if temp_last_year_turnover != partner.sales_last_year_turnover:
                    partner.sales_last_year_turnover = temp_last_year_turnover
                    has_changed = True

            if temp_last_invoice:
                # if not partner.sales_last_invoice or temp_last_invoice >= partner.sales_last_invoice.date():
                if not partner.sales_last_invoice or temp_last_invoice >= partner.sales_last_invoice.date():

                    partner.sales_last_invoice = temp_last_invoice
                    has_changed = True

            if not self.simulate and has_changed:
                partner.save()
