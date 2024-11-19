import RPi.GPIO as GPIO
import time
import serial
import csv
from datetime import datetime, timedelta
import requests

limite_umidade = 40  
intervalo_verificacao = 10  
nivel_reservatorio_chuva = 100  
umidade = 0

porta_serial = '/dev/ttyACM0'  # Atualize para a porta correta, se necessário
taxa_bauds = 9600

#servo_pin = 3
pino_valvula = 3
pino_valvula2 = 8

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pino_valvula, GPIO.OUT)
GPIO.setup(pino_valvula2, GPIO.OUT)

#servo = GPIO.PWM(servo_pin, 50)
#servo.start(0)

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
    #umidade = int(input("Digite a umidade do solo "))
    #return umidade
    try:
        # Abre a comunicação serial
        arduino = serial.Serial(porta_serial, taxa_bauds, timeout=1)
        time.sleep(2)  # Aguarda o Arduino inicializar a comunicação
        print("Conexão com Arduino estabelecida!")
    except serial.SerialException:
        print("Erro ao conectar com Arduino.")
        exit()
    
    try:
        while True:
            # Lê os dados do Arduino
            if arduino.in_waiting > 0:
                global nivel_reservatorio_chuva
                linha = arduino.readline().decode().strip()  # Lê e decodifica os dados
                dados = linha.split(",")  # Divide a linha CSV
                print(f"Dados recebidos: '{linha}'")
                # Converte os dados para inteiros
                umidade = int(dados[0])
                nivel_reservatorio_chuva = float(dados[1])
                
                print(f"Umidade do solo: {umidade}%")
                #print(f"Temperatura: {temperatura}°C")
                return umidade, nivel_reservatorio_chuva
            

            time.sleep(intervalo_verificacao)  # Aguarda um segundo entre as leituras

    except KeyboardInterrupt:
        print("Programa interrompido.")
    finally:
        arduino.close()  # Fecha a porta serial

def irrigar(origem_agua):
    global nivel_reservatorio_chuva
    if origem_agua == 'chuva' and nivel_reservatorio_chuva >= 0:
        #servo.ChangeDutyCycle(7.5)
        GPIO.output(pino_valvula, GPIO.HIGH)
        time.sleep(5)
        GPIO.output(pino_valvula, GPIO.LOW)
        #servo.ChangeDutyCycle(2.5)
        print("Reservatório da chuva utilizado")  
        print(nivel_reservatorio_chuva)
    else:
        GPIO.output(pino_valvula2, GPIO.HIGH)
        time.sleep(5)
        GPIO.output(pino_valvula2, GPIO.LOW)

def novo_log(umidade, origem, nivel):
    with open('logs.csv', mode='a', newline='', encoding='utf-8') as arquivo_csv:
        dados = csv.writer(arquivo_csv)
        data_hora = datetime.now().strftime('%d-%m-%Y %H:%M')
        dados.writerow([data_hora, f"{umidade}%", origem, f"{nivel}L"])

try:
    while True:
        ler_umidade()
        horario_atual = time.strftime("%d/%m/%Y %H:%M")
        origem_agua = 'chuva' if nivel_reservatorio_chuva >= 1 else 'distribuidora'
        
        
        if int(umidade) < limite_umidade:
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



