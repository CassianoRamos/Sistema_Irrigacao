#import RPi.GPIO as GPIO
import time
import csv
from datetime import datetime, timedelta
import requests

limite_umidade = 40  
intervalo_verificacao = 10  
nivel_reservatorio_chuva = 100  
umidade = 0

#GPIO.setmode(GPIO.BOARD)


def send_post_request(mensagem,horario_atual,nivel_reservatorio_chuva):
    data = {'data': mensagem,
            'soilMoisture': horario_atual,
            'waterLevel': nivel_reservatorio_chuva
        }
    try:
        response = requests.post('http://localhost:5000', json=data)
        if response.status_code == 201:
            print("Mensagem enviada com sucesso!")
        else:
            print(f"Erro ao enviar mensagem: {response.status_code}")
    except Exception as e:
        print(f"Erro na conexão: {e}")

def ler_umidade():
    global umidade
    umidade = int(input("Digite a umidade do solo "))
    return umidade

def irrigar(origem_agua):
    global nivel_reservatorio_chuva
    if origem_agua == 'chuva' and nivel_reservatorio_chuva >= 10:
        nivel_reservatorio_chuva -= 10
        print("Reservatório da chuva utilizado")  
        print(nivel_reservatorio_chuva)

def novo_log(umidade, origem, nivel):
    with open('logs.csv', mode='a', newline='', encoding='utf-8') as arquivo_csv:
        dados = csv.writer(arquivo_csv)
        data_hora = datetime.now().strftime('%d-%m-%Y %H:%M')
        dados.writerow([data_hora, f"{umidade}%", origem, f"{nivel}L"])

try:
    while True:
        ler_umidade()
        horario_atual = time.strftime("%d/%m/%Y %H:%M")
        origem_agua = 'chuva' if nivel_reservatorio_chuva >= 10 else 'distribuidora'
        
        
        if umidade < limite_umidade:
            irrigar(origem_agua)
            print("Sistema de irrigação ativado")
            send_post_request(f"Sistema de irrigação ativado usando água da {origem_agua}. Horário: {horario_atual}. Nivel da agua atual: {nivel_reservatorio_chuva}",
            horario_atual, nivel_reservatorio_chuva)
            novo_log(umidade, origem_agua, nivel_reservatorio_chuva)

        

        time.sleep(intervalo_verificacao)
except KeyboardInterrupt:
    print("Programa interrompido")
finally:
    #GPIO.cleanup()
    print("Fim do programa")



