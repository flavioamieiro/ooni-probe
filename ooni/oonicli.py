#!/usr/bin/env python
# -*- coding: UTF-8
#
#    oonicli
#    *******
#
#    :copyright: (c) 2012 by Arturo Filastò
#    :license: see LICENSE for more details.
#

import sys

from twisted.python import usage
from twisted.plugin import getPlugins
from twisted.internet import reactor

from zope.interface.exceptions import BrokenImplementation
from zope.interface.exceptions import BrokenMethodImplementation
from zope.interface.verify import verifyObject
from pprint import pprint

from ooni.plugoo import tests, work, assets
from ooni.logo import getlogo
from ooni import plugins

__version__ = "0.0.1-prealpha"

def retrieve_plugoo():
    """
    Get all the plugins that implement the ITest interface and get the data
    associated to them into a dict.
    """
    interface = tests.ITest
    d = {}
    error = False
    for p in getPlugins(interface, plugins):
        try:
            verifyObject(interface, p)
            d[p.shortName] = p
        except BrokenImplementation, bi:
            print "Plugin Broken"
            print bi
            error = True
    if error != False:
        print "Plugin Loaded!"
    return d

plugoo = retrieve_plugoo()

def runTest(test, options, global_options):

    parallelism = int(global_options['parallelism'])
    worker = work.Worker(parallelism)
    test = plugoo[test].__class__

    #if options['asset']:
    #    print options['asset']
    #    asset = assets.Asset(options['asset'])
    #    print asset

    wgen = work.WorkGenerator(test(options, global_options),
                              dict(options),
                              start=options['resume'])

    for x in wgen:
        worker.push(x)

    reactor.run()

class Options(usage.Options):
    tests = plugoo.keys()
    subCommands = []
    for test in tests:
        subCommands.append([test, None, plugoo[test].options, "Run the %s test" % test])

    optFlags = [
        #['remote', 'r', "If the test should be run remotely (not supported)"],
        #['status', 'x', 'Show current state'],
        #['restart', 'r', 'Restart OONI']
    ]

    optParameters = [
        ['parallelism', 'n', 10, "Specify the number of parallel tests to run"],
        #['target-node', 't', 'localhost:31415', 'Select target node'],
        ['output', 'o', 'report.log', "Specify output report file"],
        ['log', 'l', 'oonicli.log', "Specify output log file"],
        #['password', 'p', 'opennetwork', "Specify the password for authentication"],
    ]

    def opt_version(self):
        """
        Display OONI version and exit.
        """
        print "OONI version:", __version__
        sys.exit(0)

    def __str__(self):
        """
        Hack to get the sweet ascii art into the help output and replace the
        strings "Commands" with "Tests".
        """
        return getlogo() + '\n' + self.getSynopsis() + '\n' + \
               self.getUsage(width=None).replace("Commands:", "Tests:")

config = Options()
config.parseOptions()

if not config.subCommand:
    print "Error! No Test Specified."
    config.opt_help()
    sys.exit(1)

runTest(config.subCommand, config.subOptions, config)

