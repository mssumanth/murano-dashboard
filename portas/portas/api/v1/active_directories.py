from portas import utils
from portas.api.v1 import save_draft, get_draft, get_service_status
from portas.common import uuidutils
from portas.openstack.common import wsgi, timeutils
from portas.openstack.common import log as logging

log = logging.getLogger(__name__)


class Controller(object):
    def index(self, request, environment_id):
        log.debug(_('ActiveDirectory:Index <EnvId: {0}>'.
                    format(environment_id)))

        draft = prepare_draft(get_draft(environment_id,
                                        request.context.session))

        for dc in draft['services']['activeDirectories']:
            dc['status'] = get_service_status(environment_id,
                                              request.context.session,
                                              dc)

        return {'activeDirectories': draft['services']['activeDirectories']}

    @utils.verify_session
    def create(self, request, environment_id, body):
        log.debug(_('ActiveDirectory:Create <EnvId: {0}, Body: {1}>'.
                    format(environment_id, body)))

        draft = get_draft(session_id=request.context.session)

        active_directory = body.copy()
        active_directory['id'] = uuidutils.generate_uuid()
        active_directory['created'] = str(timeutils.utcnow())
        active_directory['updated'] = str(timeutils.utcnow())

        unit_count = 0
        for unit in active_directory['units']:
            unit_count += 1
            unit['id'] = uuidutils.generate_uuid()
            unit['name'] = 'dc{0}'.format(unit_count)

        draft = prepare_draft(draft)
        draft['services']['activeDirectories'].append(active_directory)
        save_draft(request.context.session, draft)

        return active_directory

    def delete(self, request, environment_id, active_directory_id):
        log.debug(_('ActiveDirectory:Delete <EnvId: {0}, Id: {1}>'.
                    format(environment_id, active_directory_id)))

        draft = get_draft(request.context.session)
        items = [service for service in draft['services']['activeDirectories']
                 if service['id'] != active_directory_id]
        draft['services']['activeDirectories'] = items
        save_draft(request.context.session, draft)


def prepare_draft(draft):
    if not 'services' in draft:
        draft['services'] = {}

    if not 'activeDirectories' in draft['services']:
        draft['services']['activeDirectories'] = []

    return draft


def create_resource():
    return wsgi.Resource(Controller())