import requests
import random
import time


def buildNextPageQuery(cursor: str):
    if cursor is None:
        return ""
    return ', after:"{0}"'.format(cursor)


def runGraphqlRequest(pat: str, query: str):
    headers = {"Authorization": "Bearer {0}".format(pat)}
    
    max_retries = 15
    retry_count = 0
    last_exception = None
    
    while retry_count <= max_retries:
        try:
            if retry_count > 0:
                sleep_time = random.randint(2, 5) * retry_count
                print(f"🔄 Tentativa {retry_count + 1}/{max_retries + 1}. Aguardando {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                sleep_time = random.randint(1, 3)
                time.sleep(sleep_time)
            
            request = requests.post(
                "https://api.github.com/graphql", 
                json={"query": query}, 
                headers=headers,
                timeout=30
            )
            
            if request.status_code == 200:
                response_data = request.json()
                
                if 'errors' in response_data:
                    for error in response_data['errors']:
                        if 'RATE_LIMITED' in error.get('type', ''):
                            handle_rate_limit(request.headers, pat)
                            continue
                        
                        if 'type' in error:
                            error_msg = f"GraphQL error: {error['type']} - {error.get('message', '')}"
                            raise Exception(error_msg)
                
                return response_data.get("data", {})
            
            elif request.status_code == 403:
                if 'X-RateLimit-Remaining' in request.headers:
                    remaining = int(request.headers['X-RateLimit-Remaining'])
                    if remaining <= 0:
                        handle_rate_limit(request.headers, pat)
                        continue
                
                raise Exception(f"Access forbidden: {request.text}")
            
            elif request.status_code == 502 or request.status_code == 503:
                print(f"⚠️ Servidor indisponível (HTTP {request.status_code}), tentando novamente...")
                retry_count += 1
                continue
                
            else:
                raise Exception(
                    "Query execution failed with code {0}: {1}".format(
                        request.status_code, request.text
                    )
                )
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout na requisição, tentando novamente...")
            retry_count += 1
            last_exception = "Timeout"
            continue
            
        except requests.exceptions.ConnectionError:
            print("🌐 Erro de conexão, tentando novamente...")
            retry_count += 1
            last_exception = "Connection error"
            continue
            
        except Exception as e:
            last_exception = str(e)
            
            if "rate limit" in str(e).lower() or "rate_limit" in str(e).lower():
                print("🔁 Rate limit detectado pela mensagem, verificando...")

                try:
                    rate_info = check_rate_limit(pat)
                    if rate_info and rate_info['remaining'] <= 0:
                        wait_time = calculate_wait_time(rate_info['resetAt'])
                        print(f"⏳ Rate limit atingido. Aguardando {wait_time:.1f} segundos...")
                        time.sleep(wait_time)
                        continue
                except:
                    pass
            
            print(f"❌ Erro na tentativa {retry_count + 1}: {e}")
            retry_count += 1
    
    raise Exception(
        f"Todas as {max_retries + 1} tentativas falharam. Último erro: {last_exception}"
    )


def addLogin(node, authors: list):
    login = extractAuthorLogin(node)

    if not login is None:
        authors.append(login)


def extractAuthorLogin(node):
    if node is None or not "login" in node or node["login"] is None:
        return None

    return node["login"]

def handle_rate_limit(headers, pat):
    """
    Trata especificamente o rate limit da API
    """
    try:
        if 'X-RateLimit-Reset' in headers:
            reset_timestamp = int(headers['X-RateLimit-Reset'])
            current_time = time.time()
            wait_time = max(reset_timestamp - current_time + 2, 2)
            
            print(f"⏰ Rate limit atingido! Aguardando {wait_time:.1f} segundos...")
            time.sleep(wait_time)
            return
        
        rate_info = check_rate_limit(pat)
        if rate_info:
            wait_time = calculate_wait_time(rate_info['resetAt'])
            print(f"⏰ Rate limit atingido! Aguardando {wait_time:.1f} segundos...")
            time.sleep(wait_time)
        else:
            print("⏰ Rate limit atingido! Aguardando 1 hora...")
            time.sleep(3600)
            
    except Exception as e:
        print(f"Erro ao tratar rate limit: {e}")
        time.sleep(3600)

def check_rate_limit(pat):
    try:
        query = """
        query {
            rateLimit {
                limit
                remaining
                resetAt
                used
            }
        }
        """
        
        headers = {"Authorization": f"Bearer {pat}"}
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'rateLimit' in data['data']:
                return data['data']['rateLimit']
    
    except Exception as e:
        print(f"Erro ao verificar rate limit: {e}")
    
    return None

def calculate_wait_time(reset_at_str):
    """
    Calcula quanto tempo esperar até o reset do rate limit
    """
    try:
        reset_time = datetime.fromisoformat(reset_at_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        
        wait_seconds = (reset_time - now).total_seconds()
        return max(wait_seconds + 5, 5)
        
    except Exception:
        return 3600