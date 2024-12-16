# Projeto de uma aplicação de agendamento para Doutores (mais especificamente: Veterinarios)

### Este projeto serve mais para uma pratica, utilizando framework *Flask* e fixando o conhecimento para a conectivade com o banco de dados!
---
Antes de tudo, vamos verificar o que eu fiz para poder iniciar o projeto:

![image](https://github.com/user-attachments/assets/22f7fd27-d0b8-474c-8165-7683e24aff58)

Com isso feito, podemos já ir inserindo os codigos.

---

## Codificação

Primeiramente criamos o nosso ` app `:

~~~python
app = Flask(__name__)
~~~

Logo em seguida, criamos uma variavel para fazer a conectividade com o banco de dados:

~~~python
BD = {
    'database': 'agendamentos',
    'user': 'postgres',
    'password': 'BDPHP023',
    'host': 'localhost',
    'port': '5432'
}
~~~

**_Os dados que são mostrados é meramente para teste!_**

Após inserir os dados para conectar o banco de dados, iremos fazer uma função que realizará a conexão de fato!

~~~python
def conexaoBD():
    return psycopg2.connect(
        dbname=BD['database'],
        user=BD['user'],
        password=BD['password'],
        host=BD['host'],
        port=BD['port'],
        options="-c client_encoding=UTF8"
    )
~~~

A questão ` options ` não é obrigatoria. Utilizei em meu codigo pois estava tendo uma incompatibilidade com o UTF-8.

---

### Toda essa parte a cima, foi somente para configurar: Importar Framework e bibliotecas; Criar uma instancia para criarmos nosso aplicativo; Fazer conexão com o banco de dados.

---

Depois de toda a configuração, criamos rotas, trabalhamos com rotas no Flask.

Como nossa aplicação, por enquanto, é web, devemos criar paginas HTML, então, uma das rotas, será a nossa ` home `. Criamos uma landing page simples com links

![image](https://github.com/user-attachments/assets/5b0a4348-a85f-4cee-bac5-e60dbfd5d88f)

Depois de criar a home, criamos tambem as outras paginas: ` marcar consulta ` e  ` agendar retorno ` (a fazer!).

--- 

Voltando para o codigo em python, criaremos a rota para o link ` marcar consulta `:

~~~python
@app.route('/marcarConsulta', methods=['GET','POST'])

def marcarConsulta():


    if request.method == 'POST':
        print("POST")
        try:

            # Obter os dados do formulário
            nome_tutor = request.form.get('nome_tutor')
            telefone = request.form.get('telefone')
            email = request.form.get('email')
            nome_pet = request.form.get('nome_pet')
            especie = request.form.get('especie')
            raca = request.form.get('raca')
            idade = request.form.get('idade')
            sexo = request.form.get('sexo')
            peso = request.form.get('peso')

            print(f'nome_tutor={nome_tutor}\ntelefone={telefone}\nemail={email}\nnome_pet={nome_pet}\nespecie={especie}\nraca={raca}\nidade={idade}\nsexo={sexo}\npeso={peso}')
            
            conexao = conexaoBD()
            cursor = conexao.cursor()

            # Query para a tabela dos tutores
            cursor.execute(
                "INSERT INTO tutores (nome, telefone, email) VALUES (%s, %s, %s) RETURNING id",
                (nome_tutor, telefone, email)
            )
            # Obter o ID do tutor inserido
            tutor_id = cursor.fetchone()[0]
            print(f'tutor_id={tutor_id}')

            # Query para a tabela dos pets
            cursor.execute(
                "INSERT INTO pets (nome, especie, raca, idade, sexo, peso, tutor_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (nome_pet, especie, raca, idade, sexo, peso, tutor_id)
            )
            
            conexao.commit()
            cursor.close()
            conexao.close()
            
            
            print("Consulta marcada com sucesso!")
            return jsonify({'message': 'Consulta marcada com sucesso!'}), 201
        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    if request.method == 'GET':
        print("GET")
    return render_template('marcarConsulta.html')
    
~~~
