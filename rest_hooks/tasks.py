# -*- coding: utf-8 -*-

import requests
import json
import hmac
import hashlib

from celery.task import Task
from django.conf import settings

from django.core.serializers.json import DjangoJSONEncoder

from rest_hooks.models import Hook


class DeliverHook(Task):
    def run(self, target, payload, instance=None, hook_id=None, **kwargs):
        """
        target:     the url to receive the payload.
        payload:    a python primitive data structure
        instance:   a possibly null "trigger" instance
        hook:       the defining Hook object (useful for removing)
        """
        data = json.dumps(payload, cls=DjangoJSONEncoder)
        headers = {
            'Content-Type': 'application/json'
        }

        if hasattr(settings, 'DJANGO_REST_HOOKS_HMAC_ENABLED') and settings.DJANGO_REST_HOOKS_HMAC_ENABLED:
            secret = settings.DJANGO_REST_HOOKS_HMAC_SECRET

            signature = hmac.new(secret, data, hashlib.sha256).hexdigest()
            headers['X-Rest-Hooks-Signature'] = signature

        response = requests.post(url=target, data=data, headers=headers)

        if response.status_code == 410 and hook_id:
            hook = Hook.object.get(id=hook_id)
            hook.delete()

        # would be nice to log this, at least for a little while...

def deliver_hook_wrapper(target, payload, instance=None, hook=None, **kwargs):
    if hook:
        kwargs['hook_id'] = hook.id
    return DeliverHook.delay(target, payload, **kwargs)
