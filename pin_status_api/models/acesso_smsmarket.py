import requests, datetime, time
from pin_status_api.exceptions.exceptions import ErrorProcessReturnSMSMarket, AuthenticationErrorOnSMSMarket


class ConsultaSms:

    def url_format(self):
        start_in_seconds = 15000  # 300 = 5 minutos
        end_in_seconds = 900  # 900 = 15 minutos

        now = datetime.datetime.now()
        now_format = now.strftime("%H:%M:%S")

        ftr = [3600, 60, 1]
        now_in_seconds = (sum([a * b for a, b in zip(ftr, map(int, now_format.split(':')))]))

        # now_in_seconds = now_in_seconds - 10800 #10800 segundos - subtração de 3 horas para caso o servidor esteja com GMT-0

        start_search_time = now_in_seconds - start_in_seconds
        end_search_time = now_in_seconds + end_in_seconds

        start_time_format = time.strftime('%H:%M:%S', time.gmtime(start_search_time))
        end_time_format = time.strftime('%H:%M:%S', time.gmtime(end_search_time))

        url_start_date = now.strftime("%Y-%m-%dT{}".format(start_time_format))
        url_end_date = now.strftime("%Y-%m-%dT{}".format(end_time_format))

        url = 'https://api.smsmarket.com.br/webservice-rest/mt_date?user=fssmsmarket&password=s3nh%40123%40%21%40&start_date={}&end_date={}&type=0&status=0%2C1&timezone=-03%3A00'.format(
            url_start_date, url_end_date)

        return url

    def consult_smsmarket(self, number, url):

        r = requests.get(url)
        dados = r.json()

        return_filtered = []
        keys = ['number', 'sent_date', 'status', 'carrier_name']

        try:
            for message in dados['messages']:
                if number == message['number']:
                    return_filtered.append({key: message[key] for key in keys})

            return return_filtered
        except:
            if 'responseCode' in dados:
                if dados['responseCode'] == '010':
                    raise AuthenticationErrorOnSMSMarket()
            else:
                raise ErrorProcessReturnSMSMarket()

    def return_format(self, filtered_response):
        status_ptbr = {'-2': 'Erro de rede da operadora',
                       '1': 'Mensagem recebida pelo dispositivo',
                       '9': 'Mensagem não recebida pelo dispositivo',
                       '-9': 'Bloqueado - Sem Cobertura',
                       '-8': 'Bloqueado - Conteúdo não permitido',
                       '-6': 'Mensagem cancelada com sucesso',
                       '-5': 'Bloqueado - Lista de bloqueio',
                       '-4': 'Bloqueado - Número fixo',
                       '-3': 'Bloqueado - Número inválido',
                       '0': 'Mensagem recebida pela operadora',
                       '7': 'Mensagem expirada pela operadora',
                       '8': 'Mensagem rejeitada pela operadora',
                       '-1': 'Mensagem na fila',
                       '3': 'Preparando mensagem para enviar',
                       '6': 'Mensagem Pausada'
                       }

        for element in filtered_response:
            try:
                element['status'] = status_ptbr.get(element.get('status'))
            except:
                element['status'] = None

            try:
                formated_date = datetime.datetime.strptime(element['sent_date'], "%Y-%m-%d %H:%M:%S")
                formated_date = formated_date.strftime("%d-%m-%Y %H:%M:%S")
                element['sent_date'] = formated_date
            except:
                element['sent_date'] = None

        return filtered_response
