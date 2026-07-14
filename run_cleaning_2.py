from backend.data_processor import clean_pedidos, clean_clientes

print("Cleaning pedidos2.csv...")
nro_lider_dict, df_estadisticas = clean_pedidos(input_filename="pedidos2.csv", output_filename="pedidos_limpio2.csv")

print("Cleaning clientes2.csv...")
clean_clientes(nro_to_lider=nro_lider_dict, df_stats=df_estadisticas, input_filename="clientes2.csv", output_filename="clientes_limpio2.csv")

print("Done cleaning *2 files.")
