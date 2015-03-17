#!/usr/bin/python2
# -*- coding: utf-8 -*-
#
# The Qubes OS Project, http://www.qubes-os.org
#
# Copyright (C) 2010  Rafal Wojtczuk  <rafal@invisiblethingslab.com>
# Copyright (C) 2013  Marek Marczykowski <marmarek@invisiblethingslab.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#
import xen.lowlevel.xc
import xen.lowlevel.xs
import string
import time
import qmemman_algo
import os
from notify import notify_error_qubes_manager, clear_error_qubes_manager

import logging

no_progress_msg="VM refused to give back requested memory"
slow_memset_react_msg="VM didn't give back all requested memory"

class DomainState:
    def __init__(self, id):
        self.meminfo = None		#dictionary of memory info read from client
        self.memory_actual = None	#the current memory size
        self.memory_maximum = None	#the maximum memory size
        self.mem_used = None		#used memory, computed based on meminfo
        self.id = id			#domain id
        self.last_target = 0		#the last memset target
        self.no_progress = False    #no react to memset
        self.slow_memset_react = False #slow react to memset (after few tries still above target)

class SystemState(object):
    def __init__(self):
        self.log = logging.getLogger('qmemman.systemstate')
        self.log.debug('SystemState()')

        self.domdict = {}
        self.xc = xen.lowlevel.xc.xc()
        self.xs = xen.lowlevel.xs.xs()
        self.BALOON_DELAY = 0.1
        self.XEN_FREE_MEM_LEFT = 50*1024*1024
        self.XEN_FREE_MEM_MIN = 25*1024*1024
        self.ALL_PHYS_MEM = self.xc.physinfo()['total_memory']*1024

    def add_domain(self, id):
        self.log.debug('add_domain(id={!r})'.format(id))
        self.domdict[id] = DomainState(id)

    def del_domain(self, id):
        self.log.debug('del_domain(id={!r})'.format(id))
        self.domdict.pop(id)

    def get_free_xen_memory(self):
        return self.xc.physinfo()['free_memory']*1024
#        hosts = self.xend_session.session.xenapi.host.get_all()
#        host_record = self.xend_session.session.xenapi.host.get_record(hosts[0])
#        host_metrics_record = self.xend_session.session.xenapi.host_metrics.get_record(host_record["metrics"])
#        ret = host_metrics_record["memory_free"]
#        return long(ret)

#refresh information on memory assigned to all domains
    def refresh_memactual(self):
        for domain in self.xc.domain_getinfo():
            id = str(domain['domid'])
            if self.domdict.has_key(id):
                self.domdict[id].memory_actual = domain['mem_kb']*1024
                self.domdict[id].memory_maximum = self.xs.read('', '/local/domain/%s/memory/static-max' % str(id))
                if self.domdict[id].memory_maximum:
                    self.domdict[id].memory_maximum = int(self.domdict[id].memory_maximum)*1024
                else:
                    self.domdict[id].memory_maximum = self.ALL_PHYS_MEM
# the previous line used to be
#                    self.domdict[id].memory_maximum = domain['maxmem_kb']*1024
# but domain['maxmem_kb'] changes in self.mem_set as well, and this results in
# the memory never increasing
# in fact, the only possible case of nonexisting memory/static-max is dom0
# see #307

    def clear_outdated_error_markers(self):
        # Clear outdated errors
        for i in self.domdict.keys():
            if self.domdict[i].slow_memset_react and \
                    self.domdict[i].memory_actual <= self.domdict[i].last_target + self.XEN_FREE_MEM_LEFT/4:
                dom_name = self.xs.read('', '/local/domain/%s/name' % str(i))
                if dom_name is not None:
                    clear_error_qubes_manager(dom_name, slow_memset_react_msg)
                self.domdict[i].slow_memset_react = False

            if self.domdict[i].no_progress and \
                    self.domdict[i].memory_actual <= self.domdict[i].last_target + self.XEN_FREE_MEM_LEFT/4:
                dom_name = self.xs.read('', '/local/domain/%s/name' % str(i))
                if dom_name is not None:
                    clear_error_qubes_manager(dom_name, no_progress_msg)
                self.domdict[i].no_progress = False

#the below works (and is fast), but then 'xm list' shows unchanged memory value
    def mem_set(self, id, val):
        self.log.info('mem-set domain {} to {}'.format(id, val))
        self.domdict[id].last_target = val
#can happen in the middle of domain shutdown
#apparently xc.lowlevel throws exceptions too
        try:
            self.xc.domain_setmaxmem(int(id), int(val/1024) + 1024) # LIBXL_MAXMEM_CONSTANT=1024
            self.xc.domain_set_target_mem(int(id), int(val/1024))
        except:
            pass
        self.xs.write('', '/local/domain/' + id + '/memory/target', str(int(val/1024)))

# this is called at the end of ballooning, when we have Xen free mem already
# make sure that past mem_set will not decrease Xen free mem
    def inhibit_balloon_up(self):
        self.log.debug('inhibit_balloon_up()')
        for i in self.domdict.keys():
            dom = self.domdict[i]
            if dom.memory_actual is not None and dom.memory_actual + 200*1024 < dom.last_target:
                self.log.info(
                    'Preventing balloon up to {}'.format(dom.last_target))
                self.mem_set(i, dom.memory_actual)

#perform memory ballooning, across all domains, to add "memsize" to Xen free memory
    def do_balloon(self, memsize):
        self.log.info('do_balloon(memsize={!r})'.format(memsize))
        MAX_TRIES = 20
        niter = 0
        prev_memory_actual = None

        for i in self.domdict.keys():
            self.domdict[i].no_progress = False

        while True:
            self.log.debug('niter={:2d}/{:2d}'.format(niter, MAX_TRIES))
            self.refresh_memactual()
            xenfree = self.get_free_xen_memory()
            self.log.info('xenfree={!r}'.format(xenfree))
            if xenfree >= memsize + self.XEN_FREE_MEM_MIN:
                self.inhibit_balloon_up()
                return True
            if prev_memory_actual is not None:
                for i in prev_memory_actual.keys():
                    if prev_memory_actual[i] == self.domdict[i].memory_actual:
                        #domain not responding to memset requests, remove it from donors
                        self.domdict[i].no_progress = True
                        self.log.info('domain {} stuck at {}'.format(i, self.domdict[i].memory_actual))
            memset_reqs = qmemman_algo.balloon(memsize + self.XEN_FREE_MEM_LEFT - xenfree, self.domdict)
            self.log.info('memset_reqs={!r}'.format(memset_reqs))
            if niter > MAX_TRIES or len(memset_reqs) == 0:
                return False
            prev_memory_actual = {}
            for i in memset_reqs:
                dom, mem = i
                self.mem_set(dom, mem)
                prev_memory_actual[dom] = self.domdict[dom].memory_actual
            self.log.debug('sleeping for {} s'.format(self.BALOON_DELAY))
            time.sleep(self.BALOON_DELAY)
            niter = niter + 1

    def refresh_meminfo(self, domid, untrusted_meminfo_key):
        self.log.debug(
            'refresh_meminfo(domid={}, untrusted_meminfo_key={!r})'.format(
                domid, untrusted_meminfo_key))

        qmemman_algo.refresh_meminfo_for_domain(
            self.domdict[domid], untrusted_meminfo_key)
        self.do_balance()

#is the computed balance request big enough ?
#so that we do not trash with small adjustments
    def is_balance_req_significant(self, memset_reqs, xenfree):
        self.log.debug(
            'is_balance_req_significant(memset_reqs={}, xenfree={})'.format(
                memset_reqs, xenfree))

        total_memory_transfer = 0
        MIN_TOTAL_MEMORY_TRANSFER = 150*1024*1024
        MIN_MEM_CHANGE_WHEN_UNDER_PREF = 15*1024*1024

        # If xenfree to low, return immediately
        if self.XEN_FREE_MEM_LEFT - xenfree > MIN_MEM_CHANGE_WHEN_UNDER_PREF:
            self.log.debug('xenfree is too low, returning')
            return True

        for rq in memset_reqs:
            dom, mem = rq
            last_target = self.domdict[dom].last_target
            memory_change = mem - last_target
            total_memory_transfer += abs(memory_change)
            pref = qmemman_algo.prefmem(self.domdict[dom])

            if last_target > 0 and last_target < pref and memory_change > MIN_MEM_CHANGE_WHEN_UNDER_PREF:
                self.log.info(
                    'dom {} is below pref, allowing balance'.format(dom))
                return True

        ret = total_memory_transfer + abs(xenfree - self.XEN_FREE_MEM_LEFT) > MIN_TOTAL_MEMORY_TRANSFER
        self.log.debug('is_balance_req_significant return {}'.format(ret))
        return ret


    def print_stats(self, xenfree, memset_reqs):
        for i in self.domdict.keys():
            if self.domdict[i].meminfo is not None:
                self.log.info('stat: dom {!r} act={} pref={}'.format(i,
                    self.domdict[i].memory_actual,
                    qmemman_algo.prefmem(self.domdict[i])))

        self.log.info('stat: xenfree={} memset_reqs={}'.format(xenfree, memset_reqs))


    def do_balance(self):
        self.log.debug('do_balance()')
        if os.path.isfile('/var/run/qubes/do-not-membalance'):
            self.log.debug('do-not-membalance file preset, returning')
            return

        self.refresh_memactual()
        self.clear_outdated_error_markers()
        xenfree = self.get_free_xen_memory()
        memset_reqs = qmemman_algo.balance(xenfree - self.XEN_FREE_MEM_LEFT, self.domdict)
        if not self.is_balance_req_significant(memset_reqs, xenfree):
            return

        self.print_stats(xenfree, memset_reqs)

        prev_memactual = {}
        for i in self.domdict.keys():
            prev_memactual[i] = self.domdict[i].memory_actual
        for rq in memset_reqs:
            dom, mem = rq
            # Force to always have at least 0.9*self.XEN_FREE_MEM_LEFT (some
            # margin for rounding errors). Before giving memory to
            # domain, ensure that others have gived it back.
            # If not - wait a little.
            ntries = 5
            while self.get_free_xen_memory() - (mem - self.domdict[dom].memory_actual) < 0.9*self.XEN_FREE_MEM_LEFT:
                self.log.debug('do_balance dom={!r} sleeping ntries={}'.format(
                    dom, ntries))
                time.sleep(self.BALOON_DELAY)
                ntries -= 1
                if ntries <= 0:
                    # Waiting haven't helped; Find which domain get stuck and
                    # abort balance (after distributing what we have)
                    self.refresh_memactual()
                    for rq2 in memset_reqs:
                        dom2, mem2 = rq2
                        if dom2 == dom:
                            # All donors have been procesed
                             break
                        # allow some small margin
                        if self.domdict[dom2].memory_actual > self.domdict[dom2].last_target + self.XEN_FREE_MEM_LEFT/4:
                            # VM didn't react to memory request at all, remove from donors
                            if prev_memactual[dom2] == self.domdict[dom2].memory_actual:
                                self.log.warning(
                                    'dom {!r} didnt react to memory request'
                                    ' (holds {}, requested balloon down to {})'
                                        .format(dom2,
                                            self.domdict[dom2].memory_actual,
                                            mem2))
                                self.domdict[dom2].no_progress = True
                                dom_name = self.xs.read('', '/local/domain/%s/name' % str(dom2))
                                if dom_name is not None:
                                    notify_error_qubes_manager(str(dom_name), no_progress_msg)
                            else:
                                self.log.warning('dom {!r} still hold more'
                                    ' memory than have assigned ({} > {})'
                                        .format(dom2,
                                            self.domdict[dom2].memory_actual,
                                            mem2))
                                self.domdict[dom2].slow_memset_react = True
                                dom_name = self.xs.read('', '/local/domain/%s/name' % str(dom2))
                                if dom_name is not None:
                                    notify_error_qubes_manager(str(dom_name), slow_memset_react_msg)
                    self.mem_set(dom, self.get_free_xen_memory() + self.domdict[dom].memory_actual - self.XEN_FREE_MEM_LEFT)
                    return

            self.mem_set(dom, mem)

#        for i in self.domdict.keys():
#            print 'domain ', i, ' meminfo=', self.domdict[i].meminfo, 'actual mem', self.domdict[i].memory_actual
#            print 'domain ', i, 'actual mem', self.domdict[i].memory_actual
#        print 'xen free mem', self.get_free_xen_memory()
