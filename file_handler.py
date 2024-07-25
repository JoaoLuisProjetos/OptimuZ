
from re import sub
from string import Template

def carregar_dclgen(file: str ,operacao: str ='G'):

    # print('* Arquivo de Entrada:', file)

    """Parametros adicionados para reuso:
    V - Validar se o arquivo é uma DCLGEN
    G - Gerar código COBOL
    """

    lista_db2_var=[]; lista_db2_def=[]; lista_cobol_var=[]; lista_cobol_def=[]; tabela_include = ''
    nivel_de_estruturas=['10','49']; lista_varchar=[]; nomes_varchar=['-LEN','TEXT']; names=''; i=0; p=0

    try:
        # print('vai abrir')
        with open(file,"r")as arquivo_entrada:
            #print('abriu')
            for l in arquivo_entrada:
                # print('line ', l)

                i +=1
                l = '      ' + l[6:80]

                #print(l,'\nposicao7',l[6])

                if 'NAMES(' in l:
                    names = l[l.index('(')+1:l.index(')')]

                if "*" != l[6] and len(l.split()) != 0:

                    if ('EXEC' in l)\
                    and ('EXEC' in l)\
                    and ('DECLARE' in l):
                        p=3
                        parte_leitura = 'DB2'
                        split_line  = l.split()
                        nome_tab_db2 = split_line[3]

                    if 'END-EXEC' in l:
                        parte_leitura = 'CBL'

                    if (parte_leitura == 'DB2')\
                    and ('DECLARE' not in l)\
                    and ('END-EXEC' not in l):
                        split_line  = l.split()

                        if 'VARCHAR' in l:
                            fl_vc = True
                            lista_varchar.append(fl_vc)
                        else:
                            fl_vc = False
                            lista_varchar.append(fl_vc)

                        if split_line[0] == '(':
                            lista_db2_var.append(split_line[1])
                            lista_db2_def.append(sub(r'[?|$|.|!]',r'',' '.join(split_line[2:])))
                        else:
                            lista_db2_var.append(split_line[0])
                            lista_db2_def.append(sub(r'[?|$|.|!|,]',r'',' '.join(split_line[1:])))

                    if (parte_leitura == 'CBL'):
                        split_line  = l.split()

                        if split_line[0] == '01':
                            tabela_include = (split_line[1])[:-1]

                        if split_line[0] in nivel_de_estruturas[0]:
                            split_line[1] = split_line[1].replace(names,'')
                            lista_cobol_var.append(sub(r'[?|$|.|!]',r'',''.join(split_line[1])))

                        if 'PIC' in l and nomes_varchar[0] not in split_line:
                            lista_cobol_def.append(sub(r'[?|$|.|!|,]',r'',' '.join(split_line[(split_line.index('PIC') + 1):])))

                    elif (split_line[0] in nivel_de_estruturas[1]) and nomes_varchar[0] not in l:
                        if 'PIC' in l and split_line[1][-4:] in nomes_varchar[1]:
                            lista_cobol_def.append(sub(r'[?|$|.|!]', r'', ' '.join(split_line[(split_line.index('PIC') + 1):])))

        """ Corrige diferenca de quantidade quando é Varchar"""
        for i in range(len(lista_varchar)):
            if lista_varchar[i] == True:
                lista_cobol_def.pop(i)

        #print('Nome DB2:', nome_tab_db2,'\nPref DB2:', names,'\nInclude :', tabela_include)
        #print('var DB2:', len(lista_db2_var), lista_db2_var,'\nDef DB2:', len(lista_db2_def), lista_db2_def)
        #print('Flag DB2:', len(lista_varchar), lista_varchar,'\nNome COB:', len(lista_cobol_var), lista_cobol_var,'\nDef COB:',\
        #len(lista_cobol_def), lista_cobol_def)

    except:
        return ('Não é DCLGEN!')

    if operacao == 'V':
        if nome_tab_db2:
            return nome_tab_db2

    elif operacao == 'G':
        groups = zip(lista_db2_var,lista_db2_def, lista_varchar, lista_cobol_var, lista_cobol_def)
        zip_groups = list(groups)

        return names, nome_tab_db2,tabela_include, zip_groups
#n0, n1, n2, zip_groups = carregar_dclgen('C:/Users/e_jlnascimento/Desktop/BATCH-CODES_v20180910/DB2/DCLGEN/SIART/ARTV001')
#print(n0,'\n',n1,'\n',n2,'\n',zip_groups)


def consome_arquivo_template(file1, parametros_principais, move_cond, move_host, lista_tp_cmd, lista_tp_query,\
                             host_fields=' '):

    linhas_codigo = []
    arquivo = parametros_principais[3].split('.')[0]

    with open(file1, "r", encoding='utf-8')as arquivo_entrada:
        for linha in arquivo_entrada:
           linhas_codigo.append(linha)

    temp_code = ''.join(linhas_codigo)
    temp_code = Template(temp_code)

    if parametros_principais[2] in lista_tp_query:
        temp_code = temp_code.substitute(tabela=arquivo,
                                         move_condition=move_cond,
                                         move_host=move_host,
                                         crud=parametros_principais[2],
                                         fetch=host_fields,
                                         erro_db2=' ',
                                            )

    elif parametros_principais[2] in lista_tp_cmd:

        if parametros_principais[2] == 'READ':
            in_out = 'INPUT'

            temp_code = temp_code.substitute(arquivo=arquivo,
                                         move_condition=move_host,
                                         in_out=in_out,
                                         trecho_valida=[]
                                            )

        elif parametros_principais[2] == 'WRITE':
            in_out = 'OUTPUT'

            temp_code = temp_code.substitute(arquivo=arquivo,
                                         move_condition=move_host,
                                         in_out=in_out,
                                         #trecho_valida=[]
                                            )

    temp_code = temp_code.splitlines(True)

    return temp_code


def escreve_arquivo_saida(file2, parametros_principais, temp_query, declarative, lista_tp_query, \
                          lista_tp_cmd, temp_code='', trecho_valida=' '):

    with open(file2, "w+", encoding='utf-8')as arquivo_saida:
        # arquivo_saida.write(linhas_codigo)
        if parametros_principais[1] == 'SQL' or parametros_principais[2] == 'VALIDAR':
            for linha in temp_query:
                arquivo_saida.write(linha)

        else:
            #parametros_principais[1].split()[0] == 'COBOL':
            for linha in declarative:
                arquivo_saida.write(linha)
            for linha in temp_code:
                if parametros_principais[2] in lista_tp_query:
                    linha = linha.replace('(QUERY)', temp_query)
                elif parametros_principais[2] in lista_tp_cmd:
                    linha = linha.replace('(trecho_valida)', trecho_valida)
                arquivo_saida.write(linha)

    return


def carregar_arquivo_em_memoria(arquivo_entrada): # Carrega arquivo de texto em memoria em formato array = []

    linhas_de_texto = []

    with open(arquivo_entrada, "r", encoding='utf-8')as arquivo_entrada:
        for linha in arquivo_entrada:
            linhas_de_texto.append(linha)

    return linhas_de_texto
