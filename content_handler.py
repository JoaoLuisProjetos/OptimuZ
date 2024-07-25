

prefixo_ws = 'W-'
from re import sub
from collections import Counter
from string import Template
from base_templates import cursor_query, select_query, insert_query, update_query, delete_query, sum_query,\
    count_query, valida_statement

def RemoveRepetidosLista(lista):
    t = []
    [t.append(item) for item in lista if not t.count(item)]
    return t


def compara_maior_string(lista_str, lista_idx): # Calcula o tamanho da maior variavel utilizada nas queryes para alinhamento de codigo
    tamanho = 0

    #if len(lista_str) > 1:
    for item in lista_str:
            if len(item[3]) > tamanho and lista_str.index(item) in lista_idx:
                tamanho = len(item[3])
    #else:
    #    len(lista_str[3])

    return tamanho


def gera_declaracao_variaveis(lista1, lista2, zip_groups, tab): # Monta variaveis de WSS a partir das selecionadas

    display_var = False #Declara variavel igual DCLGEN ou display
    master_lista = list(set(lista1) | set(lista2))
    master_lista.sort()
    tamanho = compara_maior_string(zip_groups, master_lista)
    elementar_01 = tab.split('.')[0]

    if len(master_lista) > 0:
        declarative = '       01  ' + prefixo_ws + elementar_01 + '.\n'
    else:
        return

    if '_' not in zip_groups[0][0]: # verifica se existe '_' no nome da variavel[0], caso exista a origem é DCL
        idx_w = 0
    else:
        idx_w = 3

    for item in master_lista:
        try:
            if display_var == False:
                declarative = declarative + ('          10  ' + prefixo_ws + zip_groups[item][idx_w].ljust(tamanho + 10) \
                                     + 'PIC ' + str(zip_groups[item][4] + '.\n'))
            else:
                declarative = declarative + ('          10  ' + prefixo_ws + zip_groups[item][idx_w].ljust(tamanho + 10) \
                                   + 'PIC ' + str(zip_groups[item][4].split()[:1])[2:-2] + '.\n')
        except:
            pass

    declarative = declarative + '      *\n'

    return declarative


def monta_selected_hosts_DB2(selecionados, zip_groups):  # Monta sentencas das variaveis para seleção
    try:
        last = selecionados[-1]
    except IndexError:
        return '', ''

    hosts = ''; selected = ''

    for item in selecionados:
        if last == item: crlf = ''
        else:            crlf = '\n'

        if selected == '': selected = selected + ('                    ' + zip_groups[item][0] + crlf)
        else:              selected = selected + ('                   ,' + zip_groups[item][0] + crlf)

        if hosts == '':    hosts = hosts + ('                   :' + zip_groups[item][3] + crlf)
        else:              hosts = hosts + ('                  ,:' + zip_groups[item][3] + crlf)

    return selected, hosts


def monta_cond_fields_DB2(selecionados, zip_groups):  # Monta sentencas das variaveis dos campos condição
    try:
        last = selecionados[-1]
    except IndexError:
        return  ''

    tamanho = compara_maior_string(zip_groups, selecionados)
    cond = ''

    for item in selecionados:
        if last == item: crlf = ''
        else:            crlf = '\n'

        if cond == '': cond = cond + ('                  WHERE ' + zip_groups[item][0].ljust(tamanho) + ' = :' + zip_groups[item][3] + crlf)
        else:          cond = cond + ('                  AND   ' + zip_groups[item][0].ljust(tamanho) + ' = :' + zip_groups[item][3] + crlf)
    return cond


def monta_move_condition(selecionados, zip_groups):  # Monta sentencas das movimentações de WS para Hosts
    try:
        last = selecionados[-1]
    except IndexError:
        return ''

    moves = ''
    tamanho = compara_maior_string(zip_groups,selecionados)

    for item in selecionados:
        if last == item: crlf = ''
        else:            crlf = '\n'

        # Testa varchar = sim
        if zip_groups[item][2] == True:
            moves = moves + ('      * Varchar sendo utilizada para campo condicao, nao recomendado!!!' + crlf)

        moves = moves + ('           MOVE  ' + prefixo_ws + zip_groups[item][3].ljust(tamanho) +
                         '  TO  ' + zip_groups[item][3] + '.' + crlf)
    return moves


def monta_move_host(selecionados, zip_groups):   # Monta sentencas das movimentações de Hosts para WS
    try:
        last = selecionados[-1]
    except IndexError:
        return ''

    moves = ''
    tamanho = compara_maior_string(zip_groups, selecionados)

    # verifica se existe '_' no nome da variavel[0], caso exista a origem é DCL
    if '_' not in zip_groups[0][0]:
        idx_w = 0
    else:
        idx_w = 3

    for item in selecionados:
        if last == item:
            crlf = ''
        else:
            crlf = '\n'

        # Testa varchar = nao
        if zip_groups[item][2] == False:
            moves = moves + ('           MOVE  ' + zip_groups[item][3].ljust(tamanho) + '  TO  ' + prefixo_ws + zip_groups[item][idx_w] + crlf)
        else:
            moves = moves + ('           MOVE  ' + zip_groups[item][3] + '-TEXT(1:' + zip_groups[item][3] + ':LEN)'+ crlf)
            moves = moves + ('                                          TO  ' + prefixo_ws + zip_groups[item][idx_w] + crlf)

    return moves


def gerar_campos_selecionados(lista_select, lista_cond, zip_groups, parametros_principais):

    sel_fields, host_fields = monta_selected_hosts_DB2(lista_select, zip_groups)
    cond_fields = monta_cond_fields_DB2(lista_cond, zip_groups)

    move_cond = monta_move_condition(lista_cond, zip_groups)
    move_host = monta_move_host(lista_select, zip_groups)
    declarative = gera_declaracao_variaveis(lista_select, lista_cond, zip_groups, parametros_principais[3])

    return sel_fields, host_fields, cond_fields, move_cond, move_host, declarative


def agrupar_comando_em_linha(texto_):    # Agrupa comandos de array de texto (Book, programa ) COBOL
    #import pprint
    linha_comando = ''
    linhas_texto_1 = []
    ctl_linhas = 0

    if texto_:
        for linha in texto_:
            #print(linha)
            ctl_linhas += 1

            if '-INC' in linha[0:4] or '=INC' in linha[0:4]:
                linha = linha[0:72]
            else:
                linha = '      ' + linha[6:72]
            if '\n' not in linha:
                linha = linha + '\n'

            split_linha = linha.split()
            #print('len(linha.split()) ',len(linha.split()))
            if len(linha.split()) != 0:
                if split_linha[0] == 'PROCEDURE':
                    #print('brekou')
                    return linhas_texto_1

                if "*" not in linha[6]:

                    # caso seja fim de comando, inclui a linha no array, caso contrario concatena a linha_comando
                    # monta includes no array texto
                    if linha.endswith('.\n') or '-INC' in linha[0:4] or '=INC' in linha[0:4] or split_linha[-1][-1] == '.':
                        linha_comando = linha_comando + linha[:-1]
                        #print('++',linha_comando)
                        linhas_texto_1.append(linha_comando)
                        linha_comando = ''
                    else:
                        linha_comando = linha_comando + linha[:-1]

        #pprint.pprint(linhas_texto_1)

    return linhas_texto_1


def capture_cobol_definitions(texto):
    # COBOL - Resposta - lista zip de variaveis
    # formato: (lista_ws_var, lista_cobol_lvl, lista_casos_esp, lista_cobol_var, lista_cobol_def)

    lista_cobol_lvl = []  # lista o nivel da variavel
    lista_cobol_var = []  # lista o nome variavel COBOL
    lista_cobol_def = []  # lista a definicao das variaveis
    lista_casos_esp = []  # lista OCCURS, REDEFINES

    for linha in texto:

        #print('linha', linha)
        split_linha = linha.split()

        if len(split_linha) > 0 and ("*" not in linha[6]): # Caso nao seja uma linha vazia ou comentario
            if split_linha[0].isdigit():
                lista_cobol_lvl.append(int(split_linha[0]))
                lista_cobol_var.append(sub(r'[?|$|.|!]', r'', ''.join(split_linha[1])))

                if (' OCCURS' not in linha) and ('REDEFINES' not in linha):
                    if 'PIC' in split_linha:
                        if 'VALUE' in split_linha:
                            # Monta somente com Value
                            if 'VALUE' in split_linha[2] and 'COMP' not in linha:
                                monta = split_linha[-1] + ' ' + split_linha[2] + ' ' + ' '.join(split_linha[3:(split_linha.index('PIC'))])
                                lista_cobol_def.append(sub(r'[?|$|.|!]', r'', monta))
                            # Monta com comp e Value
                            elif 'VALUE' in split_linha[2] and 'COMP' in linha:
                                monta = split_linha[-2] + ' ' + split_linha[-1] + ' ' + split_linha[2] + ' ' + ' '.join(split_linha[3:(split_linha.index('PIC'))])
                                lista_cobol_def.append(sub(r'[?|$|.|!]', r'', monta))
                            # Demais casos
                            else:
                                lista_cobol_def.append(sub(r'[?|$|.|!]', r'', ' '.join(split_linha[3:])))
                        # Monta variavel sem valor a inicializar
                        else:
                            lista_cobol_def.append(sub(r'[?|$|.|!]', r'', ' '.join(split_linha[3:])))
                    # Monta variavel sem definicao
                    else:
                        if split_linha[0] == '88':
                            lista_cobol_def.append(sub(r'[?|$|.|!]', r'', ' '.join(split_linha[2:])))
                        else:
                            lista_cobol_def.append(False)

                    lista_casos_esp.append(False)

                else:
                    lista_cobol_def.append(False)
                    try:
                        caso = 'OCCURS' + ' ' + split_linha[3] if ('OCCURS' in linha) else 'REDEFINES'
                    except IndexError:
                        caso = 'OCCURS' + ' ' + split_linha[2] if ('OCCURS' in linha) else 'REDEFINES'

                    if 'DEPENDING' in split_linha:
                        for word in range(len(split_linha)):
                            if split_linha[word] == 'DEPENDING':
                                caso = caso + ' ' + sub(r'[?|$|.|!]', r'', ''.join(split_linha[word]))
                                caso = caso + ' ' + sub(r'[?|$|.|!]', r'', ''.join(split_linha[word + 2]))
                                break
                    elif 'REDEFINES' not in caso:
                        #print(lista_cobol_var[-2])
                        caso = caso + ' ' + lista_cobol_var[-2]

                    lista_casos_esp.append(caso)

    prefixos = verifica_prefixo_variaveis(lista_cobol_var)
    lista_ws_var = retira_prefixo_variavel(lista_cobol_var, prefixos)
    zip_groups = list(zip(lista_ws_var, lista_cobol_lvl, lista_casos_esp, lista_cobol_var, lista_cobol_def))  # zipping

    #print('\nws-var:', len(lista_ws_var), lista_ws_var, '\ncobol lvl:', len(lista_cobol_lvl), lista_cobol_lvl,\
          # '\nCasos Especiais:', len(lista_casos_esp), lista_casos_esp, '\nCobol var:', len(lista_casos_esp) ,\
          #  lista_cobol_var, '\ncbl def:', lista_cobol_def)

    return zip_groups


def verifica_prefixo_variaveis(lista_var):

    lista_pref = []
    for item in lista_var:
        split_var = item.split('-')
        split_var[0] = split_var[0] + '-'
        lista_pref.append(sub(r'[?|$|.|!]', r'', ''.join(split_var[0])))

    # Lista {Prefixo: Qtd}
    lista_pref = dict(Counter(lista_pref))
    lista_pref = {key: val for key, val in lista_pref.items() if (val/len(lista_var)) >= 0.33}

    return lista_pref


def retira_prefixo_variavel(lista_var, dict_pref):
    lista_var_saida = []
    for key in dict_pref:
        for item in lista_var:
            if item[:len(key)] == key:
                lista_var_saida.append(item[len(key):])
            else:
                lista_var_saida.append(item)

    # print(lista_var_saida)
    return lista_var_saida


def monta_template(parametros_principais, sel_fields, host_fields, tabela, cond_fields):

    db2_cmd = ['CURSOR', 'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'SUM', 'COUNT', 'CSR_SCROLL']

    if parametros_principais[2] == 'CURSOR' or parametros_principais[2] == 'SELECT' and parametros_principais[1] == 'SQL':
        temp_query = Template(cursor_query)
    elif parametros_principais[2] == 'SELECT':
        temp_query = Template(select_query)
    elif parametros_principais[2] == 'INSERT':
        temp_query = Template(insert_query)
        cond_fields = ''
    elif parametros_principais[2] == 'UPDATE':
        temp_query = Template(update_query)
        sel_fields = sel_fields.replace('\n', ' = Valor\n') + ' = Valor'
    elif parametros_principais[2] == 'DELETE':
        temp_query = Template(delete_query)
    elif parametros_principais[2] == 'SUM':
        temp_query = Template(sum_query)
    elif parametros_principais[2] == 'COUNT':
        temp_query = Template(count_query)
    elif parametros_principais[2] == 'CSR_SCROLL':
        temp_query = Template(cursor_query)

    if parametros_principais[2] in db2_cmd:
        temp_query = str(temp_query.substitute(sel_fields=sel_fields,
                                               host_fields=host_fields,
                                               tabela=tabela,
                                               cond_fields=cond_fields,
                                               ))

    return temp_query


def gera_validacao(zip_group, ls_select):

    temp_query = Template(valida_statement)
    ls_valida = []
    valida_texto = []

    for idx in ls_select: # Monta Lista somente com os items selecionados para depois gerar cobol
        ls_valida.append(zip_group[idx])

    for item in ls_valida:
        if item[4] == False:
            operador = 'EQUAL SPACES'
        elif item[4][0] == 'S' or item[4][0] == '9':
            operador = 'NOT NUMERIC OR EQUAL ZEROES'
        else:
            operador = 'EQUAL SPACES'

        valida_texto.append(str(temp_query.substitute(variavel=item[3],
                                                      operador=operador)))

    return valida_texto

#from file_handler import carregar_arquivo_em_memoria
#texto = carregar_arquivo_em_memoria('C:\\Users\\joaol\\ws_kdz150\\sigla-mainframe_ORIGINAL150\\zOSsrc\\copybook\\ATCKRSEG.cpy')
#zipado = capture_cobol_definitions(texto)

# lista = verifica_prefixo_variaveis(zipado)
# retira_prefixo_variavel(zipado, lista)


#for item in zipado:
#    print(item)

# db2 = lista_db2_var,lista_db2_def, lista_varchar, lista_cobol_var,lista_cobol_def
# file= Nr, nm_var, def, in

# file= 'X', Nr, in, nm_var, def