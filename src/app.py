import MetaTrader5 as mt5
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

def conectar_mt5():
    login_str = os.getenv("MT5_LOGIN")
    password = os.getenv("MT5_PASSWORD")
    server = os.getenv("MT5_SERVER")

    if not all([login_str, password, server]):
        print("❌ Error: No se encontraron todas las variables en el archivo .env")
        return False # Devolvemos False para controlar el flujo

    try:
        login = int(login_str)
    except ValueError:
        print("❌ Error: MT5_LOGIN debe ser un número.")
        return False

    # Inicializar
    if not mt5.initialize(login=login, password=password, server=server):
        print(f"❌ Error al iniciar MT5: {mt5.last_error()}")
        return False 

    cuenta = mt5.account_info()
    if cuenta is not None:
        print("-" * 30)
        print(f"✅ CONEXIÓN EXITOSA - Cuenta: {cuenta.login} ({cuenta.currency})")
        print("-" * 30)
        return True # Conexión confirmada
    
    return False

def get_data_from(symbol="SP500m", n_bars=100):
    # Verificamos si el símbolo existe y está visible
    symbol_info = mt5.symbol_select(symbol, True)
    if not symbol_info:
        print(f"❌ Error: El símbolo {symbol} no está disponible.")
        return None

    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 1, n_bars)
    print(rates)

    if rates is not None and len(rates) > 0:
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df[['time', 'open', 'high', 'low', 'close']]
    else:
        print("❌ No se pudieron obtener los datos.")
        return None

if __name__ == "__main__":
    # Controlamos que solo pida datos si la conexión fue exitosa
    if conectar_mt5():
        df = get_data_from()
        if df is not None:
            print(df.head())
            #df.to_csv("sp500.csv")
        
        # Opcional: Aquí podrías llamar a tu RNN
        # model.predict(df_btc)
        
        mt5.shutdown() # Cerramos solo si se abrió
    else:
        print("Finalizando script debido a error de conexión.")