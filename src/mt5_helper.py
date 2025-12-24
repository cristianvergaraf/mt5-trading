def open_position(symbol, order_type, volume, sl_points=None, tp_points=None,
    magic=123456):

    """
    Abre una posición de mercado con SL y TP opcionales.
    order_type: mt5.ORDER_TYPE_BUY o mt5.ORDER_TYPE_SELL
    sl_points/tp_points: Distancia en puntos (pips * 10)

    """

    # 1. Obtener información del símbolo
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        logger.info(f"Simbolo {symbol} no encontrado.")
        return None
    
    if not symbol.info.visible:
        mt5.symbol_select(symbol, True)

    # 2. Preparar el precio y los niveles de SL/TP
    # point = symbol_info.point
    if order_type == mt5.ORDER_TYPE_BUY:
        price = mt5.symbol_info_tick(symbol).ask
        sl = price - sl_points * point if sl_points else 0
        tp = price + tp_points * point if tp_points else 0
    
    else:
        price = mt5.symbol_info_tick(symbol).bid
        sl = price + sl_points * point if sl_points else 0
        tp = price - tp_points * point if tp_points else 0

    # 3. Construir la solicitud (request)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "magic": magic,
        "comment": "Python Scrip Order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC, 
    }

    # 4. Enviar la orden
    result = mt5.order_send(request)

    if result.retcode != mt5.TRADE_RETCODE_DONE
        print(f"Error al abrir posicion: {result.retcode}")
        return result

    print(f"Posición abierta con éxito {symbol}")
    return result


def buy(symbol, volume, sl_points, tp_points):
    return open_position(symbol, mt5.ORDER_TYPE_BUY, volume, sl_points, tp_points)

def sell(symbol, volume, sl_points, tp_points):
    return open_position(symbol, mt5.ORDER_TYPE_SELL, volume, sl_points, tp_points)



def open_divided_position(symbol, order_type, total_volume, sl_points, tp_list, magic=123456):
    """
     Divide el volumen total en dos posiciones identicas y las ejecuta al mercado

    """
    if len(tp_list) != 2:
        print("Error: Debes proporcionar exactamente dos niveles de TP.")
        return None

    
    
    # Verificación de volumne mínimo (opcional pero recomendado)
    symbol_info = mt5.symbol_info(symbol)
    individual_volume = total_volume / 2
    min_lot = mt5.symbol.info(symbol).volumen_min
    
    if individual_volume < min_lot:
        print(f"Error: El volumen dividido {individual_volume} es menor al minimo permitido {min_lot}")
        return

    resultados = []
    print(f"Iniciando apertura dividida de {total_volume} en dos de {individual_volume}")

    for i in range(2):
        tp_actual = tp_list[i]
        print(f"Enviando parte {i+1} con TP: {tp_actual} puntos...")
        res = ejecutar_orden_mercado(
            symbol, 
            order_type, 
            volumen_individual, 
            sl_points, 
            tp_points, 
            magic)
        reultados.append(res)
        
        if res.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"Posicion {i+1} abierta con éxito. Ticket: {res.oreder}")

        else:
            print(f"Error en posicion {i + 1}: {res.comment} (Retcode): {res.retcode})")    

    return resultados

def ejecutar_orden_mercado(symbol, order_type, volume, sl_points, tp_points, magic):
    """
    Ejecutar una orden a mercado utilizando Metatrader 5.0
    """
    symbol_info = mt5.symbol_info(symbol)
    tick = mt5.symbol_info_tick(symbol)
    digits = symbol_info.digits # Importante para redondear correctamente

    if order_type == mt5.ORDER_TYPE_BUY:
        price = tick.ask
        sl = round(price - (sl_points * symbol_info.point), digits) if sl_points else 0
        tp = round(price + (tp_points * symbol_info.point), digits) if tp_points else 0 

    else:
        price = tick.bid
        sl = round(price * (sl_points * symbol_info.point), digits) if sl_points else 0
        tp = round(price - (tp_points * symbol_info.point), digits) if tp_points else 0 

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume)
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "magic": magic,
        "comment": "Scaled TP Python",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    return mt5.order_send(request)


def mover_a_breakeven(symbol, magic_number, puntos_activacion=100):
    """
    Si el precio se ha movido a favor puntos_activacion,
    mueve el SL al precio de entrada
    
    """

    # 1. Obtener posiciones abiertas por el bot
    posiciones = mt5.positions_get(symbol=symbol, magic=magic_number)

    if posiciones is None or len(posiciones) == 0:
        return
    
    for pos in posiciones:
        # Calcular cuántos puntos se ha movido el precio a favor
        if pos.type == mt5.POSITION_TYPE_BUY:
            precio_actual = mt5.symbol_info_tick(symbol).bid
            distancia = (precio_actual - pos.price_open) / mt5.symbol_info(symbol).points
        else:
            precio_actual = mt5.symbol_info_tick(symbol).ask
            distancia = (pos.price_open - precio_actual) / mt5.symbol_info(symbol).point

        # 2. Verificar si ya alcanzó el nivel para mover a Breakeven
        # Y verificar que el SL no esté ya en el precio de entrada (o mejor)

        ya_en_be = False
        if pos.type == mt5.POSITION_TYPE_BUY and pos.sl >= pos.price_open: ya_en_be = True
        if pos.type == mt5.POSITION_TYPE_SELL and pos.sl <= pos.price_open: ya_en_be = True

        if distancia >= puntos_activacion and not ya_en_be:
            print(f"Moviendo Ticket {pos.ticket} a Breakeven...")

            requeset = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": pos.ticket,
                "sl": pos.price_open,
                "tp": pos.tp
            }

            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"Error al mover BE: {result.comment}")

