import csv
import os

def clear_monthly_analysis(config):
    """Cria arquivo limpo com headers"""
    filepath = __filepath(config)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(['batch_date', 'results'])

    print(f"📁 Arquivo preparado: {filepath}")

def add_to_monthly_analysis(config, detected_smells, batchDate):
    """Adiciona linha ao arquivo (assume que clear foi chamado antes)"""
    filepath = __filepath(config)
    
    with open(filepath, 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow([batchDate, str(detected_smells)])

    print(f"✅ Dados adicionados: {filepath}")

def __filepath(config):
    output_dir = "./out/smells_by_month"
    os.makedirs(output_dir, exist_ok=True)
    
    repo_name = config.repositoryName.replace("/", "_")
    filename = f"{repo_name}.csv"
    filepath = os.path.join(output_dir, filename)

    return filepath