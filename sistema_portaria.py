#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Portaria - Controle de Entrada e Saída
Desenvolvido para gerenciamento de visitantes e clientes
Versão 3.1 - Com Edição e Exclusão de Registros
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import re
import requests
from typing import Optional
from PIL import Image, ImageTk
import os

class SistemaPortaria:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Portaria - Controle de Acesso")
        self.root.geometry("950x800")
        self.root.resizable(True, True)
        
        # Configurar tamanho mínimo
        self.root.minsize(900, 750)
        
        # Configurar cores
        self.bg_color = "#f0f0f0"
        self.primary_color = "#2c3e50"
        self.secondary_color = "#3498db"
        self.success_color = "#27ae60"
        
        self.root.configure(bg=self.bg_color)
        
        # Lista de vendedores
        self.vendedores = [
            "THIAGO MOTA",
            "PRISCILA ARAUJO",
            "TAIS ARAUJO",
            "MARIA JULIA SOARES",
            "CLAUDINEI CRUZ",
            "ALEXANDRE",
            "JOSE ADRIANO",
            "KEVIN SILVA",
            "EROS RODRIGUES",
            "ADEMAR AURELIO",
            "ANSELMO CUNHA",
            "FERNANDA TAVARES",
            "JUNIOR",
            "DESCARGA DE MATERIAL",
            "ANDERSON ALMEIDA",
            "DOX BRASIL"
        ]
        
        # Carregar logos
        self.logo_topo = None
        self.logo_marca_dagua = None
        self.carregar_logos()
        
        # Inicializar banco de dados
        self.inicializar_banco()
        
        # Criar interface
        self.criar_interface()
    
    def carregar_logos(self):
        """Carrega os logos da empresa se existirem"""
        try:
            # Logo do topo (100x60 pixels)
            if os.path.exists('logo_topo.png'):
                img_topo = Image.open('logo_topo.png')
                img_topo = img_topo.resize((80, 60), Image.Resampling.LANCZOS)
                self.logo_topo = ImageTk.PhotoImage(img_topo)
            
            # Logo marca d'água (300x300 pixels com transparência)
            if os.path.exists('logo_marca_dagua.png'):
                img_marca = Image.open('logo_marca_dagua.png').convert('RGBA')
                img_marca = img_marca.resize((500, 500), Image.Resampling.LANCZOS)
                
                # Adicionar transparência
                alpha = img_marca.split()[3]
                alpha = alpha.point(lambda p: int(p * 0.1))  # 10% de opacidade
                img_marca.putalpha(alpha)
                
                self.logo_marca_dagua = ImageTk.PhotoImage(img_marca)
                
        except Exception as e:
            print(f"Aviso: Não foi possível carregar os logos: {e}")
        
    def inicializar_banco(self):
        """Cria o banco de dados e tabelas necessárias"""
        self.conn = sqlite3.connect('portaria.db')
        self.cursor = self.conn.cursor()
        
        # Verificar se as colunas novas existem
        self.cursor.execute("PRAGMA table_info(registros)")
        colunas_existentes = [col[1] for col in self.cursor.fetchall()]
        
        if 'registros' not in [table[0] for table in self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
            # Criar tabela com todas as colunas
            self.cursor.execute('''
                CREATE TABLE registros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_cliente TEXT NOT NULL,
                    empresa TEXT NOT NULL,
                    empresa_representada TEXT,
                    cpf TEXT NOT NULL,
                    telefone TEXT NOT NULL,
                    placa_veiculo TEXT,
                    tipo_pessoa TEXT NOT NULL,
                    vendedor TEXT NOT NULL,
                    nf_saida TEXT NOT NULL,
                    horario_entrada TEXT NOT NULL,
                    horario_saida TEXT,
                    data_registro TEXT NOT NULL,
                    cpf_valido INTEGER DEFAULT 0
                )
            ''')
        else:
            # Adicionar colunas se não existirem
            if 'placa_veiculo' not in colunas_existentes:
                self.cursor.execute('ALTER TABLE registros ADD COLUMN placa_veiculo TEXT')
            
            if 'empresa_representada' not in colunas_existentes:
                self.cursor.execute('ALTER TABLE registros ADD COLUMN empresa_representada TEXT')
        
        self.conn.commit()
        
    def criar_interface(self):
        """Cria toda a interface gráfica do sistema"""
        
        # Título com logo
        frame_titulo = tk.Frame(self.root, bg=self.primary_color, height=80)
        frame_titulo.pack(fill=tk.X)
        frame_titulo.pack_propagate(False)
        
        # Container para logo e título
        container_titulo = tk.Frame(frame_titulo, bg=self.primary_color)
        container_titulo.pack(fill=tk.BOTH, expand=True)
        
        # Logo no topo (esquerda)
        if self.logo_topo:
            label_logo_topo = tk.Label(
                container_titulo,
                image=self.logo_topo,
                bg=self.primary_color
            )
            label_logo_topo.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Título centralizado
        titulo = tk.Label(
            container_titulo,
            text="SISTEMA DE PORTARIA",
            font=("Arial", 24, "bold"),
            bg=self.primary_color,
            fg="white"
        )
        titulo.pack(side=tk.LEFT, expand=True, pady=20)
        
        # Frame principal com scroll
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Canvas e Scrollbar
        canvas = tk.Canvas(main_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        
        # Logo marca d'água no centro (se existir)
        if self.logo_marca_dagua:
            label_marca_dagua = tk.Label(
                scrollable_frame,
                image=self.logo_marca_dagua,
                bg=self.bg_color
            )
            label_marca_dagua.place(relx=0.5, rely=0.4, anchor="center")
        
        def on_frame_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.update_idletasks()
        
        scrollable_frame.bind("<Configure>", on_frame_configure)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Permitir scroll com mouse wheel
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # ===== SEÇÃO 1: DADOS DO CLIENTE =====
        self.criar_secao(scrollable_frame, "DADOS DO CLIENTE", 0)
        
        # Nome do Cliente
        self.criar_campo(scrollable_frame, "Nome do Cliente:", 1, obrigatorio=True)
        self.entry_nome = self.criar_entrada(scrollable_frame, 1)
        
        # Empresa
        self.criar_campo(scrollable_frame, "Empresa:", 2, obrigatorio=True)
        self.entry_empresa = self.criar_entrada(scrollable_frame, 2)
        
        # Empresa Representada
        self.criar_campo(scrollable_frame, "Empresa Representada:", 3, obrigatorio=True)
        self.entry_empresa_representada = self.criar_entrada(scrollable_frame, 3)
        
        # CPF
        self.criar_campo(scrollable_frame, "CPF:", 4, obrigatorio=False)
        cpf_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
        cpf_frame.grid(row=4, column=1, sticky="w", pady=5, padx=(0, 10))
        
        self.entry_cpf = tk.Entry(cpf_frame, font=("Arial", 11), width=20)
        self.entry_cpf.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_cpf.bind('<KeyRelease>', self.formatar_cpf)
        
        btn_validar_cpf = tk.Button(
            cpf_frame,
            text="Validar CPF",
            command=self.validar_cpf,
            bg=self.secondary_color,
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        btn_validar_cpf.pack(side=tk.LEFT)
        
        self.label_cpf_status = tk.Label(
            cpf_frame,
            text="",
            font=("Arial", 9),
            bg=self.bg_color
        )
        self.label_cpf_status.pack(side=tk.LEFT, padx=10)
        
        # Telefone
        self.criar_campo(scrollable_frame, "Telefone:", 5, obrigatorio=True)
        self.entry_telefone = self.criar_entrada(scrollable_frame, 5)
        self.entry_telefone.bind('<KeyRelease>', self.formatar_telefone)
        
        # Placa do Veículo
        self.criar_campo(scrollable_frame, "Placa do Veículo:", 6, obrigatorio=True)
        placa_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
        placa_frame.grid(row=6, column=1, sticky="w", pady=5, padx=(0, 10))
        
        self.entry_placa = tk.Entry(placa_frame, font=("Arial", 11), width=20)
        self.entry_placa.pack(side=tk.LEFT)
        self.entry_placa.bind('<KeyRelease>', self.formatar_placa)
        
        label_exemplo_placa = tk.Label(
            placa_frame,
            text="Ex: ABC-1234 ou ABC1D23",
            font=("Arial", 9, "italic"),
            bg=self.bg_color,
            fg="#7f8c8d"
        )
        label_exemplo_placa.pack(side=tk.LEFT, padx=10)
        
        # ===== SEÇÃO 2: TIPO DE PESSOA =====
        self.criar_secao(scrollable_frame, "TIPO DE PESSOA", 7)
        
        tipo_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
        tipo_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        self.tipo_pessoa = tk.StringVar(value="Cliente Ativo")
        self.tipo_pessoa.trace('w', self.on_tipo_pessoa_change)
        
        rb_cliente = tk.Radiobutton(
            tipo_frame,
            text="Cliente Ativo",
            variable=self.tipo_pessoa,
            value="Cliente Ativo",
            font=("Arial", 11),
            bg=self.bg_color,
            cursor="hand2"
        )
        rb_cliente.pack(side=tk.LEFT, padx=20)
        
        rb_visitante = tk.Radiobutton(
            tipo_frame,
            text="Visitante",
            variable=self.tipo_pessoa,
            value="Visitante",
            font=("Arial", 11),
            bg=self.bg_color,
            cursor="hand2"
        )
        rb_visitante.pack(side=tk.LEFT, padx=20)
        
        rb_descarga = tk.Radiobutton(
            tipo_frame,
            text="Descarga de Material",
            variable=self.tipo_pessoa,
            value="Descarga de Material",
            font=("Arial", 11),
            bg=self.bg_color,
            cursor="hand2"
        )
        rb_descarga.pack(side=tk.LEFT, padx=20)
        
        # NF de Entrada (só aparece para Descarga de Material)
        self.label_nf_entrada = tk.Label(
            scrollable_frame,
            text="NF de Entrada: *",
            font=("Arial", 11, "bold"),
            bg=self.bg_color,
            fg="#e74c3c",
            anchor="e"
        )
        
        self.entry_nf_entrada = tk.Entry(scrollable_frame, font=("Arial", 11), width=35)
        
        # Inicialmente escondido
        self.nf_entrada_row = 8.5  # Entre tipo de pessoa e atendimento
        
        # ===== SEÇÃO 3: ATENDIMENTO =====
        self.criar_secao(scrollable_frame, "INFORMAÇÕES DE ATENDIMENTO", 9)
        
        # Vendedor
        self.criar_campo(scrollable_frame, "Vendedor:", 10, obrigatorio=True)
        self.combo_vendedor = ttk.Combobox(
            scrollable_frame,
            values=self.vendedores,
            font=("Arial", 11),
            width=33,
            state="readonly"
        )
        self.combo_vendedor.grid(row=10, column=1, sticky="w", pady=5, padx=(0, 10))
        
        # NF de Saída
        self.criar_campo(scrollable_frame, "NF de Saída:", 11, obrigatorio=False)
        self.entry_nf = self.criar_entrada(scrollable_frame, 11)
        self.label_nf_saida_info = tk.Label(
            scrollable_frame,
            text="(Mesma da NF de Entrada)",
            font=("Arial", 9, "italic"),
            bg=self.bg_color,
            fg="#7f8c8d"
        )
        # Inicialmente escondido
        self.nf_saida_info_visible = False
        
        # ===== SEÇÃO 4: HORÁRIOS =====
        self.criar_secao(scrollable_frame, "HORÁRIOS", 12)
        
        # Horário de Entrada
        self.criar_campo(scrollable_frame, "Horário de Entrada:", 13, obrigatorio=True)
        horario_entrada_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
        horario_entrada_frame.grid(row=13, column=1, sticky="w", pady=5, padx=(0, 10))
        
        self.entry_horario_entrada = tk.Entry(
            horario_entrada_frame,
            font=("Arial", 11),
            width=20
        )
        self.entry_horario_entrada.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_horario_entrada.insert(0, datetime.now().strftime("%H:%M"))
        
        btn_hora_entrada = tk.Button(
            horario_entrada_frame,
            text="Hora Atual",
            command=lambda: self.entry_horario_entrada.delete(0, tk.END) or 
                          self.entry_horario_entrada.insert(0, datetime.now().strftime("%H:%M")),
            bg=self.secondary_color,
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            relief=tk.FLAT,
            padx=8,
            pady=3
        )
        btn_hora_entrada.pack(side=tk.LEFT)
        
        # Horário de Saída
        self.criar_campo(scrollable_frame, "Horário de Saída:", 14)
        horario_saida_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
        horario_saida_frame.grid(row=14, column=1, sticky="w", pady=5, padx=(0, 10))
        
        self.entry_horario_saida = tk.Entry(
            horario_saida_frame,
            font=("Arial", 11),
            width=20
        )
        self.entry_horario_saida.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_hora_saida = tk.Button(
            horario_saida_frame,
            text="Hora Atual",
            command=lambda: self.entry_horario_saida.delete(0, tk.END) or 
                          self.entry_horario_saida.insert(0, datetime.now().strftime("%H:%M")),
            bg=self.secondary_color,
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            relief=tk.FLAT,
            padx=8,
            pady=3
        )
        btn_hora_saida.pack(side=tk.LEFT)
        
        # ===== BOTÕES DE AÇÃO =====
        botoes_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
        botoes_frame.grid(row=15, column=0, columnspan=2, pady=30)
        
        btn_salvar = tk.Button(
            botoes_frame,
            text="REGISTRAR ENTRADA",
            command=self.salvar_registro,
            bg=self.success_color,
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=30,
            pady=12
        )
        btn_salvar.pack(side=tk.LEFT, padx=10)
        
        btn_liberar = tk.Button(
            botoes_frame,
            text="LIBERAR SAÍDA",
            command=self.abrir_liberacao,
            bg="#f39c12",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=30,
            pady=12
        )
        btn_liberar.pack(side=tk.LEFT, padx=10)
        
        btn_limpar = tk.Button(
            botoes_frame,
            text="LIMPAR CAMPOS",
            command=self.limpar_campos,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=30,
            pady=12
        )
        btn_limpar.pack(side=tk.LEFT, padx=10)
        
        btn_consultar = tk.Button(
            botoes_frame,
            text="CONSULTAR REGISTROS",
            command=self.abrir_consulta,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=30,
            pady=12
        )
        btn_consultar.pack(side=tk.LEFT, padx=10)
        
        # Empacotar canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Atualizar o tamanho do canvas quando a janela redimensionar
        def on_canvas_resize(event):
            canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width)
        
        canvas.bind("<Configure>", on_canvas_resize)
        
    def criar_secao(self, parent, titulo, row):
        """Cria um cabeçalho de seção"""
        frame = tk.Frame(parent, bg=self.primary_color, height=35)
        frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(15, 5), padx=5)
        frame.grid_propagate(False)
        
        # Configurar expansão do grid
        parent.grid_columnconfigure(0, weight=0, minsize=200)
        parent.grid_columnconfigure(1, weight=1)
        
        label = tk.Label(
            frame,
            text=titulo,
            font=("Arial", 11, "bold"),
            bg=self.primary_color,
            fg="white"
        )
        label.pack(pady=7)
        
    def criar_campo(self, parent, texto, row, obrigatorio=False):
        """Cria um label de campo"""
        if obrigatorio:
            texto += " *"
        label = tk.Label(
            parent,
            text=texto,
            font=("Arial", 11, "bold"),
            bg=self.bg_color,
            fg=self.primary_color if not obrigatorio else "#e74c3c",
            anchor="e"
        )
        label.grid(row=row, column=0, sticky="e", padx=(10, 15), pady=5)
        
    def criar_entrada(self, parent, row):
        """Cria um campo de entrada"""
        entry = tk.Entry(parent, font=("Arial", 11), width=35)
        entry.grid(row=row, column=1, sticky="w", pady=5, padx=(0, 10))
        return entry
    
    def on_tipo_pessoa_change(self, *args):
        """Controla a visibilidade dos campos baseado no tipo de pessoa"""
        tipo = self.tipo_pessoa.get()
        
        if tipo == "Descarga de Material":
            # Mostrar NF de Entrada
            self.label_nf_entrada.grid(row=9, column=0, sticky="e", padx=(10, 15), pady=5)
            self.entry_nf_entrada.grid(row=9, column=1, sticky="w", pady=5, padx=(0, 10))
            
            # Preencher vendedor automaticamente
            self.combo_vendedor.set("DOX BRASIL")
            self.combo_vendedor.config(state="disabled")
            
            # Adicionar info na NF de Saída
            if not self.nf_saida_info_visible:
                self.label_nf_saida_info.grid(row=11, column=1, sticky="w", padx=(10, 0), pady=(0, 5))
                self.nf_saida_info_visible = True
            
        else:
            # Ocultar NF de Entrada
            self.label_nf_entrada.grid_remove()
            self.entry_nf_entrada.grid_remove()
            self.entry_nf_entrada.delete(0, tk.END)
            
            # Habilitar vendedor
            self.combo_vendedor.config(state="readonly")
            if self.combo_vendedor.get() == "DOX BRASIL":
                self.combo_vendedor.set("")
            
            # Remover info da NF de Saída
            if self.nf_saida_info_visible:
                self.label_nf_saida_info.grid_remove()
                self.nf_saida_info_visible = False
    
    def formatar_placa(self, event):
        """Formata a placa do veículo automaticamente"""
        placa = self.entry_placa.get().upper().replace("-", "")
        
        if len(placa) <= 7:
            if len(placa) == 7:
                placa_formatada = placa[:3] + "-" + placa[3:]
            else:
                placa_formatada = placa
            
            self.entry_placa.delete(0, tk.END)
            self.entry_placa.insert(0, placa_formatada)
        
    def formatar_cpf(self, event):
        """Formata o CPF automaticamente"""
        cpf = self.entry_cpf.get().replace(".", "").replace("-", "")
        if len(cpf) <= 11 and cpf.isdigit():
            if len(cpf) >= 3:
                cpf = cpf[:3] + "." + cpf[3:]
            if len(cpf) >= 7:
                cpf = cpf[:7] + "." + cpf[7:]
            if len(cpf) >= 11:
                cpf = cpf[:11] + "-" + cpf[11:]
            
            self.entry_cpf.delete(0, tk.END)
            self.entry_cpf.insert(0, cpf)
            
    def formatar_telefone(self, event):
        """Formata o telefone automaticamente"""
        telefone = self.entry_telefone.get().replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
        if telefone.isdigit():
            if len(telefone) <= 11:
                if len(telefone) >= 2:
                    telefone = "(" + telefone[:2] + ") " + telefone[2:]
                if len(telefone) >= 10:
                    telefone = telefone[:10] + "-" + telefone[10:]
                
                self.entry_telefone.delete(0, tk.END)
                self.entry_telefone.insert(0, telefone)
    
    def validar_cpf(self):
        """Valida o CPF usando API externa"""
        cpf = self.entry_cpf.get().replace(".", "").replace("-", "")
        
        if len(cpf) != 11 or not cpf.isdigit():
            self.label_cpf_status.config(text="❌ CPF inválido", fg="red")
            return False
        
        if not self.validar_cpf_matematico(cpf):
            self.label_cpf_status.config(text="❌ CPF inválido", fg="red")
            return False
        
        try:
            url = f"https://api.cpfcnpj.com.br/{cpf}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                self.label_cpf_status.config(text="✓ CPF válido", fg="green")
                return True
            else:
                self.label_cpf_status.config(text="✓ CPF válido (offline)", fg="orange")
                return True
        except:
            self.label_cpf_status.config(text="✓ CPF válido (offline)", fg="orange")
            return True
    
    def validar_cpf_matematico(self, cpf):
        """Validação matemática do CPF"""
        if cpf == cpf[0] * 11:
            return False
        
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito1 = 11 - (soma % 11)
        if digito1 > 9:
            digito1 = 0
        if int(cpf[9]) != digito1:
            return False
        
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito2 = 11 - (soma % 11)
        if digito2 > 9:
            digito2 = 0
        if int(cpf[10]) != digito2:
            return False
        
        return True
    
    def salvar_registro(self):
        """Salva o registro no banco de dados"""
        if not self.entry_nome.get().strip():
            messagebox.showerror("Erro", "Nome do cliente é obrigatório!")
            return
        
        if not self.entry_empresa.get().strip():
            messagebox.showerror("Erro", "Empresa é obrigatória!")
            return
        
        if not self.entry_empresa_representada.get().strip():
            messagebox.showerror("Erro", "Empresa Representada é obrigatória!")
            return
        
        # CPF não é mais obrigatório, mas se fornecido deve ser válido
        cpf = self.entry_cpf.get().replace(".", "").replace("-", "")
        if cpf and (len(cpf) != 11 or not cpf.isdigit()):
            messagebox.showerror("Erro", "CPF inválido! Deixe em branco ou informe um CPF válido.")
            return
        
        # Se CPF não for fornecido, usar string vazia
        if not cpf:
            cpf = ""
        
        if not self.entry_telefone.get().strip():
            messagebox.showerror("Erro", "Telefone é obrigatório!")
            return
        
        if not self.entry_placa.get().strip():
            messagebox.showerror("Erro", "Placa do veículo é obrigatória!")
            return
        
        if not self.combo_vendedor.get():
            messagebox.showerror("Erro", "Selecione um vendedor!")
            return
        
        if not self.entry_horario_entrada.get().strip():
            messagebox.showerror("Erro", "Horário de entrada é obrigatório!")
            return
        
        # Validação específica para Descarga de Material
        if self.tipo_pessoa.get() == "Descarga de Material":
            if not self.entry_nf_entrada.get().strip():
                messagebox.showerror("Erro", "NF de Entrada é obrigatória para Descarga de Material!")
                return
            # Para descarga de material, NF de saída = NF de entrada
            nf_saida = self.entry_nf_entrada.get().strip()
        else:
            nf_saida = self.entry_nf.get().strip()
        
        try:
            cpf_valido = 1 if cpf and "válido" in self.label_cpf_status.cget("text") else 0
            
            self.cursor.execute('''
                INSERT INTO registros 
                (nome_cliente, empresa, empresa_representada, cpf, telefone, placa_veiculo, 
                 tipo_pessoa, vendedor, nf_saida, horario_entrada, horario_saida, data_registro, cpf_valido)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.entry_nome.get().strip().upper(),
                self.entry_empresa.get().strip().upper(),
                self.entry_empresa_representada.get().strip().upper(),
                cpf,
                self.entry_telefone.get().strip(),
                self.entry_placa.get().strip().upper(),
                self.tipo_pessoa.get(),
                self.combo_vendedor.get(),
                nf_saida,
                self.entry_horario_entrada.get().strip(),
                self.entry_horario_saida.get().strip() if self.entry_horario_saida.get().strip() else None,
                datetime.now().strftime("%Y-%m-%d"),
                cpf_valido
            ))
            
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Registro salvo com sucesso!")
            self.limpar_campos()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
    
    def limpar_campos(self):
        """Limpa todos os campos do formulário"""
        self.entry_nome.delete(0, tk.END)
        self.entry_empresa.delete(0, tk.END)
        self.entry_empresa_representada.delete(0, tk.END)
        self.entry_cpf.delete(0, tk.END)
        self.entry_telefone.delete(0, tk.END)
        self.entry_placa.delete(0, tk.END)
        self.entry_nf.delete(0, tk.END)
        self.entry_nf_entrada.delete(0, tk.END)
        self.entry_horario_entrada.delete(0, tk.END)
        self.entry_horario_entrada.insert(0, datetime.now().strftime("%H:%M"))
        self.entry_horario_saida.delete(0, tk.END)
        self.combo_vendedor.set('')
        self.tipo_pessoa.set("Cliente Ativo")
        self.label_cpf_status.config(text="")
    
    def abrir_consulta(self):
        """Abre janela de consulta de registros"""
        ConsultaRegistros(self.root, self.conn, self.vendedores)
    
    def abrir_liberacao(self):
        """Abre janela de liberação de saída"""
        LiberacaoSaida(self.root, self.conn)
    
    def __del__(self):
        """Fecha a conexão com o banco ao encerrar"""
        if hasattr(self, 'conn'):
            self.conn.close()


class LiberacaoSaida:
    """Janela para liberar saída de motoristas/clientes com exigência de NF"""
    def __init__(self, parent, conn):
        self.conn = conn
        self.cursor = conn.cursor()
        
        self.janela = tk.Toplevel(parent)
        self.janela.title("Liberação de Saída")
        self.janela.geometry("1200x600")
        self.janela.configure(bg="#f0f0f0")
        
        frame_titulo = tk.Frame(self.janela, bg="#e67e22", height=60)
        frame_titulo.pack(fill=tk.X)
        frame_titulo.pack_propagate(False)
        
        titulo = tk.Label(
            frame_titulo,
            text="LIBERAÇÃO DE SAÍDA - PORTARIA",
            font=("Arial", 18, "bold"),
            bg="#e67e22",
            fg="white"
        )
        titulo.pack(pady=15)
        
        frame_busca = tk.Frame(self.janela, bg="#f0f0f0", pady=15)
        frame_busca.pack(fill=tk.X, padx=20)
        
        tk.Label(
            frame_busca,
            text="Buscar (Nome, CPF, Empresa ou Placa):",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=5)
        
        self.entry_busca = tk.Entry(frame_busca, font=("Arial", 11), width=40)
        self.entry_busca.pack(side=tk.LEFT, padx=5)
        self.entry_busca.bind('<KeyRelease>', lambda e: self.buscar_registros())
        
        btn_buscar = tk.Button(
            frame_busca,
            text="Buscar",
            command=self.buscar_registros,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)
        
        btn_pendentes = tk.Button(
            frame_busca,
            text="Ver Pendentes",
            command=self.mostrar_pendentes,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        btn_pendentes.pack(side=tk.LEFT, padx=5)
        
        frame_lista = tk.Frame(self.janela, bg="#f0f0f0")
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        scroll_y = ttk.Scrollbar(frame_lista, orient="vertical")
        scroll_x = ttk.Scrollbar(frame_lista, orient="horizontal")
        
        colunas = ("ID", "Data", "Nome", "Empresa Rep.", "Placa", "Vendedor", "Entrada", "Status")
        self.tree = ttk.Treeview(
            frame_lista,
            columns=colunas,
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            height=12
        )
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        larguras = [50, 100, 150, 150, 100, 120, 80, 100]
        for col, largura in zip(colunas, larguras):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=largura, anchor="center")
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree.bind('<Double-1>', self.selecionar_registro)
        
        frame_liberacao = tk.Frame(self.janela, bg="#ecf0f1", relief=tk.RIDGE, bd=2)
        frame_liberacao.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        tk.Label(
            frame_liberacao,
            text="DADOS DA LIBERAÇÃO",
            font=("Arial", 12, "bold"),
            bg="#34495e",
            fg="white",
            pady=8
        ).pack(fill=tk.X)
        
        campos_frame = tk.Frame(frame_liberacao, bg="#ecf0f1", pady=10)
        campos_frame.pack(fill=tk.X, padx=20)
        
        nf_frame = tk.Frame(campos_frame, bg="#ecf0f1")
        nf_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            nf_frame,
            text="NF de Saída: *",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1",
            fg="#e74c3c"
        ).pack(side=tk.LEFT, padx=5)
        
        self.entry_nf_liberacao = tk.Entry(nf_frame, font=("Arial", 11), width=20)
        self.entry_nf_liberacao.pack(side=tk.LEFT, padx=5)
        
        hora_frame = tk.Frame(campos_frame, bg="#ecf0f1")
        hora_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            hora_frame,
            text="Horário Saída: *",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1",
            fg="#e74c3c"
        ).pack(side=tk.LEFT, padx=5)
        
        self.entry_hora_saida = tk.Entry(hora_frame, font=("Arial", 11), width=15)
        self.entry_hora_saida.pack(side=tk.LEFT, padx=5)
        self.entry_hora_saida.insert(0, datetime.now().strftime("%H:%M"))
        
        btn_hora_atual = tk.Button(
            hora_frame,
            text="Agora",
            command=lambda: [
                self.entry_hora_saida.delete(0, tk.END),
                self.entry_hora_saida.insert(0, datetime.now().strftime("%H:%M"))
            ],
            bg="#3498db",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            relief=tk.FLAT,
            padx=8,
            pady=3
        )
        btn_hora_atual.pack(side=tk.LEFT, padx=5)
        
        btn_liberar = tk.Button(
            campos_frame,
            text="🚗 LIBERAR SAÍDA",
            command=self.liberar_saida,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=25,
            pady=8
        )
        btn_liberar.pack(side=tk.LEFT, padx=20)
        
        self.label_info = tk.Label(
            frame_liberacao,
            text="Selecione um registro na lista acima (duplo clique)",
            font=("Arial", 10, "italic"),
            bg="#ecf0f1",
            fg="#7f8c8d"
        )
        self.label_info.pack(pady=(0, 10))
        
        self.registro_selecionado = None
        self.mostrar_pendentes()
    
    def buscar_registros(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filtro = self.entry_busca.get().strip()
        
        if filtro:
            query = '''
                SELECT id, data_registro, nome_cliente, empresa_representada, placa_veiculo, 
                       vendedor, horario_entrada, horario_saida, nf_saida
                FROM registros
                WHERE (nome_cliente LIKE ? OR cpf LIKE ? OR empresa LIKE ? OR placa_veiculo LIKE ?)
                ORDER BY data_registro DESC, horario_entrada DESC
                LIMIT 50
            '''
            self.cursor.execute(query, (f'%{filtro}%', f'%{filtro}%', f'%{filtro}%', f'%{filtro}%'))
        else:
            self.mostrar_pendentes()
            return
        
        self.preencher_lista()
    
    def mostrar_pendentes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        query = '''
            SELECT id, data_registro, nome_cliente, empresa_representada, placa_veiculo, 
                   vendedor, horario_entrada, horario_saida, nf_saida
            FROM registros
            WHERE horario_saida IS NULL OR horario_saida = ''
            ORDER BY data_registro DESC, horario_entrada DESC
        '''
        self.cursor.execute(query)
        self.preencher_lista()
    
    def preencher_lista(self):
        registros = self.cursor.fetchall()
        
        for reg in registros:
            data_formatada = datetime.strptime(reg[1], "%Y-%m-%d").strftime("%d/%m/%Y")
            
            if reg[7] and reg[8]:
                status = "✓ Liberado"
                tag = "liberado"
            elif reg[7]:
                status = "⚠ Sem NF"
                tag = "alerta"
            else:
                status = "🔴 Pendente"
                tag = "pendente"
            
            valores = (
                reg[0],
                data_formatada,
                reg[2],
                reg[3] if reg[3] else "-",
                reg[4] if reg[4] else "-",
                reg[5],
                reg[6],
                status
            )
            
            self.tree.insert("", tk.END, values=valores, tags=(tag,))
        
        self.tree.tag_configure("pendente", background="#ffcccc")
        self.tree.tag_configure("alerta", background="#fff4cc")
        self.tree.tag_configure("liberado", background="#ccffcc")
    
    def selecionar_registro(self, event):
        selecionado = self.tree.selection()
        if not selecionado:
            return
        
        item = self.tree.item(selecionado[0])
        valores = item['values']
        
        self.registro_selecionado = valores[0]
        
        self.cursor.execute(
            'SELECT nf_saida, horario_saida FROM registros WHERE id = ?',
            (self.registro_selecionado,)
        )
        dados = self.cursor.fetchone()
        
        if dados[0]:
            self.entry_nf_liberacao.delete(0, tk.END)
            self.entry_nf_liberacao.insert(0, dados[0])
        
        if dados[1]:
            self.entry_hora_saida.delete(0, tk.END)
            self.entry_hora_saida.insert(0, dados[1])
        
        self.label_info.config(
            text=f"Selecionado: {valores[2]} - Placa: {valores[4]} - Entrada: {valores[6]}",
            fg="#27ae60"
        )
    
    def liberar_saida(self):
        if not self.registro_selecionado:
            messagebox.showerror("Erro", "Selecione um registro na lista!")
            return
        
        nf = self.entry_nf_liberacao.get().strip()
        if not nf:
            messagebox.showerror("Erro", "NF de Saída é obrigatória para liberar!")
            self.entry_nf_liberacao.focus()
            return
        
        hora_saida = self.entry_hora_saida.get().strip()
        if not hora_saida:
            messagebox.showerror("Erro", "Horário de saída é obrigatório!")
            return
        
        resposta = messagebox.askyesno(
            "Confirmar Liberação",
            f"Liberar saída com:\n\nNF: {nf}\nHorário: {hora_saida}\n\nConfirma?"
        )
        
        if not resposta:
            return
        
        try:
            self.cursor.execute('''
                UPDATE registros 
                SET nf_saida = ?, horario_saida = ?
                WHERE id = ?
            ''', (nf, hora_saida, self.registro_selecionado))
            
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "✓ Saída liberada com sucesso!")
            
            self.entry_nf_liberacao.delete(0, tk.END)
            self.entry_hora_saida.delete(0, tk.END)
            self.entry_hora_saida.insert(0, datetime.now().strftime("%H:%M"))
            self.registro_selecionado = None
            self.label_info.config(
                text="Selecione um registro na lista acima (duplo clique)",
                fg="#7f8c8d"
            )
            
            self.mostrar_pendentes()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao liberar saída: {str(e)}")


class ConsultaRegistros:
    def __init__(self, parent, conn, vendedores):
        self.conn = conn
        self.cursor = conn.cursor()
        self.vendedores = vendedores
        
        self.janela = tk.Toplevel(parent)
        self.janela.title("Consulta de Registros")
        self.janela.geometry("1400x650")
        
        frame_filtros = tk.Frame(self.janela, bg="#f0f0f0", pady=10)
        frame_filtros.pack(fill=tk.X, padx=10)
        
        tk.Label(frame_filtros, text="Filtrar por:", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        
        self.entry_filtro = tk.Entry(frame_filtros, font=("Arial", 10), width=30)
        self.entry_filtro.pack(side=tk.LEFT, padx=5)
        
        btn_filtrar = tk.Button(
            frame_filtros,
            text="Buscar",
            command=self.carregar_registros,
            bg="#3498db",
            fg="white",
            font=("Arial", 10),
            cursor="hand2"
        )
        btn_filtrar.pack(side=tk.LEFT, padx=5)
        
        btn_todos = tk.Button(
            frame_filtros,
            text="Mostrar Todos",
            command=lambda: [self.entry_filtro.delete(0, tk.END), self.carregar_registros()],
            bg="#27ae60",
            fg="white",
            font=("Arial", 10),
            cursor="hand2"
        )
        btn_todos.pack(side=tk.LEFT, padx=5)
        
        # Botões de Editar e Excluir
        btn_editar = tk.Button(
            frame_filtros,
            text="✏️ Editar",
            command=self.editar_registro,
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            padx=15
        )
        btn_editar.pack(side=tk.LEFT, padx=5)
        
        btn_excluir = tk.Button(
            frame_filtros,
            text="🗑️ Excluir",
            command=self.excluir_registro,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            padx=15
        )
        btn_excluir.pack(side=tk.LEFT, padx=5)
        
        frame_tabela = tk.Frame(self.janela)
        frame_tabela.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scroll_y = ttk.Scrollbar(frame_tabela, orient="vertical")
        scroll_x = ttk.Scrollbar(frame_tabela, orient="horizontal")
        
        colunas = ("ID", "Data", "Nome", "Empresa", "Empresa Rep.", "Placa", "Telefone", "Tipo", "Vendedor", "NF", "Entrada", "Saída")
        self.tree = ttk.Treeview(
            frame_tabela,
            columns=colunas,
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        larguras = [50, 90, 140, 140, 140, 90, 110, 100, 120, 80, 70, 70]
        for col, largura in zip(colunas, larguras):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=largura, anchor="center")
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.carregar_registros()
    
    def carregar_registros(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filtro = self.entry_filtro.get().strip()
        if filtro:
            query = '''
                SELECT id, data_registro, nome_cliente, empresa, empresa_representada, 
                       placa_veiculo, telefone, tipo_pessoa, vendedor, nf_saida, 
                       horario_entrada, horario_saida
                FROM registros
                WHERE nome_cliente LIKE ? OR empresa LIKE ? OR empresa_representada LIKE ? 
                      OR placa_veiculo LIKE ? OR nf_saida LIKE ?
                ORDER BY data_registro DESC, horario_entrada DESC
            '''
            self.cursor.execute(query, (f'%{filtro}%', f'%{filtro}%', f'%{filtro}%', f'%{filtro}%', f'%{filtro}%'))
        else:
            query = '''
                SELECT id, data_registro, nome_cliente, empresa, empresa_representada, 
                       placa_veiculo, telefone, tipo_pessoa, vendedor, nf_saida, 
                       horario_entrada, horario_saida
                FROM registros
                ORDER BY data_registro DESC, horario_entrada DESC
            '''
            self.cursor.execute(query)
        
        registros = self.cursor.fetchall()
        
        for reg in registros:
            data_formatada = datetime.strptime(reg[1], "%Y-%m-%d").strftime("%d/%m/%Y")
            
            valores = (
                reg[0],
                data_formatada,
                reg[2],
                reg[3],
                reg[4] if reg[4] else "-",
                reg[5] if reg[5] else "-",
                reg[6],
                reg[7],
                reg[8],
                reg[9] if reg[9] else "-",
                reg[10],
                reg[11] if reg[11] else "-"
            )
            self.tree.insert("", tk.END, values=valores)
    
    def editar_registro(self):
        """Abre janela para editar o registro selecionado"""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um registro para editar!")
            return
        
        item = self.tree.item(selecionado[0])
        valores = item['values']
        registro_id = valores[0]
        
        # Buscar dados completos do registro
        self.cursor.execute('''
            SELECT nome_cliente, empresa, empresa_representada, cpf, telefone, placa_veiculo,
                   tipo_pessoa, vendedor, nf_saida, horario_entrada, horario_saida
            FROM registros WHERE id = ?
        ''', (registro_id,))
        
        dados = self.cursor.fetchone()
        if not dados:
            messagebox.showerror("Erro", "Registro não encontrado!")
            return
        
        # Abrir janela de edição
        EditorRegistro(self.janela, self.conn, self.vendedores, registro_id, dados, self.carregar_registros)
    
    def excluir_registro(self):
        """Exclui o registro selecionado após confirmação"""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um registro para excluir!")
            return
        
        item = self.tree.item(selecionado[0])
        valores = item['values']
        registro_id = valores[0]
        nome_cliente = valores[2]
        
        # Confirmação
        resposta = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o registro?\n\n"
            f"ID: {registro_id}\n"
            f"Nome: {nome_cliente}\n\n"
            f"Esta ação não pode ser desfeita!",
            icon='warning'
        )
        
        if not resposta:
            return
        
        try:
            self.cursor.execute('DELETE FROM registros WHERE id = ?', (registro_id,))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Registro excluído com sucesso!")
            self.carregar_registros()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir registro: {str(e)}")


class EditorRegistro:
    """Janela para editar um registro existente"""
    def __init__(self, parent, conn, vendedores, registro_id, dados, callback_atualizar):
        self.conn = conn
        self.cursor = conn.cursor()
        self.vendedores = vendedores
        self.registro_id = registro_id
        self.callback_atualizar = callback_atualizar
        
        self.janela = tk.Toplevel(parent)
        self.janela.title(f"Editar Registro #{registro_id}")
        self.janela.geometry("700x750")
        self.janela.configure(bg="#f0f0f0")
        self.janela.resizable(False, False)
        
        # Título
        frame_titulo = tk.Frame(self.janela, bg="#3498db", height=60)
        frame_titulo.pack(fill=tk.X)
        frame_titulo.pack_propagate(False)
        
        titulo = tk.Label(
            frame_titulo,
            text=f"EDITAR REGISTRO #{registro_id}",
            font=("Arial", 16, "bold"),
            bg="#3498db",
            fg="white"
        )
        titulo.pack(pady=15)
        
        # Frame com scroll
        main_frame = tk.Frame(self.janela, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        canvas = tk.Canvas(main_frame, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Campos do formulário
        row = 0
        
        # Nome
        self.criar_campo(scrollable_frame, "Nome do Cliente:", row)
        self.entry_nome = tk.Entry(scrollable_frame, font=("Arial", 11), width=40)
        self.entry_nome.grid(row=row, column=1, sticky="w", pady=5, padx=10)
        self.entry_nome.insert(0, dados[0])
        row += 1
        
        # Empresa
        self.criar_campo(scrollable_frame, "Empresa:", row)
        self.entry_empresa = tk.Entry(scrollable_frame, font=("Arial", 11), width=40)
        self.entry_empresa.grid(row=row, column=1, sticky="w", pady=5, padx=10)
        self.entry_empresa.insert(0, dados[1])
        row += 1
        
        # Empresa Representada
        self.criar_campo(scrollable_frame, "Empresa Representada:", row)
        self.entry_empresa_rep = tk.Entry(scrollable_frame, font=("Arial", 11), width=40)
        self.entry_empresa_rep.grid(row=row, column=1, sticky="w", pady=5, padx=10)
        self.entry_empresa_rep.insert(0, dados[2] if dados[2] else "")
        row += 1
        
        # CPF
        self.criar_campo(scrollable_frame, "CPF:", row)
        self.entry_cpf = tk.Entry(scrollable_frame, font=("Arial", 11), width=40)
        self.entry_cpf.grid(row=row, column=1, sticky="w", pady=5, padx=10)
        self.entry_cpf.insert(0, self.formatar_cpf_exibicao(dados[3]))
        row += 1
        
        # Telefone
        self.criar_campo(scrollable_frame, "Telefone:", row)
        self.entry_telefone = tk.Entry(scrollable_frame, font=("Arial", 11), width=40)
        self.entry_telefone.grid(row=row, column=1, sticky="w", pady=5, padx=10)
        self.entry_telefone.insert(0, dados[4])
        row += 1
        
        # Placa
        self.criar_campo(scrollable_frame, "Placa do Veículo:", row)
        self.entry_placa = tk.Entry(scrollable_frame, font=("Arial", 11), width=40)
        self.entry_placa.grid(row=row, column=1, sticky="w", pady=5, padx=10)
        self.entry_placa.insert(0, dados[5] if dados[5] else "")
        row += 1
        
        # Tipo de Pessoa
        self.criar_campo(scrollable_frame, "Tipo de Pessoa:", row)
        tipo_frame = tk.Frame(scrollable_frame, bg="#f0f0f0")
        tipo_frame.grid(row=row, column=1, sticky="w", pady=5, padx=10)
        
        self.tipo_pessoa = tk.StringVar(value=dados[6])
        
        rb_cliente = tk.Radiobutton(
            tipo_frame,
            text="Cliente Ativo",
            variable=self.tipo_pessoa,
            value="Cliente Ativo",
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        rb_cliente.pack(side=tk.LEFT, padx=10)
        
        rb_visitante = tk.Radiobutton(
            tipo_frame,
            text="Visitante",
            variable=self.tipo_pessoa,
            value="Visitante",
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        rb_visitante.pack(side=tk.LEFT, padx=10)
        row += 1
        
        # Vendedor
        self.criar_campo(scrollable_frame, "Vendedor:", row)
        self.combo_vendedor = ttk.Combobox(
            scrollable_frame,
            values=self.vendedores,
            font=("Arial", 11),
            width=37,
            state="readonly"
        )
        self.combo_vendedor.grid(row=row, column=1, sticky="w", pady=5, padx=10)
        self.combo_vendedor.set(dados[7])
        row += 1
        
        # NF de Saída
        self.criar_campo(scrollable_frame, "NF de Saída:", row)
        self.entry_nf = tk.Entry(scrollable_frame, font=("Arial", 11), width=40)
        self.entry_nf.grid(row=row, column=1, sticky="w", pady=5, padx=10)
        self.entry_nf.insert(0, dados[8] if dados[8] else "")
        row += 1
        
        # Horário de Entrada
        self.criar_campo(scrollable_frame, "Horário de Entrada:", row)
        self.entry_hora_entrada = tk.Entry(scrollable_frame, font=("Arial", 11), width=40)
        self.entry_hora_entrada.grid(row=row, column=1, sticky="w", pady=5, padx=10)
        self.entry_hora_entrada.insert(0, dados[9])
        row += 1
        
        # Horário de Saída
        self.criar_campo(scrollable_frame, "Horário de Saída:", row)
        self.entry_hora_saida = tk.Entry(scrollable_frame, font=("Arial", 11), width=40)
        self.entry_hora_saida.grid(row=row, column=1, sticky="w", pady=5, padx=10)
        self.entry_hora_saida.insert(0, dados[10] if dados[10] else "")
        row += 1
        
        # Botões
        frame_botoes = tk.Frame(scrollable_frame, bg="#f0f0f0")
        frame_botoes.grid(row=row, column=0, columnspan=2, pady=30)
        
        btn_salvar = tk.Button(
            frame_botoes,
            text="💾 SALVAR ALTERAÇÕES",
            command=self.salvar_alteracoes,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        btn_salvar.pack(side=tk.LEFT, padx=10)
        
        btn_cancelar = tk.Button(
            frame_botoes,
            text="❌ CANCELAR",
            command=self.janela.destroy,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        btn_cancelar.pack(side=tk.LEFT, padx=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def criar_campo(self, parent, texto, row):
        """Cria um label de campo"""
        label = tk.Label(
            parent,
            text=texto,
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            anchor="e"
        )
        label.grid(row=row, column=0, sticky="e", padx=10, pady=5)
    
    def formatar_cpf_exibicao(self, cpf):
        """Formata CPF para exibição"""
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf
    
    def salvar_alteracoes(self):
        """Salva as alterações no banco de dados"""
        # Validações
        if not self.entry_nome.get().strip():
            messagebox.showerror("Erro", "Nome do cliente é obrigatório!")
            return
        
        if not self.entry_empresa.get().strip():
            messagebox.showerror("Erro", "Empresa é obrigatória!")
            return
        
        # CPF não é mais obrigatório, mas se fornecido deve ser válido
        cpf = self.entry_cpf.get().replace(".", "").replace("-", "")
        if cpf and (len(cpf) != 11 or not cpf.isdigit()):
            messagebox.showerror("Erro", "CPF inválido! Deixe em branco ou informe um CPF válido.")
            return
        
        # Se CPF não for fornecido, usar string vazia
        if not cpf:
            cpf = ""
        
        if not self.entry_telefone.get().strip():
            messagebox.showerror("Erro", "Telefone é obrigatório!")
            return
        
        if not self.combo_vendedor.get():
            messagebox.showerror("Erro", "Selecione um vendedor!")
            return
        
        if not self.entry_hora_entrada.get().strip():
            messagebox.showerror("Erro", "Horário de entrada é obrigatório!")
            return
        
        # Confirmação
        resposta = messagebox.askyesno(
            "Confirmar Alterações",
            "Deseja salvar as alterações realizadas neste registro?"
        )
        
        if not resposta:
            return
        
        try:
            self.cursor.execute('''
                UPDATE registros
                SET nome_cliente = ?, empresa = ?, empresa_representada = ?, cpf = ?,
                    telefone = ?, placa_veiculo = ?, tipo_pessoa = ?, vendedor = ?,
                    nf_saida = ?, horario_entrada = ?, horario_saida = ?
                WHERE id = ?
            ''', (
                self.entry_nome.get().strip().upper(),
                self.entry_empresa.get().strip().upper(),
                self.entry_empresa_rep.get().strip().upper(),
                cpf,
                self.entry_telefone.get().strip(),
                self.entry_placa.get().strip().upper(),
                self.tipo_pessoa.get(),
                self.combo_vendedor.get(),
                self.entry_nf.get().strip(),
                self.entry_hora_entrada.get().strip(),
                self.entry_hora_saida.get().strip() if self.entry_hora_saida.get().strip() else None,
                self.registro_id
            ))
            
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Registro atualizado com sucesso!")
            self.callback_atualizar()  # Atualizar a lista
            self.janela.destroy()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar alterações: {str(e)}")


def main():
    root = tk.Tk()
    app = SistemaPortaria(root)
    root.mainloop()


if __name__ == "__main__":
    main()