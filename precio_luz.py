from datetime import datetime

#OUTPUT_FILE = "./precio.txt"

now = datetime.now()
hora = now.hour
minuto = now.minute
dia_semana = now.weekday()  # 0 = lunes, 6 = domingo

VALLE = "Hora Valle, la más barata"
LLANO = "Hora Llano, precio intermedio"
PUNTA = "Hora Punta, la más cara"
# Fines de semana (sábado=5, domingo=6)
if dia_semana >= 5:
    periodo = VALLE
else:
    # Lunes a viernes
    if hora < 8 and hora >= 0:
        periodo = VALLE
    elif 8 <= hora < 10 or 14 <= hora < 18 or 22 <= hora < 24:
        periodo = LLANO
    elif 10 <= hora < 14 or 18 <= hora < 22:
        periodo = PUNTA
    else:
        periodo = "Periodo desconocido"

texto = (
    f"Estás en {periodo}."
)

#with open(OUTPUT_FILE, "w") as f:
#    f.write(texto)

print(texto)