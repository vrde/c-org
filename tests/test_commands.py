#!/usr/bin/python3
# Blackbox tests of C-ORG.
#
# Copyright (C) 2018 Continuous Organisation
# Author: Pierre-Louis Guhur <pierre-louis.guhur@laposte.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import unittest
import tempfile
import subprocess
import yaml
from web3 import Web3
from web3.auto import w3
import c_org
from .test_base import TestBase
from c_org.cli import main
from c_org import ContinuousOrganisationManager
import c_org.utils as utils
from c_org.manager import Vault

exe_cli="c-org"

class TestDeploy(TestBase):

    def setUp(self):
        self.temp_files()
        self.init_wallet()

    def test_deploy(self):
        sys.argv = [exe_cli] + ["deploy", "my-co", "--wallet", self.wallet.name]
        main()
        self.assertTrue(os.path.isfile(self.c_org_manager.build_file))
        contract = self.c_org_manager.contract
        self.assertTrue(len(contract.find_functions_by_name('buy')))


class TestInit(TestBase):

    def setUp(self):
        self.temp_files()

    def test_init(self):
        sys.argv = [exe_cli] + ["init", "my-co"]
        main()
        with open(self.c_org_manager.param_file, "r") as f:
            param = yaml.load(f)
        self.assertTrue('my-co', param.get('name'))
        self.assertNotIn('buy', param)


class TestCommandWallet(TestBase):

    def setUp(self):
        self.temp_files()

    def test_add_wallet(self):
        sys.argv = [exe_cli] + ["wallet", "add", "test",
                                utils.generate_random_private_key()]
        main()
        vault = Vault()
        self.assertTrue(vault.exist_wallet("test"))

    def test_rm_wallet(self):
        sys.argv = [exe_cli, "wallet", "add", "name",
                    utils.generate_random_private_key()]
        main()
        sys.argv = [exe_cli, "wallet", "remove", "name"]
        main()
        vault = Vault()
        self.assertFalse(vault.exist_wallet("test"))

    def test_create_wallet(self):
        pass #TODO


class TestOtherCommands(TestBase):

    def setUp(self):
        self.temp_files()
        self.init_wallet()
        self.c_org_manager.deploy(self.wallet)

    def test_buy(self):
        sys.argv = [exe_cli] + [ "buy", "my-co",  "--wallet", self.wallet.name, "--amount", "0.1"]
        main()

    def test_sell(self):
        self.c_org_manager.buy(0.1, self.wallet)
        sys.argv = [exe_cli] + ["sell", "my-co", "--wallet", self.wallet.name, "--amount", "1"]
        main()

    # def test_revenue(self):
    #     sys.argv = [exe_cli] + ["revenue",  "--revenue", "10"]
    #     main()

    def test_stats(self):
        self.c_org_manager.buy(0.1, self.wallet)
        sys.argv = [exe_cli] + ["stats", "my-co", "--wallet", self.wallet.name]
        main()




if __name__ == '__main__':
   unittest.main()
