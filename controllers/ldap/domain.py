#!/usr/bin/env python
# encoding: utf-8

# Author: Zhang Huangbin <michaelbibby (at) gmail.com>

import sys
import web
from web import render
from web import iredconfig as cfg
from controllers.ldap import base
from controllers.ldap.basic import dbinit
from libs.ldaplib import core, admin, domain

session = web.config.get('_session')

adminLib = admin.Admin()
domainLib = domain.Domain()

#
# Domain related.
#
class list(dbinit):
    '''List all virtual mail domains.'''
    @base.protected
    def GET(self):
        i = web.input()
        self.domains = domainLib.list()
        return render.domains(domains=self.domains, msg=i.get('msg', None))

    @base.check_global_admin
    @base.protected
    def POST(self):
        i = web.input(domainName=[])
        domainName = i.get('domainName', None)
        result = domainLib.delete(domainName)
        web.seeother('/domains')

class profile(dbinit):
    @base.protected
    def GET(self, domain):
        i = web.input()
        domain = web.safestr(domain.split('/', 1)[0])
        if domain != '' and domain is not None and \
            profile_type in ['general', 'admins', 'services', 'bcc', 'quotas', 'backupmx', 'advanced', ]:

            domain = web.safestr(domain)
            profile = domainLib.profile(domain)

            if profile:
                allDomains = domainLib.list(attrs=['domainName'])
                allAdmins = adminLib.list()
                domainAdmins = domainLib.admins(domain)

                return render.domain_profile(
                        cur_domain=domain,
                        allDomains=allDomains,
                        profile=profile,
                        profile_type=profile_type,
                        admins=allAdmins,
                        # We need only mail address of domain admins.
                        domainAdmins=domainAdmins[0][1].get('domainAdmin', []),
                        msg=i.get('msg', None),
                        )
            else:
                web.seeother('/domains?msg=%s' % i.get('msg', None))
        else:
            web.seeother('/domains?msg=%s' % i.get('msg', None))

    @base.protected
    def POST(self, profile_type, domain):
        self.profile_type = web.safestr(profile_type)
        self.domain = web.safestr(domain)

        i = web.input(enabledService=[],)

        result = domainLib.update(
                profile_type=self.profile_type,
                domain=self.domain,
                data=i,
                )
        if result[0] is True:
            web.seeother('/profile/domain/%s/%s?msg=SUCCESS' % (self.profile_type, self.domain) )
        elif result[0] is False:
            web.seeother('/profile/domain/%s/%s?msg=%s' % (self.profile_type, self.domain, result[1]) )

class create(dbinit):
    @base.check_global_admin
    @base.protected
    def GET(self):
        return render.domain_create()

    @base.check_global_admin
    @base.protected
    def POST(self):
        i = web.input()
        domainName = i.get('domainName', None)
        cn = i.get('cn', None)
        result = domainLib.add(domainName=domainName, cn=cn)
        if result is True:
            web.seeother('/domains')
        else:
            return render.domain_create(msg=result)
