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

if __name__ == "__main__":
    load_dotenv()
    SECRET_PAT = os.getenv("SECRET_PAT")

    tool = CsDetector()

    # repo = "https://github.com/altair-graphql/altair"
    # branch = "master"
    repo = "https://github.com/JabRef/jabref"
    branch = "main"

    out_folder = f"./out/output_default"
    os.makedirs(out_folder, exist_ok=True)

    print(f"➡️ Rodando análise")

    try:
        cmd_args = [
            "-p", SECRET_PAT,
            "-r", repo,
            "-b", branch,
            "-s", "./senti",
            "-o", out_folder,
            "-m", '1'
        ]

        formatted_result, result, config, excep = tool.executeTool(cmd_args)
        
        if excep:
            print(f"❌ Erro na análise: {excep}")
        else:
            print(f"✅ Análise concluída!")
            
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")