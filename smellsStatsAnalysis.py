import pandas as pd
import os
import glob
from pathlib import Path

def analyze_repository_smells(csv_file_path):
    """
    Analisa um arquivo CSV de smells de repositório e retorna estatísticas
    """
    try:
        # Ler o arquivo CSV com separador de espaços
        df = pd.read_csv(csv_file_path, sep='\s+', engine='python')
        
        print(f"Colunas encontradas em {Path(csv_file_path).stem}: {list(df.columns)}")
        
        # Verificar se temos uma coluna de data (pode ter nomes diferentes)
        date_columns = [col for col in df.columns if 'date' in col.lower() or 'batch' in col.lower()]
        
        # Separar colunas (assumindo que todas exceto colunas de data são smells)
        if date_columns:
            smell_columns = [col for col in df.columns if col not in date_columns]
        else:
            # Se não encontrar coluna de data, todas as colunas são smells
            smell_columns = list(df.columns)
        
        if not smell_columns:
            print(f"Aviso: Nenhuma coluna de smell encontrada em {csv_file_path}")
            return None
        
        print(f"Smells analisados: {smell_columns}")
        
        # Calcular estatísticas para cada smell
        stats_data = {}
        
        for smell in smell_columns:
            # Garantir que a coluna é numérica
            df[smell] = pd.to_numeric(df[smell], errors='coerce').fillna(0)
            
            stats_data[smell] = {
                'Media': df[smell].mean(),
                'Moda': df[smell].mode().iloc[0] if not df[smell].mode().empty else 0,
                'Soma': df[smell].sum(),
                'Frequencia_%': df[smell].mean() * 100
            }
        
        return stats_data
        
    except Exception as e:
        print(f"Erro ao processar {csv_file_path}: {e}")
        return None

def generate_stats_for_all_repositories():
    """
    Gera estatísticas para todos os arquivos CSV no diretório smells_by_month
    """
    # Caminho para o diretório
    base_dir = './out/smells_by_month'
    csv_files = glob.glob(os.path.join(base_dir, '*.csv'))
    
    if not csv_files:
        print(f"Nenhum arquivo CSV encontrado em {base_dir}")
        return
    
    print(f"Encontrados {len(csv_files)} arquivos CSV para análise")
    
    # DataFrame para armazenar todas as estatísticas
    all_stats = []
    
    for csv_file in csv_files:
        # Extrair nome do repositório do nome do arquivo
        repo_name = Path(csv_file).stem
        
        print(f"\n=== Analisando: {repo_name} ===")
        
        # Analisar o arquivo
        repo_stats = analyze_repository_smells(csv_file)
        
        if repo_stats is not None:
            # Adicionar estatísticas ao DataFrame consolidado
            for smell, stats in repo_stats.items():
                all_stats.append({
                    'Repositorio': repo_name,
                    'Smell': smell,
                    'Media': stats['Media'],
                    'Moda': stats['Moda'],
                    'Soma': stats['Soma'],
                    'Frequencia_%': stats['Frequencia_%']
                })
            print(f"✓ {repo_name} processado com sucesso!")
        else:
            print(f"✗ Falha ao processar {repo_name}")
    
    if not all_stats:
        print("Nenhuma estatística foi gerada.")
        return
    
    # Criar DataFrame final
    stats_df = pd.DataFrame(all_stats)
    
    # Salvar arquivo de estatísticas
    output_file = os.path.join(base_dir, 'stats.csv')
    stats_df.to_csv(output_file, index=False, float_format='%.4f')
    
    print(f"\nEstatísticas salvas em: {output_file}")
    print(f"Total de repositórios analisados: {stats_df['Repositorio'].nunique()}")
    print(f"Total de smells analisados: {len(stats_df)}")
    
    # Mostrar preview dos dados
    print("\nPreview das estatísticas:")
    print(stats_df.head(10))
    
    return stats_df

def create_summary_table(stats_df):
    """
    Cria uma tabela resumo com estatísticas agregadas
    """
    if stats_df is None:
        return
    
    # Estatísticas resumidas por smell
    summary = stats_df.groupby('Smell').agg({
        'Media': ['mean', 'std', 'min', 'max'],
        'Frequencia_%': ['mean', 'std', 'min', 'max'],
        'Repositorio': 'count'
    }).round(4)
    
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    summary = summary.rename(columns={'Repositorio_count': 'Num_Repositorios'})
    
    # Salvar resumo
    base_dir = './out/smells_by_month'
    summary_file = os.path.join(base_dir, 'stats_summary.csv')
    summary.to_csv(summary_file)
    
    print(f"\nTabela resumo salva em: {summary_file}")
    print("\nResumo por smell:")
    print(summary)
    
    return summary

if __name__ == "__main__":
    # Verificar se o diretório existe
    if not os.path.exists('./out/smells_by_month'):
        print("Diretório './out/smells_by_month' não encontrado!")
        print("Certifique-se de que o diretório existe e contém arquivos CSV")
    else:
        # Gerar estatísticas
        stats_df = generate_stats_for_all_repositories()
        
        # Gerar tabela resumo se houve dados
        if stats_df is not None:
            create_summary_table(stats_df)