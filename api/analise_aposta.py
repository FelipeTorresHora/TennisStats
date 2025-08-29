import json
import os

def analyze_betting_opportunities(collected_data, min_odds=1.60):
    """
    Analisa oportunidades de apostas baseadas em estatísticas com odds mínimas
    
    Args:
        collected_data: Lista de eventos coletados com odds e estatísticas
        min_odds: Odds mínimas para considerar a aposta (default: 1.60)
    
    Returns:
        Lista de oportunidades de apostas ranqueadas por valor esperado
    """
    
    betting_opportunities = []
    
    for event in collected_data:
        if not event.get('odds_bet365') or len(event['odds_bet365']) == 0:
            continue
            
        participant1 = event['participant1']
        participant2 = event['participant2']
        
        # Verificar se ambos jogadores têm estatísticas válidas
        if (participant1.get('stats') == "N/A" or 
            participant2.get('stats') == "N/A" or
            not participant1.get('stats') or 
            not isinstance(participant1.get('stats'), dict) or
            not isinstance(participant2.get('stats'), dict)):
            continue
        
        p1_stats = participant1['stats']
        p2_stats = participant2['stats']
        
        # Analisar odds de vitória (Winner/Match Winner)
        match_winner_odds = {}
        for odd in event['odds_bet365']:
            if odd['market'] in ['Match Winner', 'Winner', 'Moneyline']:
                try:
                    odds_value = float(odd['odds'])
                    if odds_value >= min_odds:
                        match_winner_odds[odd['outcome']] = odds_value
                except (ValueError, TypeError):
                    continue
        
        if not match_winner_odds:
            continue
        
        # Calcular métricas de performance para cada jogador
        p1_metrics = calculate_player_performance_metrics(p1_stats)
        p2_metrics = calculate_player_performance_metrics(p2_stats)
        
        # Analisar cada outcome (assumindo "1" = participant1, "2" = participant2)
        for outcome, odds_value in match_winner_odds.items():
            implied_prob = 1 / odds_value
            
            # Mapear outcome para jogador
            if outcome == "1":
                player_stats = p1_metrics
                player_name = participant1['name_api']
                opponent_stats = p2_metrics
                player_raw_stats = p1_stats
                opponent_raw_stats = p2_stats
            elif outcome == "2":
                player_stats = p2_metrics
                player_name = participant2['name_api']
                opponent_stats = p1_metrics
                player_raw_stats = p2_stats
                opponent_raw_stats = p1_stats
            else:
                continue
            
            # Calcular probabilidade estatística de vitória
            statistical_prob = calculate_win_probability(player_stats, opponent_stats)
            
            # Calcular valor esperado da aposta apenas se há edge positivo
            if statistical_prob > implied_prob:
                edge = statistical_prob - implied_prob
                expected_value = (statistical_prob * (odds_value - 1)) - ((1 - statistical_prob) * 1)
                
                # Calcular confiança baseada na qualidade dos dados
                confidence = calculate_confidence_score(player_raw_stats, opponent_raw_stats)
                
                betting_opportunity = {
                    'event_id': event['event_id'],
                    'tournament': event['tournament_name'],
                    'match': f"{participant1['name_api']} vs {participant2['name_api']}",
                    'recommended_bet': f"{player_name} to win",
                    'odds': odds_value,
                    'implied_probability': round(implied_prob * 100, 2),
                    'statistical_probability': round(statistical_prob * 100, 2),
                    'edge': round(edge * 100, 2),
                    'expected_value': round(expected_value * 100, 2),
                    'confidence_score': round(confidence * 100, 2),
                    'reasoning': generate_betting_reasoning(player_raw_stats, opponent_raw_stats, player_name, participant1['name_api'], participant2['name_api']),
                    'risk_level': categorize_risk_level(edge, confidence),
                    'event_date': event.get('event_date'),
                    'event_time': event.get('event_time'),
                    'player_metrics': {
                        'recommended_player': player_stats,
                        'opponent': opponent_stats
                    }
                }
                
                betting_opportunities.append(betting_opportunity)
    
    # Ordenar por valor esperado e confiança
    betting_opportunities.sort(key=lambda x: (x['expected_value'], x['confidence_score']), reverse=True)
    
    return betting_opportunities

def calculate_player_performance_metrics(player_stats):
    """Calcula métricas de performance do jogador baseado na estrutura real dos dados"""
    metrics = {
        'service_dominance': 0,
        'serve_efficiency': 0,
        'overall_rating': 0,
        'raw_stats': player_stats  # Manter stats originais para referência
    }
    
    try:
        # Métricas de saque baseadas nos dados disponíveis
        aces_per_match = float(player_stats.get('avg_aces_match', 0))
        dbl_faults = float(player_stats.get('avg_dbl_faults_match', 0))
        first_serve_pct = float(player_stats.get('first_serve_pct', 0))
        first_serve_won_pct = float(player_stats.get('first_serve_points_won_pct', 0))
        second_serve_won_pct = float(player_stats.get('second_serve_points_won_pct', 0))
        serve_rating = float(player_stats.get('serve_rating', 0))
        service_games_won_pct = float(player_stats.get('service_games_won_pct', 0))
        
        # Calcular dominância no saque (0-1)
        # Normalizar aces (assumindo máximo de 20 aces por partida como excelente)
        aces_score = min(1.0, aces_per_match / 20)
        
        # Penalizar duplas faltas (assumindo máximo de 8 como muito ruim)
        dbl_faults_penalty = max(0, 1 - (dbl_faults / 8))
        
        # Combinar métricas de saque
        metrics['service_dominance'] = (
            aces_score * 0.25 +
            (first_serve_pct / 100) * 0.2 +
            (first_serve_won_pct / 100) * 0.25 +
            (second_serve_won_pct / 100) * 0.2 +
            dbl_faults_penalty * 0.1
        )
        
        # Eficiência geral do saque
        metrics['serve_efficiency'] = (
            (service_games_won_pct / 100) * 0.7 +
            min(1.0, serve_rating / 350) * 0.3  # Normalizar rating
        )
        
        # Rating geral (combinação de todas as métricas)
        metrics['overall_rating'] = (
            metrics['service_dominance'] * 0.4 +
            metrics['serve_efficiency'] * 0.6
        )
        
    except (ValueError, TypeError) as e:
        print(f"Erro ao calcular métricas: {e}")
    
    return metrics

def calculate_win_probability(player_metrics, opponent_metrics):
    """Calcula probabilidade de vitória baseada nas métricas"""
    
    # Pesos para diferentes aspectos do jogo
    weights = {
        'service_dominance': 0.35,
        'serve_efficiency': 0.45,
        'overall_rating': 0.2
    }
    
    player_score = 0
    opponent_score = 0
    
    for metric, weight in weights.items():
        player_value = player_metrics.get(metric, 0)
        opponent_value = opponent_metrics.get(metric, 0)
        
        # Comparação relativa com ajuste para evitar divisão por zero
        total_value = player_value + opponent_value
        if total_value > 0:
            player_advantage = player_value / total_value
        else:
            player_advantage = 0.5  # Neutro se ambos são zero
        
        player_score += player_advantage * weight
        opponent_score += (1 - player_advantage) * weight
    
    # Normalizar para probabilidade
    total_score = player_score + opponent_score
    if total_score > 0:
        return player_score / total_score
    else:
        return 0.5  # 50-50 se não há dados suficientes

def calculate_confidence_score(player1_stats, player2_stats):
    """Calcula score de confiança baseado na qualidade dos dados"""
    
    # Verificar se ambos jogadores têm dados completos
    required_fields = ['avg_aces_match', 'first_serve_pct', 'first_serve_points_won_pct', 
                      'second_serve_points_won_pct', 'serve_rating', 'service_games_won_pct']
    
    p1_completeness = sum(1 for field in required_fields 
                         if player1_stats.get(field) not in [None, 0, ''])
    p2_completeness = sum(1 for field in required_fields 
                         if player2_stats.get(field) not in [None, 0, ''])
    
    # Confiança baseada na completude dos dados (0-1)
    avg_completeness = (p1_completeness + p2_completeness) / (2 * len(required_fields))
    
    return avg_completeness

def generate_betting_reasoning(p1_stats, p2_stats, recommended_player, p1_name, p2_name):
    """Gera explicação detalhada para a recomendação de aposta"""
    reasons = []
    
    try:
        # Determinar qual jogador foi recomendado
        if recommended_player == p1_name:
            player_stats = p1_stats
            opponent_stats = p2_stats
        else:
            player_stats = p2_stats
            opponent_stats = p1_stats
        
        # Comparar aces
        p_aces = float(player_stats.get('avg_aces_match', 0))
        o_aces = float(opponent_stats.get('avg_aces_match', 0))
        if p_aces > o_aces + 1:  # Diferença significativa
            reasons.append(f"Superior ace rate ({p_aces:.1f} vs {o_aces:.1f}/match)")
        
        # Comparar duplas faltas
        p_df = float(player_stats.get('avg_dbl_faults_match', 0))
        o_df = float(opponent_stats.get('avg_dbl_faults_match', 0))
        if p_df < o_df - 0.5:  # Menos duplas faltas
            reasons.append(f"Fewer double faults ({p_df:.1f} vs {o_df:.1f}/match)")
        
        # Comparar primeiro saque
        p_first_serve = float(player_stats.get('first_serve_points_won_pct', 0))
        o_first_serve = float(opponent_stats.get('first_serve_points_won_pct', 0))
        if p_first_serve > o_first_serve + 2:
            reasons.append(f"Better first serve efficiency ({p_first_serve:.1f}% vs {o_first_serve:.1f}%)")
        
        # Comparar segundo saque
        p_second_serve = float(player_stats.get('second_serve_points_won_pct', 0))
        o_second_serve = float(opponent_stats.get('second_serve_points_won_pct', 0))
        if p_second_serve > o_second_serve + 3:
            reasons.append(f"Stronger second serve ({p_second_serve:.1f}% vs {o_second_serve:.1f}%)")
        
        # Comparar rating de saque
        p_rating = float(player_stats.get('serve_rating', 0))
        o_rating = float(opponent_stats.get('serve_rating', 0))
        if p_rating > o_rating + 10:
            reasons.append(f"Higher serve rating ({p_rating:.1f} vs {o_rating:.1f})")
        
        # Comparar games de saque ganhos
        p_service_games = float(player_stats.get('service_games_won_pct', 0))
        o_service_games = float(opponent_stats.get('service_games_won_pct', 0))
        if p_service_games > o_service_games + 2:
            reasons.append(f"Better service game hold ({p_service_games:.1f}% vs {o_service_games:.1f}%)")
    
    except (ValueError, TypeError):
        reasons.append("Statistical advantage based on available metrics")
    
    return "; ".join(reasons) if reasons else "Marginal statistical advantage based on overall performance metrics"

def categorize_risk_level(edge, confidence):
    """Categoriza o nível de risco da aposta"""
    if edge >= 8 and confidence >= 0.8:
        return "LOW"
    elif edge >= 4 and confidence >= 0.6:
        return "MEDIUM"
    else:
        return "HIGH"

def print_betting_recommendations(opportunities, top_n=10):
    """Imprime as melhores recomendações de apostas"""
    
    print(f"\\n🎯 TOP {min(top_n, len(opportunities))} BETTING OPPORTUNITIES (Odds ≥ 1.60)")
    print("=" * 100)
    
    if not opportunities:
        print("❌ No betting opportunities found with the current criteria.")
        print("\\nPossible reasons:")
        print("• No events with valid statistics for both players")
        print("• No odds ≥ 1.60 available")
        print("• Statistical probabilities don't exceed implied probabilities")
        return []
    
    for i, opp in enumerate(opportunities[:top_n], 1):
        risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
        
        print(f"\\n#{i} {risk_emoji.get(opp['risk_level'], '⚪')} {opp['risk_level']} RISK")
        print(f"🎾 Match: {opp['match']}")
        print(f"🏆 Tournament: {opp['tournament']}")
        print(f"💰 Recommended Bet: {opp['recommended_bet']} @ {opp['odds']}")
        print(f"📊 Edge: {opp['edge']}% | Expected Value: {opp['expected_value']}%")
        print(f"🎯 Statistical Prob: {opp['statistical_probability']}% vs Implied: {opp['implied_probability']}%")
        print(f"✅ Confidence: {opp['confidence_score']}%")
        print(f"📝 Reasoning: {opp['reasoning']}")
        
        if opp['event_date']:
            print(f"📅 Date: {opp['event_date']} {opp['event_time'] or ''}")
        
        # Mostrar métricas detalhadas
        rec_metrics = opp['player_metrics']['recommended_player']
        opp_metrics = opp['player_metrics']['opponent']
        print(f"📈 Player Metrics - Service Dom: {rec_metrics['service_dominance']:.3f}, "
              f"Serve Eff: {rec_metrics['serve_efficiency']:.3f}, "
              f"Overall: {rec_metrics['overall_rating']:.3f}")
        print(f"📉 Opponent Metrics - Service Dom: {opp_metrics['service_dominance']:.3f}, "
              f"Serve Eff: {opp_metrics['serve_efficiency']:.3f}, "
              f"Overall: {opp_metrics['overall_rating']:.3f}")
        
        print("-" * 80)
    
    return opportunities[:top_n]

def save_betting_analysis(opportunities, filename="betting_analysis.json"):
    """Salva a análise de apostas em arquivo JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(opportunities, f, indent=2, ensure_ascii=False)
        print(f"\\n💾 Análise completa salva em '{filename}'")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")
        return False

# Função principal
def main():
    """Função principal para executar a análise de apostas"""
    
    # Verificar se o arquivo de dados existe
    data_file = 'dados/clean/collected_tennis_data_atp_singles_pregame_with_stats.json'
    if not os.path.exists(data_file):
        print(f"❌ Arquivo '{data_file}' não encontrado.")
        print("Execute primeiro o odds.py para coletar os dados.")
        return
    
    try:
        # Carregar dados coletados
        with open(data_file, 'r', encoding='utf-8') as f:
            collected_data = json.load(f)
        
        print(f"📊 Dados carregados: {len(collected_data)} eventos")
        
        # Analisar oportunidades de apostas
        print("\\n🔍 Analisando oportunidades de apostas...")
        opportunities = analyze_betting_opportunities(collected_data, min_odds=1.60)
        
        # Mostrar recomendações
        top_bets = print_betting_recommendations(opportunities, top_n=10)
        
        # Salvar análise
        save_betting_analysis(opportunities)
        
        # Resumo final
        print(f"\\n📈 RESUMO FINAL:")
        print(f"• Total de eventos analisados: {len(collected_data)}")
        print(f"• Oportunidades de apostas encontradas: {len(opportunities)}")
        
        if opportunities:
            risk_counts = {}
            for opp in opportunities:
                risk = opp['risk_level']
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
            
            print(f"• Distribuição por risco: {dict(risk_counts)}")
            
            avg_edge = sum(opp['edge'] for opp in opportunities) / len(opportunities)
            avg_ev = sum(opp['expected_value'] for opp in opportunities) / len(opportunities)
            print(f"• Edge médio: {avg_edge:.2f}%")
            print(f"• Valor esperado médio: {avg_ev:.2f}%")
        
        print("\\n✅ Análise concluída!")
        
    except FileNotFoundError:
        print(f"❌ Arquivo '{data_file}' não encontrado.")
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON: {e}")
    except Exception as e:
        print(f"❌ Erro durante análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
