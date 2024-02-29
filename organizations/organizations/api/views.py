import json
import re
from datetime import date, datetime

from flask import Blueprint, Response
from flask import current_app as app
from flask import request
from sqlalchemy import func

from ..models import OrgAdmDocOrganization, Organization

api = Blueprint('api', __name__, url_prefix='/api')
db = app.extensions['db']

regions_pattern = re.compile(r'\b\d{1,2}\b')
docs_pattern = re.compile(r'\b\d+\b')


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


@api.route('/organizations/with_docs/',
           methods=['GET', 'HEAD', 'OPTIONS'])
def get_orgs_docs_by_region():
    """Возвращает информацию об организациях, расположенных в <region_id>
    и имеющих документ <doc_id>."""
    regions = request.args.get('regions')
    docs = request.args.get('docs')

    orgs = (
        db.session
        .query(Organization.inn, Organization.kpp,
               Organization.full_name, OrgAdmDocOrganization.props,
               OrgAdmDocOrganization.date_approved,
               OrgAdmDocOrganization.comment)
        .join(OrgAdmDocOrganization, Organization.org_adm_doc)
    )

    count = (
        db.session
        .query(func.count(Organization.org_id))
        .join(OrgAdmDocOrganization, Organization.org_adm_doc)
    )

    if regions and re.search(regions_pattern, regions):
        regions = [int(r) for r in re.findall(regions_pattern, regions)]
        orgs = orgs.filter(Organization.region_id.in_(regions))
        count = count.filter(Organization.region_id.in_(regions))

    if docs and re.search(docs_pattern, docs):
        search_docs = re.findall(docs_pattern, docs)
        orgs = orgs.filter(OrgAdmDocOrganization.orgadm_id.in_(search_docs))
        count = count.filter(OrgAdmDocOrganization.orgadm_id.in_(search_docs))

    count = count.scalar()
    orgs = orgs.order_by(Organization.full_name).all()

    response = json.dumps({"count": count,
                           "results": [dict(org) for org in orgs]},
                          cls=JsonExtendEncoder)
    return Response(response=response,
                    mimetype='application/json')
