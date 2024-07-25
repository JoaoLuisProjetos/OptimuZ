
from configurations import monta_file_saida, monta_file_entrada, lista_tp_cmd, lista_tp_query
from file_handler import consome_arquivo_template, escreve_arquivo_saida
from content_handler import gerar_campos_selecionados, monta_move_host, gera_declaracao_variaveis, monta_template, \
    gera_validacao
import sys
import subprocess


def gerar_cobol_dcl(lista_select, lista_cond, zip_groups, parametros_principais, local_cobol, local_gera, tabela, lbe):

    """ Monta os campos selecionados """
    sel_fields, host_fields, cond_fields, move_cond, move_host, declarative = \
        gerar_campos_selecionados(lista_select, lista_cond, zip_groups, parametros_principais)

    if parametros_principais[1] == 'SQL':
        temp_code = ''

    if parametros_principais[1].split()[0] == 'COBOL':

        """ Carrega Cobol Modelo"""
        file1 = monta_file_entrada(parametros_principais, local_cobol)

        """ Consome arquivo de entrada """
        try:
            temp_code = consome_arquivo_template(file1, parametros_principais, move_cond, move_host,  \
                                                 lista_tp_cmd, lista_tp_query, host_fields)
        except FileNotFoundError:
            error = 'Arquivo ' + file1 + ' não encontrado'
            lbe.configure(text=error)

    """ Seleciona correspondete para montar geração """
    temp_query = monta_template(parametros_principais, sel_fields, host_fields, tabela, cond_fields)

    """ Escreve arquivo de saida e abre-o no notepad """
    file2 = monta_file_saida(parametros_principais, local_gera)

    try:
        escreve_arquivo_saida(file2, parametros_principais, temp_query, declarative, lista_tp_query, lista_tp_cmd,\
                              temp_code)

        """  abre o arquivo texto gerado  COMANDO  WINDOWS"""
        subprocess.Popen(['cmd /S /C', file2], shell=True, universal_newlines=True)

    except FileNotFoundError:
        error = 'Arquivo ' + file2 + ' não encontrado'
        lbe.configure(text=error)
    except:
        e = sys.exc_info()[0]
        lbe.configure(text=e)

    return


def gerar_cobol_dados(lista_select, zip_groups, parametros_principais, local_cobol, local_gera, tabela, lbe):

    """ Carrega Cobol Modelo"""
    file1 = monta_file_entrada(parametros_principais, local_cobol)
    move_host = monta_move_host(lista_select, zip_groups)
    declarative = gera_declaracao_variaveis(lista_select, [], zip_groups, parametros_principais[3])

    """ Consome arquivo de entrada """
    try:
        temp_code = consome_arquivo_template(file1, parametros_principais, [], move_host, lista_tp_cmd, lista_tp_query)
    except FileNotFoundError:
        error = 'Arquivo ' + file1 + ' não encontrado'
        lbe.configure(text=error)

    #import pprint
    #pprint.pprint(temp_code)

    """ Seleciona correspondete para montar geração """
    #temp_query = monta_template(parametros_principais, lista_select, ' ', tabela, ' ') TODO

    """ Escreve arquivo de saida e abre-o no notepad """
    file2 = monta_file_saida(parametros_principais, local_gera)

    try:
        escreve_arquivo_saida(file2, parametros_principais, '\n', declarative, lista_tp_query, lista_tp_cmd,\
                              temp_code)
        """  abre o arquivo texto gerado  COMANDO  WINDOWS"""
        subprocess.Popen(['cmd /S /C', file2], shell=True, universal_newlines=True)

    except FileNotFoundError:
        error = 'Arquivo ' + file2 + ' não encontrado'
        lbe.configure(text=error)
    except:
        e = sys.exc_info()[0]
        lbe.configure(text=e)

    return


def gerar_validacao_campos(lista_select, zip_groups, parametros_principais, local_cobol, local_gera, tabela, lbe):

    """ Seleciona correspondete para montar geração """
    temp_query = gera_validacao(zip_groups, lista_select)

    """ Escreve arquivo de saida e abre-o no notepad """
    file2 = monta_file_saida(parametros_principais, local_gera)

    try:
        escreve_arquivo_saida(file2, parametros_principais, temp_query, [], lista_tp_query, lista_tp_cmd, [])
        """  abre o arquivo texto gerado  COMANDO  WINDOWS"""
        subprocess.Popen(['cmd /S /C', file2], shell=True, universal_newlines=True)

    except FileNotFoundError:
        error = 'Arquivo ' + file2 + ' não encontrado'
        lbe.configure(text=error)
    except:
        e = sys.exc_info()[0]
        lbe.configure(text=e)

    return

