import requests
import smbus
import time

apikey = "123456789"
SLAVE_ADDRESS = 0x04  # Ugyanaz, mint az Arduino kódban
bus = smbus.SMBus(1)  # I2C bus 1 a Pi-n

# Adatok kuldese a sajat php api-ra
def send_data_to_api(temperature, humidity):
    url = f'http://192.168.0.181/sensor/insert_data_apikey.php?api_key={apikey}&temperature={temperature}&humidity={humidity}'
    print(f"Kuldesi URL: {url}")
    try:
        response = requests.get(url)
        print(f"Valasz kod: {response.status_code}")
        print(f"Valasz szoveg: {response.text}")
        
        if response.status_code == 200:
            print(f"Sikeres adatkuuldes: Homerseklet={temperature}, Paratartalom={humidity}")
        else:
            print(f"Sikertelen adatkuuldes: {response.status_code}")
    except Exception as e:
        print(f"Hiba a kuldes soran: {e}")

# Vegtelen ciklus 10 masodperces idokozonken
while True:
    try:
        # Olvasás az Arduino-tól: 32 byte-ig, de elég a mi adatunkhoz
        data = bus.read_i2c_block_data(SLAVE_ADDRESS, 0, 32)
        line = ''.join(chr(byte) for byte in data if byte != 0).strip()  # Byte-okból string
        print(line)  # Kiírja: "Homerseklet: 25.00 Paratartalom: 50.00"
        
        if line.startswith("Error"):
            print("Ervenytelen szenzor olvasas")
        else:
            # Parse the line: assuming format "Homerseklet: XX.XX Paratartalom: XX.XX"
            parts = line.split()
            if len(parts) == 4 and parts[0] == "Homerseklet:" and parts[2] == "Paratartalom:":
                temperature = round(float(parts[1]), 2)
                humidity = round(float(parts[3]), 2)
                print(f"{temperature:05.2f}*C {humidity:05.2f}%")
                
                # Adatok kuldese
                send_data_to_api(temperature, humidity)
            else:
                print("Ervenytelen formatumu adat")
    except Exception as e:
        print(f"I2C hiba: {e}")
    
    # 10 masodperces varakozas
    time.sleep(10)
