# api/telegram_poster.py
import json
import os
import asyncio # Usaremos asyncio para a versão mais recente da biblioteca
from dotenv import load_dotenv
from telegram import Bot

# --- Configuração ---
# Mova isso para um arquivo de configuração no futuro!
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Caminhos dos arquivos
ANALYSIS_FILE_PATH = "dados/clean/betting_analysis.json"
POSTED_BETS_LOG_PATH = "dados/log/posted_bets.log"

# --- Funções ---

def load_posted_bets_ids():
    """Carrega os IDs das apostas que já foram postadas."""
    if not os.path.exists(POSTED_BETS_LOG_PATH):
        return set()
    with open(POSTED_BETS_LOG_PATH, 'r') as f:
        return set(line.strip() for line in f)

def log_posted_bet_id(bet_id):
    """Salva o ID de uma aposta que acabou de ser postada."""
    os.makedirs(os.path.dirname(POSTED_BETS_LOG_PATH), exist_ok=True)
    with open(POSTED_BETS_LOG_PATH, 'a') as f:
        f.write(f"{bet_id}\n")

def format_bet_message(bet_details):
    """Formata os detalhes da aposta em uma mensagem legível para o Telegram."""
    
    # Emojis para dar um toque visual
    player_emoji = "🎾"
    odds_emoji = "📊"
    stake_emoji = "💰"
    edge_emoji = "📈"
    confidence_emoji = "⭐"

    message = (
        f"{player_emoji} *Oportunidade de Aposta em Tênis* {player_emoji}\n\n"
        f"**Partida:** {bet_details['home_player']} vs {bet_details['away_player']}\n"
        f"**Torneio:** {bet_details['tournament']}\n"
        f"**Aposta em:** *{bet_details['player_to_bet_on']}*\n\n"
        f"{odds_emoji} *Análise de Valor:*\n"
        f"  - *Odd do Mercado:* `{bet_details['market_odd']}`\n"
        f"  - *Probabilidade Justa (Calculada):* `{bet_tetaidetails['fair_odd']:.2f}`\n"
        f"  - *Probabilidade Implícita:* `{bet_details['implied_probability']:.2%}`\n"
        f"  - *Probabilidade Calculada:* `{bet_details['win_probability']:.2%}`\n\n"
        f"{edge_emoji} *Vantagem (Edge):* `{bet_details['edge']:.2%}`\n"
        f"{confidence_emoji} *Confiança:* `{bet_details['confidence_score']:.2f} / 10`\n\n"
        f"{stake_emoji} *Sugestão de Stake (Kelly Criterion):* `{bet_details['kelly_stake']:.2%}` da sua banca."
    )
    return message

async def main():
    """Função principal para ler análises e postar no Telegram."""
    
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    print("--- Iniciando postador do Telegram ---")

    if not os.path.exists(ANALYSIS_FILE_PATH):
        print(f"Arquivo de análise '{ANALYSIS_FILE_PATH}' não encontrado. Encerrando.")
        return

    with open(ANALYSIS_FILE_PATH, 'r') as f:
        try:
            bets = json.load(f)
        except json.JSONDecodeError:
            print("Arquivo de análise vazio ou corrompido. Encerrando.")
            return

    if not bets:
        print("Nenhuma oportunidade de aposta encontrada no arquivo. Encerrando.")
        return

    posted_bet_ids = load_posted_bets_ids()
    new_bets_posted_count = 0

    for bet in bets:
        # Cria um ID único para a partida para evitar repostagens
        bet_id = f"{bet['match_id']}-{bet['player_to_bet_on']}"

        if bet_id in posted_bet_ids:
            print(f"Aposta para '{bet['player_to_bet_on']}' na partida {bet['match_id']} já foi postada. Ignorando.")
            continue
        
        print(f"Nova aposta encontrada para '{bet['player_to_bet_on']}'. Formatando e enviando...")
        
        message = format_bet_message(bet)
        
        try:
            await bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=message,
                parse_mode='Markdown' # ou 'HTML'
            )
            print(f"Mensagem enviada para o canal {TELEGRAM_CHANNEL_ID} com sucesso!")
            
            # Se o envio for bem-sucedido, registre o ID
            log_posted_bet_id(bet_id)
            new_bets_posted_count += 1

        except Exception as e:
            print(f"Erro ao enviar mensagem para o Telegram: {e}")

    print(f"--- Processo concluído. {new_bets_posted_count} nova(s) aposta(s) postada(s). ---")

if __name__ == "__main__":
    # Para rodar o script diretamente
    asyncio.run(main())