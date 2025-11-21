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

    repo_list = [
        # {
        #     "url": "https://github.com/vuejs/core",
        #     "branch": "main"
        # },
        # {
        #     "url": "https://github.com/rust-lang/rust",
        #     "branch": "main" #tava andando, mas demora demais, deixei a noite nota e não terminou
        # },
        # {
        #     "url": "https://github.com/python/cpython",
        #     "branch": "main"
        # },
        # {
        #     "url": "https://github.com/GNOME/gnome-shell",
        #     "branch": "main"
        # },
        # {
        #     "url": "https://github.com/jupyter/notebook",
        #     "branch": "main" #quebra rápido em algum momento puxa zero dados
        # },
        # {
        #     "url": "https://github.com/JabRef/jabref",
        #     "branch": "main"
        # },
        # {
        #     "url": "https://github.com/okfn-brasil/querido-diario",
        #     "branch": "main"
        # },
        # {
        #     "url": "https://github.com/pyladies/pyladies",
        #     "branch": "main"
        # }
        {
            "url": "https://github.com/torvalds/linux",
            "branch": "master"
        }
    ]



    out_folder = f"./out/output_default"
    os.makedirs(out_folder, exist_ok=True)

    # for repo in repo_list:
    repo = repo_list[0]
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
            print(f"❌ Erro na análise: {excep}")
            sys.exit()
        else:
            print(f"✅ Análise concluída!")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        sys.exit()