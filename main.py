import psycopg2 #Para o banco de dados

from flask import Flask #Para o desenvolvimento do app web

from flask import request, jsonify, render_template #Para adicionar uma rota que faça com que o usuario possa adicionar dados no banco de dados

app = Flask(__name__)

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
    

@app.route('/adicionarPet', methods=['GET', 'POST'])
def adicionarPet():

    if request.method == 'POST':
        print("POST")
        try:
            nome = request.form.get('nome')
            especie = request.form.get('especie')
            raca = request.form.get('raca')
            idade = request.form.get('idade')
            sexo = request.form.get('sexo')
            peso = request.form.get('peso')
            tutor_id = request.form.get('tutor_id')
            print(f'nome={nome}, especie={especie}, raca={raca}, idade={idade}, sexo={sexo}, peso={peso}, tutor_id={tutor_id}')
            conexao = conexaoBD()
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO pets (nome, especie, raca, idade, sexo, peso, tutor_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (nome, especie, raca, idade, sexo, peso, tutor_id)
            )
            conexao.commit()
            cursor.close()
            conexao.close()
            if cursor.rowcount == 0:
                print("Pet adicionado com sucesso!")
                return jsonify({'message': 'Pet adicionado com sucesso!'}), 201
        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    if request.method == 'GET':
        print("GET")
    return render_template('adicionarPet.html')




    '''data = request.json
    nome = data.get('nome')
    especie = data.get('especie')
    raca = data.get('raca')
    idade = data.get('idade')
    sexo = data.get('sexo')
    peso = data.get('peso')
    tutor_id = data.get('tutor_id')

    try:
        conexao = conexaoBD()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO pets (nome, especie, raca, idade, sexo, peso, tutor_id), VALUES (%s, %s, %s, %s, %s)",
            (nome, especie, raca, idade, sexo, peso, tutor_id)
        )
        conexao.commit()
        cursor.close()
        conexao.close()
        return jsonify({'message': 'Pet adicionado com sucesso!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
'''
if __name__ == '__main__':
    app.run(debug=True)