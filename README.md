# Chatbot de análise de sentimentos
Esse projeto se trata de um chatbot construído no Dialogflox CX que usa a ferramenta **Natural Language AI** para analisar a avaliação de um determinado produto da loja ficticia **FagTec**, uma loja de aparelhos eletronicos.

## Arquitetura do projeto
<img src="./images/architecture.png">

1. O usuário manda uma mensagem pelo prompt de um chat
2. Essa mensagem é encaminhado para o Dialogflox CX, e responde com base nas intenções, entidades, páginas e fluxos configurados
3. O Dialogflow envia a avaliação feita pelo usuário para a Cloud Function
4. A Cloud Function passa a avaliação para a Natural Languagem API
5. A Natural Languagem API retorna um objeto com a analise de sentimento (de -1 a 1) de volta para a Cloud Function
6. A Cloud Function salva o nome, a avaliação, o produto avaliado e o score analisado em uma tabela no BigQuery
7. A Cloud function retorna uma mensagem para o Dialogflow CX
8. O Dialogflow CX exibe a mensagem ao chat do usuário 

## Etapas do desenvolvimento
### Service Account
Primeiro, vamos criar uma service account para a nossa Cloud Function, para que ela possa ter acesso ao BigQuery
- Para criar a Service Account, execute o seguinte comando
```sh
gcloud iam service-accounts create virtual-assistant \
  --description="Service account that will be used in the Cloud Function to access BigQuery" \
  --display-name="Virtual Assistant"
```
- Agora, para atribuir a permissão de **BigQuery Admin** a Service Account, execute o seguinte comando:
```sh
gcloud projects add-iam-policy-binding $DEVSHELL_PROJECT_ID \
  --member="serviceAccount:virtual-assistant@$DEVSHELL_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.admin"
```
Agora, na console da Google Cloud, vá para <a href="https://console.cloud.google.com/iam-admin/iam?referrer=search">iam & admin</a>. Na seção IAM, podemos visualizar nossa Service account criada, com a permissão Bigquery Admin

<img src="./images/doc/iam.png"/>

### BigQuery
Agora, para configurar o BigQuery, vamos:
- No Cloud Shell, execute esse comando para criar um dataset no BigQuery chamado **evaluate_product**
```sh
bq mk evaluate_product
```
- Agora, execute o seguinte comando para criar uma tabela dentro do dataset criado
```sh
bq mk --table $DEVSHELL_PROJECT_ID:evaluate_product.evaluate Name:string,Product:string,Text:string,Score:float
```
  - Esse comando vai criar uma tabela com as seguintes schemas:
    - Name do tipo string para armazenar o nome da pessoa que irá fazer a avaliação
    - Product do tipo string para armazenar o produto avaliado
    - Text do tipo string para armazenar a avaliação enviada pelo usuário
    - Score como float que vai armazenar o valor de -1 a 1, referente a analise feita na avaliação enviada pelo usuário
      - Quanto menor o número (mais próximo de -1), pior a avaliação
  - O **$DEVSHELL_PROJECT_ID** é uma variável de ambiente que armazena do ID do seu projeto dentro da Google Cloud Platform

Agora, na console da Google Cloud, vá para <a href="https://console.cloud.google.com/bigquery">BigQuery</a> e visualize o dataset e tabela criado

<img src="./images/doc/BigQuery.png"/>