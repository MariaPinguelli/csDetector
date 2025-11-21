import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob
from pathlib import Path

def create_smell_heatmaps():
    """
    Gera heatmaps para cada arquivo CSV no diretório smells_by_month
    """
    # Configurações
    input_dir = './out/smells_by_month'
    output_dir = './out/smells_heatmaps'
    
    # Criar diretório de output se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Encontrar todos os arquivos CSV
    csv_files = glob.glob(os.path.join(input_dir, '*.csv'))
    
    if not csv_files:
        print(f"Nenhum arquivo CSV encontrado em {input_dir}")
        return
    
    print(f"Encontrados {len(csv_files)} arquivos CSV para processar")
    
    for csv_file in csv_files:
        try:
            # Extrair nome do repositório
            repo_name = Path(csv_file).stem
            print(f"Processando: {repo_name}")
            
            # Ler arquivo CSV com separador de espaços/tabs
            df = pd.read_csv(csv_file, sep='\s+', engine='python')
            
            # Verificar se temos coluna de data
            date_columns = [col for col in df.columns if 'date' in col.lower()]
            if not date_columns:
                print(f"  Aviso: Nenhuma coluna de data encontrada em {repo_name}")
                continue
            
            date_col = date_columns[0]
            
            # Converter para datetime
            df[date_col] = pd.to_datetime(df[date_col], format='%d/%m/%Y')
            
            # Colunas de smells (todas exceto a coluna de data)
            smell_columns = [col for col in df.columns if col != date_col]
            
            if not smell_columns:
                print(f"  Aviso: Nenhuma coluna de smell encontrada em {repo_name}")
                continue
            
            # Criar heatmap
            plt.figure(figsize=(16, 10))
            
            # Preparar dados para heatmap
            heatmap_data = df.set_index(date_col)[smell_columns].T
            
            # Criar heatmap
            sns.heatmap(heatmap_data,
                        cmap=['#f0f0f0', '#ff4444'],  # Branco para 0, Vermelho para 1
                        cbar_kws={'label': 'Presença (1) / Ausência (0)', 
                                 'ticks': [0, 1]},
                        linewidths=0.5,
                        linecolor='gray')
            
            # Configurações do gráfico
            plt.title(f'Presença de Code Smells - {repo_name}\n', 
                     fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Data', fontsize=12, fontweight='bold')
            plt.ylabel('Code Smells', fontsize=12, fontweight='bold')
            
            # Rotacionar labels do eixo x para melhor legibilidade
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)
            
            plt.tight_layout()
            
            # Salvar heatmap
            output_file = os.path.join(output_dir, f'{repo_name}_heatmap.png')
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"  ✓ Heatmap salvo: {output_file}")
            
        except Exception as e:
            print(f"  ✗ Erro ao processar {repo_name}: {e}")
            plt.close()

def create_combined_heatmap():
    """
    Cria um heatmap combinado com todos os repositórios (opcional)
    """
    input_dir = './out/smells_by_month'
    csv_files = glob.glob(os.path.join(input_dir, '*.csv'))
    
    if len(csv_files) < 2:
        print("Número insuficiente de arquivos para heatmap combinado")
        return
    
    all_data = []
    repo_names = []
    
    for csv_file in csv_files:
        try:
            repo_name = Path(csv_file).stem
            df = pd.read_csv(csv_file, sep='\s+', engine='python')
            
            # Encontrar coluna de data
            date_columns = [col for col in df.columns if 'date' in col.lower()]
            if not date_columns:
                continue
                
            date_col = date_columns[0]
            df[date_col] = pd.to_datetime(df[date_col], format='%d/%m/%Y')
            
            # Calcular médias por mês para este repositório
            smell_columns = [col for col in df.columns if col != date_col]
            repo_means = df[smell_columns].mean().to_frame().T
            repo_means.index = [repo_name]
            
            all_data.append(repo_means)
            repo_names.append(repo_name)
            
        except Exception as e:
            print(f"Erro em {csv_file}: {e}")
    
    if all_data:
        # Combinar todos os dados
        combined_df = pd.concat(all_data)
        
        # Criar heatmap comparativo
        plt.figure(figsize=(14, 10))
        sns.heatmap(combined_df,
                    cmap='YlOrRd',
                    annot=True,
                    fmt='.3f',
                    cbar_kws={'label': 'Frequência Média'},
                    linewidths=0.5)
        
        plt.title('Frequência Média de Code Smells por Repositório\n', 
                 fontsize=16, fontweight='bold')
        plt.xlabel('Code Smells', fontsize=12, fontweight='bold')
        plt.ylabel('Repositório', fontsize=12, fontweight='bold')
        plt.tight_layout()
        
        output_file = './out/smells_heatmaps/comparison_heatmap.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Heatmap comparativo salvo: {output_file}")

if __name__ == "__main__":
    print("=== GERANDO HEATMAPS DE CODE SMELLS ===\n")
    
    # Verificar se o diretório existe
    if not os.path.exists('./out/smells_by_month'):
        print("❌ Diretório './out/smells_by_month' não encontrado!")
        print("Certifique-se de que o diretório existe e contém arquivos CSV")
    else:
        # Criar heatmaps individuais
        create_smell_heatmaps()
        
        # Criar heatmap comparativo (opcional)
        print("\n=== GERANDO HEATMAP COMPARATIVO ===")
        create_combined_heatmap()
        
        print("\n✅ Processamento concluído!")
        print("📁 Heatmaps salvos em: ./out/smells_heatmaps/")