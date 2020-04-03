# Modelo de recomendação de investimentos

Este projeto tem como objetivo aumentar a ativação de clientes através do excelente mecanismo de recomendação de produtos.

## Execução do middleware

Para subir o ambiente basta executar o comando abaixo:

    python main.py

## Dados da API

URL: http://localhost:5000/
Metodo: POST
Exemplo do corpo da mensagem:

    {
       "Idade":22,
       "EstadoCivil":"S",
       "BillingCity":"S\\u00e3o Paulo",
       "NivelConhecimentoAtual":"0",
       "ScoreNivelConhecimento":"0",
       "PerfilInvestidor":"0",
       "RendaMensal":"1900",
       "ValorPatrimonio":"1000",
       "Ind_Guardado":"0",
       "ScoreRisco":"0",
       "ScoreObjetivos":"0",
       "ScoreSituacaoFinanceira":"0",
       "Soma_Investido_Total":"0"
    }