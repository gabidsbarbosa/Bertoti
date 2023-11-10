from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import requests
from config import OPENWEATHER_APIKEY, TELEGRAM_TOKEN

TOKEN = TELEGRAM_TOKEN
BOT_USERNAME = '@como_esta_o_clima_bot'
API_KEY = OPENWEATHER_APIKEY

# Comandos iniciais
async def start_comand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Olá! Sou o bot Como está o clima. Como posso ajudar você hoje?')

async def help_comand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Olá! Estou aqui para fornecer informações climáticas. '
                                      'Use o comando /clima seguido do nome da cidade para obter os dados do clima.')
    
async def finish_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Bot is stopping...')
    await context.application.stop()


# Comando para obter informações climáticas para uma cidade específica
async def comando_clima(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        cidade = ' '.join(context.args)
        dados_clima = obter_dados_clima(cidade)

        if dados_clima:
            texto_resposta = f'Dados para {cidade}:\n{processar_dados_clima(dados_clima)}'
        else:
            texto_resposta = 'Não foi possível obter dados climáticos para a cidade especificada.'

        await update.message.reply_text(texto_resposta)
    except IndexError:
        await update.message.reply_text('Por favor, forneça o nome de uma cidade.')

# Função para obter dados climáticos de uma cidade
def obter_dados_clima(cidade: str):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    parametros = {
        "q": cidade,
        "appid": API_KEY,
        "units": "metric"  # obtem temperaturas em celsius
    }

    resposta = requests.get(base_url, params=parametros)
    dados = resposta.json()
    return dados

# Função para processamento de dados e criação do formato desejado
def processar_dados_clima(dados_clima):
    temperatura = dados_clima['main']['temp']
    umidade = dados_clima['main']['humidity']
    pressao = dados_clima['main']['pressure']
    velocidade_vento = dados_clima['wind']['speed']

    formatted_data = (
        f'Temperatura (°C): {temperatura}\n'
        f'Umidade (%): {umidade}\n'
        f'Pressão (hPa): {pressao}\n'
        f'Velocidade do Vento (m/s): {velocidade_vento}\n'
    )

    return formatted_data

# Lidando com mensagens de texto
async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_recebido = update.message.text.lower()

    if 'olá' in texto_recebido:
        resposta = 'Olá!!!'
    elif 'como você está' in texto_recebido:
        resposta = 'Estou bem, obrigado por perguntar!'
    else:
        resposta = 'Desculpe, não entendi o que você escreveu...'

    await update.message.reply_text(resposta)

# Lidando com erros
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'A atualização {update} causou um erro: {context.error}')

if __name__ == '__main__':
    print('Iniciando o bot...')
    app = Application.builder().token(TOKEN).build()

    # Adiciona os comandos
    app.add_handler(CommandHandler('start', start_comand))
    app.add_handler(CommandHandler('help', help_comand))
    app.add_handler(CommandHandler('clima', comando_clima))
    app.add_handler(CommandHandler('finish', finish_command))

    # Adiciona o manipulador de mensagens
    app.add_handler(MessageHandler(filters.TEXT, handle_response))

    # Adiciona o manipulador de erros
    app.add_error_handler(error)

    # Aguarda novas mensagens
    print('Aguardando novas mensagens...')
    app.run_polling(poll_interval=3)
