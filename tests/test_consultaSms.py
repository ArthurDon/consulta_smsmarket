from unittest import TestCase
import requests
from acesso_smsmarket import ConsultaSms

class TestConsultaSms(TestCase):

    def setUp(self):
        self.consult = ConsultaSms()

    def test_url_format(self): #deve_ser_considerada_valida_a_url_se_o_retorno_do_acesso_for_200
        url = self.consult.url_format()
        request = requests.get(url)
        request = request.status_code

        expected_status = 200

        self.assertEqual(expected_status, request)

    def test_phone_validate(self): #Telefone valido se for composto apenas por numeros e o total de caracteres for 13
        msisdn = '551198800002a'

        vadidation_msisdn = self.consult.phone_validate(msisdn)

        expected_msisdn = True

        self.assertEqual(expected_msisdn, vadidation_msisdn)

    def test_consult_smsmarket(self):
        self.fail()

    def test_return_format(self):
        self.fail()