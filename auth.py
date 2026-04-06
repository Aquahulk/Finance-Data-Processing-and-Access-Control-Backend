from functools import wraps
from flask import request, jsonify
from models import User, RoleType, UserStatus

def get_current_user():
    # In a real app, this would be a JWT or session check.
    # For this assignment, we use a custom header to mock authentication.
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return None
    try:
        user = User.query.get(int(user_id))
        if user and user.status == UserStatus.ACTIVE.value:
            return user
    except (ValueError, TypeError):
        pass
    return None

def require_role(roles):
    if isinstance(roles, str):
        roles = [roles]
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({"error": "Unauthorized. Please provide a valid X-User-ID header."}), 401
            
            if user.role not in roles:
                return jsonify({"error": f"Forbidden. This action requires one of these roles: {', '.join(roles)}"}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return require_role([RoleType.ADMIN.value])(f)

def analyst_required(f):
    return require_role([RoleType.ADMIN.value, RoleType.ANALYST.value])(f)

def viewer_required(f):
    return require_role([RoleType.ADMIN.value, RoleType.ANALYST.value, RoleType.VIEWER.value])(f)
