# -*- coding: UTF-8 -*-
"""
Entry point logic for available backend worker tasks
"""
from celery import Celery
from vlab_api_common import get_task_logger

from vlab_router_api.lib import const
from vlab_router_api.lib.worker import vmware

app = Celery('router', backend='rpc://', broker=const.VLAB_MESSAGE_BROKER)


@app.task(name='router.show', bind=True)
def show(self, username, txn_id):
    """Obtain basic information about Router

    :Returns: Dictionary

    :param username: The name of the user who wants info about their default gateway
    :type username: String

    :param txn_id: A unique string supplied by the client to track the call through logs
    :type txn_id: String
    """
    logger = get_task_logger(txn_id=txn_id, task_id=self.request.id, loglevel=const.VLAB_ROUTER_LOG_LEVEL.upper())
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


@app.task(name='router.create', bind=True)
def create(self, username, machine_name, image, requested_networks, txn_id):
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

    :param txn_id: A unique string supplied by the client to track the call through logs
    :type txn_id: String
    """
    logger = get_task_logger(txn_id=txn_id, task_id=self.request.id, loglevel=const.VLAB_ROUTER_LOG_LEVEL.upper())
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        resp['content'] = vmware.create_router(username, machine_name, image, requested_networks, logger)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    logger.info('Task complete')
    return resp


@app.task(name='router.delete', bind=True)
def delete(self, username, machine_name, txn_id):
    """Destroy an instance of Router

    :Returns: Dictionary

    :param username: The name of the user who wants to delete an instance of Router
    :type username: String

    :param machine_name: The name of the instance of Router
    :type machine_name: String

    :param txn_id: A unique string supplied by the client to track the call through logs
    :type txn_id: String
    """
    logger = get_task_logger(txn_id=txn_id, task_id=self.request.id, loglevel=const.VLAB_ROUTER_LOG_LEVEL.upper())
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        vmware.delete_router(username, machine_name, logger)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    else:
        logger.info('Task complete')
    return resp


@app.task(name='router.image', bind=True)
def image(self, txn_id):
    """Obtain a list of available images/versions of Router that can be created

    :Returns: Dictionary

    :param txn_id: A unique string supplied by the client to track the call through logs
    :type txn_id: String
    """
    logger = get_task_logger(txn_id=txn_id, task_id=self.request.id, loglevel=const.VLAB_ROUTER_LOG_LEVEL.upper())
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    resp['content'] = {'image': vmware.list_images()}
    logger.info('Task complete')
    return resp
