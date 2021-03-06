# -*- encoding: utf-8 -*-

# Dissemin: open access policy enforcement tool
# Copyright (C) 2014 Antonin Delpeuch
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

from __future__ import unicode_literals

from os import path
from unittest import expectedFailure

from django.test import TestCase
from lxml import etree

from deposit.hal.metadataFormatter import AOFRFormatter
from deposit.hal.protocol import HALProtocol
from deposit.tests import ProtocolTest
from papers.models import Paper


class AOFRTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super(AOFRTest, cls).setUpClass()
        xsd_fname = path.join(path.dirname(__file__), 'aofr-sword.xsd')
        with open(xsd_fname, 'r') as f:
            elem = etree.parse(f)
            cls.xsd = etree.XMLSchema(elem)

    @expectedFailure
    def test_generate_metadata_doi(self):
        f = AOFRFormatter()
        dois = ['10.1175/jas-d-15-0240.1']
        for doi in dois:
            p = Paper.create_by_doi(doi)
            rendered = f.render(p, 'article.pdf')
            with open('/tmp/xml_validation.xml', 'w') as f:
                f.write(etree.tostring(rendered, pretty_print=True))
            self.xsd.assertValid(rendered)


class HALProtocolTest(ProtocolTest):

    @classmethod
    def setUpClass(self):
        super(HALProtocolTest, self).setUpClass()
        self.repo.username = 'test_ws'
        self.repo.password = 'test'
        self.proto = HALProtocol(self.repo)

    def test_lncs(self):
        """
        Submit a paper from LNCS
        """
        p = Paper.create_by_doi('10.1007/978-3-662-47666-6_5')
        r = self.dry_deposit(p,
                             abstract='this is an abstract',
                             topic='INFO')
        self.assertEqual(r.status, 'DRY_SUCCESS')

    def test_predict_topic(self):
        cases = [
                ('IBEX: Harvesting Entities from the Web Using Unique Identifiers', 'INFO'),
                ('Global climate change entails many threats and challenges for the majority of crops.', 'SDV'),
                ('', None),
            ]
        for text, topic in cases:
            self.assertEqual(self.proto.predict_topic(text), topic)
