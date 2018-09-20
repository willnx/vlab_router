# -*- coding: UTF-8 -*-
"""
TODO
"""
import ujson
from flask import current_app
from flask_classy import request, route
from vlab_inf_common.views import TaskView
from vlab_inf_common.vmware import vCenter, vim
from vlab_api_common import describe, get_logger, requires, validate_input


from vlab_router_api.lib import const


logger = get_logger(__name__, loglevel=const.VLAB_ROUTER_LOG_LEVEL)


class RouterView(TaskView):
    """API end point TODO"""
    route_base = '/api/1/inf/router'
    POST_SCHEMA = { "$schema": "http://json-schema.org/draft-04/schema#",
                    "type": "object",
                    "description": "Create a router",
                    "properties": {
                        "name": {
                            "description": "The name to give your Router instance",
                            "type": "string"
                        },
                        "image": {
                            "description": "The image/version of Router to create",
                            "type": "string"
                        },
                        "networks": {
                            "description": "The networks to hook the Router instance up to",
                            "type": "array",
                            "minItems": 2,
                            "maxItems": 4,
                        }
                    },
                    "required": ["name", "image", "networks"]
                  }
    DELETE_SCHEMA = {"$schema": "http://json-schema.org/draft-04/schema#",
                     "description": "Destroy a Router",
                     "type": "object",
                     "properties": {
                        "name": {
                            "description": "the name of the Router to destroy",
                            "type": "string"
                        }
                     },
                     "required": ["name"]
                    }
    GET_SCHEMA = {"$schema": "http://json-schema.org/draft-04/schema#",
                  "description": "Display the Router instances you own"
                 }
    IMAGES_SCHEMA = {"$schema": "http://json-schema.org/draft-04/schema#",
                     "description": "View available versions of Router that can be created"
                    }


    @requires(verify=False, version=(1,2))
    @describe(post=POST_SCHEMA, delete=DELETE_SCHEMA, get=GET_SCHEMA)
    def get(self, *args, **kwargs):
        """Display the Router instances you own"""
        username = kwargs['token']['username']
        resp = {'user' : username}
        task = current_app.celery_app.send_task('router.show', [username])
        resp['content'] = {'task-id': task.id}
        return ujson.dumps(resp), 200

    @requires(verify=False, version=(1,2)) # XXX remove verify=False before commit
    @validate_input(schema=POST_SCHEMA)
    def post(self, *args, **kwargs):
        """Create a Router"""
        username = kwargs['token']['username']
        resp = {'user' : username}
        body = kwargs['body']
        machine_name = body['name']
        image = body['image']
        requested_networks = body['networks']
        task = current_app.celery_app.send_task('router.create', [username, machine_name, image, requested_networks])
        resp['content'] = {'task-id': task.id}
        return ujson.dumps(resp), 200

    @requires(verify=False, version=(1,2)) # XXX remove verify=False before commit
    @validate_input(schema=DELETE_SCHEMA)
    def delete(self, *args, **kwargs):
        """Destroy a Router"""
        username = kwargs['token']['username']
        resp = {'user' : username}
        machine_name = kwargs['body']['name']
        task = current_app.celery_app.send_task('router.delete', [username, machine_name])
        resp['content'] = {'task-id': task.id}
        return ujson.dumps(resp), 200

    @route('/image', methods=["GET"])
    @requires(verify=False, version=(1,2))
    @describe(get=IMAGES_SCHEMA)
    def image(self, *args, **kwargs):
        """Show available versions of Router that can be deployed"""
        username = kwargs['token']['username']
        resp = {'user' : username}
        task = current_app.celery_app.send_task('router.image')
        resp['content'] = {'task-id': task.id}
        return ujson.dumps(resp), 200
