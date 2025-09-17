from flask import Blueprint, jsonify, request
from utils.crud_utils import get_document_or_404, update_document_fields
from mongoengine import ReferenceField, ValidationError

def crud_factory(bp: Blueprint, model, endpoint: str, required_fields=None, user_owned=False, allow_cross_user_create=False):
    """
    CRUD Factory with JWT support and user ownership

    Args:
        bp: Blueprint to attach routes to
        model: Model class
        endpoint: API endpoint
        required_fields: list of required fields for creation
        user_owned: requires user ownership check for write operations
        allow_cross_user_create: if True, users can create documents referencing other users' content
    """
    
    # Helper function to check ownership for write operations
    def check_ownership(doc):
        """Check if the current user owns the document (for write operations)"""
        if not (user_owned and hasattr(request, 'user_id')):
            return True  

        if hasattr(doc, 'user') and hasattr(doc.user, 'id'):
            return str(doc.user.id) == request.user_id

        elif hasattr(doc, 'user_id'):
            return str(doc.user_id) == request.user_id
            
        else:
            return False

    # Helper function for permission error message
    def permission_error(action):
        return jsonify({
            "error": f"You do not have permission to {action} this {endpoint[:-1].capitalize()}"
        }), 403

    # --- helper: resolve ReferenceField IDs to documents ---
    def resolve_references(data: dict):
        """
        Convert string IDs into actual documents for ReferenceFields.
        """
        for field_name, field in model._fields.items():
            if isinstance(field, ReferenceField) and field_name in data:
                field_model = field.document_type
                try:
                    data[field_name] = field_model.objects.get(id=data[field_name])
                except field_model.DoesNotExist:
                    raise ValidationError(f"{field_model.__name__} not found for field '{field_name}'")
        return data

    # GET all 
    @bp.route(f"/{endpoint}", methods=["GET"])
    def get_all():
        docs = model.objects()
        
        if not docs:
            return jsonify({
                "message": f"No {endpoint} found",
                "data": []
            }), 200
        
        result = []
        for doc in docs:
            doc_dict = doc.to_dict()
            if hasattr(request, 'user_id'):
                doc_dict['is_owner'] = check_ownership(doc)
            result.append(doc_dict)
        
        return jsonify({
            "message": f"Found {len(result)} {endpoint}",
            "data": result
        }), 200

    # GET one 
    @bp.route(f"/{endpoint}/<doc_id>", methods=["GET"])
    def get_one(doc_id):
        doc, err, code = get_document_or_404(model, doc_id, f"{endpoint[:-1].capitalize()} not found")
        if err:
            return jsonify(err), code
        
        doc_dict = doc.to_dict()
        
        if hasattr(request, 'user_id'):
            doc_dict['is_owner'] = check_ownership(doc)
            
        return jsonify(doc_dict), 200

    # GET user's own documents only
    @bp.route(f"/my-{endpoint}", methods=["GET"])
    def get_my_documents():
        if not hasattr(request, 'user_id'):
            return jsonify({"error": "Authentication required"}), 401
            
        if hasattr(model, 'user'):  
            docs = model.objects(user=request.user_id)
        else:  
            docs = model.objects(user_id=request.user_id)
        
        if not docs:
            return jsonify({
                "message": f"You have no {endpoint} yet",
                "data": []
            }), 200
        
        result = [doc.to_dict() for doc in docs]
        return jsonify({
            "message": f"Found {len(result)} of your {endpoint}",
            "data": result
        }), 200

    # --- CREATE ---
    @bp.route(f"/{endpoint}", methods=["POST"])
    def create():
        if not hasattr(request, 'user_id'):
            return jsonify({"error": "Authentication required to create"}), 401

        data = request.get_json() or {}

        # Ownership handling
        if user_owned:
            if hasattr(model, 'user'):
                data['user'] = request.user_id
            else:
                data['user_id'] = request.user_id

        # Check required fields
        if required_fields:
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return jsonify({
                    "error": f"Missing required fields for {endpoint[:-1]}",
                    "missing_fields": missing_fields
                }), 400

        try:
            data = resolve_references(data)  
            doc = model(**data)
            doc.save()
            return jsonify(doc.to_dict()), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # --- PATCH ---
    @bp.route(f"/{endpoint}/<doc_id>", methods=["PATCH"])
    def update(doc_id):
        doc, err, code = get_document_or_404(model, doc_id, f"{endpoint[:-1].capitalize()} not found")
        if err:
            return jsonify(err), code

        # Ownership check
        if user_owned and hasattr(request, 'user_id'):
            if hasattr(doc, 'user') and str(doc.user.id) != request.user_id:
                return jsonify({"error": "You do not have permission to update this"}), 403

        data = request.get_json() or {}

        # Prevent ownership reassignment
        for field in ['user', 'user_id']:
            if field in data:
                return jsonify({"error": "Cannot change document ownership"}), 400

        try:
            data = resolve_references(data) 
            update_doc = update_document_fields(doc, data)
            return jsonify(update_doc.to_dict()), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400


    # DELETE - Only owners can delete
    @bp.route(f"/{endpoint}/<doc_id>", methods=["DELETE"])
    def delete(doc_id):
        doc, err, code = get_document_or_404(model, doc_id, f"{endpoint[:-1].capitalize()} not found")
        if err:
            return jsonify(err), code

        if not check_ownership(doc):
            return permission_error("delete")
        
        doc_name = getattr(doc, "name", getattr(doc, "body", str(doc.id)))
        doc.delete()

        return jsonify({
            "message": f"{endpoint[:-1].capitalize()} '{doc_name}' deleted successfully"
        }), 200