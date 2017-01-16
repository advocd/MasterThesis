
from django.db import models
from erp.models import BaseModelParent, BaseModelPosition
from django.conf import settings
from django.db.models import Max, Min
from django.utils.translation import ugettext_lazy as _, ugettext as __

class PeryDataRank():
    def __init__(self, display_filter_name, clazz, attr, sort_inverse=False):
        '''
        The PeryDataFilter is used to get data dynamic from a Model

        :param filter_name: is the technical name of the filter for internal use
        :param display_filter_name: is in use to display in frontend
        :param clazz_attr: is used to define the attribute for the filter
                        example:    use the attr. sales_total_turnover from the pery model
                                    attr = 'sales_total_turnover'
        :param clazz: is used to define the fk (e.g 'partner__sales_total_turnover' use 'partner')
        :param attr: is used to define the attribute which should used for the filter
                        (e.g 'partner__sales_total_turnover' use 'sales_total_turnover')
        '''

        self.display_filter_name = display_filter_name
        self.clazz = clazz
        self.attr = attr
        self.clazz_attr = '%s__%s' %(clazz, attr)
        self.sort_inverse = sort_inverse

    def get_aggregated_min_max(self, qs):
        temp_aggr_dict = qs.aggregate(min_val=Min(self.clazz_attr), max_val=Max(self.clazz_attr))
        return temp_aggr_dict.get('min_val'), temp_aggr_dict.get('max_val')

    def get_value_from_attr(self, obj):
        return getattr(obj, self.attr)


class Trip (BaseModelParent):
    '''
    Used to describe a class which act as a container for a set of selected points.
    This selection set is
    '''
    title = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), editable=False, blank=True, null=True)

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = 'erp'
        verbose_name = _('trip')
        verbose_name_plural = _('trips')

    def get_tripstations(self):
        '''
        Get all elements which are registered to the Tripstation
        :return:
            tripstations: Queryset (lazy)
        '''
        return TripStation.objects.filter(parent=self)


    def sorting_tripstations(self):
        for index, station in enumerate(self.get_tripstations().order_by('ordering'), start=1):
            station.ordering = index
            station.save()

    def remove_tripstation_by_addr(self, addr_pk):
        self.get_tripstations().get(address=addr_pk).delete()
        self.sorting_tripstations()

    def get_ordered_tripstations_pk(self):
        '''
        Get a String of the PK's from the Tripstations which are ordered
        by her ordering
        :return:
            ordered_pks: String
        '''

        ordered_pks = ''
        for tripstat in self.get_tripstations().order_by('ordering'):
            if ordered_pks:
                ordered_pks += ',%s' %tripstat.address.pk
            else:
                ordered_pks = str(tripstat.address.pk)

        return ordered_pks


class TripStation (BaseModelPosition):
    '''
    Used to describe a point which is registered into a Trip
    '''
    title = models.CharField(max_length=100, blank=True)
    parent = models.ForeignKey(Trip)
    ordering = models.IntegerField()
    partner = models.ForeignKey('erp.Partner')
    address = models.ForeignKey('erp.PartnerAddress')

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = 'erp'
        verbose_name = _('trip station')
        verbose_name_plural = _('trip stations')

    def save(self, *args, **kwargs):
        if not self.ordering:
            try:
                self.ordering = TripStation.objects.filter(parent=self.parent).order_by('-ordering')[0].ordering + 1
            except TripStation.DoesNotExist:
                self.ordering = 1
            except IndexError:
                self.ordering = 1

        super(TripStation, self).save(*args, **kwargs)

