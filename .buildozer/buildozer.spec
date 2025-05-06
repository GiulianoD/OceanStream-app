[app]

# Nome do seu app
title = OceanStream

# Nome do pacote
package.name = oceanstream

# Nome da organização
package.domain = org.oceanstream

# Fonte principal
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

# Arquivo principal
source.main = main.py

# Inclui todo o conteúdo da pasta res (se você usa imagens lá)
presplash.filename = res/logo.png

# Versão do app
version = 0.1

# Ícone do app (opcional)
# icon.filename = %(source.dir)s/icon.png

# Linguagem requerida
requirements = python3,kivy,kivymd,plyer,requests,pyjwt,kivy_garden.matplotlib,matplotlib,certifi,urllib3,chardet,idna,jnius

# Orientação de tela
orientation = portrait

# Permissões necessárias
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# Arquitetura suportada
android.arch = arm64-v8a,armeabi-v7a

# Configurações específicas
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.api = 33
android.build_tools_version = 33.0.2

# Se quiser melhorar o tamanho do APK:
# android.enable_optimizations = True

# Indica ao buildozer para incluir recursos externos (opcional)
# include_exts = kv,png,jpg,atlas,json