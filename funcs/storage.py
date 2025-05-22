import os
import jwt
from plyer import storagepath
from kivy.utils import platform
from kivy.logger import Logger
from datetime import datetime

from funcs.constantes import JWT_FILE

def get_storage_path():
    """Obtém o caminho de armazenamento apropriado para cada plataforma"""
    if platform == 'android':
        try:
            from android.storage import app_storage_path
            path = app_storage_path()
            # Garante que o diretório existe
            if not os.path.exists(path):
                os.makedirs(path)
            return path
        except Exception as e:
            Logger.error(f"Erro ao obter storage no Android: {str(e)}")
            return os.path.expanduser("~")
    else:
        return storagepath.get_home_dir()

def store_access_token(token):
    """Armazena o token JWT no local apropriado para a plataforma"""
    app_storage_dir = get_storage_path()
    token_file_path = os.path.join(app_storage_dir, JWT_FILE)
    
    try:
        if platform == 'android':
            from android.storage import app_storage_path
            # Garante que o diretório existe no Android
            if not os.path.exists(app_storage_dir):
                os.makedirs(app_storage_dir)

        with open(token_file_path, 'w') as token_file:
            token_file.write(token)
        Logger.info(f"Token salvo em {token_file_path}")
        return True
    except Exception as e:
        Logger.error(f"Erro ao salvar token: {str(e)}")
        return False

def get_access_token():
    """Obtém o token JWT do armazenamento local"""
    app_storage_dir = get_storage_path()
    token_file_path = os.path.join(app_storage_dir, JWT_FILE)
    
    if platform == 'android':
        # Verificação adicional para Android
        from android import mActivity
        from java.io import File
        android_file = File(mActivity.getFilesDir(), JWT_FILE)
        if not android_file.exists():
            Logger.info("Nenhum token encontrado (Android)")
            return ""

    if os.path.exists(token_file_path):
        try:
            with open(token_file_path, 'r') as token_file:
                token = token_file.read()
                Logger.info("JWT recuperado com sucesso.")
                return token
        except Exception as e:
            Logger.error(f"Erro ao ler token: {str(e)}")
            return ""
    else:
        Logger.info("Nenhum token encontrado.")
        return ""

def delete_access_token():
    """Remove o token JWT do armazenamento local"""
    app_storage_dir = get_storage_path()
    token_file_path = os.path.join(app_storage_dir, JWT_FILE)
    
    if platform == 'android':
        from android import mActivity
        from java.io import File
        android_file = File(mActivity.getFilesDir(), JWT_FILE)
        if android_file.exists():
            android_file.delete()
            Logger.info("Token deletado (Android)")
            return True
    
    if os.path.exists(token_file_path):
        try:
            os.remove(token_file_path)
            Logger.info("Token deletado.")
            return True
        except Exception as e:
            Logger.error(f"Erro ao deletar token: {str(e)}")
            return False
    else:
        Logger.info("Nenhum token para deletar.")
        return False

def is_token_valid(token):
    """Verifica se o token JWT é válido e não expirado"""
    if not token:
        Logger.info("Token vazio")
        return False

    try:
        # Decodifica sem verificar assinatura (mais rápido)
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        exp_timestamp = decoded_token.get('exp')

        if exp_timestamp:
            current_timestamp = datetime.now().timestamp()
            if exp_timestamp > current_timestamp:
                Logger.info("Token válido")
                return True

        Logger.info("Token expirado ou sem timestamp")
        return False
    except Exception as e:
        Logger.error(f"Erro ao verificar token: {str(e)}")
        return False

def android_request_permissions():
    """Solicita permissões necessárias no Android"""
    if platform == 'android':
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.INTERNET
        ])
        return True
    return False

def android_check_permissions():
    """Verifica se as permissões necessárias foram concedidas no Android"""
    if platform == 'android':
        from android.permissions import check_permission, Permission
        return (check_permission(Permission.READ_EXTERNAL_STORAGE) and
                check_permission(Permission.WRITE_EXTERNAL_STORAGE) and
                check_permission(Permission.INTERNET))
    return True  # Assume que tem permissões em outras plataformas
