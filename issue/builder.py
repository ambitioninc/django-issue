from django.db import transaction
from issue.models import Responder, ResponderAction


@transaction.atomic
def build_responder(dict_):
    """
    Construct a Responder and ResponderActions from a dictionary representation.
    """
    r = Responder.objects.create(watch_pattern=dict_['watch_pattern'])

    for action in dict_['actions']:
        ResponderAction.objects.create(responder=r, **action)

    return r
