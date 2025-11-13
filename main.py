import argparse
import logging
import sys
import json
from src.scraper.scraper import DiscogsScraper, DiscogsScraperError
from src.utils.data_processor import DataProcessor
from settings import DEFAULT_GENRE, MAX_ARTISTS, SELENIUM_HEADLESS

def setup_logging(log_level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('discogs_scraper.log', encoding='utf-8')
        ]
    )

def main():
    parser = argparse.ArgumentParser(description='Web Scraper do Discogs para teste de Engenharia de Dados')
    parser.add_argument('--genre', '-g', type=str, default=DEFAULT_GENRE,
                       help=f'Gênero musical para coletar (padrão: {DEFAULT_GENRE})')
    parser.add_argument('--max-artists', '-a', type=int, default=MAX_ARTISTS,
                       help=f'Número máximo de artistas (padrão: {MAX_ARTISTS})')
    parser.add_argument('--output', '-o', type=str,
                       help='Nome do arquivo de saída (opcional)')
    parser.add_argument('--log-level', '-l', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Nível de logging (padrão: INFO)')
    
    args = parser.parse_args()
    
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Iniciando scraping do Discogs para o gênero: {args.genre}")
        
        scraper = DiscogsScraper(headless=SELENIUM_HEADLESS)
        processor = DataProcessor()
        
        artists = scraper.scrape_genre_data(args.genre, args.max_artists)
        
        if not artists:
            logger.warning("Nenhum artista foi coletado. Verifique o gênero especificado.")
            return 1
        
        jsonl_file = processor.artists_to_jsonl(artists, args.output)
        logger.info(f"Dados exportados para: {jsonl_file}")
        
        summary = processor.generate_summary_report(artists)
        logger.info(f"Resumo da coleta: {summary['summary']}")
        
        report_file = jsonl_file.replace('.jsonl', '_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info("Scraping concluído com sucesso!")
        return 0
        
    except DiscogsScraperError as e:
        logger.error(f"Erro do scraper: {e}")
        return 1
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())