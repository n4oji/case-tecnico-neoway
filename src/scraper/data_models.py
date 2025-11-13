from dataclasses import dataclass, field
from typing import List, Optional, Dict
import hashlib
import re

@dataclass
class Track:
    number: int
    title: str
    duration: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'number': self.number,
            'title': self.title,
            'duration': self.duration
        }

@dataclass
class Album:
    name: str
    year: Optional[int] = None
    label: Optional[str] = None
    styles: List[str] = field(default_factory=list)
    tracks: List[Track] = field(default_factory=list)
    url: Optional[str] = None
    
    @property
    def album_id(self) -> str:
        if self.url:
            # Extrair id do Discogs da url (formato: /release/12345-...)
            match = re.search(r'/release/(\d+)', self.url)
            if match:
                return f"discogs-release-{match.group(1)}"

        return f"hash-{hashlib.md5(self.name.encode()).hexdigest()[:12]}"
    
    def to_dict(self) -> Dict:
        return {
            'album_id': self.album_id,
            'name': self.name,
            'year': self.year,
            'label': self.label,
            'styles': self.styles,
            'tracks': [track.to_dict() for track in self.tracks]
        }

@dataclass
class Artist:
    name: str
    genre: str
    members: List[str] = field(default_factory=list)
    websites: List[str] = field(default_factory=list)
    albums: List[Album] = field(default_factory=list)
    url: Optional[str] = None
    
    @property
    def artist_id(self) -> str:
        if self.url:
            # Extrair id do Discogs da url (formato: /artist/12345-...)
            match = re.search(r'/artist/(\d+)', self.url)
            if match:
                return f"discogs-artist-{match.group(1)}"

        return f"hash-{hashlib.md5(f'{self.name}_{self.genre}'.encode()).hexdigest()[:12]}"
    
    def add_album(self, album: Album) -> None:
        existing_albums = {alb.name.lower() for alb in self.albums}
        if album.name.lower() not in existing_albums:
            self.albums.append(album)
    
    def to_dict(self) -> Dict:
        return {
            'artist_id': self.artist_id,
            'name': self.name,
            'genre': self.genre,
            'members': self.members,
            'websites': self.websites,
            'albums': [album.to_dict() for album in self.albums]
        }