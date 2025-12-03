from flask_restx import Resource
from database.instance import get_session
from server.instance import server
from sqlalchemy import text

from models.actuator import healthz_response, healthz_response_error

api = server.api
ns = api.namespace('Actuator', description='Actuator operations', path='/')

@ns.route('/healthz')
class Actuator(Resource):

    @ns.doc(description='Get system and database status')
    @api.response(200, 'Success', healthz_response)
    @api.response(500, 'Success', healthz_response_error)
    @api.doc(security=[])
    def get(self):
        '''   Get system and database status'''
        with get_session() as session:
            try:
                session.execute(text("SELECT 1"))
                return {
                    "status": "healthy", 
                    "database": "connected"
                }, 200
                
            except Exception as e:
                return {
                    "status": "unhealthy", 
                    "database": "disconnected", 
                    "error": str(e)
                }, 500