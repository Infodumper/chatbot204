import pandas as pd
import random
import os

def random_dni():
    return str(random.randint(10000000, 99999999))

def random_phone():
    return "223" + str(random.randint(4000000, 6999999))

def generate_fake_names(names_series):
    # Extract all words from names
    all_words = []
    for name in names_series.dropna():
        all_words.extend(str(name).split())
    
    unique_words = list(set(all_words))
    return unique_words

def main():
    base_dir = r"c:\TGPN\bot204\datos_originales"
    clientes_path = os.path.join(base_dir, "clientes.csv")
    pedidos_path = os.path.join(base_dir, "pedidos.csv")
    
    # Read with string dtype for these columns to avoid dtype issues when replacing
    df_clientes = pd.read_csv(clientes_path, dtype={"NroDoc": str, "Telefono_Perla": str, "Telefono_Clip": str})
    df_pedidos = pd.read_csv(pedidos_path)
    
    # 1. Collect words for names
    words = generate_fake_names(df_clientes["Cliente"])
    
    # 2. Create mapping for Nro -> Fake Name
    nros_clientes = df_clientes["Nro"].unique()
    nros_pedidos = df_pedidos["Nro"].unique()
    all_nros = list(set(nros_clientes).union(set(nros_pedidos)))
    
    nro_to_fakename = {}
    for nro in all_nros:
        if len(words) >= 2:
            fake_name = " ".join(random.sample(words, 2))
        else:
            fake_name = "FAKE NAME"
        nro_to_fakename[nro] = fake_name

    # 3. Apply to clientes
    df_clientes["Cliente"] = df_clientes["Nro"].map(nro_to_fakename).fillna(df_clientes["Cliente"])
    df_clientes["Nombre_Clip"] = df_clientes["Nro"].map(nro_to_fakename).fillna(df_clientes["Nombre_Clip"])
    
    # Replace DNI (NroDoc) where not null
    mask_doc = df_clientes["NroDoc"].notna()
    df_clientes.loc[mask_doc, "NroDoc"] = [random_dni() for _ in range(mask_doc.sum())]
    
    # Replace Phones where not null
    mask_tel_perla = df_clientes["Telefono_Perla"].notna()
    df_clientes.loc[mask_tel_perla, "Telefono_Perla"] = [random_phone() for _ in range(mask_tel_perla.sum())]
    
    mask_tel_clip = df_clientes["Telefono_Clip"].notna()
    df_clientes.loc[mask_tel_clip, "Telefono_Clip"] = [random_phone() for _ in range(mask_tel_clip.sum())]

    # 4. Apply to pedidos
    df_pedidos["Nombre"] = df_pedidos["Nro"].map(nro_to_fakename).fillna(df_pedidos["Nombre"])
    
    # 5. Save
    df_clientes.to_csv(os.path.join(base_dir, "clientes2.csv"), index=False)
    df_pedidos.to_csv(os.path.join(base_dir, "pedidos2.csv"), index=False)
    
    print("Files created successfully.")

if __name__ == "__main__":
    main()
