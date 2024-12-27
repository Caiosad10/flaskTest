import psycopg2 #Para o banco de dados
from psycopg2.extras import RealDictCursor #Extra para o banco de dados

from datetime import datetime

from flask import Flask #Para o desenvolvimento do app web

from flask import request, jsonify, render_template #Para adicionar uma rota que faça com que o usuario possa adicionar dados no banco de dados

from flask import redirect, url_for, flash, session #Servirá para adicionar uma notificação pop-up na tela do navegador



app = Flask(__name__)
app.secret_key = 'sua_chave_secreta' #Necessario para usar flash()

BD = {
    'database': 'agendamentos',
    'user': 'postgres',
    'password': 'BDPHP023',
    'host': 'localhost',
    'port': '5432'
}

def conexaoBD():
    return psycopg2.connect(
        dbname=BD['database'],
        user=BD['user'],
        password=BD['password'],
        host=BD['host'],
        port=BD['port'],
        options="-c client_encoding=UTF8"
    )
@app.route('/')

def home():
    return render_template('index.html')

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
            data_consulta = request.form.get('data_consulta')
            motivo = request.form.get('motivo')

            print(f'nome_tutor={nome_tutor}\ntelefone={telefone}\nemail={email}\nnome_pet={nome_pet}\nespecie={especie}\nraca={raca}\nidade={idade}\nsexo={sexo}\npeso={peso}\ndata consulta={data_consulta}')
            
            conexao = conexaoBD()
            cursor = conexao.cursor()

            #Iniciar transação
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
                "INSERT INTO pets (nome, especie, raca, idade, sexo, peso, tutor_id) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (nome_pet, especie, raca, idade, sexo, peso, tutor_id)
            )

            pet_id = cursor.fetchone()[0]
            print(f'pet_id={pet_id}')

            # Query para a tabela dos agendamentos
            cursor.execute(
                "INSERT INTO agendamento (data_horario, motivo, pet_id) VALUES (%s, %s, %s) RETURNING id",
                (data_consulta, motivo, pet_id)
            )

            consulta_id = cursor.fetchone()[0]
            print(f'consulta_id={consulta_id}')
            
            #Confirmar transação
            conexao.commit()

            cursor.close()
            conexao.close()
            
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
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

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

            for agendamento in agendamentos:
                agendamento['data_horario'] = agendamento['data_horario'].strftime('%d/%m/%Y %H:%M')

            return render_template('agendarRetorno.html', agendamentos=agendamentos)
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
                pets.nome AS pet_nome,
                agendamento.data_horario,
                agendamento.status,
                'consulta' AS tipo
            FROM
                agendamento
            INNER JOIN pets ON agendamento.pet_id = pets.id
            INNER JOIN tutores ON pets.tutor_id = tutores.id
            WHERE agendamento.status != 'cancelada'
                AND (agendamento.data_horario > CURRENT_TIMESTAMP OR agendamento.status != 'confirmado')
            ORDER BY agendamento.data_horario           
        """)
        consultas = cursor.fetchall()

        #Buscar retornos agendados
        cursor.execute("""
            SELECT 
                retornos.id AS retorno_id,
                tutores.nome AS tutor_nome,
                pets.nome AS pet_nome,
                retornos.data_retorno,
                retornos.status,
                'retorno' AS tipo
            FROM
                retornos
            INNER JOIN agendamento ON retornos.agendamento_id = agendamento.id
            INNER JOIN pets ON agendamento.pet_id = pets.id
            INNER JOIN tutores ON pets.tutor_id = tutores.id
            WHERE retornos.status != 'cancelada'
                AND (retornos.data_retorno > CURRENT_TIMESTAMP OR retornos.status != 'confirmado')
                       
            ORDER BY retornos.data_retorno
        """)
        retornos = cursor.fetchall()

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
        motivo = request.form.get('motivo')

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
        """, (motivo, agendamento_id))

        #Finalizar transação
        conexao.commit()

        return redirect(url_for('ver_agenda'))
    except Exception as e:
        #Desfazer transação
        conexao.rollback()
        print(f"Error : {str(e)}")
        return jsonify({'error': str(e)}), 500
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

        return redirect(url_for('ver_agenda'))
    except Exception as e:
        #Desfazer transação
        cursor.execute("ROLLBACK")
        print(f"Error : {str(e)}")
        return jsonify({'error': str(e)}), 500
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

        return redirect(url_for('ver_agenda'))
    except Exception as e:
        #Desfazer transação
        cursor.execute("ROLLBACK")
        print(f"Error : {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conexao.close()

@app.route('/cancelar_retorno/<int:retorno_id>', methods=['POST'])
def cancelar_retorno(retorno_id):
    conexao = conexaoBD()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)

    try:

        motivo_cancelamento = request.form.get('motivo')

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

        return redirect(url_for('ver_agenda'))
    except Exception as e:
        #Desfazer transação
        cursor.execute("ROLLBACK")
        print(f"Error : {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)