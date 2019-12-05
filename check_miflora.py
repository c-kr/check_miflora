#!/usr/bin/env python3

import argparse
import logging
import nagiosplugin
import re
import sys
import time

from btlewrap.gatttool import GatttoolBackend

from miflora.miflora_poller import MiFloraPoller, \
    MI_CONDUCTIVITY, MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY

_log = logging.getLogger('nagiosplugin')

class Environment(nagiosplugin.Resource):
    def __init__(self, mac):
        self._mac = mac

    def probe(self):
        poller = MiFloraPoller(self._mac, GatttoolBackend)
        _log.info('-'*50)
        _log.info('Getting data from Mi Flora')
        _log.info('-'*50)
        # logging name and firmware creates another poll, activate only if needed
        #_log.info('Firmware: %s', poller.firmware_version())
        #_log.info('Name: %s', poller.name())

        return [
            nagiosplugin.Metric('Temperature', poller.parameter_value(MI_TEMPERATURE), min=0, context='temperature'),
            nagiosplugin.Metric('Moisture', poller.parameter_value(MI_MOISTURE), min=0, context='moisture'),
            nagiosplugin.Metric('Light', poller.parameter_value(MI_LIGHT), min=0, context='light'),
            nagiosplugin.Metric('Conductivity', poller.parameter_value(MI_CONDUCTIVITY), min=0, context='conductivity'),
            nagiosplugin.Metric('Battery', poller.parameter_value(MI_BATTERY), min=0, context='battery')
        ]

class EnvironmentSummary(nagiosplugin.Summary):

    def __init__(self):
        pass

    def ok(self, results):
        ok_list=list()
        for r in ['Temperature', 'Moisture', 'Light', 'Conductivity', 'Battery']:
            ok_list.append('%s is %s' % (r, results[r].metric))
        return ', '.join(ok_list)
   
@nagiosplugin.guarded
def main():

    contexts = ['temperature', 'moisture', 'light', 'conductivity', 'battery']

    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument('-m', '--mac', required=True, type=str,
                      help='Miflora MAC address')

    for context in contexts:
        argp.add_argument('--%s-warning' % context, metavar='RANGE', default='',
                      help='return warning if %s is outside RANGE' % context)
        argp.add_argument('--%s-critical' % context, metavar='RANGE', default='',
                      help='return critical if %s is outside RANGE' % context)

    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        Environment(args.mac),
        nagiosplugin.ScalarContext('temperature', args.temperature_warning, args.temperature_critical),
        nagiosplugin.ScalarContext('moisture', args.moisture_warning, args.moisture_critical),
        nagiosplugin.ScalarContext('light', args.light_warning, args.light_critical),
        nagiosplugin.ScalarContext('conductivity', args.conductivity_warning, args.conductivity_critical),
        nagiosplugin.ScalarContext('battery', args.battery_warning, args.battery_critical),
        EnvironmentSummary())
    check.main(verbose=args.verbose)

if __name__ == '__main__':
    main()


