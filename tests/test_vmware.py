# -*- coding: UTF-8 -*-
"""
A suite of tests for the functions in vmware.py
"""
import unittest
from unittest.mock import patch, MagicMock

from vlab_router_api.lib.worker import vmware


class TestVMware(unittest.TestCase):
    """A set of test cases for the vmware.py module"""

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_show_router(self, fake_vCenter, fake_consume_task, fake_get_info):
        """``show_router`` returns a dictionary when everything works as expected"""
        fake_vm = MagicMock()
        fake_vm.name = 'myRouter'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'meta' : {'component' : "Router",
                                                'created': 1234,
                                                'version': "1.1.8",
                                                'configured': False,
                                                'generation': 1,
                                                }}

        output = vmware.show_router(username='alice')
        expected = {'myRouter': {'meta' : {'component' : "Router",
                                           'created': 1234,
                                           'version': "1.1.8",
                                           'configured': False,
                                           'generation': 1,
                                           }}}

        self.assertEqual(output, expected)

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_delete_router(self, fake_vCenter, fake_consume_task, fake_get_info):
        """``delete_router`` returns a None when everything works as expected"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'myRouter'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'meta' : {'component' : "Router",
                                                'created': 1234,
                                                'version': "1.1.8",
                                                'configured': False,
                                                'generation': 1,
                                                }}

        output = vmware.delete_router(username='alice', machine_name='myRouter', logger=fake_logger)
        expected = None

        self.assertEqual(output, expected)

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_delete_router_value_error(self, fake_vCenter, fake_consume_task, fake_get_info):
        """``delete_router`` raises ValueError when supplied with an unknown router name"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'myRouter'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'worked': True, 'note': "Router=1.0.32"}

        with self.assertRaises(ValueError):
            vmware.delete_router(username='alice', machine_name='noSuchRouter', logger=fake_logger)

    @patch.object(vmware.virtual_machine, 'set_meta')
    @patch.object(vmware, 'map_networks')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'Ova')
    @patch.object(vmware, 'vCenter')
    def test_create_router(self, fake_vCenter, fake_Ova, fake_deploy_from_ova, fake_get_info, fake_consume_task, fake_map_networks, fake_set_meta):
        """``create_router`` returns a dictionary when everything works"""
        fake_logger = MagicMock()
        fake_deploy_from_ova.return_value.name = 'myRouter'
        fake_map_networks.return_value = [vmware.vim.Network(moId='asdf')]
        fake_get_info.return_value = {'worked': True}

        output = vmware.create_router(username='alice',
                                     machine_name='myRouter',
                                     image='1.0.32',
                                     requested_networks=['net1', 'net2'],
                                     logger=fake_logger)
        expected = {'myRouter': {'worked': True}}

        self.assertEqual(output, expected)

    @patch.object(vmware, 'map_networks')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'Ova')
    @patch.object(vmware, 'vCenter')
    def test_create_router_value_error(self, fake_vCenter, fake_Ova, fake_deploy_from_ova, fake_get_info, fake_consume_task, fake_map_networks):
        """``create_router`` raises ValueError when supplied with an invalid image/version to deploy"""
        fake_logger = MagicMock()
        fake_Ova.side_effect = FileNotFoundError('testing')
        fake_map_networks.return_value = [vmware.vim.Network(moId='asdf')]
        fake_get_info.return_value = {'worked': True}

        with self.assertRaises(ValueError):
            vmware.create_router(username='alice',
                                     machine_name='myRouter',
                                     image='32',
                                     requested_networks=['net1', 'net2'],
                                     logger=fake_logger)

    def test_map_networks(self):
        """``map_networks`` returns a List when everything works as expected"""
        ova_networks = ['network1', 'network2']
        user_networks = ['neta', 'netb']
        vcenter_networks = {'neta': vmware.vim.Network(moId='asdf'), 'netb': vmware.vim.Network(moId='asdf')}

        output = vmware.map_networks(ova_networks, user_networks, vcenter_networks)

        self.assertTrue(isinstance(output, list))

    def test_map_networks_value_error(self):
        """``map_networks`` raises ValueError if a requested network doesn't exist"""
        ova_networks = ['network1', 'network2']
        user_networks = ['neta', 'netb']
        vcenter_networks = {'neta': vmware.vim.Network(moId='asdf')}

        with self.assertRaises(ValueError):
            vmware.map_networks(ova_networks, user_networks, vcenter_networks)

    @patch.object(vmware.os, 'listdir')
    def test_list_images(self, fake_listdir):
        """``list_images`` returns a list when everything works as expected"""
        fake_listdir.return_value = ['router-toffeemocha-1.0.32.ova']

        output = vmware.list_images()
        expected = ['1.0.32']

        self.assertEqual(output, expected)

    def test_convert_name(self):
        """``convert_name`` returns an image name from a supplied version by default"""
        output = vmware.convert_name(name='1.1.8')
        expected = 'router-vyos-1.1.8.ova'

        self.assertEqual(output, expected)

    def test_convert_name_to_version(self):
        """``convert_name`` returns the version when supplied with a image name"""
        output = vmware.convert_name(name='router-vyos-1.1.8.ova', to_version=True)
        expected = '1.1.8'

        self.assertEqual(output, expected)


if __name__ == '__main__':
    unittest.main()
