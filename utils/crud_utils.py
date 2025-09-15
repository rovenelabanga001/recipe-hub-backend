from flask import jsonify, request
from mongoengine import DoesNotExist


def get_document_or_404(model, doc_id, not_found_msg="Not Found"):
    doc = model.objects(id=doc_id).first()
    if not doc:
        return None, {"error": not_found_msg}, 404
    return doc, None, 200



def update_document_fields(document, data, exclude_fields=None):
    """Update document with provided data except excluded fields"""
    exclude_fields = exclude_fields or {"id"}
    updatable_fields = set(document._fields.keys()) - set(exclude_fields)

    for field, value in data.items():
        if field in updatable_fields:
            setattr(document, field, value)

    document.save()
    return document 