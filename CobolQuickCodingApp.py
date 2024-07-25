

"""CRLF"""

""" =================== Python Packages ================="""
import tkinter as tk
from tkinter import font as tkfont
import subprocess
from os import getcwd
""" =================== Python Packages ================="""

""" ========== Funções/Módulos do Projeto ============= """
from configurations import screen_size, lista_sistemas, lista_tp_codigo,  parametros_principais, \
    local_sis, local_cobol, local_gera, caminho_fisico_de_pastas, carrega_arrays_de_arquivos_tabs_dados_cmds, \
    local_path, carrega_items_seleçao_dados
from gen_head import gerar_cobol_dcl, gerar_cobol_dados, gerar_validacao_campos
from file_handler import carregar_dclgen
""" ========== Funções do Projeto ============= """

app_title = "OptimuZ - COBOL - Author: João Luis Pasquarelli"

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

class CobolQuickCodingApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title_font = tkfont.Font(family='Courier',
                                      size=18,
                                      weight="bold",
                                      slant="italic")
        self.geometry(screen_size)
        icon_path = getcwd() + '\\img\\favicon.ico'
        self.iconbitmap(icon_path)
        self.title(app_title)

        container = tk.Frame(self, background='black')
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (TelaSistemas, TelaComandos, TelaSeleçao,):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("TelaSistemas")

    def recarrega_tela_2(self, page_name):
        self.frames[page_name].lb.delete(0, tk.END)
        #print('local_path', local_path,'\noptions', parametros_principais)

        # inicializa e Preenche a LB select de Tabelas
        lista_arquivos = []

        tmp_lista_book_dados, tmp_lista_book_dcl, tmp_lista_cmd_ger,  = carrega_arrays_de_arquivos_tabs_dados_cmds()

        #TODO melhorar esta parametrizacao
        if parametros_principais[1] == 'COBOL':
            lista_arquivos = tmp_lista_book_dados
        elif parametros_principais[1] == 'COBOL c/ DB2'\
            or parametros_principais[1] == 'SQL':
            lista_arquivos = tmp_lista_book_dcl

        # Caso lista vazia apresenta erro e mantem na tela atual
        if lista_arquivos == []:
            self.frames['TelaSistemas'].lbe.configure(text=parametros_principais[0] + ' ' + parametros_principais[1] + ' vazio')
            parametros_principais.pop()
            parametros_principais.pop()
            self.show_frame("TelaSistemas")
        else:
            for book in lista_arquivos:
                self.frames[page_name].lb.insert(tk.END, book)

            #Testa se já existem Radiobuttons dentro do container1 da tela e remove para adicionar novamente
            lista_widgets = self.frames[page_name].container1.pack_slaves()
            count = 0
            for widget in lista_widgets:
                count += 1
                if count > 1:
                    widget.destroy()

            for cmd in tmp_lista_cmd_ger:
                tk.Radiobutton(self.frames[page_name].container1,
                               text=cmd,
                               value=cmd,
                               selectcolor='green',
                               background='black',
                               foreground='white',
                               font='Courier',
                               variable=self.frames[page_name].tp_query_selecionado,
                               indicatoron=False, ).pack(fill='x')

    def recarrega_tela_3(self, page_name):
        self.frames[page_name].lb1.delete(0, tk.END)
        self.frames[page_name].lb2.delete(0, tk.END)

        try:
            if caminho_fisico_de_pastas == True:
                file = local_sis + '\\' + parametros_principais[0] + '\\' + parametros_principais[3]
            else:
                file = local_sis + '\\' + parametros_principais[3]

            """  abre o arquivo texto selecionado  COMANDO  WINDOWS"""
            subprocess.Popen(['cmd /S /C', file], shell=True, universal_newlines=True)

            if parametros_principais[1] == 'COBOL' or parametros_principais[1] == 'VALIDAR':
                # zip(lista_cobol_lvl, lista_cobol_var, lista_cobol_def, lista_casos_esp)
                items_arquivo = carrega_items_seleçao_dados(file)
                for item in items_arquivo:
                    self.frames[page_name].lb1.insert(tk.END, str(item[1]) + ' ' + item[3])

                self.frames[page_name].zip_groups = items_arquivo
                self.frames[page_name].names = ' '
                self.frames[page_name].arquivo = ' '
                self.frames[page_name].include = ' '

            else:
                #print('file --> ', file)
                names, n_tb_db2, inc, zip_groups = carregar_dclgen(file)
                # print(names, n_tb_db2,inc, zip_groups)

                for item in zip_groups:
                    self.frames[page_name].lb1.insert(tk.END, item[0])
                    self.frames[page_name].lb2.insert(tk.END, item[0])

                self.frames[page_name].zip_groups = zip_groups
                self.frames[page_name].names = names
                self.frames[page_name].arquivo = n_tb_db2
                self.frames[page_name].include = inc



        except FileNotFoundError:
            error = 'Arquivo ' + file + ' não encontrado'
            self.frames[page_name].lbe.configure(text=error)


    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

        if page_name == "TelaComandos":
            self.recarrega_tela_2(page_name)

        if page_name == "TelaSeleçao":
            self.recarrega_tela_3(page_name)


class TelaSistemas(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.container_erro = tk.Frame(self, background='black')
        self.sistema_selecionado = tk.StringVar()
        self.codigo_selecionado = tk.StringVar()
        self.container1 = tk.Frame(self, background='black')
        self.container2 = tk.Frame(self, background='black')
        self.container3 = tk.Frame(self, background='black')
        self.container4 = tk.Frame(self, background='black')
        self.container_erro.pack(fill='both', expand=True)
        self.container1.pack(fill='both', expand=True)
        self.container2.pack(fill='both', expand=True)
        self.container3.pack(fill='both', expand=True)
        self.container4.pack(fill='both', expand=True)

        self.lbe = tk.Label(self.container_erro,
                            foreground='red',
                            background='black',
                            text='  ',
                            font='Courier',
                            width=26,
                            height=3, )
        self.lbe.pack(fill='both')

        self.lb1 = tk.Label(self.container1,
                            background='black',
                            foreground='white',
                            text='Sistema:',
                            font='Courier',
                            width=26,
                            height=3, )
        self.lb1.pack(fill='both')

        if caminho_fisico_de_pastas == False:
            self.lb1 = tk.Listbox(self.container1, exportselection=0)
            self.lb1.pack(side=tk.LEFT, expand=True, fill="both")
            self.sb1 = tk.Scrollbar(self.container1)
            self.sb1.pack(side=tk.RIGHT, fill="y")
            self.sb1.configure(command=self.lb1.yview)
            self.lb1.configure(yscrollcommand=self.sb1.set, font='Courier')

            for sistema in lista_sistemas:
                self.lb1.insert(tk.END, sistema)
        else:
             for sistema in lista_sistemas:
                tk.Radiobutton(self.container1,
                               text=sistema,
                               value=sistema,
                               background='black',
                               selectcolor='black',
                               foreground='white',
                               font='Courier',
                               variable=self.sistema_selecionado,
                               indicatoron=False, ).pack(fill='x')

        self.lb2 = tk.Label(self.container2,
                            background='black',
                            foreground='white',
                            text='Tipo de Código:',
                            font='Courier',
                            width=26,
                            height=3, )
        self.lb2.pack(fill='both')

        for codigo in lista_tp_codigo:
            tk.Radiobutton(self.container2,
                           text=codigo,
                           value=codigo,
                           selectcolor='green',
                           background='black',
                           foreground='white',
                           font='Courier',
                           variable=self.codigo_selecionado,
                           indicatoron=False, ).pack(fill='x')

        self.lb4 = tk.Label(self.container4,
                            background='black',
                            foreground='white',
                            font='Courier',
                            width=26,
                            height=3, )
        self.lb4.pack(fill='both')

        self.botao = tk.Button(self.container4,
                               font='Courier',
                               text='Prosseguir',
                               background='black',
                               foreground='white')
        self.botao.bind("<Button-1>", self.prosseguir)
        self.botao.pack(fill='both', side='bottom')

    def prosseguir(self, event):

        if caminho_fisico_de_pastas:
            local_sistema = self.sistema_selecionado.get()
        else:
            sel = self.lb1.curselection()
            try:
                local_sistema = lista_sistemas[sel[0]]
            except IndexError:
                self.lbe.configure(text='Selecione um sistema')
        local_cod = self.codigo_selecionado.get()

        if local_sistema not in lista_sistemas:
            self.lbe.configure(text='Sistema invalido')
        elif local_cod not in lista_tp_codigo:
            self.lbe.configure(text='Tipo de Código invalido')
        else:
            self.lbe.configure(text=' ')
            parametros_principais.append(local_sistema)
            parametros_principais.append(local_cod)
            self.controller.show_frame("TelaComandos")


class TelaComandos(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.container_erro = tk.Frame(self, background='black')
        self.container1 = tk.Frame(self, background='black')
        self.container2 = tk.Frame(self, background='black')
        self.container3 = tk.Frame(self, background='black')
        self.container_erro.pack(fill='both', expand=True)
        self.container1.pack(fill='both', expand=True)
        self.container2.pack(fill='both', expand=True)
        self.container3.pack(fill='both', expand=True)
        self.controller = controller
        self.tp_query_selecionado = tk.StringVar()

        self.lbe = tk.Label(self.container_erro,
                            foreground='red',
                            background='black',
                            text='  ',
                            font='Courier',
                            width=26,
                            height=3, )
        self.lbe.pack(fill='both')

        self.lb1 = tk.Label(self.container1,
                            background='black',
                            foreground='white',
                            text='Gerar Comando:',
                            font='Courier',
                            width=26,
                            height=3, )
        self.lb1.pack(fill='both')

        self.lb1 = tk.Label(self.container2,
                            background='black',
                            foreground='white',
                            text='Membro:',
                            font='Courier',
                            width=26,
                            height=3, )
        self.lb1.pack(fill='both')

        self.lb = tk.Listbox(self.container2)
        self.lb.pack(side=tk.LEFT, expand=True, fill="both")
        self.sb = tk.Scrollbar(self.container2)
        self.sb.pack(side=tk.RIGHT, fill="y")
        self.sb.configure(command=self.lb.yview)
        self.lb.configure(yscrollcommand=self.sb.set, font='Courier')

        self.botao1 = tk.Button(self.container3,
                                text='Prosseguir',
                                font='Courier',
                                height=1,
                                background='black',
                                foreground='white', )
        self.botao1.bind("<Button-1>", self.prosseguir)
        self.botao1.pack(fill='both')

        self.botao2 = tk.Button(self.container3,
                                text='Voltar',
                                font='Courier',
                                height=1,
                                background='black',
                                foreground='white', )
        self.botao2.bind("<Button-1>", self.voltar)
        self.botao2.pack(fill='both')

    def voltar(self, event):
        parametros_principais.pop()
        parametros_principais.pop()
        self.controller.show_frame("TelaSistemas")

    def prosseguir(self, event):
        # print(options)
        tp_query = self.tp_query_selecionado.get()
        tabela = self.lb.get(tk.ACTIVE)

        #print('--->', tp_query, tabela, lista_arquivos)
        #if tp_query not in lista_tp_query\
        #    or tp_query not in lista_tp_cmd:
        #    self.lbe.configure(text='Tipo de Comando invalido')
        #elif tabela not in lista_arquivos:
        #    self.lbe.configure(text='Tabela invalida')
        # elif tp_query == 'CURSOR' and parametros_principais[1] == 'SQL':

        if tp_query == 'CURSOR' and parametros_principais[1] == 'SQL':
            self.lbe.configure(text='Query Cursor invalido para SQL')
        else:
            parametros_principais.append(tp_query)
            parametros_principais.append(self.lb.get(tk.ACTIVE))
            self.lbe.configure(text=' ')
            self.controller.show_frame("TelaSeleçao")


class TelaSeleçao(tk.Frame):

    def __init__(self, parent, controller, names='', arquivo='', inc='', zip_groups=[]):
        tk.Frame.__init__(self, parent)

        self.zip_groups = zip_groups
        self.names = names
        self.arquivo = arquivo
        self.include = inc

        self.container_erro = tk.Frame(self, background='black')
        self.container_erro.pack(side='top', fill='both')

        self.container_lbs = tk.Frame(self, background='red', height=40)
        self.container_lbs.pack(side='top', fill='both')

        self.container_mid = tk.Frame(self, background='black', height=3)
        self.container_mid.pack(fill='both', expand=True)

        self.container_e = tk.Frame(self.container_mid, background='black', border=10)
        self.container_e.pack(fill='both', side='left', expand=True)

        self.lb_mid = tk.Label(self.container_mid, background='black', width=10)
        self.lb_mid.pack(fill='y', side='left')

        self.container_d = tk.Frame(self.container_mid, background='black', border=10)
        self.container_d.pack(fill='both', side='right', expand=True)

        self.container_bot = tk.Frame(self, background='black', height=40)
        self.container_bot.pack(side='bottom', fill='both')

        self.controller = controller
        self.tp_query_selecionado = tk.StringVar()

        self.lbe = tk.Label(self.container_erro,
                            foreground='red',
                            background='black',
                            text='  ',
                            font='Courier',
                            width=26,
                            height=3, )
        self.lbe.pack(fill='both')

        self.lb1 = tk.Label(self.container_lbs,
                            foreground='light blue',
                            background='black',
                            text='Selecione Campos',
                            font='Courier',
                            )
        self.lb1.pack(side='left', fill='both', expand=True)

        self.lb2 = tk.Label(self.container_lbs,
                            foreground='light blue',
                            background='black',
                            text='Campos Condição',
                            font='Courier',
                            )
        self.lb2.pack(side='right', fill='both', expand=True)

        self.lb1 = tk.Listbox(self.container_e, selectmode=tk.MULTIPLE, exportselection=0)
        self.lb1.pack(side=tk.LEFT, expand=True, fill="both")
        self.sb1 = tk.Scrollbar(self.container_e)
        self.sb1.pack(side=tk.RIGHT, fill="y")
        self.sb1.configure(command=self.lb1.yview)
        self.lb1.configure(yscrollcommand=self.sb1.set, font='Courier')

        self.lb2 = tk.Listbox(self.container_d, selectmode=tk.MULTIPLE, exportselection=0)
        self.lb2.pack(side=tk.LEFT, expand=True, fill="both")
        self.sb2 = tk.Scrollbar(self.container_d)
        self.sb2.pack(side=tk.RIGHT, fill="y")
        self.sb2.configure(command=self.lb2.yview)
        self.lb2.configure(yscrollcommand=self.sb2.set, font='Courier')

        self.botao_v = tk.Button(self.container_bot,
                                 text='Voltar',
                                 font='Courier',
                                 background='black',
                                 foreground='white',
                                 height=1, )
        self.botao_v.bind("<Button-1>", self.voltar)
        self.botao_v.pack(fill='both', side='left')

        self.botao_g = tk.Button(self.container_bot,
                                 text='Gerar Código',
                                 font='Courier',
                                 background='black',
                                 foreground='white',
                                 height=1, )
        self.botao_g.bind("<Button-1>", self.gerar)
        self.botao_g.pack(fill='both', side='right')

    def voltar(self, event):
        parametros_principais.pop()
        parametros_principais.pop()
        self.lbe.configure(text=' ')
        self.controller.show_frame("TelaComandos")


#=============
#  MAX EVENT
#=============

    def gerar(self, event):
        lista_esquerda = self.lb1.curselection()
        lista_direita = self.lb2.curselection()

        if parametros_principais[2] == 'VALIDAR':
            gerar_validacao_campos(lista_esquerda, self.zip_groups, parametros_principais,
                     local_cobol, local_gera, self.arquivo, self.lbe)
        elif parametros_principais[1] == 'COBOL':
            gerar_cobol_dados(lista_esquerda, self.zip_groups, parametros_principais,
                     local_cobol, local_gera, self.arquivo, self.lbe)
        else:
            gerar_cobol_dcl(lista_esquerda, lista_direita, self.zip_groups, parametros_principais,
                     local_cobol, local_gera, self.arquivo, self.lbe)



if __name__ ==  "__main__":

    app = CobolQuickCodingApp()
    app.mainloop()
