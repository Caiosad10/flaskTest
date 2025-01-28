# Projeto de uma aplicação de agendamento para Doutores (mais especificamente: Veterinarios)

### Este projeto serve mais para uma pratica, utilizando framework *Flask* e fixando o conhecimento para a conectivade com o banco de dados!
---
Antes de tudo, vamos verificar o que eu fiz para poder iniciar o projeto:

![image](https://github.com/user-attachments/assets/fc3b4daa-004c-4f7f-a95f-872523fcee06)


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

### Tudo o que foi explicado agora foi somente para configurar nosso ambiente para o projeto. Importamos o Framework e suas bibliotecas; Criamos uma instancia para criar nosso aplicativo; Fazemos a conexão com o banco de dados.

---

Depois de toda a configuração, criamos as rotas, nela conterá toda a regra de negócio.

Como nossa aplicação é web, devemos criar paginas HTML, então, uma das rotas, será a nossa ` home `, essa rota tem que fazer renderizar a página Home. 

Para isso, criamos uma landing page simples, já estilizada, com 3 botões: 

![image](https://github.com/user-attachments/assets/94dd9baa-8d48-49d5-8705-97ffe9eacdfa)


Os 3 botões são links para outras de nossas páginas: ` Marcar Consulta `, ` Agendar Retorno `, ` Ver Agenda `.

--- 



Voltando para o codigo em python, criaremos a rota para a pagina ` Marcar Consulta `. A página em si é para inserir dados de cadastro, ela solicita dados do tutor, descrição do pet e a seleção para quando será a consulta!

A rota servirá para coletar os dados do formulário e registrar no banco de dados através de uma Query. Veja a estrutura da rota:

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
            idade_tipo = request.form.get('idade_tipo')
            sexo = request.form.get('sexo')
            peso = request.form.get('peso')
            data_nascimento = request.form.get('data_nascimento')
            data_consulta = request.form.get('data_consulta')
            motivo = request.form.get('motivo')
            hora_consulta = request.form.get('hora_consulta')
            data_consulta_str = request.form.get('data_consulta')

            #Combinar data e horario para criar um objeto datetime
            try:
                agendamento_datetime = datetime.strptime(f"{data_consulta_str} {hora_consulta}", '%Y-%m-%d %H:%M')
                #Criamos a variavel para armazenar o valor, e utilizamos o "strptime" para converter a string para uma data, dentro do () passamos as variaveis que serão utilizadas para formatar a data e hora e a forma em que ela vai ser formatada
            except ValueError:
                flash('Formato de data ou hora inválido.', 'error')
                return redirect(url_for('marcarConsulta'))
                #"ValueError" nesse contexto significa que houve um erro ao formatar a data/hora
            #Debug para saber se os valores estão corretos
            print(f'nome_tutor={nome_tutor}\ntelefone={telefone}\nemail={email}\nnome_pet={nome_pet}\nespecie={especie}\nraca={raca}\nidade={idade}\nsexo={sexo}\npeso={peso}')

            #Conexão com o banco de dados
            conexao = conexaoBD()
            #Criamos um cursor, ele serve para interagirmos com o banco e fazer as querys
            cursor = conexao.cursor()

            # Query para a tabela dos tutores
            cursor.execute(
                "INSERT INTO tutores (nome, telefone, email) VALUES (%s, %s, %s) RETURNING id",
                (nome_tutor, telefone, email)
            )
            # Obter o ID do tutor inserido
            tutor_id = cursor.fetchone()[0]
            print(f'tutor_id={tutor_id}')

            # Função para calcular a idade do pet mediante a data de nascimento
            def calcular_idade_pet(data_nascimento):
                if data_nascimento:
                    today = date.today()
                    age = today.year - data_nascimento.year

                    if today.month < data_nascimento.month or (today.month == data_nascimento.month and today.day < data_nascimento.day):
                        age -=1

                    # Calcular a diferença em meses
                    meses = (today.year - data_nascimento.year) * 12 + (today.month - data_nascimento.month)

                    if meses < 12:
                        return meses, 'Meses'
                    else:
                        return age, 'Anos'
                else:
                    return None, None

            # Verificar se a data de nascimento existe, se não calcular a idade
            if data_nascimento:
                idade, idade_tipo = calcular_idade_pet(datetime.strptime(data_nascimento, '%Y-%m-%d').date())
            else:
                data_nascimento = None

            # Query para a tabela dos pets
            cursor.execute(
                "INSERT INTO pets (nome, especie, raca, idade, sexo, peso, tutor_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (nome_pet, especie, raca, idade, sexo, peso, tutor_id)
            )
            # Obter o ID do pet inserido
            pet_id = cursor.fetchone()[0]
            print(f'pet_id={pet_id}')

            # Query para a tabela dos agendamentos
            cursor.execute(
                "INSERT INTO agendamento (data_horario, motivo, pet_id) VALUES (%s, %s, %s) RETURNING id",
                (agendamento_datetime, motivo, pet_id)
            )
            # Obter o ID do agendamento inserido
            consulta_id = cursor.fetchone()[0]
            print(f'consulta_id={consulta_id}')
            
            conexao.commit()
            cursor.close()
            conexao.close()
            
            print("Consulta agendada com sucesso!")
            flash('Consulta agendada com sucesso!', 'success')
            return redirect(url_for('home'))
        except psycopg2.Error as e:
            conexao.rollback()
            print(f"Erro no banco de dados: {str(e)}")
            flash(f"Ocorreu um erro no banco de dados: {str(e)}", 'error')
            return redirect(url_for('marcarConsulta'))    
        except Exception as e:
            #Fazer rollback em caso de erro
            conexao.rollback()
            print(f"Error inesperado: {str(e)}")
            flash(f"Ocorreu um erro inesperado: {str(e)}", 'error')
            return redirect(url_for('marcarConsulta'))
    if request.method == 'GET':
        print("GET")
    return render_template('marcarConsulta.html')
~~~
