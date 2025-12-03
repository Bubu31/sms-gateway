from flask_restx import fields
from server.instance import server

healthz_response = server.api.model('Healthz Response', {
    'status': fields.String(
        example='healthy'
    ),
    'database': fields.String(
        example='connected'
    )
})

healthz_response_error = server.api.model('Healthz Response', {
    'status': fields.String(
        example='unhealthy'
    ),
    'database': fields.String(
        example='disconnected'
    ),
    'error': fields.String(
        example='Unable to connect to mysql server'
    )
})
