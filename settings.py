DISCOGS_BASE_URL = "https://www.discogs.com"
DEFAULT_GENRE = "Pop"
MAX_ARTISTS = 10
MAX_ALBUMS_PER_ARTIST = 10

MIN_DELAY = 2
MAX_DELAY = 4

SELENIUM_HEADLESS = False  # Headless não funciona devido ao Cloudflare do Discogs
SELENIUM_TIMEOUT = 10  
SELENIUM_PAGE_LOAD_WAIT = 2  

OUTPUT_DIR = "data/output"
LOG_LEVEL = "INFO"

DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}