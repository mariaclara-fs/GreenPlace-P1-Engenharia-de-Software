from flask import Flask, url_for, session, flash, render_template, redirect, request
import csv
import os

# Inicializa aa aplicação Flask
app = Flask(__name__)

# Chave secreta de sessões
app.secret_key = 'chave-secreta-aqui'

# Caminho para arquivos de dados
data_dir =  'data'
cadastro_file = os.path.join(data_dir, 'cadastro_dos_usuarios.csv')

# cria o arquivo CSV se ele não existe
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Vai garatir o cabeçalho correto para o arquivo csv
if not os.path.exists(cadastro_file):
    with open(cadastro_file, mode='w', encoding='utf-8', newline='') as arquivo_csv:
        escritor = csv.DictWriter(arquivo_csv, fieldnames=['perfil','cpf','nome','cnpj','nome_empresa','senha'])
        escritor.writeheader()

# Importando as blueprints
from app.usuario_comum import user_bp
from app.empresas import empresa_bp

# Registrando as blueprints na aplicação
app.register_blueprint(user_bp)
app.register_blueprint(empresa_bp, url_prefix='/empresas')

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    """
    lógica da página de cadastro
    """
    if request.method == 'POST':
        """
        Vai abrir o arquivo em modo de append, 'a', em que ele  vai fazer alterações sem apagar o que já existe
        """
        with open(cadastro_file, mode='a',  encoding='utf-8', newline='') as arquivo_csv:
            escrever = csv.DictWriter(arquivo_csv, fieldnames=['perfil','cpf','nome','cnpj','nome_empresa','senha'])
            # O request.form já tem as colunas nomeadas corretamente
            escrever.writerow(request.form.to_dict())
        flash('Cadastro realizado com sucesso! Faça seu  login', 'success')
        return redirect(url_for('login'))
    
    return render_template('cadastro.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    """
    Rota GET/POST /login
    Exibe o formulário e processa autenticação
    """
    if request.method == 'GET':
        # Caso já esteja logado
        if 'user_role' in session:
            return redirect(url_for('index'))
        else:
            return render_template('login.html')
    elif request.method ==  'POST':
        cpf = request.form.get('cpf')
        cnpj = request.form.get('cnpj')
        senha =  request.form.get('senha')
        
        # Quando enviar o form como usuário empresa
        if cpf == None and cnpj != None:
            with open('data/cadastro_dos_usuarios.csv', mode='r', encoding='utf-8') as arquivo_csv:
                # Armazena os dados em um dicionário
                leitor = csv.DictReader(arquivo_csv)

                # Passa por cada linha do dicionário
                for linha in leitor:
                    # Caso ache o CNPJ
                    if linha.get('cnpj') == cnpj:
                        # Verifica se a senha corresponde e, se sim, procede login
                        if linha.get('senha') == senha:
                            username = linha.get('nome')
                            flash(f'Login bem sucedido, bem vindo(a) {username}!', 'success')
                            session['user_role'] = 'empresa'
                            return redirect(url_for('index'))
                        else:
                            break
                # Caso não ache ou senha não corresponda, exibe mensagem de erro
                flash('CNPJ ou senha incorretos.', 'error')

        # Quando enviar o form como usuário comum
        elif cpf != None and cnpj == None:
            with open('data/cadastro_dos_usuarios.csv', mode='r', encoding='utf-8') as arquivo_csv:
                # Armazena os dados em um dicionário
                leitor = csv.DictReader(arquivo_csv)
                for linha in leitor:
                    # Caso ache o CPF
                    if linha.get('cpf') == cpf:
                        # Verifica se a senha corresponde e, se sim, procede login
                        if linha.get('senha') == senha:
                            username = linha.get('nome')
                            flash(f'Login bem sucedido, bem vindo(a) {username}!', 'success')
                            session['user_role'] = 'user'
                            return redirect(url_for('index'))
                        else:
                            break
                # Caso não ache ou senha não corresponda, exibe mensagem de erro
                flash('CPF ou senha incorretos.', 'error')
                return redirect(url_for('login'))
        else:
            flash('Digite um CPF/CNPJ válido', 'error')


# Ponto de entrada da aplicação
if __name__ == '__main__':
    app.run(debug=True)