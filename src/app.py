import MetaTrader5 as mt5
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

def conectar_mt5():
    login_str = os.getenv("MT5_LOGIN")
    password = os.getenv("MT5_PASSWORD")
    server = os.getenv("MT5_SERVER")

    # Validar que las variables existen
    if not all([login_str, password, server]):
        print("❌ Error: No se encontraron todas las variables en el archivo .env")
        return

    try:
        login = int(login_str)
    except ValueError:
        print("❌ Error: MT5_LOGIN en el archivo .env debe ser un número.")
        return

    # 1. Intentar establecer conexión con el terminal de MT5
    if not mt5.initialize(login=login, password=password, server=server):
        # Eliminamos password del print por seguridad
        print(f"❌ Error al iniciar MT5 para el login {login} en el servidor {server}")
        print(f"Código de error de MT5: {mt5.last_error()}")
        return 

    # 2. Obtener información de la cuenta
    cuenta = mt5.account_info()

    if cuenta is not None:
        print("-" * 30)
        print(f"✅ CONEXIÓN EXITOSA")
        print(f"Cuenta: {cuenta.login}")
        print(f"Broker: {cuenta.company}")
        print(f"Balance: {cuenta.balance} {cuenta.currency}")
        print("-" * 30)
        
        # --- AQUÍ EMPIEZA TU LÓGICA DE TRADING ---
        # Ejemplo: obtener_datos_para_rnn() o ejecutar_prediccion()
        # -----------------------------------------

    else:
        print(f"❌ Conectado al terminal, pero falló el login para la cuenta {login}")
        print(f"Error: {mt5.last_error()}")

    # 3. Cerrar la conexión solo al final de TODO el proceso
    mt5.shutdown()

if __name__ == "__main__":
    conectar_mt5()