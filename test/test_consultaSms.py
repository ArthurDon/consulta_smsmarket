from unittest import TestCase
import requests
from pin_status_api.models.acesso_smsmarket import ConsultaSms
from pin_status_api.exceptions.exceptions import ErrorProcessReturnSMSMarket, AuthenticationErrorOnSMSMarket


class TestConsultaSms(TestCase):

    def setUp(self):
        self.consult = ConsultaSms()

    def test_url_format(self):  # deve_ser_considerada_valida_a_url_se_o_retorno_do_acesso_for_200
        url = self.consult.url_format()
        request = requests.get(url)
        request = request.status_code

        expected_status = 200
        self.assertEqual(expected_status, request)
        print(request)

    def test_consult_smsmarket(
            self):  # o_retorno_deve_ser_valido_se_retornar_uma_lista_de_dicionario com as chaves
        # esperadas_ou_uma_lista_vazia
        msisdn = '5511988000020'
        url = self.consult.url_format()

        retorno_sms = self.consult.consult_smsmarket(msisdn, url)

        expected_keys = ['number', 'sent_date', 'status', 'carrier_name']
        returned_keys = []
        validation_flag = False
        expected_validation_flag = True

        if len(retorno_sms) == 0:
            validation_flag = True
        else:
            for element in retorno_sms:
                for key in element:
                    returned_keys.append(key)
                if returned_keys == expected_keys:
                    validation_flag = True

        self.assertEqual(expected_validation_flag, validation_flag)

        print(expected_keys)
        print(returned_keys)

    def test_consult_smsmarket_2(
            self):  # Deve retornar uma exception caso a chave 'Messages' ou 'responseCode' não sejam informadas
        msisdn = '5511988000024'
        url = "https://viacep.com.br/ws/04571011/json/"

        with self.assertRaises(ErrorProcessReturnSMSMarket):
            self.consult.consult_smsmarket(msisdn, url)

    def test_consult_smsmarket_3(self):  # Deve retornar uma exception caso_ocorra_erro_de_autenticacao_no_smsmarket
        msisdn = '5511988000024'
        url = "https://api.smsmarket.com.br/webservice-rest/mt_date?user=000fssmsmarket&password=s3nh%40123%40%21%40&type=0&status=0%2C1&timezone=-03%3A00"  # usuario correto: fssmsmarket

        with self.assertRaises(AuthenticationErrorOnSMSMarket):
            self.consult.consult_smsmarket(msisdn, url)

    def test_return_format_1(
            self):  # deve retornar o valor 'None' caso o campo 'send_date' seja nao informe corresponda ao layout
        # #%Y-%m-%d %H:%M:%S (fornecido pela SMSMarket)
        dados = [
            {
                "number": "5511988000024",
                "sent_date": "28-09-2020 20:30:20",
                "status": "1"
            },
            {
                "number": "5511988000024",
                "sent_date": "20:30:20",
                "status": "0"
            }

        ]
        expected_date = None

        retorno_formatado = self.consult.return_format(dados)

        for element in retorno_formatado:
            self.assertEqual(expected_date, element['sent_date'])

    def test_return_format_2(
            self):  # deve retornar o valor 'None' não exista a flag no dicionario 'status_ptbr'(fixado no codigo) na
        # função 'acesso_smsmarket.return_format'
        dados = [
            {
                "number": "5511988000024",
                "sent_date": "2020-09-28 20:30:20",
                "status": "001"
            },
            {
                "number": "5511988000024",
                "sent_date": "2020-09-28 20:30:20",
                "status": "01"
            }

        ]
        expected_status = None

        retorno_formatado = self.consult.return_format(dados)

        for element in retorno_formatado:
            self.assertEqual(expected_status, element['status'])
