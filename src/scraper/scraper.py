import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Optional
from urllib.parse import urljoin
from .data_models import Artist, Album, Track
from src.scraper.data_models import Track
import json

class DiscogsScraperError(Exception):
    pass

class DiscogsScraper:
    def __init__(self, base_url: str = "https://www.discogs.com", headless: bool = True):
        self.base_url = base_url
        self.headless = headless
        self.logger = logging.getLogger(__name__)
        
        try:
            options = uc.ChromeOptions()
            
            # Configurar caminho do Chromium
            options.binary_location = "/snap/bin/chromium"
            
            if headless:
                options.add_argument('--headless=new')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            self.driver = uc.Chrome(
                options=options,
                version_main=142,
                use_subprocess=True
            )
            
            self.logger.info("Selenium WebDriver inicializado com sucesso")
        except Exception as e:
            raise DiscogsScraperError(f"Erro ao inicializar WebDriver: {e}")
    
    def __del__(self):
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
                self.logger.info("WebDriver fechado")
            except:
                pass
    
    def _make_request(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Acessando: {url}")
                self.driver.get(url)
                
                self.logger.info("Aguardando página carregar...")
                time.sleep(5)
                
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                page_source = self.driver.page_source
                if 'cloudflare' in page_source.lower() and 'challenge' in page_source.lower():
                    self.logger.warning("Cloudflare challenge ainda ativo, aguardando resolução...")
                    time.sleep(10)
                    page_source = self.driver.page_source
                
                soup = BeautifulSoup(page_source, 'html.parser')
                
                title = soup.find('title')
                if title:
                    self.logger.info(f"Página carregada: {title.get_text()}")
                
                return soup

            except (TimeoutException, WebDriverException) as e:
                self.logger.warning(f"Tentativa {attempt + 1} falhou para {url}: {e}")
                if attempt == max_retries - 1:
                    raise DiscogsScraperError(f"Falha ao acessar {url} após {max_retries} tentativas")
                time.sleep(5 * (attempt + 1))
        
        return None
    
    def search_artists_by_genre(self, genre: str, limit: int = 10) -> List[str]:
        # URL de busca por gênero - exige primeira letra maiúscula
        genre_capitalized = genre.capitalize()
        search_url = f"{self.base_url}/search/?q=&type=all&genre_exact={genre_capitalized}"
        
        self.logger.info(f"Buscando artistas do gênero: {genre} (URL: {search_url})")
        soup = self._make_request(search_url)
        
        if not soup:
            raise DiscogsScraperError(f"Não foi possível acessar a página de busca para o gênero {genre}")
        
        artist_links = []
        artist_link_tags = soup.find_all('a', href=lambda x: x and '/artist/' in x)
        
        self.logger.debug(f"Encontrados {len(artist_link_tags)} links de artista na página")
        for link_tag in artist_link_tags:
            if len(artist_links) >= limit:
                break
            
            href = link_tag.get('href', '')
            if not href:
                continue
            
            artist_url = urljoin(self.base_url, href)
            
            if artist_url not in artist_links:
                artist_links.append(artist_url)
                self.logger.debug(f"Artista encontrado: {artist_url}")
        
        self.logger.info(f"Encontrados {len(artist_links)} artistas")
        return artist_links
    
    def scrape_artist_info(self, artist_url: str, genre: str) -> Optional[Artist]:
        self.logger.info(f"Coletando dados do artista: {artist_url}")
        
        soup = self._make_request(artist_url)
        if not soup:
            return None
        
        try:
            name_tag = soup.find('h1', class_='profile')
            if not name_tag:
                name_tag = soup.find('h1')
            if not name_tag:
                meta_title = soup.find('meta', property='og:title')
                if meta_title:
                    artist_name = meta_title.get('content', '').split('|')[0].strip()
                else:
                    artist_name = "Nome não encontrado"
            else:
                artist_name = name_tag.get_text(strip=True)
            
            members = []
            script_tag = soup.find('script', id='dsdata')
            if script_tag:
                try:
                    data = json.loads(script_tag.string)
                    
                    # Procurar pelo Artist object
                    for key in data.get('data', {}).keys():
                        if key.startswith('Artist:'):
                            artist_data = data['data'][key]
                            members_list = artist_data.get('members', [])
                            
                            # members é uma lista de referências: {'__ref': 'Artist:{"discogsId":123}'}
                            for member_ref in members_list:
                                if isinstance(member_ref, dict) and 'artist' in member_ref:
                                    artist_ref_key = member_ref['artist'].get('__ref')
                                    if artist_ref_key and artist_ref_key in data['data']:
                                        member_artist = data['data'][artist_ref_key]
                                        member_name = member_artist.get('name')
                                        if member_name and member_name != artist_name:
                                            members.append(member_name)
                            break
                except Exception as e:
                    self.logger.warning(f"Erro ao extrair membros do JSON: {e}")
            
            websites = []
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                if href.startswith(('http://', 'https://')) and 'discogs' not in href.lower():
                    if href not in websites:
                        websites.append(href)
            
            artist = Artist(
                name=artist_name,
                genre=genre,
                members=members,
                websites=websites,
                url=artist_url
            )
            
            self._scrape_artist_albums(artist, artist_url)
            
            return artist
            
        except Exception as e:
            self.logger.error(f"Erro ao processar artista {artist_url}: {e}")
            return None
    
    def _scrape_artist_albums(self, artist: Artist, artist_url: str, max_albums: int = 10) -> None:
        discography_url = f"{artist_url}?superFilter=Releases&subFilter=Albums"
        
        soup = self._make_request(discography_url)
        if not soup:
            return
        
        album_links = []
        
        script_tag = soup.find('script', id='dsdata')
        
        if script_tag:
            try:
                data = json.loads(script_tag.string)
                
                # Os álbuns estão diretamente no data como Release: objects
                if 'data' in data:
                    release_keys = []
                    for key in data['data'].keys():
                        if key.startswith('Release:'):
                            release_keys.append(key)
                    
                    for key in release_keys[:max_albums]:
                        release_data = data['data'][key]
                        site_url = release_data.get('siteUrl')
                        if site_url:
                            album_url = urljoin(self.base_url, site_url)
                            album_links.append(album_url)
                    
                    self.logger.info(f"Encontrados {len(album_links)} álbuns")
            
            except Exception as e:
                self.logger.error(f"Erro ao extrair dados JSON: {e}")
        
        # Fallback: tentar seletores CSS se JSON falhar
        if not album_links:
            self.logger.warning("JSON não encontrado, tentando CSS selectors...")
            releases = soup.find_all('tr', class_='card')
            if not releases:
                releases = soup.find_all('div', class_='card')
            if not releases:
                releases = soup.select('tr[data-object-type="release"]')
            
            for release in releases[:max_albums]:
                link_tag = release.find('a', class_='link_1ctor')
                if not link_tag:
                    link_tag = release.find('a', href=lambda x: x and '/release/' in x)
                
                if link_tag and 'href' in link_tag.attrs:
                    album_url = urljoin(self.base_url, link_tag['href'])
                    album_links.append(album_url)
        
        for album_url in album_links:
            album = self._scrape_album_details(album_url)
            if album:
                artist.add_album(album)
    
    def _scrape_album_details(self, album_url: str) -> Optional[Album]:
        soup = self._make_request(album_url)
        if not soup:
            return None
        
        try:
            script_tag = soup.find('script', id='dsdata')
            
            album_name = "Álbum sem nome"
            year = None
            label = None
            tracks = []
            styles = []
            
            if script_tag:
                try:
                    data = json.loads(script_tag.string)
                    
                    release_id = album_url.split('/release/')[-1].split('-')[0]
                    release_data = None
                    
                    for key in data['data'].keys():
                        if key.startswith('Release:') and release_id in key:
                            release_data = data['data'][key]
                            break
                    
                    if release_data:
                        album_name = release_data.get('title', 'Álbum sem nome')
                        released = release_data.get('released')
                        if released:
                            year = int(released.split('-')[0])
                        
                        labels = release_data.get('labels', [])
                        if labels and len(labels) > 0:
                            for label_rel in labels:
                                if isinstance(label_rel, dict) and label_rel.get('labelRole') == 'LABEL':
                                    label = label_rel.get('displayName')
                                    break
                            if not label and isinstance(labels[0], dict):
                                label = labels[0].get('displayName')
                        
                        styles_list = release_data.get('styles', [])
                        if isinstance(styles_list, list):
                            styles = [s for s in styles_list if isinstance(s, str)]
                        
                        track_refs = release_data.get('tracks', [])
                        for track_ref in track_refs:
                            if isinstance(track_ref, dict) and '__ref' in track_ref:
                                track_key = track_ref['__ref']
                                if track_key in data['data']:
                                    track_data = data['data'][track_key]
                                    
                                    track_title = track_data.get('title', 'Track sem título')
                                    
                                    duration_seconds = track_data.get('durationInSeconds')
                                    if duration_seconds:
                                        minutes = duration_seconds // 60
                                        seconds = duration_seconds % 60
                                        track_duration = f"{minutes}:{seconds:02d}"
                                    else:
                                        track_duration = ''
                                    
                                    track_position = track_data.get('position', '')
                                    
                                    try:
                                        track_number = int(track_position) if track_position and str(track_position).isdigit() else len(tracks) + 1
                                    except:
                                        track_number = len(tracks) + 1
                                                                        
                                    track = Track(
                                        number=track_number,
                                        title=track_title,
                                        duration=track_duration
                                    )
                                    tracks.append(track)
                        
                        self.logger.info(f"Extraídos dados JSON: {album_name}, {len(tracks)} tracks")
                
                except Exception as e:
                    self.logger.warning(f"Erro ao extrair JSON do álbum: {e}, tentando CSS...")
            
            # Fallback: CSS selectors se JSON falhar
            if album_name == "Álbum sem nome":
                title_tag = soup.find('h1', id='profile_title')
                album_name = title_tag.get_text(strip=True) if title_tag else "Álbum sem nome"
            
            if not year:
                year_tag = soup.find('a', class_='link_1ctor')
                if year_tag and year_tag.get_text().isdigit():
                    year = int(year_tag.get_text())
            
            if not label:
                label_tag = soup.find('div', class_='profile')
                if label_tag:
                    label_links = label_tag.find_all('a', href=lambda x: x and '/label/' in x)
                    if label_links:
                        label = label_links[0].get_text(strip=True)
            
            if not styles:
                styles_section = soup.find('div', class_='profile')
                if styles_section:
                    style_links = styles_section.find_all('a', href=lambda x: x and '/style/' in x)
                    styles = [link.get_text(strip=True) for link in style_links]
            
            if not tracks:
                tracks = self._scrape_tracks(soup)
            
            return Album(
                name=album_name,
                year=year,
                label=label,
                styles=styles,
                tracks=tracks,
                url=album_url
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao processar álbum {album_url}: {e}")
            return None
    
    def _scrape_tracks(self, soup: BeautifulSoup) -> List[Track]:
        tracks = []
        tracklist = soup.find('table', class_='tracklist_3QGDK')
        
        if not tracklist:
            return tracks
        
        track_rows = tracklist.find_all('tr', class_='tracklist_track_2Wen5')
        
        for i, row in enumerate(track_rows, 1):
            try:
                position_tag = row.find('td', class_='tracklist_track_pos_3VEVD')
                track_number = i
                if position_tag:
                    pos_text = position_tag.get_text(strip=True)
                    if pos_text.isdigit():
                        track_number = int(pos_text)
                
                title_tag = row.find('span', class_='tracklist_track_title_3lohU')
                title = title_tag.get_text(strip=True) if title_tag else f"Faixa {track_number}"
                
                duration = None
                duration_tag = row.find('td', class_='tracklist_track_duration_3CEiG')
                if duration_tag:
                    duration = duration_tag.get_text(strip=True)
                
                tracks.append(Track(
                    number=track_number,
                    title=title,
                    duration=duration
                ))
                
            except Exception as e:
                self.logger.warning(f"Erro ao processar faixa {i}: {e}")
                continue
        
        return tracks
    
    def scrape_genre_data(self, genre: str, max_artists: int = 10) -> List[Artist]:
        self.logger.info(f"Iniciando coleta de dados para o gênero: {genre}")
        
        artist_urls = self.search_artists_by_genre(genre, max_artists)
        artists = []
        for artist_url in artist_urls:
            try:
                artist = self.scrape_artist_info(artist_url, genre)
                if artist:  
                    artists.append(artist)
                    self.logger.info(f"Coletado: {artist.name} com {len(artist.albums)} álbum(s)")
                
            except Exception as e:
                self.logger.error(f"Erro ao coletar dados do artista {artist_url}: {e}")
                continue
        
        self.logger.info(f"Coleta finalizada. Total de artistas: {len(artists)}")
        return artists