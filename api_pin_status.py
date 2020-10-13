from acesso_smsmarket import ConsultaSms
from flask import  Flask, jsonify
import requests
from jsonschema import validate, exceptions
import json

app = Flask(__name__)

@app.route('/consultar/<string:msisdn>', methods=['GET'])
def consultar(msisdn):
    consulta = ConsultaSms()

    schema = {
        "type": "string",
        "pattern": "^[0-9]{13}$"
        }

    validate(msisdn, schema=schema)
    url = consulta.url_format()
    consult_smsmarket = consulta.consult_smsmarket(msisdn, url)
    return_format = consulta.return_format(consult_smsmarket)

    return json.dumps(return_format),200

@app.errorhandler(exceptions.ValidationError)
def validation_error(e):
    return json.dumps({"message": "Telefone informado incorretamente"}), 400

if __name__ == "__main__":
    app.run()