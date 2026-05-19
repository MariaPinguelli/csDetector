import os
import sys
import subprocess
import datetime
import csv
import json
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import requests
from csDetector import CsDetector

def log_error(repo_url, error_message, log_file="error_log.txt"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"""
        [{timestamp}]
        Repositório: {repo_url}
        Erro: {error_message}
        {'='*50}
    """
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"📝 Erro registrado em {log_file}")
    except Exception as e:
        print(f"❌ Falha ao registrar erro no log: {e}")

if __name__ == "__main__":
    load_dotenv()
    SECRET_PAT = os.getenv("SECRET_PAT")

    tool = CsDetector()

    repo_list = [
        {
            "url": "https://github.com/pyladies/pyladies",
            "branch": "main"
        },
        {
            "url": "https://github.com/okfn-brasil/querido-diario",
            "branch": "main"
        },
        {
            "url": "https://github.com/facebook/create-react-app",
            "branch": "main"
        },
        {
            "url": "https://github.com/altair-graphql/altair",
            "branch": "master"
        },
        {
            "url": "https://github.com/vuejs/core",
            "branch": "main"
        },
        {
            "url": "https://github.com/JabRef/jabref",
            "branch": "main"
        },
    ]

    out_folder = f"./out/output_default"
    os.makedirs(out_folder, exist_ok=True)

    for repo in repo_list:
        print(f"➡️ Rodando análise de {repo['url']}")

        try:
            cmd_args = [
                "-p", SECRET_PAT,
                "-r", repo["url"],
                "-b", repo["branch"],
                "-s", "./senti",
                "-o", out_folder,
                "-m", '1'
            ]

            formatted_result, result, config, excep = tool.executeTool(cmd_args)
            
            if excep:
                error_msg = f"Erro na análise: {excep}"
                print(f"❌ {error_msg}")
                log_error(repo["url"], error_msg)
            else:
                print(f"✅ Análise de {repo['url']} concluída!")
            
        except Exception as e:
            error_msg = f"Erro durante execução: {e}"
            print(f"❌ {error_msg}")
            log_error(repo["url"], error_msg)