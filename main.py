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
                <h1>Serviço de recomendação de investimentos</h1>
                <br/>
                <p>Metodo: POST</p>
                <p>Exemplo do corpo da mensagem:</p>
                <div style="border: solid 1px gray;padding: 5px;background-color: lightgray;width: 400px;">
                    <p>
                        {<br/>
                           &emsp;"Idade":22,<br/>
                           &emsp;"EstadoCivil":"S",<br/>
                           &emsp;"BillingCity":"S\\u00e3o Paulo",<br/>
                           &emsp;"NivelConhecimentoAtual":"0",<br/>
                           &emsp;"ScoreNivelConhecimento":"0",<br/>
                           &emsp;"PerfilInvestidor":"0",<br/>
                           &emsp;"RendaMensal":"1900",<br/>
                           &emsp;"ValorPatrimonio":"1000",<br/>
                           &emsp;"Ind_Guardado":"0",<br/>
                           &emsp;"ScoreRisco":"0",<br/>
                           &emsp;"ScoreObjetivos":"0",<br/>
                           &emsp;"ScoreSituacaoFinanceira":"0",<br/>
                           &emsp;"Soma_Investido_Total":"0"<br/>
                        }<br/>
                    </p>
                </div>
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
