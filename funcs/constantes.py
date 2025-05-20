# Mapeamento de parâmetros para imagens
PARAMETROS_IMAGENS = {
    "Bateria":                 "res/bateria.png",                                                     # Corrente
    "Vel. Corr.":              "res/corrente- oceanstream.png",                                       # Corrente
    "Dir. Corr.":              "res/corrente-seta-direita.png",                                       # Corrente
    "Pitch":                   "res/Pitch-Roll.png",                                                  # Corrente
    "Roll":                    "res/Pitch-Roll.png",                                                  # Corrente
    "Altura Onda":             "res/Onda com linha- oceanstream.png",                                 # Onda
    "Período Onda":            "res/Onda - oceanstream.png",                                          # Onda
    "Altura":                  "res/Onda com linha- oceanstream.png",                                 # Ondógrafo
    "Período":                 "res/Onda - oceanstream.png",                                          # Ondógrafo
    "Maré Reduzida":           "res/Régua maregrafo com seta - oceanstream (2).png",                  # Marégrafo
    "Vel. Vento":              "res/Pressão atmosférica - oceanstream.png",                           # Est.M
    "Rajada":                  "res/Pressão atmosférica - oceanstream.png",                           # Est.M
    "Dir. Vento":              "res/Rosa dos ventos - com direção de cor diferente-oceanstream.png",  # Est.M
    "Chuva":                   "res/Chuva - oceanstream.png",                                         # Est.M
}

# Mapeamento dos equipamentos para os nomes das tabelas
EQUIPAMENTOS_TABELAS = {
    "Boia 04 - Corrente": "ADCP-Boia04_corrente",
    "Boia 08 - Corrente": "ADCP-Boia08_corrente",
    "Boia 10 - Corrente": "ADCP-Boia10_corrente",
    "Boia 04 - Onda": "ADCP-Boia04_onda",
    "Boia 08 - Onda": "ADCP-Boia08_onda",
    "Boia 10 - Onda": "ADCP-Boia10_onda",
    "Ondógrafo Píer-II": "Ondografo-PII_tab_parametros",
    "Ondógrafo TGL": "Ondografo-TGL_tab_parametros",
    "Ondógrafo TPD": "Ondografo-TPD_tab_parametros",
    "Ondógrafo TPM": "Ondografo-TPM_tab_parametros",
    "Marégrafo": "Maregrafo-TU_Maregrafo_Troll",
    "Estação Meteorológica": "TU_Estacao_Meteorologica"
}

# Cabecalho da tabela na tela Equipamento
CABECALHO_TABELA = {
    '_corrente': [
        ['TmStamp', 'TimeStamp']
        ,['PNORS_Pitch', 'Pitch']
        ,['PNORS_Roll', 'Roll']
        ,['vel11', 'Velocidade']
        ,['dir11', 'Direção (°)']
        ,['PNORS_Battery_Voltage', 'Bateria (V)']
    ],
    '_onda': [
        ['TmStamp', 'TimeStamp']
        ,['PNORW_Hm0', 'Altura (m)']
        ,['PNORW_Tp', 'Período (s)']
        ,['PNORW_DirTp', 'Direção (°)']
    ],
    'Ondografo': [
        ['TmStamp', 'TimeStamp']
        ,['hm0_alisado', 'Altura (m)']
        ,['tp_alisado', 'Período (s)']
    ],
    'Estacao': [
        ['TmStamp', 'TimeStamp']
        ,['Velocidade_Vento', 'Vel. Vento']
        ,['Rajada_Vento', 'Rajada']
        ,['Direcao_Vento', 'Dir. Vento (°)']
        ,['Chuva', 'Chuva (mm)']
    ],
    'Maregrafo': [
        ['TmStamp', 'TimeStamp']
        ,['Mare_Reduzida', 'Maré Reduzida (m)']
    ]
}
