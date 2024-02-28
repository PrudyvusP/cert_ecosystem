from flask import Blueprint, Response, current_app as app
from sqlalchemy import func

from ..models import Organization, OrgAdmDocOrganization

api = Blueprint('api', __name__, url_prefix='/api')
db = app.extensions['db']

import json
from datetime import date
from datetime import datetime


class JsonExtendEncoder(json.JSONEncoder):

    def default(self, obj):
        """
            provide a interface for datetime/date
        """
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


@api.route('/regions/<int:region_id>/docs/<int:doc_id>/',
           methods=['GET', 'HEAD', 'OPTIONS'])
def get_orgs_docs_by_region(region_id, doc_id):
    """Возвращает информацию об организациях, расположенных в <region_id>
    и имеющих документ <doc_id>."""

    docs = (
        db.session
        .query(Organization.inn, Organization.kpp,
               Organization.full_name, OrgAdmDocOrganization.props,
               OrgAdmDocOrganization.date_approved,
               OrgAdmDocOrganization.comment)
        .join(OrgAdmDocOrganization, Organization.org_adm_doc)
        .filter(OrgAdmDocOrganization.orgadm_id == doc_id)
        .filter(Organization.region_id == region_id)
        .order_by(Organization.full_name)
        .all()
    )
    docs_count = (
        db.session
        .query(func.count(Organization.org_id))
        .join(OrgAdmDocOrganization, Organization.org_adm_doc)
        .filter(OrgAdmDocOrganization.orgadm_id == doc_id)
        .filter(Organization.region_id == region_id)
        .scalar()
    )
    response = json.dumps({"count": docs_count,
                           "results": [dict(doc) for doc in docs]},
                          cls=JsonExtendEncoder)
    return Response(response=response,
                    mimetype='application/json')
