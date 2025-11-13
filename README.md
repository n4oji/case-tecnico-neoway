# Discogs Web Scraper - Teste Técnico Neoway

Solução completa para coleta, processamento e exportação de dados musicais do Discogs para o teste técnico de Engenharia de Dados.

## Visão Geral

Este projeto realiza web scraping automatizado do site [Discogs](https://www.discogs.com) para coletar informações detalhadas sobre artistas, álbuns e faixas de um gênero musical específico. Os dados são processados e exportados em formato JSONL hierárquico otimizado.

### Funcionalidades

- Coleta automatizada de até 10 artistas por gênero
- Extração de até 10 álbuns por artista
- Captura de metadados completos (labels, styles, durações)

- IDs únicos baseados no Discogs ID
- Estrutura hierárquica otimizada (sem duplicação)
- Geração automática de relatórios

### Dados Coletados

#### Por Artista
- **ID único**: Baseado no Discogs ID (`discogs-artist-1124645`)
- **Nome do artista**
- **Gênero musical** (conforme busca)
- **Membros**
- **Websites oficiais** (filtrados, sem links do Discogs)

#### Por Álbum
- **ID único**: Baseado no Discogs ID (`discogs-release-10189548`)
- **Nome do álbum**
- **Ano de lançamento**
- **Gravadora/Label**
- **Estilos musicais** (lista)

#### Por Faixa
- **Número da faixa**
- **Título**
- **Duração** (formato MM:SS)

## Instalação e Configuração

### Pré-requisitos

- **Python 3.10+**
- **Chromium/Chrome** instalado
- **Conexão estável com internet**

### Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/n4oji/case-tecnico-neoway.git
cd case-tecnico-neoway

# 2. Crie o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt
```

### Dependências Principais

```txt
selenium==4.15.2
undetected-chromedriver==3.5.5
beautifulsoup4==4.12.2
lxml==4.9.3
```

## Uso

### Comando Básico

```bash
# Coletar 10 artistas do gênero Rock (padrão)
python3 main.py

# Especificar gênero e quantidade
python3 main.py --genre "Electronic" --max-artists 5

# Com nível de log detalhado
python3 main.py --genre "Jazz" --max-artists 3 --log-level DEBUG
```

### Parâmetros CLI

| Parâmetro | Short | Padrão | Descrição |
|-----------|-------|--------|-----------|
| `--genre` | `-g` | `Pop` | Gênero musical a coletar |
| `--max-artists` | `-a` | `10` | Número máximo de artistas |
| `--output` | `-o` | Auto | Nome do arquivo de saída |
| `--log-level` | `-l` | `INFO` | Nível de logging (DEBUG/INFO/WARNING/ERROR) |

### Exemplos de Uso

```bash
# Coletar Rock com log detalhado
python3 main.py --genre "rock" --log-level DEBUG

# Coletar Jazz e salvar com nome específico
python3 main.py --genre "jazz" --max-artists 5 --output jazz_collection.jsonl

# Coletar Electronic music
python3 main.py --genre "electronic" --max-artists 10
```

## Estrutura do Projeto

```
case-tecnico-neoway/
├── main.py                          # Script principal de execução
├── settings.py                      # Configurações globais
├── requirements.txt                 # Dependências Python
├── README.md                        # Documentação
│
├── src/
│   ├── scraper/
│   │   ├── scraper.py              # Web scraper com Selenium
│   │   └── data_models.py          # Modelos de dados (Artist, Album, Track)
│   └── utils/
│       └── data_processor.py       # Processamento e exportação JSONL
│
├── data/
│   └── output/                     # Arquivos de saída gerados
│       ├── *.jsonl                 # Dados coletados
│       └── *_report.json           # Relatórios de coleta
│
└── tests/
    ├── test_scraper.py             # Testes do scraper
    └── test_data_processor.py      # Testes do processador
```

## Formato de Saída

### Estrutura JSONL Hierárquica

Cada linha do arquivo JSONL contém **um artista completo** com seus álbuns e faixas aninhados:

```json
{
  "id": "discogs-artist-138556",
  "name": "Neil Young",
  "genre": "rock",
  "members": [],  // Alguns artistas solo não têm membros listados
  "websites": [
    "https://www.neilyoung.com/",
    "https://www.facebook.com/NeilYoung"
  ],
  "websites": [
    "https://www.neilyoung.com/",
    "https://www.facebook.com/NeilYoung"
  ],
  "albums": [
    {
      "id": "discogs-release-1336190",
      "name": "Everybody Knows This Is Nowhere",
      "year": 1969,
      "label": "Reprise Records",
      "styles": ["Country Rock", "Classic Rock"],
      "tracks": [
        {
          "number": 1,
          "title": "Cinnamon Girl",
          "duration": "2:58"
        },
        {
          "number": 2,
          "title": "Everybody Knows This Is Nowhere",
          "duration": "2:36"
        }
      ]
    }
  ]
}
```

### Relatório Automático

Arquivo `*_report.json` gerado automaticamente:

```json
{
  "summary": {
    "total_artists": 10,
    "total_albums": 98,
    "total_tracks": 1064,
    "collection_date": "2025-11-12T23:19:08.163970"
  },
  "artist_details": [
    {
      "name": "Radiohead",
      "albums_count": 10,
      "tracks_count": 148,
      "members_count": 5
    }
  ]
}
```

## Arquitetura Técnica

### Tecnologias Utilizadas

- **Selenium + undetected-chromedriver**: Bypass de proteções anti-bot (Cloudflare Turnstile)
- **BeautifulSoup4**: Parsing de HTML
- **JSON extraction**: Extração de dados GraphQL embutidos no HTML
- **Python dataclasses**: Modelagem de dados tipada
- **Logging nativo**: Sistema robusto de logs

### Desafio do Cloudflare

**Problema enfrentado**: O Discogs utiliza proteção Cloudflare com CAPTCHA, impossibilitando scraping headless tradicional.

**Soluções testadas**:
- ❌ **Requests + BeautifulSoup**: Bloqueado pelo Cloudflare
- ❌ **Selenium headless**: CAPTCHA detecta automação
- ❌ **Cloudscraper**: Não consegue resolver CAPTCHA moderno
- ✅ **Selenium com interface gráfica**: Única solução funcional sem usar API oficial

**Solução adotada**: Selenium com navegador visível (`headless=False`) usando `undetected-chromedriver` para bypass parcial. O navegador abre interface gráfica permitindo resolução automática ou manual do CAPTCHA quando necessário. Esta foi a única abordagem bem-sucedida sem recorrer à API oficial do Discogs.

### Características Técnicas

#### Robustez
- **Bypass Cloudflare**: undetected-chromedriver contorna proteções
- **Retry automático**: Tentativas com backoff exponencial
- **Tratamento de erros**: Exceções customizadas (`DiscogsScraperError`)
- **Timeouts configuráveis**: Espera inteligente de carregamento

#### Qualidade dos Dados
- **IDs únicos semânticos**: Baseados no Discogs ID real
- **Deduplicação**: Evita álbuns e artistas repetidos
- **Validação**: Campos obrigatórios verificados
- **Filtros**: Remove links do Discogs, mantém apenas externos
- **Estrutura hierárquica**: Elimina redundância (1 artista/linha)

#### Performance
- **Extração JSON**: Usa dados GraphQL embutidos (mais rápido que CSS selectors)
- **Caching de páginas**: BeautifulSoup processa HTML uma única vez
- **Logging otimizado**: Níveis configuráveis (DEBUG/INFO/WARNING/ERROR)

#### Manutenibilidade
- **Código modular**: Separação clara de responsabilidades
- **Type hints**: Tipagem completa para IDE support
- **Documentação inline**: Docstrings em funções principais
- **Configurações centralizadas**: `settings.py`

## Resultados Reais

### Coleta de 10 Artistas (Gênero: Rock)

```
10 artistas coletados
98 álbuns extraídos (~10 por artista)
1.064 faixas catalogadas
Tempo médio: ~3 minutos
Taxa de sucesso: 100%
```

**Artistas coletados:**
1. Radiohead (148 tracks, 5 membros)
2. Neil Young (98 tracks, artista solo)
3. Mad Season (43 tracks, 5 membros)
4. Fugazi (116 tracks, 5 membros)
5. Fiona Apple (76 tracks, artista solo)
6. The Black Keys (114 tracks, 2 membros)
7. Paramore (119 tracks)
8. The Raconteurs (128 tracks, 5 membros)
9. U2 (115 tracks)
10. Bob Dylan (107 tracks, artista solo)

### Arquivo Gerado

```
📁 discogs_data_20251113_000559.jsonl (88KB)
📁 discogs_data_20251113_000559_report.json (1.3KB)
```

### Extração de Membros

**Membros de bandas extraídos com sucesso!**

O scraper agora captura corretamente os membros das bandas quando disponíveis no Discogs:

- **Radiohead**: 5 membros (Colin Greenwood, Ed O'Brien, Jonny Greenwood, Phil Selway, Thom Yorke)
- **Mad Season**: 5 membros (Barrett Martin, John Baker Saunders, Layne Staley, Mike McCready, Mike Inez)
- **Fugazi**: 5 membros (Brendan Canty, Colin Sears, Guy Picciotto, Ian MacKaye, Joe Lally)
- **The Black Keys**: 2 membros (Dan Auerbach, Patrick Carney)
- **The Raconteurs**: 5 membros (Brendan Benson, Dean Fertita, Jack Lawrence, Jack White, Patrick Keeler)

**Artistas solo**: Artistas como Neil Young, Fiona Apple, Bob Dylan não possuem membros listados (campo vazio é esperado)

## Considerações Importantes

### Limitações do Discogs

**Labels podem estar vazios**: Alguns releases não têm label cadastrado no Discogs

**Membros**: Artistas solo naturalmente não possuem membros listados (campo vazio é comportamento esperado)

### Rate Limiting

- **Delays automáticos**: 5 segundos entre requisições
- **Cloudflare**: Aguarda até 15 segundos resolução automática
- **Respeito ao site**: Não faça scraping excessivo

### Formato da URL de Busca

**Importante**: O Discogs exige primeira letra maiúscula no gênero:

```python
https://www.discogs.com/search/?q=&type=all&genre_exact=Rock


## Testes

### Suíte de Testes Completa

O projeto inclui testes unitários abrangentes para validar modelos de dados e processamento:

```bash
# Executar todos os testes
python3 -m pytest tests/ -v

# Com cobertura de código
python3 -m pytest --cov=src tests/

# Teste específico
python3 -m pytest tests/test_scraper.py -v
python3 -m pytest tests/test_data_processor.py -v
```

### Testes Implementados

#### test_scraper.py (8 testes)
- Criação de objetos Track, Album, Artist
- Extração de IDs do Discogs via URL regex
- Fallback para hash MD5 quando URL não disponível
- Adição e deduplicação de álbuns
- Serialização para dicionário (to_dict)

#### test_data_processor.py (4 testes)
- Estrutura hierárquica do JSONL (1 artista por linha)
- Filtro de websites do Discogs
- Geração de relatório com contagens corretas
- Manipulação de lista vazia

### Resultados dos Testes

```
========== test session starts ==========
collected 12 items

tests/test_data_processor.py::TestDataProcessor::test_artists_to_jsonl_structure PASSED     [  8%]
tests/test_data_processor.py::TestDataProcessor::test_artists_to_jsonl_filters_discogs PASSED [ 16%]
tests/test_data_processor.py::TestDataProcessor::test_generate_summary_report PASSED        [ 25%]
tests/test_data_processor.py::TestDataProcessor::test_empty_artists_list PASSED             [ 33%]
tests/test_scraper.py::TestDataModels::test_track_creation PASSED                           [ 41%]
tests/test_scraper.py::TestDataModels::test_album_creation PASSED                           [ 50%]
tests/test_scraper.py::TestDataModels::test_album_id_fallback PASSED                        [ 58%]
tests/test_scraper.py::TestDataModels::test_artist_creation PASSED                          [ 66%]
tests/test_scraper.py::TestDataModels::test_artist_id_fallback PASSED                       [ 75%]
tests/test_scraper.py::TestDataModels::test_artist_add_album PASSED                         [ 83%]
tests/test_scraper.py::TestDataModels::test_album_with_tracks PASSED                        [ 91%]
tests/test_scraper.py::TestDataModels::test_artist_to_dict PASSED                           [100%]

========== 12 passed in 0.22s ==========
```

## Troubleshooting

### Problema: Cloudflare bloqueando
**Causa**: Muitas requisições em pouco tempo

**Solução**:
- Aguardar alguns minutos
- Reduzir `--max-artists`
- Aumentar delays em `settings.py`

## Desenvolvimento

### Estrutura de Classes

```python
# Modelos de dados
@dataclass
class Artist:
    name: str
    genre: str
    url: str
    members: List[str]
    websites: List[str]
    albums: List[Album]
    
    @property
    def artist_id(self) -> str:
        """Extrai ID do Discogs da URL"""
        return f"discogs-artist-{id}"

# Scraper principal
class DiscogsScraper:
    def scrape_genre_data(genre: str, max_artists: int)
    def search_artists_by_genre(genre: str)
    def scrape_artist_info(artist_url: str)
    def _scrape_album_details(album_url: str)
```

## Licença

Este projeto foi desenvolvido para fins educacionais como parte de um teste técnico.

---

**Desenvolvido por**: [@n4oji](https://github.com/n4oji)  
**Data**: Novembro 2025  
**Desafio**: Neoway - Engenheiro de Dados
