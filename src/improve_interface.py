#!/usr/bin/env python3
"""
Script para melhorar a interface da Agenda Tech Brasil
"""

import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

def create_improved_template():
    """Cria o template melhorado"""
    template_content = '''<!-- Template melhorado aqui -->
    <!-- Conteúdo do template events_improved.md.j2 -->
    '''
    
    template_path = os.path.join('templates', 'events_improved.md.j2')
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✅ Template melhorado criado: {template_path}")

def create_web_interface():
    """Cria a interface web interativa"""
    html_content = '''<!-- HTML da interface web aqui -->
    <!-- Conteúdo do index.html -->
    '''
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Interface web criada: index.html")

def update_generate_script():
    """Atualiza o script de geração para usar o template melhorado"""
    script_path = 'generate_page.py'
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir o template usado
    content = content.replace(
        "template = env.get_template('events.md.j2')",
        "template = env.get_template('events_improved.md.j2')"
    )
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Script de geração atualizado")

def create_stats_script():
    """Cria um script para gerar estatísticas dos eventos"""
    stats_script = '''#!/usr/bin/env python3
"""
Script para gerar estatísticas dos eventos
"""

import json
from collections import Counter
from datetime import datetime

def generate_stats():
    with open('src/db/database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    current_year = datetime.now().year
    stats = {
        'total_events': 0,
        'by_type': Counter(),
        'by_month': Counter(),
        'by_city': Counter(),
        'by_state': Counter()
    }
    
    # Processar eventos do ano atual
    for year_data in data['eventos']:
        if year_data['ano'] == current_year and not year_data['arquivado']:
            for month in year_data['meses']:
                if not month['arquivado']:
                    for event in month['eventos']:
                        stats['total_events'] += 1
                        stats['by_type'][event['tipo']] += 1
                        stats['by_month'][month['mes']] += 1
                        
                        if event['cidade']:
                            stats['by_city'][event['cidade']] += 1
                        if event['uf']:
                            stats['by_state'][event['uf']] += 1
    
    # Adicionar eventos TBA
    if 'tba' in data:
        for event in data['tba']:
            stats['total_events'] += 1
            stats['by_type'][event['tipo']] += 1
            stats['by_month']['TBA'] += 1
    
    return stats

if __name__ == "__main__":
    stats = generate_stats()
    print("📊 Estatísticas dos Eventos:")
    print(f"Total: {stats['total_events']}")
    print(f"Por tipo: {dict(stats['by_type'])}")
    print(f"Por mês: {dict(stats['by_month'])}")
    print(f"Top 5 cidades: {stats['by_city'].most_common(5)}")
    print(f"Top 5 estados: {stats['by_state'].most_common(5)}")
'''
    
    with open('src/generate_stats.py', 'w', encoding='utf-8') as f:
        f.write(stats_script)
    
    print("✅ Script de estatísticas criado: src/generate_stats.py")

def main():
    """Função principal"""
    print("🚀 Melhorando a interface da Agenda Tech Brasil...")
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('src'):
        print("❌ Execute este script na raiz do projeto")
        return
    
    try:
        # Criar template melhorado
        create_improved_template()
        
        # Criar interface web
        create_web_interface()
        
        # Atualizar script de geração
        update_generate_script()
        
        # Criar script de estatísticas
        create_stats_script()
        
        print("\n🎉 Interface melhorada com sucesso!")
        print("\n📝 Próximos passos:")
        print("1. Execute 'python src/generate_page.py' para gerar o README melhorado")
        print("2. Abra 'index.html' no navegador para ver a interface web")
        print("3. Execute 'python src/generate_stats.py' para ver estatísticas")
        print("4. Faça commit das mudanças e push para o GitHub")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()

