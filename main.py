import psycopg2 #Para o banco de dados
from psycopg2.extras import RealDictCursor #Extra para o banco de dados

from datetime import datetime #Para trabalhar com datas

from flask import Flask #Para o desenvolvimento do app web

from flask import request, jsonify, render_template #Para adicionar uma rota que faça com que o usuario possa adicionar dados no banco de dados

from flask import redirect, url_for, flash, session #Servirá para adicionar uma notificação pop-up na tela do navegador

from datetime import datetime #Para trabalhar com datas (utilizado para adicionar o horário no banco de dados de "marcarConsulta")


app = Flask(__name__)
app.secret_key = 'sua_chave_secreta' #Necessario para usar flash()

#Conectividade com o banco de dados
BD = {
    'database': 'agendamentos',
    'user': 'postgres',
    'password': 'BDPHP023',
    'host': 'localhost',
    'port': '5432'
}

#Função para fazer a conexão com o banco de dados, iremos utilizar para todas as rotas quando necessario fazer registros no banco
def conexaoBD():
    return psycopg2.connect(
        dbname=BD['database'],
        user=BD['user'],
        password=BD['password'],
        host=BD['host'],
        port=BD['port'],
        options="-c client_encoding=UTF8"
    )

#Primeira Rota - Home
@app.route('/')

def home():
    return render_template('index.html')

#Rota para notificações em "verAgenda"
#@app.route('/notificacoes')

#def notificacoes():
    #return render_template('notificacoes.html')


#Rota para marcar consulta. O methods tem que ser GET e POST pois o "GET" serve para obter dados do banco ou do backend, e o "POST" serve para adicionar dados ao banco
@app.route('/marcarConsulta', methods=['GET','POST'])

#Função para marcar consulta
def marcarConsulta():

    #"requqest.method" significa que vamos fazer uma requisição do tipo POST, que é para adicionar dados ao banco de dados
    if request.method == 'POST': #Então se o request é do metodo POST
        print("POST") #Debug
        #"Try e Except" é para tratar erros e não fazer o programa parar. 
        try:
            #Inserimos os codigos normalmente dentro de "try", a diferença é que, como o nome já diz, ele tenta executar todos os codigos dentro dele, e se der erro, ele vai para o "except"

            # Obter os dados do formulário com "request.form.get". Com isso, criamos uma variavel que irá armazenar o dado que for inserido na pagina, é bom identificarmos o input com o mesmo nome em "for", "name" e "id".
            nome_tutor = request.form.get('nome_tutor') #O valor dentro do () representa o "name" do input no HTML
            telefone = request.form.get('telefone')
            email = request.form.get('email')
            nome_pet = request.form.get('nome_pet')
            especie = request.form.get('especie')
            raca = request.form.get('raca')
            idade = request.form.get('idade')
            idade_tipo = request.form.get('idade_tipo')
            sexo = request.form.get('sexo')
            peso = request.form.get('peso')
            data_consulta = request.form.get('data_consulta')
            motivo = request.form.get('motivo')
            hora_consulta = request.form.get('hora_consulta')
            data_consulta_str = request.form.get('data_consulta')


            #Combinar data e horario para criar um objeto datetime
            try:
                #Esse try dentro do try é para formatar a forma que a data vai ser armazenada no banco de dados
                agendamento_datetime = datetime.strptime(f"{data_consulta_str} {hora_consulta}", '%Y-%m-%d %H:%M') #Criamos a variavel para armazenar o valor, e utilizamos o "strptime" para converter a string para uma data, dentro do () passamos as variaveis que serão utilizadas para formatar a data e hora e a forma em que ela vai ser formatada
            except ValueError: #"ValueError" nesse contexto significa que houve um erro ao formatar a data/hora
                flash('Formato de data ou hora inválido.', 'error')
                return redirect(url_for('marcarConsulta'))

            #Debug para verificar se os dados foram recebidos
            print(f'nome_tutor={nome_tutor}\ntelefone={telefone}\nemail={email}\nnome_pet={nome_pet}\nespecie={especie}\nraca={raca}\nidade={idade}\nidade tipo = {idade_tipo}\nsexo={sexo}\npeso={peso}\ndata consulta={data_consulta}\nhora consulta={hora_consulta}\ndata consulta str={agendamento_datetime}')
            
            #Conecta com o banco utilizando a funcao conexaoBD
            conexao = conexaoBD()
            #Criamos um cursor, ele serve para interagir com o banco e fazer as Querys. Ele leva a variavel "conexão" + instancia "cursor()", isso fará com que ele possa interagir com o banco por meio de Querys
            cursor = conexao.cursor()

            #Para validar a query com o sintaxe SQL, utilizamos a instancia ".execute()", ele da a permissão para realizar a query

            #Iniciar transação para evitar erros
            cursor.execute("BEGIN")

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
                "INSERT INTO pets (nome, especie, raca, idade, sexo, peso, tutor_id, idade_tipo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (nome_pet, especie, raca, idade, sexo, peso, tutor_id, idade_tipo)
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
            
            #Finalizar transação
            conexao.commit() #Para confirmar a transação (querys), utilizamos a instancia ".commit()" com a "conexão" pois meio que envia toda essa query lá para o banco

            cursor.close() # Fechamos o cursor para encerrar a interacao com o BD
            conexao.close() # Fechamos a conexao para encerrar a conexao com o BD
            
            print("Consulta agendada com sucesso!")
            flash('Consulta agendada com sucesso!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            #Fazer rollback em caso de erro
            conexao.rollback()
            print(f"Error: {str(e)}")
            flash(f"Ocorreu um erro: {str(e)}", 'error')
            return redirect(url_for('marcarConsulta'))
    if request.method == 'GET':
        print("GET")
    return render_template('marcarConsulta.html')
    

@app.route('/agendarRetorno', methods=['GET', 'POST'])
def agendarRetorno():
    conexao = conexaoBD()
    cursor = conexao.cursor(cursor_factory=RealDictCursor) # "cursor_factory=RealDictCursor" servirá para retornar o resultado da query em um dicionario

    if request.method == 'POST':
        try:
            # Receber os dados do formulario
            agendamento_id = request.form.get('agendamento_id')
            data_retorno = request.form.get('data_retorno')
            motivo = request.form.get('motivo')
        
            # Inserir os dados na tabela de retornos
            cursor.execute(
                "INSERT INTO retornos (data_retorno, motivo, agendamento_id) VALUES (%s, %s, %s) RETURNING id",
                (data_retorno, motivo, agendamento_id)
            )
            conexao.commit()
            #cursor.close()
            #conexao.close()

            print("Retorno agendada com sucesso!")
            flash('Retorno agendada com sucesso!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f"Ocorreu um erro: {str(e)}", 'error')
            return redirect(url_for('agendarRetorno'))
        finally:
            cursor.close()
            conexao.close()

    elif request.method == 'GET':
        try:
            # Buscar todos os agendamentos para exibir no formulario
            cursor.execute("""
                SELECT
                    agendamento.id AS agendamento_id,
                    pets.nome AS pet_nome, 
                    agendamento.data_horario 
                FROM
                    agendamento 
                INNER JOIN pets ON agendamento.pet_id =pets.id
                ORDER BY agendamento.data_horario DESC
            """)
            agendamentos = cursor.fetchall() # Lista de agendamentos disponiveis
            print(agendamentos) #debug

            for agendamento in agendamentos: # Formata a data e hora para o formato brasileiro
                agendamento['data_horario'] = agendamento['data_horario'].strftime('%d/%m/%Y %H:%M')

            return render_template('agendarRetorno.html', agendamentos=agendamentos) #"agendamentos" recebe o "agendamentos" e passa para o template
        except Exception as e:
            print(f"Erro ao carregar agendamentos: {str(e)}")
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            conexao.close()
            
@app.route('/ver_agenda', methods=['GET', 'POST'])
def ver_agenda():
    conexao = conexaoBD()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    try:
        #Buscar consultas agendadas
        cursor.execute("""
            SELECT 
                agendamento.id AS agendamento_id,
                tutores.nome AS tutor_nome,
                tutores.telefone AS tutor_telefone,
                pets.nome AS pet_nome,
                agendamento.motivo,
                agendamento.data_horario,
                agendamento.status,
                'consulta' AS tipo
            FROM
                agendamento
            INNER JOIN pets ON agendamento.pet_id = pets.id
            INNER JOIN tutores ON pets.tutor_id = tutores.id
            WHERE agendamento.status IN ('pendente') AND agendamento.data_horario > CURRENT_TIMESTAMP
            ORDER BY agendamento.data_horario           
        """)
        consultas = cursor.fetchall() # Armazenar o resultado da query para consultas agendadas

        #Buscar retornos agendados
        cursor.execute("""
            SELECT 
                retornos.id AS retorno_id,
                tutores.nome AS tutor_nome,
                pets.nome AS pet_nome,
                retornos.motivo,
                retornos.data_retorno,
                retornos.status,
                'retorno' AS tipo
            FROM
                retornos
            INNER JOIN agendamento ON retornos.agendamento_id = agendamento.id
            INNER JOIN pets ON agendamento.pet_id = pets.id
            INNER JOIN tutores ON pets.tutor_id = tutores.id
            WHERE retornos.status IN ('pendente') AND retornos.data_retorno > CURRENT_TIMESTAMP
                       
            ORDER BY retornos.data_retorno
        """)
        retornos = cursor.fetchall() # Armazenar o resultado da query para retornos agendados

        return render_template('verAgenda.html', consultas=consultas, retornos=retornos)
    except Exception as e:
        print(f"Error : {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conexao.close()
    
#Rota para confirmar consulta
@app.route('/confirmar_consulta/<int:agendamento_id>', methods=['POST'])
def confirmar_consulta(agendamento_id):
    conexao = conexaoBD()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    try:
        #Obter observação fornecida
        observacores = request.form.get('observacoes')

        #Iniciar transação
        cursor.execute("BEGIN")

        #Atualizar o status do agendamento para confirmado
        cursor.execute("""
            UPDATE agendamento
            SET status = 'confirmado'
            WHERE id = %s
        """, (agendamento_id,))

        #Adicionar ao historico
        cursor.execute("""
            INSERT INTO historico (pet_id, data_consulta, observacoes) 
            SELECT pet_id, data_horario, %s
            FROM agendamento
            WHERE id = %s
        """, (observacores, agendamento_id))

        #Finalizar transação
        conexao.commit()

        print("Consulta confirmada com sucesso!")
        flash("Consulta confirmada com sucesso!", "success")
        return redirect(url_for('ver_agenda'))
    except Exception as e:
        #Desfazer transação
        conexao.rollback()
        print(f"Error : {str(e)}")
        flash(f"Erro ao confirmar consulta: {str(e)}", "error")
        return redirect(url_for('ver_agenda'))
    finally:
        cursor.close()
        conexao.close()

@app.route('/cancelar_consulta/<int:agendamento_id>', methods=['POST'])
def cancelar_consulta(agendamento_id):
    conexao = conexaoBD()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    try:
        #Iniciar transação
        cursor.execute("BEGIN")

        #Atualizar o status do agendamento para cancelado
        cursor.execute("""
            UPDATE agendamento
            SET status = 'cancelado'
            WHERE id = %s
        """, (agendamento_id,))

        #Finalizar transação
        conexao.commit()

        print("Consulta cancelada com sucesso!")
        flash("Consulta cancelada com sucesso!", "success")
        return redirect(url_for('ver_agenda'))
    except Exception as e:
        #Desfazer transação
        cursor.rollback()
        print(f"Erro ao cancelar consulta: {str(e)}")
        flash(f"Erro ao cancelar consulta: {str(e)}", "error")
        return redirect(url_for('ver_agenda'))
    finally:
        cursor.close()
        conexao.close()

@app.route('/confirmar_retorno/<int:retorno_id>', methods=['POST'])
def confirmar_retorno(retorno_id):
    conexao = conexaoBD()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    try:
        #Iniciar transação
        cursor.execute("BEGIN")

        #Atualizar o status do agendamento para confirmado
        cursor.execute("""
            UPDATE retornos
            SET status = 'confirmado'
            WHERE id = %s
        """, (retorno_id,))

        #Finalizar transação
        conexao.commit()

        print("Retorno confirmado com sucesso!")
        flash("Retorno confirmado com sucesso!", "success")
        return redirect(url_for('ver_agenda'))
    except Exception as e:
        #Desfazer transação
        cursor.rollback()
        print(f"Error : {str(e)}")
        flash(f"Erro ao confirmar retorno: {str(e)}", "error")
        return redirect(url_for('ver_agenda'))
    finally:
        cursor.close()
        conexao.close()

@app.route('/cancelar_retorno/<int:retorno_id>', methods=['POST'])
def cancelar_retorno(retorno_id):
    conexao = conexaoBD()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    try:

        motivo_cancelamento = request.form.get('motivo_cancelamento')

        #Iniciar transação
        cursor.execute("BEGIN")

        #Atualizar o status do agendamento para cancelado
        cursor.execute("""
            UPDATE retornos
            SET status = 'cancelado',
                motivo_cancelamento = %s
            WHERE id = %s
        """, (motivo_cancelamento,retorno_id))

        #Finalizar transação
        conexao.commit()

        print("Retorno cancelado com sucesso!")
        flash("Retorno cancelado com sucesso!", "success")
        return redirect(url_for('ver_agenda'))
    except Exception as e:
        #Desfazer transação
        cursor.rollback()
        print(f"Error : {str(e)}")
        flash(f"Erro ao cancelar retorno: {str(e)}", "error")
        return redirect(url_for('ver_agenda'))
    finally:
        cursor.close()
        conexao.close()

if __name__ == '__main__':
    app.run(debug=True)