from flask import Flask
from flask import request
import db
import processar_ml

app = Flask(__name__)

@app.route('/')
def index():
    html = '''
        <html>
            <body>
                <h1>Serviço de recomendação</h1>
                <p></p>
            </body>
        </html>
    '''
    return html


@app.route('/', methods=['POST'])
def incluirElemento():
    requisicao = request.get_json(force=True)

    client = processar_ml.cleanData(requisicao)

    predict = processar_ml.predict(client)

    print("Grupo de cliente = " + str(predict[0]))

    recommendation = processar_ml.recommendation(predict[0], requisicao['PerfilInvestidor'])

    return recommendation

if __name__ == '__main__':
    # Inicia o banco de dados de controle
    db.initDb()

    app.run(host="0.0.0.0")
