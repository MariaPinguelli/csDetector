import csv
import os
from datetime import datetime

ALL_SMELLS = ["OSE", "BCE", "PDE", "SV", "OS", "SD", "RS", "TFS", "UI", "TC"]
OUTPUT_DIR = "./out/smells_by_month"

def _get_filepath(config):
    repo_name = config.repositoryName.replace("/", "_")
    filename = f"{repo_name}.csv"
    return os.path.join(OUTPUT_DIR, filename)

def _convert_smells_to_binary(detected_smells):
    smells_binary = {smell: 0 for smell in ALL_SMELLS}
    for smell in detected_smells:
        if smell in smells_binary:
            smells_binary[smell] = 1
    return smells_binary

def _create_file_with_header(filepath):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        header = ["batch_date"] + ALL_SMELLS
        writer.writerow(header)

def clear_monthly_analysis(config):
    filepath = _get_filepath(config)
    
    try:
        _create_file_with_header(filepath)
        print(f"📁 Arquivo criado/recriado: {filepath}")
    except Exception as e:
        print(f"❌ Erro ao criar arquivo: {e}")

def add_to_monthly_analysis(config, detected_smells, batchDate):
    filepath = _get_filepath(config)
    
    try:
        smells_binary = _convert_smells_to_binary(detected_smells)
        
        formatted_date = batchDate.strftime("%d/%m/%Y")
        
        row_data = [formatted_date] + [smells_binary[smell] for smell in ALL_SMELLS]
        
        with open(filepath, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter='\t')
            writer.writerow(row_data)
            
        print(f"✅ Dados adicionados: {filepath}")
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado. Execute clear_monthly_analysis() primeiro.")
    except Exception as e:
        print(f"❌ Erro ao adicionar dados: {e}")