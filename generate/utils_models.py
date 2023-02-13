import uuid


def generate_reff_code():
    return str(uuid.uuid4()).replace('-', '')[:12]


def generate_auth_token():
    return str(uuid.uuid4())
