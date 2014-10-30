import abc

import six
from django.db import models
from django.db.models.base import ModelBase


class ABCModelMeta(abc.ABCMeta, ModelBase):

    pass


class BackendInstanceBase(six.with_metaclass(ABCModelMeta, models.Model)):

    name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class MonitoringSourceBase(BackendInstanceBase):
    '''
    Base model for monitoring sources.
    '''

    @abc.abstractmethod
    def get_check_results(self):
        '''
        Return a list of check results.

        This must return a list of dicts of the form::

            {
                'host': 'foo.com',
                'name': 'memory',
                'status': Status.passing,
                'output': 'OK - 75.0% used',
                'metrics': {
                    'free': '2G',
                    'used': '6G',
                    'swap': 0,
                },
            }

        Metrics must be a dict containing integers, floats or human-readable
        byte sizes values. It can also be None if the check does not have
        associated metrics.
        '''

    def get_removed_hosts(self):
        '''
        Return the list of hosts names that must be removed from monitoring.

        The default implementation returns an empty list.
        '''
        return []

    class Meta:
        abstract = True


class AlertSinkBase(BackendInstanceBase):
    '''
    Base model for alert sinks.
    '''

    @abc.abstractmethod
    def send_alert(self, prev_state, new_state, user=None):
        '''
        Format and send an alert when a :class:`japper.monitoring.models.State`
        changes from *prev_state* to *new_state*.

        *user* may or may not be given depending on the scope of the sink
        (per-user or global), it is the responsibility of the implementation to
        send a message or not depending on its presence.
        '''

    class Meta:
        abstract = True
