from flask import Blueprint, current_app as app, jsonify, wrappers
from sqlalchemy import func

from ..models import Organization, OrgAdmDocOrganization

api = Blueprint('api', __name__, url_prefix='/api')
db = app.extensions['db']


@api.route('/regions/<int:region_id>/docs/<int:doc_id>/',
           methods=['GET', 'HEAD', 'OPTIONS'])
def get_orgs_docs_by_region(region_id, doc_id) -> wrappers.Response:
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
    return jsonify(count=docs_count,
                   results=[dict(doc) for doc in docs])
