from pin_status_api.models.acesso_smsmarket import ConsultaSms
from flask import jsonify, Blueprint
from jsonschema import validate, exceptions

return_status_blueprint = Blueprint('return_status', __name__)
health_check_blueprint = Blueprint('health_check',__name__)


@health_check_blueprint.route("/", methods=['GET'])
def status():
    """
    Short Health Check
        ---
          tags:
            - HealthCheck
          responses:
            200:
              description: 'OK'
    """
    return "Pin Status API"


@return_status_blueprint.route('/msisdn/<string:msisdn>', methods=['GET'])
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

    return jsonify(return_format), 200


@return_status_blueprint.errorhandler(exceptions.ValidationError)
def validation_error(e):
    return jsonify({"message": "Telefone informado incorretamente"}), 400
