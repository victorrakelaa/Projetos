import json
import os
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import simpledialog, filedialog
from datetime import datetime, timedelta
from collections import Counter
try:
    from fpdf import FPDF
except ImportError:
    messagebox.showerror("Erro", "Biblioteca fpdf não encontrada. Instale com: pip install fpdf")
    exit(1)

# Arquivo para salvar os dados
ARQUIVO_DADOS = 'pagamentos.json'

# Lista para armazenar os pagamentos (carregada do arquivo)
pagamentos = []

# Dicionário para ordem dos meses (para ordenação)
MESES_ORDENADOS = {
    'Janeiro': 1, 'Fevereiro': 2, 'Marco': 3, 'Abril': 4, 'Maio': 5, 'Junho': 6,
    'Julho': 7, 'Agosto': 8, 'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
}

ESCOLAS = [
    "Altenfelder - Manhã", "Altenfelder - Tarde",
    "Josué de Castro - Manhã", "Josué de Castro - Tarde",
    "Paulo Nogueira - Manhã", "Paulo Nogueira - Tarde",
    "Antonio Candido - Manhã", "Antonio Candido - Tarde",
    "Gepan", "Creche VP", "Creche dos Anjos", "Creche EC", "Parquinho", "CCA"
]

# Dia atual para verificação de atraso (ajustável)
CURRENT_DAY = 15

def validar_data(data_str):
    """Valida e converte data de DD/MM/AAAA para YYYY-MM-DD. Retorna None se inválida."""
    try:
        dt = datetime.strptime(data_str, '%d/%m/%Y')
        data_formatada = dt.strftime('%Y-%m-%d')  
        data_exibicao = dt.strftime('%d/%m/%Y')  

        return {'interna': data_formatada, 'exibicao': data_exibicao}
    except ValueError:
        return None

def carregar_dados():
    """Carrega os pagamentos do arquivo JSON, se existir."""
    global pagamentos
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as arquivo:
                pagamentos = json.load(arquivo)
            for pag in pagamentos:
                if 'data' not in pag:
                    pag['data'] = ''
                if 'escola' not in pag:
                    pag['escola'] = ''
            print(f"Dados carregados: {len(pagamentos)} pagamentos encontrados.")
        except json.JSONDecodeError:
            print("Arquivo de dados corrompido. Iniciando vazio.")
            pagamentos = []
    else:
        print("Nenhum arquivo de dados encontrado. Iniciando vazio.")
        pagamentos = []

def salvar_dados():
    """Salva os pagamentos no arquivo JSON."""
    try:
        with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as arquivo:
            json.dump(pagamentos, arquivo, ensure_ascii=False, indent=4)
        print("Dados salvos com sucesso.")
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        messagebox.showerror("Erro", f"Erro ao salvar dados: {e}")

def obter_meses_unicos():
    """Retorna lista de meses únicos ordenados."""
    meses_set = set(pag['mes'] for pag in pagamentos if pag['mes'].strip())
    meses_ordenados = sorted(meses_set, key=lambda m: MESES_ORDENADOS.get(m.capitalize(), 13))
    return ['Todos os Meses'] + meses_ordenados

def obter_nomes_unicos():
    """Retorna lista de nomes únicos ordenados alfabeticamente."""
    nomes_set = set(pag['nome'] for pag in pagamentos if pag['nome'].strip())
    return sorted(nomes_set)

def get_usual_payment_day(nome):
    """Retorna o dia usual de pagamento da criança baseado no histórico. Padrão 13 se nenhum."""
    dias = []
    for pag in pagamentos:
        if pag['nome'] == nome and pag.get('data'):
            try:
                dt = datetime.strptime(pag['data'], '%Y-%m-%d')
                dias.append(dt.day)
            except:
                pass
    if dias:
        return Counter(dias).most_common(1)[0][0]
    return 13

def popular_combobox_criancas():
    """Popula o Combobox com nomes únicos de crianças."""
    nomes = obter_nomes_unicos()
    combo_criancas['values'] = ['Todas as Crianças'] + nomes
    combo_criancas.set('Todas as Crianças')

def popular_combobox_escolas():
    """Popula o Combobox com escolas."""
    combo_escolas['values'] = ['Todas as Escolas'] + ESCOLAS
    combo_escolas.set('Todas as Escolas')

def escolher_mes_e_escola():
    """Abre um diálogo para escolher o mês e a escola via comboboxes."""
    dialog = tk.Toplevel(root)
    dialog.title("Escolher Mês e Escola")
    dialog.geometry("350x200")
    dialog.resizable(False, False)
    
    tk.Label(dialog, text="Selecione o mês:", font=("Arial", 10)).pack(pady=5)
    meses = list(MESES_ORDENADOS.keys())
    combo_mes = ttk.Combobox(dialog, values=meses, state="readonly", font=("Arial", 10))
    combo_mes.pack(pady=5)
    if meses:
        combo_mes.set(meses[0])
    
    tk.Label(dialog, text="Selecione a escola:", font=("Arial", 10)).pack(pady=5)
    escolas = ["Josué de Castro", "Paulo Nogueira", "Altenfelder", "Gepan", "Creche VP", "Creche dos Anjos", "Creche EC", "Parquinho", "CCA", "Antonio Candido"]
    combo_escola = ttk.Combobox(dialog, values=escolas, state="readonly", font=("Arial", 10))
    combo_escola.pack(pady=5)
    if escolas:
        combo_escola.set(escolas[0])
    
    selected_mes = None
    selected_escola = None
    def confirmar():
        nonlocal selected_mes, selected_escola
        selected_mes = combo_mes.get()
        selected_escola = combo_escola.get()
        dialog.destroy()
    def cancelar():
        nonlocal selected_mes, selected_escola
        selected_mes = None
        selected_escola = None
        dialog.destroy()
    frame_botoes_dialog = tk.Frame(dialog)
    frame_botoes_dialog.pack(pady=10)
    tk.Button(frame_botoes_dialog, text="Confirmar", command=confirmar, bg="lightgreen").pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botoes_dialog, text="Cancelar", command=cancelar, bg="red", fg="white").pack(side=tk.LEFT, padx=5)
    dialog.wait_window()
    return selected_mes, selected_escola

def popular_combobox():
    """Popula o Combobox com todos os meses ordenados."""
    meses = ['Todos os Meses'] + list(MESES_ORDENADOS.keys())
    combo_meses['values'] = meses
    combo_meses.set(meses[0])

def adicionar_pagamento(nome=None):
    """Abre uma janela para adicionar um novo pagamento."""
    if nome is None:
        nome = simpledialog.askstring("Adicionar Pagamento", "Digite o nome da criança:")
        if not nome or not nome.strip():
            messagebox.showwarning("Aviso", "Nome inválido. Tente novamente.")
            return
        nome = nome.strip()

    mes, escola = escolher_mes_e_escola()
    if not mes or not escola:
        messagebox.showwarning("Aviso", "Mês ou escola não selecionados. Tente novamente.")
        return
    
    data_str = simpledialog.askstring("Adicionar Pagamento", "Digite a data do pagamento (DD/MM/AAAA, ex: 15/03/2024):")
    if not data_str or not data_str.strip():
        messagebox.showwarning("Aviso", "Data inválida. Tente novamente.")
        return
    
    data_validada = validar_data(data_str.strip())
    if not data_validada:
        messagebox.showwarning("Aviso", "Data inválida. Use formato DD/MM/AAAA e verifique se é válida (não futura).")
        return
    
    valor_str = simpledialog.askstring("Adicionar Pagamento", "Digite o valor pago (ex: 100.50):")
    try:
        valor = float(valor_str)
    except ValueError:
        messagebox.showwarning("Aviso", "Valor inválido. Deve ser um número.")
        return
    
    pagamento = {
        'nome': nome,
        'mes': mes,
        'escola': escola,
        'data': data_validada['interna'],  
        'data_exibicao': data_validada['exibicao'],  
        'valor': valor
    }
    pagamentos.append(pagamento)
    messagebox.showinfo("Sucesso", f"Pagamento adicionado:\n{nome} - {mes} - {escola} - {data_validada['exibicao']} - R$ {valor:.2f}")
    salvar_dados()
    popular_combobox()
    popular_combobox_criancas()
    atualizar_lista()

def obter_data_exibicao(pag):
    """Retorna data de exibição ou '--' se vazia."""
    if 'data_exibicao' in pag and pag['data_exibicao']:
        return pag['data_exibicao']
    elif pag.get('data'):
        try:
            dt = datetime.strptime(pag['data'], '%Y-%m-%d')
            return dt.strftime('%d/%m/%Y')
        except:
            pass
    return '--'

def filtrar_e_listar():
    """Filtra e lista pagamentos por mês, criança e escola selecionados, incluindo atrasados e anteriores."""
    mes_selecionado = combo_meses.get()
    nome_selecionado = combo_criancas.get()
    escola_selecionada = combo_escolas.get()

    for item in tree.get_children():
        tree.delete(item)

    if not pagamentos:
        tree.insert("", "end", values=("Nenhum pagamento cadastrado.", "", "", "", "", ""))
        return

    # Obter crianças únicas que atendem aos filtros
    mes_order = MESES_ORDENADOS.get(mes_selecionado, 13)
    if mes_order >= 10:  # Outubro ou posterior
        # Incluir todas as crianças únicas do dataset, filtradas por nome e escola se selecionados
        criancas_filtradas = set()
        for pag in pagamentos:
            if (nome_selecionado == 'Todas as Crianças' or pag['nome'] == nome_selecionado) \
               and (escola_selecionada == 'Todas as Escolas' or pag['escola'] == escola_selecionada):
                criancas_filtradas.add((pag['nome'], pag.get('escola', '')))
    else:
        # Lógica original para meses anteriores
        criancas_filtradas = set()
        for pag in pagamentos:
            if (mes_selecionado == 'Todos os Meses' or pag['mes'] == mes_selecionado) \
               and (nome_selecionado == 'Todas as Crianças' or pag['nome'] == nome_selecionado) \
               and (escola_selecionada == 'Todas as Escolas' or pag['escola'] == escola_selecionada):
                criancas_filtradas.add((pag['nome'], pag.get('escola', '')))

    if not criancas_filtradas:
        filtro_msg = f"Nenhum pagamento para {mes_selecionado} - {nome_selecionado} - {escola_selecionada}."
        tree.insert("", "end", values=(filtro_msg, "", "", "", "", ""))
        return

    # Para cada criança, verificar status
    total = 0
    hoje = datetime.now()
    for nome, escola in sorted(criancas_filtradas, key=lambda x: (x[1], x[0])):  # Ordenar por escola, depois por nome
        # Verificar se há pagamento no mês selecionado
        pag_mes = None
        for pag in pagamentos:
            if pag['nome'] == nome and pag['mes'] == mes_selecionado and pag.get('escola', '') == escola:
                pag_mes = pag
                break

        if pag_mes:
            # Pago
            data_exib = obter_data_exibicao(pag_mes)
            tree.insert("", "end", values=(nome, data_exib, mes_selecionado, escola, "Pago", f"R$ {pag_mes['valor']:.2f}"), tags=('pago',))
            total += pag_mes['valor']
        else:
            # Para meses a partir de Outubro, verificar atraso baseado na data do último pagamento
            if mes_order >= 10:
                # Encontrar último pagamento da criança
                ultimo_pag = None
                for pag in pagamentos:
                    if pag['nome'] == nome and pag.get('escola', '') == escola and pag.get('data'):
                        try:
                            data_pag = datetime.strptime(pag['data'], '%Y-%m-%d')
                            if ultimo_pag is None or data_pag > ultimo_pag:
                                ultimo_pag = data_pag
                        except:
                            pass
                if ultimo_pag:
                    # Verificar se passaram 25 dias desde o último pagamento
                    if hoje - ultimo_pag > timedelta(days=25):
                        tree.insert("", "end", values=(nome, "--", mes_selecionado, escola, "Pagamento Atrasado", "--"), tags=('atrasado',))
                    else:
                        tree.insert("", "end", values=(nome, "--", mes_selecionado, escola, "não pago", "--"), tags=('nao_pago',))
                else:
                    # Nunca pagou, considerar atrasado se mês atual
                    tree.insert("", "end", values=(nome, "--", mes_selecionado, escola, "Pagamento Atrasado", "--"), tags=('atrasado',))
            else:
                # Lógica original para meses anteriores
                # Verificar se tem pagamento em mês anterior (para Outubro, Setembro)
                pag_anterior = None
                if mes_selecionado == 'Outubro':
                    for pag in pagamentos:
                        if pag['nome'] == nome and pag['mes'] == 'Setembro' and pag.get('escola', '') == escola:
                            pag_anterior = pag
                            break
                if pag_anterior:
                    # Não pago, mas pagou anterior
                    tree.insert("", "end", values=(nome, "--", mes_selecionado, escola, "não pago", "--"), tags=('nao_pago',))
                else:
                    # Verificar se atrasado
                    usual_day = get_usual_payment_day(nome)
                    due_day = usual_day + 5
                    if CURRENT_DAY > due_day:
                        # Atrasado
                        tree.insert("", "end", values=(nome, "--", mes_selecionado, escola, "atrasado", "--"), tags=('atrasado',))

    # Adiciona linha de total (apenas dos pagos)
    total_label = f"Total para {mes_selecionado} - {nome_selecionado} - {escola_selecionada}:"
    tree.insert("", "end", values=("", "", "", "", total_label, f"R$ {total:.2f}"))

def atualizar_lista():
    """Atualiza a lista baseada nas seleções de mês e criança."""
    filtrar_e_listar()

def on_selecao_mes(event=None):
    """Evento chamado ao selecionar um mês no Combobox."""
    atualizar_lista()

def on_selecao_crianca(event=None):
    """Evento chamado ao selecionar uma criança no Combobox."""
    atualizar_lista()

def on_selecao_escola(event=None):
    """Evento chamado ao selecionar uma escola no Combobox."""
    atualizar_lista()

def ver_mes_crianca():
    """Abre a janela mensal para uma criança selecionada."""
    nome_crianca = selecionar_crianca()
    if nome_crianca:
        abrir_janela_crianca(nome_crianca)

def selecionar_crianca():
    """Abre diálogo para selecionar uma criança."""
    nomes = obter_nomes_unicos()
    if not nomes:
        messagebox.showwarning("Aviso", "Nenhuma criança cadastrada.")
        return None
    
    dialog = tk.Toplevel(root)
    dialog.title("Selecionar Criança")
    dialog.geometry("300x150")
    dialog.resizable(False, False)
    
    tk.Label(dialog, text="Selecione a criança:", font=("Arial", 10)).pack(pady=10)
    combo = ttk.Combobox(dialog, values=nomes, state="readonly", width=30, font=("Arial", 10))
    combo.pack(pady=5)
    if nomes:
        combo.set(nomes[0])
    
    selected = None
    def confirmar():
        nonlocal selected
        selected = combo.get()
        dialog.destroy()
    def cancelar():
        nonlocal selected
        selected = None
        dialog.destroy()
    
    frame_botoes = tk.Frame(dialog)
    frame_botoes.pack(pady=10)
    tk.Button(frame_botoes, text="Confirmar", command=confirmar, bg="lightgreen").pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botoes, text="Cancelar", command=cancelar, bg="red", fg="white").pack(side=tk.LEFT, padx=5)
    
    dialog.wait_window()
    return selected

def abrir_janela_crianca(nome):
    """Abre a janela com visão mensal da criança."""
    meses = list(MESES_ORDENADOS.keys())
    window = tk.Toplevel(root)
    window.title(f"Pagamentos Mensais - {nome}")
    window.geometry("800x600")
    window.resizable(True, True)

    # Frame principal
    frame = tk.Frame(window)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Cabeçalho
    tk.Label(frame, text=f"Pagamentos para {nome}", font=("Arial", 14, "bold")).pack(pady=10)

    # Canvas e Scrollbar para rolagem
    canvas = tk.Canvas(frame)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Dicionários para armazenar widgets por mês
    check_vars = {}
    data_entries = {}
    escola_combos = {}
    valor_entries = {}

    # Para cada mês, criar linha
    for mes in meses:
        row_frame = tk.Frame(scrollable_frame)
        row_frame.pack(fill=tk.X, pady=2)

        # Label do mês
        tk.Label(row_frame, text=mes, width=15, anchor="w", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

        # Checkbox Pago
        var = tk.BooleanVar()
        chk = tk.Checkbutton(row_frame, variable=var)
        chk.pack(side=tk.LEFT, padx=5)
        check_vars[mes] = var

        # Entry Data
        data_entry = tk.Entry(row_frame, width=15, font=("Arial", 10))
        data_entry.pack(side=tk.LEFT, padx=5)
        data_entries[mes] = data_entry

        # Combobox Escola
        escola_combo = ttk.Combobox(row_frame, values=ESCOLAS, state="readonly", width=15, font=("Arial", 10))
        escola_combo.pack(side=tk.LEFT, padx=5)
        escola_combos[mes] = escola_combo

        # Entry Valor
        valor_entry = tk.Entry(row_frame, width=15, font=("Arial", 10))
        valor_entry.pack(side=tk.LEFT, padx=5)
        valor_entries[mes] = valor_entry

        # Preencher se existe pagamento
        existing_pag = None
        for pag in pagamentos:
            if pag['nome'] == nome and pag['mes'] == mes:
                existing_pag = pag
                break
        if existing_pag:
            var.set(True)
            data_entries[mes].insert(0, obter_data_exibicao(existing_pag))
            escola_combos[mes].set(existing_pag.get('escola', ''))
            valor_entries[mes].insert(0, str(existing_pag['valor']))

    # Botão Salvar
    def salvar_alteracoes():
        for mes in meses:
            checked = check_vars[mes].get()
            data_str = data_entries[mes].get().strip()
            escola = escola_combos[mes].get()
            valor_str = valor_entries[mes].get().strip()

            # Encontrar pagamento existente
            existing_pag = None
            for i, pag in enumerate(pagamentos):
                if pag['nome'] == nome and pag['mes'] == mes:
                    existing_pag = (i, pag)
                    break

            if checked:
                # Validar dados
                if not data_str:
                    messagebox.showerror("Erro", f"Data obrigatória para {mes}.")
                    return
                data_validada = validar_data(data_str)
                if not data_validada:
                    messagebox.showerror("Erro", f"Data inválida para {mes}.")
                    return
                if not escola:
                    messagebox.showerror("Erro", f"Escola obrigatória para {mes}.")
                    return
                try:
                    valor = float(valor_str)
                except ValueError:
                    messagebox.showerror("Erro", f"Valor inválido para {mes}.")
                    return

                if existing_pag:
                    # Atualizar
                    i, pag = existing_pag
                    pagamentos[i] = {
                        'nome': nome,
                        'mes': mes,
                        'escola': escola,
                        'data': data_validada['interna'],
                        'data_exibicao': data_validada['exibicao'],
                        'valor': valor
                    }
                else:
                    # Adicionar novo
                    pagamentos.append({
                        'nome': nome,
                        'mes': mes,
                        'escola': escola,
                        'data': data_validada['interna'],
                        'data_exibicao': data_validada['exibicao'],
                        'valor': valor
                    })
            else:
                # Remover se existir
                if existing_pag:
                    i, _ = existing_pag
                    del pagamentos[i]

        salvar_dados()
        atualizar_lista()
        messagebox.showinfo("Sucesso", "Alterações salvas com sucesso.")
        window.destroy()

    tk.Button(scrollable_frame, text="Salvar Alterações", command=salvar_alteracoes, bg="lightgreen", font=("Arial", 12)).pack(pady=20)

def on_tree_double_click(event):
    """Permite editar a escola ao clicar duas vezes na coluna Escola."""
    item = tree.identify('item', event.x, event.y)
    column = tree.identify('column', event.x, event.y)
    if column == '#4':  # Coluna Escola (agora #4 é Escola, #5 Pago, #6 Valor)
        values = tree.item(item, 'values')
        if len(values) >= 4:
            nome = values[0]
            mes = values[2]
            escola_atual = values[3]
            # Encontra o pagamento correspondente
            for pag in pagamentos:
                if pag['nome'] == nome and pag['mes'] == mes and pag.get('escola', '') == escola_atual:
                    # Abre diálogo para editar escola
                    dialog = tk.Toplevel(root)
                    dialog.title("Editar Escola")
                    dialog.geometry("300x150")
                    tk.Label(dialog, text=f"Editar escola para {nome}:").pack(pady=10)
                    combo = ttk.Combobox(dialog, values=ESCOLAS, state="readonly")
                    combo.set(escola_atual if escola_atual in ESCOLAS else ESCOLAS[0])
                    combo.pack(pady=5)
                    def salvar():
                        nova_escola = combo.get()
                        pag['escola'] = nova_escola
                        salvar_dados()
                        atualizar_lista()
                        dialog.destroy()
                    tk.Button(dialog, text="Salvar", command=salvar).pack(pady=10)
                    break

def on_right_click(event):
    """Mostra menu de contexto ao clicar com botão direito no nome da criança."""
    item = tree.identify('item', event.x, event.y)
    column = tree.identify('column', event.x, event.y)
    if column == '#1':  # Coluna Nome
        values = tree.item(item, 'values')
        if values and values[0] not in ("Nenhum pagamento cadastrado.",) and not values[0].startswith("Nenhum") and not values[0].startswith("Total"):
            nome = values[0]
            menu = tk.Menu(root, tearoff=0)
            menu.add_command(label="Editar Criança", command=lambda: editar_crianca(nome))
            menu.add_command(label="Adicionar Pagamento", command=lambda: adicionar_pagamento_para(nome))
            menu.add_command(label="Remover Criança", command=lambda: remover_crianca(nome))
            menu.post(event.x_root, event.y_root)

def editar_crianca(nome):
    """Edita o nome da criança."""
    novo_nome = simpledialog.askstring("Editar Criança", f"Digite o novo nome para {nome}:")
    if novo_nome and novo_nome.strip():
        novo_nome = novo_nome.strip()
        for pag in pagamentos:
            if pag['nome'] == nome:
                pag['nome'] = novo_nome
        salvar_dados()
        popular_combobox_criancas()
        atualizar_lista()
        messagebox.showinfo("Sucesso", f"Nome alterado para {novo_nome}.")
    else:
        messagebox.showwarning("Aviso", "Nome inválido.")

def adicionar_pagamento_para(nome):
    """Abre a tela de pagamentos mensais para a criança selecionada."""
    abrir_janela_crianca(nome)

def remover_crianca(nome):
    """Remove todas as informações da criança."""
    if messagebox.askyesno("Confirmar", f"Tem certeza que deseja remover todas as informações de {nome}?"):
        pagamentos[:] = [pag for pag in pagamentos if pag['nome'] != nome]
        salvar_dados()
        popular_combobox_criancas()
        atualizar_lista()
        messagebox.showinfo("Sucesso", f"Criança {nome} removida.")

def gerar_relatorio_pdf():
    """Gera relatório PDF das crianças que não pagaram até hoje."""
    hoje = datetime.now()
    data_relatorio = hoje.strftime('%d/%m/%Y')

    # Coletar crianças não pagas
    nao_pagaram = []
    for nome in obter_nomes_unicos():
        ultimo_pag = None
        for pag in pagamentos:
            if pag['nome'] == nome and pag.get('data'):
                try:
                    data_pag = datetime.strptime(pag['data'], '%Y-%m-%d')
                    if ultimo_pag is None or data_pag > ultimo_pag:
                        ultimo_pag = data_pag
                except:
                    pass
        if ultimo_pag is None or hoje - ultimo_pag > timedelta(days=25):
            nao_pagaram.append((nome, ultimo_pag.strftime('%d/%m/%Y') if ultimo_pag else 'Nunca pagou'))

    if not nao_pagaram:
        messagebox.showinfo("Relatório", "Todas as crianças estão em dia com os pagamentos.")
        return

    # Gerar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Relatório de Pagamentos Atrasados - {data_relatorio}", ln=True, align='C')
    pdf.ln(10)

    pdf.cell(100, 10, txt="Nome da Criança", border=1)
    pdf.cell(100, 10, txt="Último Pagamento", border=1, ln=True)

    for nome, ultimo in nao_pagaram:
        pdf.cell(100, 10, txt=nome, border=1)
        pdf.cell(100, 10, txt=ultimo, border=1, ln=True)

    # Salvar arquivo
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if file_path:
        pdf.output(file_path)
        messagebox.showinfo("Sucesso", f"Relatório salvo em {file_path}")

def abrir_dashboard_atrasados():
    """Abre uma janela com dashboard das crianças com pagamentos atrasados."""
    hoje = datetime.now()

    # Coletar crianças atrasadas
    atrasados = []
    for nome in obter_nomes_unicos():
        ultimo_pag = None
        escola = ""
        for pag in pagamentos:
            if pag['nome'] == nome and pag.get('data'):
                try:
                    data_pag = datetime.strptime(pag['data'], '%Y-%m-%d')
                    if ultimo_pag is None or data_pag > ultimo_pag:
                        ultimo_pag = data_pag
                        escola = pag.get('escola', '')
                except:
                    pass
        if ultimo_pag is None or hoje - ultimo_pag > timedelta(days=25):
            dias_atraso = (hoje - ultimo_pag).days if ultimo_pag else "Nunca pagou"
            ultimo_str = ultimo_pag.strftime('%d/%m/%Y') if ultimo_pag else 'Nunca pagou'
            atrasados.append((nome, escola, ultimo_str, dias_atraso))

    if not atrasados:
        messagebox.showinfo("Dashboard", "Nenhuma criança com pagamentos atrasados.")
        return

    # Criar janela
    window = tk.Toplevel(root)
    window.title("Dashboard - Pagamentos Atrasados")
    window.geometry("800x600")
    window.resizable(True, True)

    # Frame principal
    frame = tk.Frame(window)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Cabeçalho
    tk.Label(frame, text="Crianças com Pagamentos Atrasados", font=("Arial", 14, "bold")).pack(pady=10)

    # Tabela
    columns = ("Nome", "Escola", "Último Pagamento", "Dias em Atraso")
    tree_atrasados = ttk.Treeview(frame, columns=columns, show="headings", height=20)
    tree_atrasados.heading("Nome", text="Nome da Criança")
    tree_atrasados.heading("Escola", text="Escola")
    tree_atrasados.heading("Último Pagamento", text="Último Pagamento")
    tree_atrasados.heading("Dias em Atraso", text="Dias em Atraso")
    tree_atrasados.column("Nome", width=200, anchor=tk.W)
    tree_atrasados.column("Escola", width=150, anchor=tk.CENTER)
    tree_atrasados.column("Último Pagamento", width=120, anchor=tk.CENTER)
    tree_atrasados.column("Dias em Atraso", width=100, anchor=tk.CENTER)

    # Configurar tag para texto vermelho
    tree_atrasados.tag_configure('atrasado', foreground='red')

    # Scrollbar
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree_atrasados.yview)
    tree_atrasados.configure(yscroll=scrollbar.set)
    tree_atrasados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Preencher tabela
    for nome, escola, ultimo, dias in sorted(atrasados, key=lambda x: (x[1], x[0])):  # Ordenar por escola, depois por nome
        tree_atrasados.insert("", "end", values=(nome, escola, ultimo, dias), tags=('atrasado',))

    # Botão fechar
    tk.Button(frame, text="Fechar", command=window.destroy, bg="red", fg="white", font=("Arial", 10)).pack(pady=10)

def sair_app():
    """Fecha o app e salva os dados."""
    salvar_dados()
    root.quit()

# Cria a janela principal
root = tk.Tk()
root.title("Sistema de Pagamentos - Crianças (com Data)")
root.geometry("700x500")
root.resizable(True, True)

# Frame superior para filtro e botões
frame_superior = tk.Frame(root)
frame_superior.pack(pady=10)

# Label e Combobox para mês
tk.Label(frame_superior, text="Selecione o Mês:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
combo_meses = ttk.Combobox(frame_superior, state="readonly", width=15, font=("Arial", 10))
combo_meses.pack(side=tk.LEFT, padx=5)
combo_meses.bind('<<ComboboxSelected>>', on_selecao_mes)

# Label e Combobox para criança
tk.Label(frame_superior, text="Selecione a Criança:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
combo_criancas = ttk.Combobox(frame_superior, state="readonly", width=25, font=("Arial", 10))
combo_criancas.pack(side=tk.LEFT, padx=5)
combo_criancas.bind('<<ComboboxSelected>>', on_selecao_crianca)

# Label e Combobox para escola
tk.Label(frame_superior, text="Selecione a Escola:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
combo_escolas = ttk.Combobox(frame_superior, state="readonly", width=20, font=("Arial", 10))
combo_escolas.pack(side=tk.LEFT, padx=5)
combo_escolas.bind('<<ComboboxSelected>>', on_selecao_escola)

# Frame para botões
frame_botoes = tk.Frame(frame_superior)
frame_botoes.pack(side=tk.LEFT, padx=20)

btn_adicionar = tk.Button(frame_botoes, text="Adicionar Pagamento", command=adicionar_pagamento, bg="lightgreen", font=("Arial", 10))
btn_adicionar.pack(side=tk.TOP, pady=2)

btn_relatorio = tk.Button(frame_botoes, text="Gerar Relatório PDF", command=gerar_relatorio_pdf, bg="orange", font=("Arial", 10))
btn_relatorio.pack(side=tk.TOP, pady=2)

btn_dashboard = tk.Button(frame_botoes, text="Dashboard Atrasados", command=abrir_dashboard_atrasados, bg="yellow", font=("Arial", 10))
btn_dashboard.pack(side=tk.TOP, pady=2)

btn_sair = tk.Button(frame_botoes, text="Sair", command=sair_app, bg="red", fg="white", font=("Arial", 10))
btn_sair.pack(side=tk.TOP, pady=2)

columns = ("Nome", "Data", "Mês", "Escola", "Status", "Valor")
tree = ttk.Treeview(root, columns=columns, show="headings", height=20)
tree.heading("Nome", text="Nome da Criança")
tree.heading("Data", text="Data do Pagamento")
tree.heading("Mês", text="Mês")
tree.heading("Escola", text="Escola")
tree.heading("Status", text="Status")
tree.heading("Valor", text="Valor Pago")
tree.column("Nome", width=200, anchor=tk.W)
tree.column("Data", width=120, anchor=tk.CENTER)
tree.column("Mês", width=100, anchor=tk.CENTER)
tree.column("Escola", width=120, anchor=tk.CENTER)
tree.column("Status", width=80, anchor=tk.CENTER)
tree.column("Valor", width=120, anchor=tk.E)

# Configurar tags para cores
tree.tag_configure('pago', foreground='green')
tree.tag_configure('atrasado', foreground='red')
tree.tag_configure('nao_pago', foreground='black')

scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

tree.bind('<Double-1>', on_tree_double_click)

tree.bind('<Button-3>', on_right_click)

carregar_dados()
popular_combobox()
popular_combobox_criancas()
popular_combobox_escolas()
atualizar_lista()

root.mainloop()
