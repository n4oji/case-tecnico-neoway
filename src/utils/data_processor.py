import json
import pandas as pd
from typing import List, Dict, Any
import os
from datetime import datetime
from ..scraper.data_models import Artist

class DataProcessor:   
    def __init__(self, output_dir: str = "data/output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def artists_to_jsonl(self, artists: List[Artist], filename: str = None) -> str:
        """
        Exporta artistas para JSONL
        Cada linha representa um artista com álbuns e tracks aninhados
        ids são baseados no discogs id quando disponível
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"discogs_data_{timestamp}.jsonl"
        
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for artist in artists:
                record = {
                    'id': artist.artist_id,
                    'name': artist.name,
                    'genre': artist.genre,
                    'members': artist.members if artist.members else [],
                    'websites': [
                        w for w in artist.websites 
                        if w and 'discogs' not in w.lower()
                    ],
                    'albums': [
                        {
                            'id': album.album_id,
                            'name': album.name,
                            'year': album.year,
                            'label': album.label,
                            'styles': album.styles if album.styles else [],
                            'tracks': [
                                {
                                    'number': track.number,
                                    'title': track.title,
                                    'duration': track.duration
                                }
                                for track in album.tracks
                            ]
                        }
                        for album in artist.albums
                    ]
                }
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        return output_path
    
    def generate_summary_report(self, artists: List[Artist]) -> Dict[str, Any]:
        total_artists = len(artists)
        total_albums = sum(len(artist.albums) for artist in artists)
        total_tracks = sum(len(album.tracks) for artist in artists for album in artist.albums)
        
        artist_stats = []
        for artist in artists:
            artist_stats.append({
                'name': artist.name,
                'albums_count': len(artist.albums),
                'tracks_count': sum(len(album.tracks) for album in artist.albums),
                'members_count': len(artist.members)
            })
        
        return {
            'summary': {
                'total_artists': total_artists,
                'total_albums': total_albums,
                'total_tracks': total_tracks,
                'collection_date': datetime.now().isoformat()
            },
            'artist_details': artist_stats
        }