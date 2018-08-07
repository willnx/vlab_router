# -*- coding: UTF-8 -*-
"""
Entry point logic for available backend worker tasks
"""
from celery import Celery
from celery.utils.log import get_task_logger

from vlab_router_api.lib import const
from vlab_router_api.lib.worker import vmware

app = Celery('router', backend='rpc://', broker=const.VLAB_MESSAGE_BROKER)
logger = get_task_logger(__name__)
logger.setLevel(const.VLAB_ROUTER_LOG_LEVEL.upper())


@app.task(name='router.show')
def show(username):
    """Obtain basic information about Router

    :Returns: Dictionary

    :param username: The name of the user who wants info about their default gateway
    :type username: String
    """
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        info = vmware.show_router(username)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    else:
        logger.info('Task complete')
        resp['content'] = info
    return resp


@app.task(name='router.create')
def create(username, machine_name, image, requested_networks):
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
    """
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        resp['content'] = vmware.create_router(username, machine_name, image, requested_networks)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    logger.info('Task complete')
    return resp


@app.task(name='router.delete')
def delete(username, machine_name):
    """Destroy an instance of Router

    :Returns: Dictionary

    :param username: The name of the user who wants to delete an instance of Router
    :type username: String

    :param machine_name: The name of the instance of Router
    :type machine_name: String
    """
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        vmware.delete_router(username, machine_name)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    else:
        logger.info('Task complete')
    return resp


@app.task(name='router.image')
def image():
    """Obtain a list of available images/versions of Router that can be created

    :Returns: Dictionary
    """
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    resp['content'] = {'image': vmware.list_images()}
    logger.info('Task complete')
    return resp
