import operator

from django.db import models
from django.core.urlresolvers import reverse
from raven.contrib.django.raven_compat.models import client as raven_client

from japper.monitoring.plugins.models import MonitoringSourceBase
from japper.monitoring.status import Status
from .client import GraphiteClient, average
from .exceptions import InvalidDataFormat, EmptyData


class MonitoringSource(MonitoringSourceBase):

    endpoint = models.CharField(max_length=4096,
            help_text='The base URL of the graphite endpoint')

    def get_check_results(self):
        client = GraphiteClient(self.endpoint)
        ret = []
        for check in self.checks.all():
            ret.append(check.run(client))
        return ret

    def get_absolute_url(self):
        return reverse('graphite_update_monitoring_source',
                kwargs={'pk': self.pk})

    def get_ui_entry_points(self):
        return [
            ('checks', reverse('graphite_checks', kwargs={'pk': self.pk})),
        ]

    def has_dynamic_hosts(self):
        # The notion of hosts in graphite backend is for grouping only
        return True


class Check(models.Model):

    OPERATORS = [
        (0, '<'),
        (1, '<='),
        (2, '=='),
        (3, '!='),
        (4, '>='),
        (5, '>'),
    ]
    OPERATOR_FUNCS = [
        operator.lt,
        operator.le,
        operator.eq,
        operator.ne,
        operator.ge,
        operator.gt,
    ]
    AGGREGATORS = [
        (0, 'average'),
        (1, 'max'),
        (2, 'min'),
    ]
    AGGREGATOR_FUNCS = [average, max, min]

    source = models.ForeignKey(MonitoringSource, related_name='checks',
            editable=False)

    name = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)
    target = models.CharField(max_length=4096)
    metric_aggregator = models.SmallIntegerField(choices=AGGREGATORS, default=0)
    host = models.CharField(max_length=255, null=True, blank=True)
    warning_operator = models.SmallIntegerField(choices=OPERATORS, default=0)
    warning_value = models.FloatField()
    critical_operator = models.SmallIntegerField(choices=OPERATORS, default=0)
    critical_value = models.FloatField()

    def run(self, client):
        try:
            agg_func = self.AGGREGATOR_FUNCS[self.metric_aggregator]
            try:
                value = client.get_metric(self.target, aggregator=agg_func)
            except (InvalidDataFormat, EmptyData) as exc:
                return self.build_check_dict(Status.unknown, str(exc))
            warning_func = self.OPERATOR_FUNCS[self.warning_operator]
            critical_func = self.OPERATOR_FUNCS[self.critical_operator]
            if critical_func(value, self.critical_value):
                status = Status.critical
            elif warning_func(value, self.warning_value):
                status = Status.warning
            else:
                status = Status.passing
            return self.build_check_dict(status,
                    '%s %s' % (self.name, status.name),
                    metrics={self.name: value})
        except Exception as exc:
            raven_client.captureException()
            return self.build_check_dict(Status.unknown,
                'unexpected error: %s' % exc)

    def build_check_dict(self, status, output=None, metrics={}):
        return {
            'name': self.name,
            'host': self.host,
            'status': status,
            'output': output,
            'metrics': metrics,
        }

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('graphite_update_check', kwargs={'pk': self.pk})
