from datetime import datetime
import json

def ler_arquivo_json(caminho_arquivo):
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        print("JSON carregado com sucesso!")
        return dados
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar o JSON: {e}")
    return None

def salvar_arquivo_json(data, caminho_arquivo):
    try:
        with open(caminho_arquivo, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erro ao salvar JSON: {e}")

def salvar_cards(dict):
    dict_completo = {
        "nome": "Overview - Cards",
        "atualizado_em": str(datetime.now()),
        "cartoes": dict
    }
    salvar_arquivo_json(data=dict_completo, caminho_arquivo='data/cards.json')
