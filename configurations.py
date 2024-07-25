
from os import getcwd, listdir
from content_handler import RemoveRepetidosLista, agrupar_comando_em_linha, capture_cobol_definitions
from file_handler import carregar_dclgen, carregar_arquivo_em_memoria

version = "1.0"

""" ===== Tamanho da Janela de Programa ===== """
from screeninfo import get_monitors
#print(get_monitors())
monitor_principal = get_monitors()[0]
height = monitor_principal.height
width = monitor_principal.width
screen_size = str(round(width * 0.3)) + 'x' + str(round(height * 0.92)) + '-1+1'

print('Monitor Size   (width=' + str(width) + ', height=' + str(height) + ')' )
print('App Screen Size(' + str(screen_size) + ')')
""" 
*-----------------------------------------------*
     Parametros de geração de Código
*-----------------------------------------------*"""

tipos_de_arquivo = ['.txt', '.cbl', ]
file_type = tipos_de_arquivo[1]

lista_tp_codigo = ['COBOL c/ DB2', 'COBOL', 'SQL', ]
lista_tp_query = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'SUM', 'COUNT', 'CURSOR', 'CSR_SCROLL', 'VALIDAR',]
lista_tp_cmd = ['VALIDAR', 'READ', 'WRITE',] #  'CALL',
dict_sigla_x_book = {}
dict_alias = {}


local_path = getcwd()
local_cobol = local_path + '\\cbl'
local_gera = local_path + '\\codigo'

""" 
*-----------------------------------*
              PARMS (*Options)
*-----------------------------------*
Sistema         = 0
Linguagem       = 1
Tipo de Comando = 2 
Nome do Arquivo = 3
Tipo de Arquivo = 4 
*-----------------------------------*"""
parametros_principais = []

""" Branch para atualização dos caminhos de pastas """
"""  
------------------------------------
Os Path para montagem da arvore (fisica!!!)
------------------------------------
          +--- Root ----+
          |      |      |
     sistemas   cbl     codigo
         |    (Skel)   (Saidas)
       pastas
     (Dados)   
------------------------------------"""
caminho_fisico_de_pastas = False

if caminho_fisico_de_pastas:

    local_db2 = "\\db2"
    local_area = "\\area"
    local_sis = local_path + "\\sistemas\\"

    """ Procura todas as pastas de sistemas"""
    lista_sistemas = [file for file in listdir(local_sis)]

    for sistema in lista_sistemas:
        lista_arquivos_desta_pasta = [file for file in listdir(local_sis + sistema)]
        dict_sigla_x_book.update({sistema: lista_arquivos_desta_pasta})
else:
    """  
    ------------------------------------
    Os Path para montagem da arvore de arquivos do app (LAZY!!!)
    ------------------------------------
              +--- Root ----+
              |      |      |
         copybooks  cbl     codigo
     (Membros cpy)  (Skel)   (Saidas)
    ------------------------------------"""

    """ Procura nas pasta copybook na area local do projeto"""
    local_sis = local_path + "\\copybook"
    local_sis = 'C:\\Users\\joaol\\ws_kdz\\sigla-mainframe_ORIGINAL\\zOSsrc\\copybook'
    print('local_sis', local_sis)
    lista_books = [file for file in listdir(local_sis)]

    lista = []
    for file in lista_books:
        if file.endswith('.cpy'):
            lista.append(file)
    lista_books = lista

    lista_books = [file for file in lista_books ]
    lista_siglas = [file[0:3] for file in listdir(local_sis)]
    zip_siglas = list(zip(lista_siglas, lista_books))

    lista_infra = ['DB2', 'IIB', 'HLP', '_ma', 'ALM', 'BDD', 'DBU']
    lista_sistemas = []
    lista_books_sigla = []
    sigla_ant = ''

    """ Classifica todos os arquivos em SIGLAS e inclui programas em formato dict[SIGLA]"""
    #print(lista_books)
    for file in lista_books:
        #print('arquivo:', file )
        sigla = file[0:3]

        #Ler as 3 iniciais do arquivo para montar a lista de Siglas disponiveis
        if sigla not in lista_sistemas and \
           sigla not in lista_infra:
            lista_sistemas = lista_sistemas + [sigla]
            #print('add sigla:', sigla)

        #caso a mude a sigla, grava a lista de programas no dicionario
        if sigla_ant != sigla and sigla_ant != '':
            dict_sigla_x_book.update({sigla_ant: lista_books_sigla})
            #print('atualiza',file, '-', sigla ,'sigla_ant', sigla_ant)
            #print('ini lista_books_sigla', lista_books_sigla )
            lista_books_sigla = []
            lista_books_sigla.append(file)

        if sigla == sigla_ant\
            or sigla_ant == '':
            lista_books_sigla.append(file)
            #print('add book:', file, '-', sigla)
        sigla_ant = sigla

    lista_sistemas.sort()

    """Inclui as books unicas que ficaram de fora do algoritmo anterior"""
    for file in lista_books:
        sigla = file[0:3]

        try:
            if dict_sigla_x_book[sigla] == []:
                programa = [file]
                dict_sigla_x_book.update({sigla: programa})
        except KeyError:
            if sigla in lista_siglas:
                sigla_eh_chave = True
            else:
                sigla_eh_chave = False
            print('Erro ao tentar incluir sigla/programa: ',file,\
                  'Sigla Cadastrada: ', sigla)

    '''******'''
    lista_sistemas = RemoveRepetidosLista(lista_sistemas)


""" Monta caminho do arquivo de entrada """
def monta_file_entrada(parametros_principais, file_path):

    if parametros_principais[2] in ('INSERT', 'UPDATE', 'DELETE', 'SUM', 'COUNT'):  # Nao inserir 'CURSOR'
        file_path = file_path + '\\CRUD'
    else:
        file_path = file_path + '\\' + parametros_principais[2]

    return file_path


""" Monta caminho do arquivo de saida """
def monta_file_saida(parametros_principais, file_path):
    file_path = file_path + '\\' + parametros_principais[3] + '_' + parametros_principais[2] + file_type

    return file_path

def carrega_arrays_de_arquivos_tabs_dados_cmds():

    # Divide os membros presentes na lista em duas listas de programas
    # Lista Books DCLs e Demais books de dados
    lista_book_dados = []
    lista_book_dcl = []

    # Carrega lista de membros a ser apresentada na tela pré geração
    membros = dict_sigla_x_book[parametros_principais[0]]

    # Valida os membros
    for membro in membros:
        file_path = local_sis + '\\' + membro
        valida_arquivo = carregar_dclgen(file_path, "V")
        # print('filepath ' , file_path)
        # print('valida_arquivo ' , valida_arquivo)
        if valida_arquivo == 'Não é DCLGEN!':
            lista_book_dados.append(membro)
        else:

            lista_book_dcl.append(membro)

    # Repassa lista de comandos de geração de codigo
    if parametros_principais[1] == 'COBOL':
        lista_cmd_ger = lista_tp_cmd
    else:
        lista_cmd_ger = lista_tp_query

    return lista_book_dados, lista_book_dcl, lista_cmd_ger


def carrega_items_seleçao_dados(file):


    texto = carregar_arquivo_em_memoria(file)
    texto = agrupar_comando_em_linha(texto)
    items_arquivo = capture_cobol_definitions(texto) # zip(lista_cobol_lvl, lista_cobol_var, lista_cobol_def, lista_casos_esp)

    return items_arquivo
