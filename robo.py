import urllib.request
import socket
import tkinter as tk
import requests
from io import BytesIO
import os
from urllib.parse import urlparse
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import random
from datetime import datetime, timedelta
import json
from config_manager import app_config
import threading
import time


# Configuração do tema dark
DARK_BG = "#2a2a2a"
DARK_FG = "#ffffff"
DARK_ENTRY = "#3a3a3a"
DARK_BUTTON = "#3a3a3a"
DARK_SELECT = "#4a4a4a"
DARK_HOVER = "#5a5a5a"

class LoadingScreen:
    def __init__(self, root):
        self.producao = False
        self.root = root
        self.root.title("Carregando...")
        self.root.geometry("400x200")
        self.root.configure(bg=DARK_BG)
        self.center_window(400, 200)
        
        self.create_widgets()
        self.start_loading()
    
    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        self.main_frame = tk.Frame(self.root, bg=DARK_BG)
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        self.loading_label = tk.Label(
            self.main_frame,
            text="Carregando configurações...",
            font=("Arial", 12),
            fg=DARK_FG,
            bg=DARK_BG
        )
        self.loading_label.pack(pady=(0, 20))
        
        self.progress = ttk.Progressbar(
            self.main_frame,
            orient='horizontal',
            mode='indeterminate',
            length=300
        )
        self.progress.pack()
        
        self.status_label = tk.Label(
            self.main_frame,
            text="Verificando conexão com a internet...",
            font=("Arial", 9),
            fg=DARK_FG,
            bg=DARK_BG
        )
        self.status_label.pack(pady=(20, 0))
    
    def start_loading(self):
        self.progress.start()
        # Inicia o carregamento em uma thread separada
        threading.Thread(target=self.load_configurations, daemon=True).start()
    
    def load_configurations(self):
        """Verifica conexão e carrega configurações da API"""
        try:
            # Verifica conexão com a internet
            self.update_status("Verificando conexão com a internet...")
            if not self.check_internet_connection():
                self.show_error("Sem conexão com a internet. Verifique sua rede.")
                return
            if self.producao:
                time.sleep(1)
            # Simula requisição à API para obter configurações
            self.update_status("Conectando ao servidor...")
            config_from_api = self.get_config_from_api()
            
            if self.producao:
                time.sleep(2)
            if config_from_api:
                # Atualiza configurações locais
                self.update_status("Atualizando configurações locais...")
                self.update_local_config(config_from_api)
                if self.producao:
                    time.sleep(2)

                # Carrega imagem do logo se existir na API
                if not os.path.exists(app_config.get('local_logo')):
                    self.update_status("Baixando recursos...")
                    self.download_and_save_image(app_config.get('api').replace('/api/v1', '') + 'storage/' + app_config.get('logo'), None, 'logo')
                    if self.producao:
                        time.sleep(3)
                
                self.update_status("Configurações carregadas com sucesso!")
                self.progress.stop()
                if self.producao:
                    time.sleep(1)
                self.root.after(1000, self.open_login_screen)
            else:
                self.show_error("Não foi possível carregar as configurações do servidor.")
        
        except Exception as e:
            self.show_error(f"Erro durante o carregamento: {str(e)}")
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def show_error(self, message):
        self.progress.stop()
        self.status_label.config(text=message, fg="#ff5555")
        self.root.after(3000, self.root.destroy)
    
    def check_internet_connection(self):
        try:
            # Tentamos acessar um servidor confiável com timeout de 5 segundos
            urllib.request.urlopen(app_config.get('site'), timeout=15)
            return True
        except (urllib.request.URLError, socket.timeout):
            return False
    
    def get_config_from_api(self):
        try:
            info = requests.get(app_config.get('api') + 'tenant/', headers={'token': app_config.get('token')}).json()
            info = info['setting']

            symbols = requests.get(app_config.get('api') + 'get-symbols/', headers={'token': app_config.get('token')}).json()
            info['symbols'] = symbols

            return info
        
        except Exception as e:
            print(f"Erro ao obter configurações da API: {e}")
            return None
    
    def update_local_config(self, api_config):
        """Atualiza configurações locais com base na API"""
        try:
            app_config.set_config('name', "Robo (" + api_config['name'] + ")")
            app_config.set_config('dominio', api_config['dominio'])	
            app_config.set_config('min_deposit', api_config['min_deposit'])	
            app_config.set_config('min_deposit', api_config['min_deposit'])	
            app_config.set_config('max_deposit', api_config['max_deposit'])	
            app_config.set_config('min_withdrawal', api_config['min_withdrawal'])	
            app_config.set_config('max_withdrawal', api_config['max_withdrawal'])	
            app_config.set_config('min_bet', api_config['min_bet'])	
            app_config.set_config('max_bet', api_config['max_bet'])	
            app_config.set_config('fav_icon', api_config['fav_icon'])	
            app_config.set_config('link_support', api_config['link_support'])	
            app_config.set_config('logo', api_config['logo'])
            app_config.set_config('symbols', api_config['symbols'])
            app_config._save_config()
            return True
        except Exception as e:
            print(f"Erro ao atualizar configurações locais: {e}")
            return False
    
    def download_and_save_image(self, url, save_path=None, filename=None, quality=85):
        """
        Baixa uma imagem da internet e salva no sistema de arquivos
        
        Parâmetros:
        - url: URL da imagem a ser baixada
        - save_path: Diretório onde a imagem será salva (opcional)
        - filename: Nome do arquivo (sem extensão) (opcional)
        - quality: Qualidade para imagens JPEG (1-100)
        
        Retorna:
        - Caminho completo do arquivo salvo ou None em caso de erro
        """
        
        try:
            # Verifica se a URL é válida
            if not url.startswith(('http://', 'https://')):
                raise ValueError("URL inválida. Deve começar com http:// ou https://")
            
            # Faz o download da imagem
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Verifica se houve erro na requisição
            
            # Determina o tipo de imagem a partir do Content-Type ou da URL
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type or url.lower().endswith(('.jpg', '.jpeg')):
                ext = '.jpg'
            elif 'png' in content_type or url.lower().endswith('.png'):
                ext = '.png'
            elif 'webp' in content_type or url.lower().endswith('.webp'):
                ext = '.webp'
            elif 'gif' in content_type or url.lower().endswith('.gif'):
                ext = '.gif'
            else:
                # Tenta determinar a extensão pelo conteúdo da imagem
                try:
                    img = Image.open(BytesIO(response.content))
                    ext = f'.{img.format.lower()}'
                except:
                    ext = '.jpg'  # Padrão
            
            # Define o nome do arquivo
            if not filename:
                # Extrai o nome do arquivo da URL se não for fornecido
                parsed = urlparse(url)
                filename = os.path.basename(parsed.path)
                if '.' in filename:
                    filename = filename.split('.')[0]
            
            # Define o diretório de salvamento
            if not save_path:
                save_path = os.getcwd()  # Diretório atual se não for fornecido
            
            # Cria o diretório se não existir
            os.makedirs(save_path, exist_ok=True)
            
            # Caminho completo do arquivo
            filepath = os.path.join(save_path, f"{filename}{ext}")
            
            # Verifica se já existe arquivo com esse nome e adiciona um número
            counter = 1
            while os.path.exists(filepath):
                filepath = os.path.join(save_path, f"{filename}_{counter}{ext}")
                counter += 1
            
            # Salva a imagem
            img = Image.open(BytesIO(response.content))
            
            if ext.lower() in ('.jpg', '.jpeg'):
                img.save(filepath, 'JPEG', quality=quality)
            elif ext.lower() == '.png':
                img.save(filepath, 'PNG', compress_level=9)
            else:
                img.save(filepath)
            
            print(f"Imagem salva com sucesso em: {filepath}")

            app_config.set_config('local_logo', filepath)
            app_config._save_config()

            return filepath
        
        except requests.exceptions.RequestException as e:
            print(f"Erro ao baixar a imagem: {e}")
        except IOError as e:
            print(f"Erro ao processar/salvar a imagem: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")
        
        return None   

    def download_logo(self, url):
        """Baixa e salva o logo da aplicação"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                img_data = response.content
                with open("logo.png", "wb") as f:
                    f.write(img_data)
                return True
        except Exception as e:
            print(f"Erro ao baixar logo: {e}")
        return False
    
    def open_login_screen(self):
        self.root.destroy()
        root = tk.Tk()
        LoginScreen(root)
        root.mainloop()

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - " + app_config.get('name'))
        self.root.geometry("400x500")
        self.root.configure(bg=DARK_BG)
        
        # Centralizar a janela
        self.center_window(400, 500)
        
        self.create_widgets()
    
    def center_window(self, width, height):
        """Centraliza a janela na tela"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg=DARK_BG, padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Logo (usando um placeholder)
        img_name = app_config.get('local_logo') if os.path.exists(app_config.get('local_logo'))  else 'logo_local.png'
        size=(150, 150)
        img = Image.open(img_name)
        img = img.resize(size, Image.LANCZOS)
        logo_img = ImageTk.PhotoImage(img)
        logo_label = tk.Label(main_frame, image=logo_img, bg=DARK_BG)
        logo_label.image = logo_img
        logo_label.pack(pady=(0, 30))
        
        # Label do título
        title_label = tk.Label(
            main_frame, 
            text=app_config.get('name'), 
            font=("Arial", 18, "bold"), 
            fg=DARK_FG, 
            bg=DARK_BG
        )
        title_label.pack(pady=(0, 20))
        
        # Frame dos campos de entrada
        entry_frame = tk.Frame(main_frame, bg=DARK_BG)
        entry_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Campo de email
        email_label = tk.Label(
            entry_frame, 
            text="Email:", 
            font=("Arial", 10), 
            fg=DARK_FG, 
            bg=DARK_BG,
            anchor='w'
        )
        email_label.pack(fill=tk.X)
        
        self.email_entry = tk.Entry(
            entry_frame, 
            font=("Arial", 12), 
            bg=DARK_ENTRY, 
            fg=DARK_FG, 
            insertbackground=DARK_FG,
            relief=tk.FLAT
        )
        self.email_entry.pack(fill=tk.X, pady=(0, 10), ipady=5)
        
        # Campo de senha
        password_label = tk.Label(
            entry_frame, 
            text="Senha:", 
            font=("Arial", 10), 
            fg=DARK_FG, 
            bg=DARK_BG,
            anchor='w'
        )
        password_label.pack(fill=tk.X)
        
        self.password_entry = tk.Entry(
            entry_frame, 
            font=("Arial", 12), 
            bg=DARK_ENTRY, 
            fg=DARK_FG, 
            show="*",
            insertbackground=DARK_FG,
            relief=tk.FLAT
        )
        self.password_entry.pack(fill=tk.X, pady=(0, 20), ipady=5)
        
        # Botão de login
        login_button = tk.Button(
            main_frame, 
            text="Acessar", 
            font=("Arial", 12, "bold"), 
            bg=DARK_BUTTON, 
            fg=DARK_FG,
            activebackground=DARK_HOVER,
            activeforeground=DARK_FG,
            relief=tk.FLAT,
            command=self.login
        )
        login_button.pack(fill=tk.X, ipady=8)
        
        # Configurar estilo para quando o mouse passa sobre o botão
        login_button.bind("<Enter>", lambda e: login_button.config(bg=DARK_HOVER))
        login_button.bind("<Leave>", lambda e: login_button.config(bg=DARK_BUTTON))
    
    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos!")
            return
        
        request_user = requests.post(app_config.get('api') + 'auth',json={'email': email, 'password': password}, headers={'token': app_config.get('token')})
        if(request_user.status_code != 200):
            messagebox.showerror("Erro", "Email ou senha incorretos!")

        user = request_user.json()
        app_config.set_config('user', user['data'])

        # Fechar a tela de login e abrir a tela principal
        self.root.destroy()
        
        root = tk.Tk()
        app = ForexTradingApp(root)
        root.mainloop()

class ForexTradingApp:      
    def __init__(self, root):
        self.root = root
        self.root.title(app_config.get('name'))
        self.root.geometry("1000x700")
        self.root.configure(bg=DARK_BG)
        
        # Centralizar a janela
        self.center_window(1000, 700)
        
        self.user_data = {
            "saldo": 0.00,
            "nome": "Carregando...",
            "sobrenome": "",
            "telefone": ""
        }

        self.create_widgets()
        self.generate_sample_data()
        self.load_user_data()  # Carrega os dados do usuário
    
    def center_window(self, width, height):
        """Centraliza a janela na tela"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg=DARK_BG)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # Frame superior (formulário + dados do usuário)
        top_frame = tk.Frame(main_frame, bg=DARK_BG)
        top_frame.pack(fill=tk.BOTH, expand=False)

        # ========== Frame do formulário (esquerda) ==========
        form_frame = tk.Frame(top_frame, bg=DARK_BG)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # Título do formulário
        title_label = tk.Label(
            form_frame, 
            text="Nova Operação", 
            font=("Arial", 14, "bold"), 
            fg=DARK_FG, 
            bg=DARK_BG,
            anchor='w'
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky='w')
        
        # Mercado (Forex symbols)
        market_label = tk.Label(
            form_frame, 
            text="Mercado:", 
            font=("Arial", 10), 
            fg=DARK_FG, 
            bg=DARK_BG,
            anchor='w'
        )
        market_label.grid(row=1, column=0, pady=(0, 5), sticky='w')
        
        self.market_var = tk.StringVar()
        # Obter os símbolos da configuração
        symbols_data = app_config.get('symbols', [])

        # Criar uma lista de labels para exibição e um dicionário para mapear label→code
        market_labels = [item["label"] for item in symbols_data]
        self.market_code_map = {item["label"]: item["code"] for item in symbols_data}
        self.market_select = ttk.Combobox(
            form_frame, 
            textvariable=self.market_var, 
            values=market_labels,
            state="readonly",
            font=("Arial", 10),
            height=10
        )
        self.market_select.grid(row=1, column=1, pady=(0, 5), sticky='ew', padx=(0, 10))
        
        # Tipo (Put/Call)
        type_label = tk.Label(
            form_frame, 
            text="Tipo:", 
            font=("Arial", 10), 
            fg=DARK_FG, 
            bg=DARK_BG,
            anchor='w'
        )
        type_label.grid(row=2, column=0, pady=(0, 5), sticky='w')
        
        self.type_var = tk.StringVar()
        type_options = ["CALL", "PUT"]
        self.type_select = ttk.Combobox(
            form_frame, 
            textvariable=self.type_var, 
            values=type_options,
            state="readonly",
            font=("Arial", 10),
            height=10
        )
        self.type_select.grid(row=2, column=1, pady=(0, 5), sticky='ew', padx=(0, 10))
        
        # Tempo de expiração
        time_label = tk.Label(
            form_frame, 
            text="Tempo:", 
            font=("Arial", 10), 
            fg=DARK_FG, 
            bg=DARK_BG,
            anchor='w'
        )
        time_label.grid(row=3, column=0, pady=(0, 5), sticky='w')
        
        self.time_var = tk.StringVar()
        time_options = ["1 minuto", "5 minutos", "10 minutos", "15 minutos", "30 minutos", "1 hora"]
        self.time_select = ttk.Combobox(
            form_frame, 
            textvariable=self.time_var, 
            values=time_options,
            state="readonly",
            font=("Arial", 10),
            height=10
        )
        self.time_select.grid(row=3, column=1, pady=(0, 5), sticky='ew', padx=(0, 10))
        
        # Data e Hora de Entrada
        entry_time_label = tk.Label(
            form_frame, 
            text="Data/Hora Entrada:", 
            font=("Arial", 10), 
            fg=DARK_FG, 
            bg=DARK_BG,
            anchor='w'
        )
        entry_time_label.grid(row=4, column=0, pady=(0, 5), sticky='w')
        
        self.entry_time_var = tk.StringVar()
        # Definir valor padrão como agora + 1 minuto
        default_time = (datetime.now() + timedelta(minutes=1)).strftime("%d/%m/%Y %H:%M")
        self.entry_time_var.set(default_time)
        
        self.entry_time_entry = tk.Entry(
            form_frame, 
            textvariable=self.entry_time_var,
            font=("Arial", 10), 
            bg=DARK_ENTRY, 
            fg=DARK_FG, 
            insertbackground=DARK_FG,
            relief=tk.FLAT
        )
        self.entry_time_entry.grid(row=4, column=1, pady=(0, 5), sticky='ew', padx=(0, 10), ipady=3)
        
        # Valor da operação
        value_label = tk.Label(
            form_frame, 
            text="Valor ($):", 
            font=("Arial", 10), 
            fg=DARK_FG, 
            bg=DARK_BG,
            anchor='w'
        )
        value_label.grid(row=5, column=0, pady=(0, 5), sticky='w')
        
        self.value_entry = tk.Entry(
            form_frame, 
            font=("Arial", 10), 
            bg=DARK_ENTRY, 
            fg=DARK_FG, 
            insertbackground=DARK_FG,
            relief=tk.FLAT
        )
        self.value_entry.grid(row=5, column=1, pady=(0, 10), sticky='ew', padx=(0, 10), ipady=3)
        
        # Botão de enviar
        submit_button = tk.Button(
            form_frame, 
            text="Enviar Operação", 
            font=("Arial", 10, "bold"), 
            bg=DARK_BUTTON, 
            fg=DARK_FG,
            activebackground=DARK_HOVER,
            activeforeground=DARK_FG,
            relief=tk.FLAT,
            command=self.submit_operation
        )
        submit_button.grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky='ew')
        
        # Configurar estilo para quando o mouse passa sobre o botão
        submit_button.bind("<Enter>", lambda e: submit_button.config(bg=DARK_HOVER))
        submit_button.bind("<Leave>", lambda e: submit_button.config(bg=DARK_BUTTON))

        # ========== Frame direito (informações do usuário) ==========
        right_frame = tk.Frame(top_frame, bg=DARK_BG, width=300, relief=tk.RAISED, bd=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        right_frame.pack_propagate(False)  # Mantém a largura fixa
        
        # Painel do Usuário
        user_panel = tk.Frame(right_frame, bg=DARK_BG, padx=10, pady=20)
        user_panel.pack(fill=tk.BOTH, expand=True)
        
        # Título do painel
        user_title = tk.Label(
            user_panel, 
            text="Informações do Usuário", 
            font=("Arial", 12, "bold"), 
            fg=DARK_FG, 
            bg=DARK_BG
        )
        user_title.pack(pady=(0, 20))
        
        # Container para os dados
        data_frame = tk.Frame(user_panel, bg=DARK_BG)
        data_frame.pack(fill=tk.X, pady=5)
        
        # Saldo
        self.saldo_label = tk.Label(
            data_frame, 
            text=f"Saldo: $0.00", 
            font=("Arial", 11), 
            fg="#4CAF50",  # Verde para saldo
            bg=DARK_BG,
            anchor='w'
        )
        self.saldo_label.pack(fill=tk.X, pady=5)
        
        # Nome
        self.nome_label = tk.Label(
            data_frame, 
            text="Nome: ", 
            font=("Arial", 10), 
            fg=DARK_FG, 
            bg=DARK_BG,
            anchor='w'
        )
        self.nome_label.pack(fill=tk.X, pady=5)
        
        # Telefone
        self.telefone_label = tk.Label(
            data_frame, 
            text="Telefone: ", 
            font=("Arial", 10), 
            fg=DARK_FG, 
            bg=DARK_BG,
            anchor='w'
        )
        self.telefone_label.pack(fill=tk.X, pady=5)
        
        # Botão de atualizar
        update_btn = tk.Button(
            user_panel, 
            text="Atualizar Dados", 
            font=("Arial", 10, "bold"), 
            bg=DARK_BUTTON, 
            fg=DARK_FG,
            activebackground=DARK_HOVER,
            activeforeground=DARK_FG,
            relief=tk.FLAT,
            command=self.load_user_data
        )
        update_btn.pack(fill=tk.X, pady=(20, 0), ipady=5)
        
        # Efeito hover no botão
        update_btn.bind("<Enter>", lambda e: update_btn.config(bg=DARK_HOVER))
        update_btn.bind("<Leave>", lambda e: update_btn.config(bg=DARK_BUTTON))

        # ========== Frame do histórico (parte inferior) ==========
        history_frame = tk.Frame(main_frame, bg=DARK_BG)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Título do histórico
        history_label = tk.Label(
            history_frame, 
            text="Histórico de Operações", 
            font=("Arial", 14, "bold"), 
            fg=DARK_FG, 
            bg=DARK_BG,
            anchor='w'
        )
        history_label.pack(fill=tk.X, pady=(0, 10))
        
        # Tabela (Treeview)
        self.tree = ttk.Treeview(
            history_frame,
            columns=("market", "type", "time", "value", "result", "entry_time", "date"),
            show="headings",
            selectmode="browse"
        )
        
        # Configurar cabeçalhos
        self.tree.heading("market", text="Mercado")
        self.tree.heading("type", text="Tipo")
        self.tree.heading("time", text="Tempo")
        self.tree.heading("value", text="Valor ($)")
        self.tree.heading("result", text="Resultado ($)")
        self.tree.heading("entry_time", text="Entrada")
        self.tree.heading("date", text="Data Operação")
        
        # Configurar largura das colunas
        self.tree.column("market", width=100, anchor='center')
        self.tree.column("type", width=80, anchor='center')
        self.tree.column("time", width=100, anchor='center')
        self.tree.column("value", width=100, anchor='center')
        self.tree.column("result", width=120, anchor='center')
        self.tree.column("entry_time", width=150, anchor='center')
        self.tree.column("date", width=150, anchor='center')
        
        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill=tk.BOTH)
        
        # Configurar estilo da Treeview para tema dark
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background=DARK_ENTRY,
                        foreground=DARK_FG,
                        rowheight=25,
                        fieldbackground=DARK_ENTRY,
                        bordercolor=DARK_BG,
                        borderwidth=0)
        style.map('Treeview', background=[('selected', DARK_HOVER)])
        
        style.configure("Treeview.Heading", 
                        background=DARK_BUTTON,
                        foreground=DARK_FG,
                        relief="flat")
        style.map("Treeview.Heading", 
                background=[('active', DARK_HOVER)])
    
    def load_user_data(self):
        try:
            response_user = requests.get(app_config.get('api') + 'user-info/' + app_config.get('user.uuid'), headers={'token': app_config.get('token')})
            if response_user.status_code != 200:
                messagebox.showerror("Erro", "Erro ao carregar os dados do usuário, informações nao atualizadas.")
                
            app_config.set_config('user', response_user.json()['data'])
            
            # Dados simulados
            simulated_data = {
                "saldo": app_config.get('user.wallet.balance'),
                "nome": app_config.get('user.name'),
                "sobrenome": app_config.get('user.last_name'),
                "telefone": f"({app_config.get('user.phone_code')}) {app_config.get('user.phone_number')}"
            }
            
            # Atualiza os dados locais
            self.user_data.update(simulated_data)
            
            # Atualiza a interface
            self.update_user_display()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar os dados: {str(e)}")
    
    def update_user_display(self):
        """Atualiza os labels com os dados do usuário"""
        self.saldo_label.config(text=f"Saldo: ${self.user_data['saldo']:,.2f}")
        self.nome_label.config(text=f"Nome: {self.user_data['nome']} {self.user_data['sobrenome']}")
        self.telefone_label.config(text=f"Telefone: {self.user_data['telefone']}")

    def generate_sample_data(self):
        """Gera dados de exemplo para a tabela"""
        '''
        markets = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD"]
        types = ["CALL", "PUT"]
        times = ["1 minuto", "5 minutos", "10 minutos", "15 minutos", "30 minutos", "1 hora"]
        
        for _ in range(20):
            market = random.choice(markets)
            op_type = random.choice(types)
            time = random.choice(times)
            value = round(random.uniform(10, 1000), 2)
            
            # Data de entrada aleatória (no passado)
            entry_time = datetime.now() - timedelta(days=random.randint(0, 7), 
                                                 hours=random.randint(0, 23),
                                                 minutes=random.randint(1, 59))
            entry_time_str = entry_time.strftime("%d/%m/%Y %H:%M")
            
            # 70% de chance de ganho, 30% de perda
            if random.random() < 0.7:
                result = round(value * random.uniform(1.1, 2.5), 2)
                result_text = f"+{result}"
            else:
                result = round(value * random.uniform(0.2, 0.9), 2)
                result_text = f"-{result}"
            
            # Data da operação (pode ser igual ou posterior à entrada)
            op_date = entry_time + timedelta(minutes=random.randint(1, int(time.split()[0]) if time != "1 hora" else 60))
            date_str = op_date.strftime("%d/%m/%Y %H:%M")
            
            self.tree.insert("", "end", values=(
                market, 
                op_type, 
                time, 
                f"${value:.2f}", 
                result_text, 
                entry_time_str,
                date_str
            ))
        '''
    
    def validate_datetime(self, datetime_str):
        """Valida se a data/hora é válida e pelo menos 1 minuto à frente"""
        try:
            input_dt = datetime.strptime(datetime_str, "%d/%m/%Y %H:%M")
            now_plus_1min = datetime.now() + timedelta(minutes=1)
            
            if input_dt < now_plus_1min:
                return False, "A data/hora de entrada deve ser pelo menos 1 minuto à frente do horário atual"
            return True, ""
        except ValueError:
            return False, "Formato de data/hora inválido. Use DD/MM/AAAA HH:MM"
    
    def submit_operation(self):
        """Valida e envia uma nova operação"""
        market = self.market_var.get()
        op_type = self.type_var.get()
        time = self.time_var.get()
        value = self.value_entry.get()
        entry_time = self.entry_time_var.get()
        
        if not all([market, op_type, time, value, entry_time]):
            messagebox.showerror("Erro", "Por favor, preencha todos os campos!")
            return
        
        # Validar data/hora de entrada
        is_valid, error_msg = self.validate_datetime(entry_time)
        if not is_valid:
            messagebox.showerror("Erro", error_msg)
            return
        
        try:
            value = float(value)
            if value <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um valor numérico válido maior que zero!")
            return
        
        # Simular resultado (70% de chance de ganho, 30% de perda)
        if random.random() < 0.7:
            result = round(value * random.uniform(1.1, 2.5), 2)
            result_text = f"+{result:.2f}"
        else:
            result = round(value * random.uniform(0.2, 0.9), 2)
            result_text = f"-{result:.2f}"
        
        # Data da operação (simulando tempo de expiração)
        time_minutes = int(time.split()[0]) if time != "1 hora" else 60
        op_date = (datetime.strptime(entry_time, "%d/%m/%Y %H:%M") + 
                  timedelta(minutes=time_minutes))
        date_str = op_date.strftime("%d/%m/%Y %H:%M")
        
        # Adicionar à tabela
        self.tree.insert("", 0, values=(
            market, 
            op_type, 
            time, 
            f"${value:.2f}", 
            result_text, 
            entry_time,
            date_str
        ))
        
        # Limpar campos (exceto data/hora que é definida para agora + 1 minuto)
        self.market_var.set('')
        self.type_var.set('')
        self.time_var.set('')
        self.value_entry.delete(0, tk.END)
        default_time = (datetime.now() + timedelta(minutes=1)).strftime("%d/%m/%Y %H:%M")
        self.entry_time_var.set(default_time)
        
        messagebox.showinfo("Sucesso", "Operação enviada com sucesso!")

# Executar a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    login_screen = LoadingScreen(root)
    root.mainloop()