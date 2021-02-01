import pandas as pd
import os 
import json


wojewodztwa = {"02": "Dolnośląskie", "04": "Kujawsko-Pomorskie",
               "06": "Lubelskie",    "08": "Lubuskie",
               "10": "Łódzkie",      "12": "Małopolskie",
               "14": "Mazowieckie",  "16": "Opolskie",
               "18": "Podkarpackie", "20": "Podlaskie",
               "22": "Pomorskie",    "24": "Śląskie",
               "26": "Świętokrzyskie","28": "Warmińsko-Mazurskie",
               "30": "Wielkopolskie", "32": "Zachodniopomorskie",
               "00": "Polska"}

def prepare_json(json_file):    
    with open(json_file) as f:
      data = json.load(f)
      
    del data["crs"]
    del data["name"]
    
    for feature in data["features"]:
        feature["id"] = wojewodztwa[feature["properties"]["JPT_KOD_JE"]]
        
        del feature["type"]
        del feature["properties"]
        
        poly = [feature["geometry"]["coordinates"][0][0]]
        
        del feature["geometry"]
        
        feature["geometry"] = {"type": "Polygon", "coordinates": poly}
        
    return data

def p(x):
    x = str(int(x/100000))
    
    if len(x) == 1:
        x = f"0{x}"
    else:
        x = f"{x}"
        
    return x
    

def calc_proportion_WPP(df, og_column, selected_column):
    data = pd.DataFrame(round(df[selected_column]/df[og_column], 2), columns=["Ratio"])
    data["Województwo"] = df["Województwo"]
    
    return data
    

def calc_proportion_WWP(df, selected_column):
    df2 = df[["Województwo", selected_column]].copy()
    suma = df2[selected_column].sum()
    stosunek = list(round(df2[selected_column]/suma, 2))
    
    dd = {"Ratio": stosunek,
          "Województwo": list(df2["Województwo"])}
    
    data = pd.DataFrame(dd, columns=["Ratio", "Województwo"])
    
    return data


def bar_data(data):
    new_data = pd.DataFrame(columns=["Year", "Sex", "Deaths", "Województwo"])

    for year, data_frame in data.items():
        data_frame.drop(data_frame.index[0], inplace=True)
        m_column = f"MĘ-80-{year}"
        f_column = f"KO-80-{year}"
        df = data_frame[[m_column, f_column, "Województwo"]]
        df2 = df.copy()
        
        for _, row in df2.iterrows():
            deaths_m = row[m_column]
            deaths_f = row[f_column]
            woj = row["Województwo"]
            append_dict_m = {"Year": year, "Sex": "Male",   "Deaths": deaths_m, "Województwo": woj}
            append_dict_f = {"Year": year, "Sex": "Female", "Deaths": deaths_f, "Województwo": woj}
            new_data = new_data.append(append_dict_m, ignore_index=True)
            new_data = new_data.append(append_dict_f, ignore_index=True)
            
    return new_data
    

def prepare_dataframe(data_dir):
    data_files = [os.path.join(data_dir, path) for path in os.listdir(data_dir)]
    data_dict = {}
    
    for file in data_files:
        data = pd.read_csv(file, sep=";")
        
        data = data.drop("Nazwa", axis=1)
        data = data.drop(list(data.columns)[-1], axis=1)
        data["Kod"] = data["Kod"].apply(lambda x: p(x))
        data = data.replace({"Kod": wojewodztwa})
        data = data.rename(columns={"Kod": "Województwo"})
        
        columns = list(data.columns)
        new_columns = {}
        
        for col in columns[1:]:
            col_split = col.split(";")
            first_part = col_split[0][0:2].upper()
            
            if len(col_split[1]) > 1:
                if "i" in col_split[1]:
                    second_part = f"{col_split[1][0:3]}+"
                    
                elif len(col_split[1]) == 3:
                    second_part = f"{col_split[1][0:3]}"
                    
                else:
                    second_part = col_split[1][0:2].upper()
                
            else:
                second_part = col_split[1]
                
            third_part = col_split[2]
                
                
            new_col = f"{first_part}-{second_part}-{third_part}"
            new_columns[col] = new_col
            
        data.rename(columns=new_columns, inplace=True)
        
        data_dict[col_split[2]] = data
        
    return data_dict


    
    

        



