import pickle
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import db

loaded_model = pickle.load(open('repository/model_cli_kmean.sav', 'rb'))

clientes = pd.read_csv("repository/clientes.csv", sep=';')

processado_fundos = pd.read_csv("repository/processado_fundos.csv")

processado_renda_fixa = pd.read_csv("repository/processado_renda_fixa.csv")

scalerVP = StandardScaler()
clientes['ValorPatrimonio'] = pd.to_numeric(clientes['ValorPatrimonio'].str.replace(',','.'))
scalerVP.fit(clientes[['ValorPatrimonio']])
scalerR = StandardScaler()
clientes['RendaMensal'] = pd.to_numeric(clientes['RendaMensal'].str.replace(',','.'))
scalerR.fit(clientes[['RendaMensal']])

def predict(client):
    return loaded_model.predict(client)

def cleanData(client):
    client['TipoCarteira__c_CDB']                           = 0
    client['TipoCarteira__c_Catálogo Padrão Tesouro Direto']= 0
    client['TipoCarteira__c_FIC de Fundo Cambial']          = 0
    client['TipoCarteira__c_FIC de Fundo Multimercado']     = 0
    client['TipoCarteira__c_FIC de Fundo de Ações']         = 0
    client['TipoCarteira__c_FIC de Fundo de Renda Fixa']    = 0
    client['TipoCarteira__c_Fundo Cambial']                 = 0
    client['TipoCarteira__c_Fundo Multimercado']            = 0
    client['TipoCarteira__c_Fundo de Ações']                = 0
    client['TipoCarteira__c_Fundo de Renda Fixa']           = 0
    client['TipoCarteira__c_LC']                            = 0
    client['TipoCarteira__c_LCA']                           = 0
    client['TipoCarteira__c_LCI']                           = 0

    client['Sao_Paulo']             = client['BillingCity'] == 'São Paulo'
    client['Rio']                   = client['BillingCity'] == 'Rio de Janeiro'
    client['Brasilia']              = client['BillingCity'] == 'Brasília'

    client['ValorPatrimonio'] = float(client['ValorPatrimonio'])
    client['RendaMensal'] = float(client['RendaMensal'])

    client['ValorPatrimonio_Scaler']= scalerVP.transform([[client['ValorPatrimonio']]])[0][0]
    client['RendaMensal_Scaler']    = scalerR.transform([[client['RendaMensal']]])[0][0]

    for estado in ['C', 'D', 'I', 'M', 'S', 'V']:

        if client['EstadoCivil'] != estado:
            client['EstadoCivil_' + estado] = 0
        else:
            client['EstadoCivil_' + estado] = 1

    client.pop('Id', None)
    client.pop('BillingCity', None)
    client.pop('Soma_Investido_Total', None)
    client.pop('ValorPatrimonio', None)
    client.pop('RendaMensal', None)
    client.pop('EstadoCivil', None)

    dados = {}
    for campo in client:
        dados[campo] = [client[campo]]

    df = pd.DataFrame.from_dict(dados)

    return df

def loadFundos(label):
    return processado_fundos[processado_fundos['label_cli'] == label]

def loadRendaFixa(label):
    return processado_renda_fixa[processado_renda_fixa['label_cli'] == label]

def recommendation(label, perfilInvestidor):
    remover_produtos = db.getRecommendation(label)

    df_remover_produtos = pd.DataFrame(remover_produtos, columns=['ProdutoId'])

    produtos_f = loadFundos(label)
    produtos_rf = loadRendaFixa(label)

    produtos_f = produtos_f[~produtos_f['ProdutoId'].isin(df_remover_produtos['ProdutoId'])]
    produtos_rf = produtos_rf[~produtos_rf['ProdutoId'].isin(df_remover_produtos['ProdutoId'])]

    if len(produtos_f) == 0:
        db.removerRecommendation(label)
        produtos_f = loadFundos(label)

    if len(produtos_rf) == 0:
        db.removerRecommendation(label)
        produtos_rf = loadRendaFixa(label)

    produtos_f = produtos_f.sort_values(by=['RentabilidadeAno__c'], ascending=False)

    count_fundos = 0
    count_renda_fixa = 0
    if perfilInvestidor == "0" or perfilInvestidor == "1" or perfilInvestidor == "2":
        count_fundos = 2
        count_renda_fixa = 8
    elif perfilInvestidor == "3":
        count_fundos = 3
        count_renda_fixa = 7
    elif perfilInvestidor == "4":
        count_fundos = 4
        count_renda_fixa = 6
    else:
        count_fundos = 6
        count_renda_fixa = 4

    # Split dos dados (Fundos)
    recomendacao_fundos = pd.DataFrame(data=None, columns=produtos_f.columns)

    serie_f = produtos_f.groupby('label')['label'].count()
    count_por_grupo = int(count_fundos/int(serie_f.count()))
    for index, value in serie_f.items():
        recomendacao_fundos = recomendacao_fundos.append(produtos_f[produtos_f['label'] == index].head(count_por_grupo))

    rest_por_grupo = int(count_fundos % int(serie_f.count()))
    if rest_por_grupo > 0:
        recomendacao_fundos = recomendacao_fundos.append(produtos_f[~produtos_f.isin(recomendacao_fundos)].dropna().head(rest_por_grupo))

    # Split dos dados (Renda fixa)
    recomendacao_renda_fixa = pd.DataFrame(data=None, columns=produtos_f.columns)

    serie_rf = produtos_rf.groupby('label')['label'].count()
    count_por_grupo = int(count_renda_fixa/int(serie_rf.count()))
    for index, value in serie_rf.items():
        recomendacao_renda_fixa = recomendacao_renda_fixa.append(produtos_rf[produtos_rf['label'] == index].head(count_por_grupo))

    rest_por_grupo = int(count_renda_fixa % int(serie_rf.count()))
    if rest_por_grupo > 0:
        recomendacao_renda_fixa = recomendacao_renda_fixa.append(produtos_rf[~produtos_rf.isin(recomendacao_renda_fixa)].dropna().head(rest_por_grupo))

    recomendacao_fundos['ProdutoId'].apply(putDbRecommendation, args=(label,))
    recomendacao_renda_fixa['ProdutoId'].apply(putDbRecommendation, args=(label,))

    recomendacao = {"fundos": recomendacao_fundos.to_dict('records'), "renda_fixa": recomendacao_renda_fixa.to_dict('records')}

    return recomendacao

def putDbRecommendation(produto, label):
    db.putRecommendation(label, produto)