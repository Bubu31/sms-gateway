from flask import request
from flask_restx import Resource
from flask_jwt_extended import ( jwt_required )
from server.instance import server
from environment.instance import gammu_smsd_config
from models.send import sms_post, send_result
from resources.decorators import ( required_bearerAuth, required_basicAuth )
from environment.instance import environment_config

import gammu
import gammu.smsd
import json

app, api = server.app, server.api
ns = api.namespace('Send', description='Send operations', path='/')

smsd = gammu.smsd.SMSD(gammu_smsd_config['conf'])

GSM_7BIT_CHARS = set(
    '@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ !"#¤%&\'()*+,-./0123456789:;<=>?'
    '¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà'
    'ÆæßÉ'
    '\f^{}\\[~]|€'
)

def requires_unicode(text):
    if not text:
        return False
    return not all(c in GSM_7BIT_CHARS for c in text)

@ns.route('/v1/send')
class SendSMS(Resource):
    @ns.expect(sms_post, validate=True)
    @ns.doc(description='Send a SMS')
    @required_bearerAuth(environment_config["require_bearer"])
    @required_basicAuth(environment_config["require_basic"])
    @api.response(200, 'Success', send_result)
    def post(self):
        '''   Send a SMS'''
        json_data = request.json
        message = json_data["message"]
        numbers = json_data["recipients"]
        use_unicode = requires_unicode(message)
        results = []
        for number in numbers:
            # Create SMS info structure
            smsinfo = {
                'Class': -1,
                'Unicode': use_unicode,
                'Entries':  [
                    {
                        'ID': 'ConcatenatedTextLong',
                        'Buffer': message
                    }
                ]}

            # Encode messages
            encoded = gammu.EncodeSMS(smsinfo)

            for sms in encoded:
                # Fill in numbers
                sms['SMSC'] = {'Location': 1}
                sms['Number'] = number

            msg_id = smsd.InjectSMS(encoded)
            results.append({ 
                "DestinationNumber" : number,
                "smsID" : msg_id
            })

        return {'results': results}, 200
