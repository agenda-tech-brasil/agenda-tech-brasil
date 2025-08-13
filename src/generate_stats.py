#!/usr/bin/env python3
"""
Script para gerar estatísticas dos eventos da Agenda Tech Brasil
"""

import json
from collections import Counter
from datetime import datetime
import os

def generate_stats():
    """Gera estatísticas detalhadas dos eventos"""
    
    # Caminho para o banco de dados
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'db', 'database.json')
    
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Arquivo de banco de dados não encontrado: {db_path}")
        return None
    except json.JSONDecodeError:
        print("❌ Erro ao decodificar o arquivo JSON")
        return None
    
    current_year = datetime.now().year
    stats = {
        'total_events': 0,
        'by_type': Counter(),
        'by_month': Counter(),
        'by_city': Counter(),
        'by_state': Counter(),
        'by_year': Counter(),
        'online_events': [],
        'presencial_events': [],
        'hibrido_events': []
    }
    
    # Processar eventos do ano atual
    for year_data in data['eventos']:
        if year_data['ano'] == current_year and not year_data['arquivado']:
            for month in year_data['meses']:
                if not month['arquivado']:
                    for event in month['eventos']:
                        stats['total_events'] += 1
                        if 'tipo' in event:
                            stats['by_type'][event['tipo']] += 1
                        stats['by_month'][month['mes']] += 1
                        stats['by_year'][year_data['ano']] += 1
                        
                        # Coletar eventos por tipo para análise
                        if 'tipo' in event:
                            if event['tipo'] == 'online':
                                stats['online_events'].append({
                                    'nome': event['nome'],
                                    'mes': month['mes'],
                                    'data': event['data']
                                })
                            elif event['tipo'] == 'presencial':
                                stats['presencial_events'].append({
                                    'nome': event['nome'],
                                    'mes': month['mes'],
                                    'data': event['data'],
                                    'cidade': event.get('cidade', ''),
                                    'uf': event.get('uf', '')
                                })
                            elif event['tipo'] == 'híbrido':
                                stats['hibrido_events'].append({
                                    'nome': event['nome'],
                                    'mes': month['mes'],
                                    'data': event['data'],
                                    'cidade': event.get('cidade', ''),
                                    'uf': event.get('uf', '')
                                })
                        
                        if event.get('cidade'):
                            stats['by_city'][event['cidade']] += 1
                        if event.get('uf'):
                            stats['by_state'][event['uf']] += 1
    
    # Adicionar eventos TBA
    if 'tba' in data:
        for event in data['tba']:
            stats['total_events'] += 1
            stats['by_type'][event['tipo']] += 1
            stats['by_month']['TBA'] += 1
            stats['by_year']['TBA'] += 1
    
    return stats

def print_stats(stats):
    """Imprime as estatísticas de forma organizada"""
    if not stats:
        return
    
    print("\n" + "="*60)
    print("📊 ESTATÍSTICAS DA AGENDA TECH BRASIL")
    print("="*60)
    
    print(f"\n🎯 TOTAL DE EVENTOS ATIVOS: {stats['total_events']}")
    
    print(f"\n📅 DISTRIBUIÇÃO POR TIPO:")
    for tipo, count in stats['by_type'].most_common():
        emoji = "🌐" if tipo == "online" else "🏢" if tipo == "presencial" else "🔄"
        print(f"   {emoji} {tipo.capitalize()}: {count}")
    
    print(f"\n🗓️ DISTRIBUIÇÃO POR MÊS:")
    month_names = {
        'janeiro': 'Janeiro', 'fevereiro': 'Fevereiro', 'março': 'Março',
        'abril': 'Abril', 'maio': 'Maio', 'junho': 'Junho',
        'julho': 'Julho', 'agosto': 'Agosto', 'setembro': 'Setembro',
        'outubro': 'Outubro', 'novembro': 'Novembro', 'dezembro': 'Dezembro'
    }
    
    for month, count in stats['by_month'].most_common():
        month_display = month_names.get(month, month.upper())
        print(f"   📅 {month_display}: {count}")
    
    if stats['by_city']:
        print(f"\n🏙️ TOP 10 CIDADES:")
        for city, count in stats['by_city'].most_common(10):
            print(f"   🏙️ {city}: {count}")
    
    if stats['by_state']:
        print(f"\n🏛️ TOP 10 ESTADOS:")
        for state, count in stats['by_state'].most_common(10):
            print(f"   🏛️ {state}: {count}")
    
    print(f"\n📈 ANÁLISE DETALHADA:")
    
    # Eventos online
    if stats['online_events']:
        print(f"   🌐 Eventos Online ({len(stats['online_events'])}):")
        for event in stats['online_events'][:5]:  # Mostrar apenas os primeiros 5
            print(f"      • {event['nome']} ({event['mes']})")
        if len(stats['online_events']) > 5:
            print(f"      ... e mais {len(stats['online_events']) - 5} eventos")
    
    # Eventos presenciais
    if stats['presencial_events']:
        print(f"   🏢 Eventos Presenciais ({len(stats['presencial_events'])}):")
        for event in stats['presencial_events'][:5]:
            location = f"{event['cidade']}/{event['uf']}" if event['cidade'] and event['uf'] else "Local não especificado"
            print(f"      • {event['nome']} - {location} ({event['mes']})")
        if len(stats['presencial_events']) > 5:
            print(f"      ... e mais {len(stats['presencial_events']) - 5} eventos")
    
    # Eventos híbridos
    if stats['hibrido_events']:
        print(f"   🔄 Eventos Híbridos ({len(stats['hibrido_events'])}):")
        for event in stats['hibrido_events'][:5]:
            location = f"{event['cidade']}/{event['uf']}" if event['cidade'] and event['uf'] else "Local não especificado"
            print(f"      • {event['nome']} - {location} ({event['mes']})")
        if len(stats['hibrido_events']) > 5:
            print(f"      ... e mais {len(stats['hibrido_events']) - 5} eventos")
    
    print("\n" + "="*60)

def save_stats_to_file(stats, filename="estatisticas_eventos.md"):
    """Salva as estatísticas em um arquivo Markdown"""
    if not stats:
        return
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 📊 Estatísticas da Agenda Tech Brasil\n\n")
            f.write(f"**Total de eventos ativos:** {stats['total_events']}\n\n")
            
            f.write("## 📅 Distribuição por Tipo\n\n")
            for tipo, count in stats['by_type'].most_common():
                emoji = "🌐" if tipo == "online" else "🏢" if tipo == "presencial" else "🔄"
                f.write(f"- {emoji} **{tipo.capitalize()}:** {count}\n")
            
            f.write("\n## 🗓️ Distribuição por Mês\n\n")
            month_names = {
                'janeiro': 'Janeiro', 'fevereiro': 'Fevereiro', 'março': 'Março',
                'abril': 'Abril', 'maio': 'Maio', 'junho': 'Junho',
                'julho': 'Julho', 'agosto': 'Agosto', 'setembro': 'Setembro',
                'outubro': 'Outubro', 'novembro': 'Novembro', 'dezembro': 'Dezembro'
            }
            
            for month, count in stats['by_month'].most_common():
                month_display = month_names.get(month, month.upper())
                f.write(f"- 📅 **{month_display}:** {count}\n")
            
            if stats['by_city']:
                f.write("\n## 🏙️ Top 10 Cidades\n\n")
                for city, count in stats['by_city'].most_common(10):
                    f.write(f"- 🏙️ **{city}:** {count}\n")
            
            if stats['by_state']:
                f.write("\n## 🏛️ Top 10 Estados\n\n")
                for state, count in stats['by_state'].most_common(10):
                    f.write(f"- 🏛️ **{state}:** {count}\n")
        
        print(f"✅ Estatísticas salvas em: {filename}")
        
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")

def main():
    """Função principal"""
    print("🚀 Gerando estatísticas da Agenda Tech Brasil...")
    
    # Gerar estatísticas
    stats = generate_stats()
    
    if stats:
        # Imprimir no console
        print_stats(stats)
        
        # Salvar em arquivo
        save_stats_to_file(stats)
        
        print("\n🎉 Estatísticas geradas com sucesso!")
    else:
        print("❌ Não foi possível gerar as estatísticas")

if __name__ == "__main__":
    main()
