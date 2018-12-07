# -*- coding: UTF-8 -*-
"""Business logic for backend worker tasks"""
import time
import random
import os.path
from celery.utils.log import get_task_logger
from vlab_inf_common.vmware import vCenter, Ova, vim, virtual_machine, consume_task

from vlab_router_api.lib import const


def show_router(username):
    """Obtain basic information about Router

    :Returns: Dictionary

    :param username: The user requesting info about their Router
    :type username: String
    """
    info = {}
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER, \
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        folder = vcenter.get_by_name(name=username, vimtype=vim.Folder)
        router_vms = {}
        for vm in folder.childEntity:
            info = virtual_machine.get_info(vcenter, vm)
            kind, version = info['note'].split('=')
            if kind == 'Router':
                router_vms[vm.name] = info
    return router_vms


def delete_router(username, machine_name, logger):
    """Unregister and destroy a user's Router

    :Returns: None

    :param username: The user who wants to delete their jumpbox
    :type username: String

    :param machine_name: The name of the VM to delete
    :type machine_name: String

    :param logger: An object for logging messages
    :type logger: logging.LoggerAdapter
    """
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER, \
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        folder = vcenter.get_by_name(name=username, vimtype=vim.Folder)
        for entity in folder.childEntity:
            if entity.name == machine_name:
                info = virtual_machine.get_info(vcenter, entity)
                kind, version = info['note'].split('=')
                if kind == 'Router':
                    logger.debug('powering off VM')
                    virtual_machine.power(entity, state='off')
                    delete_task = entity.Destroy_Task()
                    logger.debug('blocking while VM is being destroyed')
                    consume_task(delete_task)
                    break
        else:
            raise ValueError('No {} named {} found'.format('router', machine_name))


def create_router(username, machine_name, image, requested_networks, logger):
    """Deploy a new instance of Router

    :Returns: Dictionary

    :param username: The name of the user who wants to create a new Router
    :type username: String

    :param machine_name: The name of the new instance of Router
    :type machine_name: String

    :param image: The image/version of Router to create
    :type image: String

    :param requested_networks: The name of the networks to connect the new Router instance up to
    :type requested_networks: List

    :param logger: An object for logging messages
    :type logger: logging.LoggerAdapter
    """
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER,
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        image_name = convert_name(image)
        logger.info(image_name)
        ova = Ova(os.path.join(const.VLAB_ROUTER_IMAGES_DIR, image_name))
        try:
            networks = map_networks(ova.networks, requested_networks, vcenter.networks)
            the_vm = virtual_machine.deploy_from_ova(vcenter, ova, networks,
                                                     username, machine_name, logger)
        finally:
            ova.close()
        spec = vim.vm.ConfigSpec()
        spec.annotation = 'Router={}'.format(image)
        task = the_vm.ReconfigVM_Task(spec)
        consume_task(task)
        return virtual_machine.get_info(vcenter, the_vm)


def map_networks(ova_networks, user_networks, vcenter_networks):
    """Associate the user requested networks with the networks defined in the OVF

    :Returns: List

    :Raises: ValueError (when a network does not exist in vCenter)

    :param ova_networks: The networks defined within the OVF
    :type ova_networks: List

    :param user_networks: The networks the user wants hooked up to the router
    :type user_networks: List

    :param vcenter_networks: The networks defined within vCenter
    :type vcenter_networks: Dictionary
    """
    networks = []
    user_networks = [x for x in user_networks if x] # 3rd and 4th networks are optionally None
    for ova_network, user_network in zip(ova_networks, user_networks):
        net_map = vim.OvfManager.NetworkMapping()
        net_map.name = ova_network
        try:
            net_map.network = vcenter_networks[user_network]
        except KeyError:
            msg = 'No such network {}'.format(user_network)
            raise ValueError(msg)
        else:
            networks.append(net_map)
    return networks


def list_images():
    """Obtain a list of available versions of Router that can be created

    :Returns: List
    """
    images = os.listdir(const.VLAB_ROUTER_IMAGES_DIR)
    images = [convert_name(x, to_version=True) for x in images]
    return images


def convert_name(name, to_version=False):
    """This function centralizes converting between the name of the OVA, and the
    version of software it contains.

    The naming convention is ``router-<software>-<version>.ova``, like router-vyos-1.1.8.ova

    :param name: The thing to covert
    :type name: String

    :param to_version: Set to True to covert the name of an OVA to the version
    :type to_version: Boolean
    """
    if to_version:
        return name.split('-')[2].rstrip('.ova')
    else:
        return 'router-vyos-{}.ova'.format(name)
