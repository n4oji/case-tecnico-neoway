from src.scraper.data_models import Artist, Album, Track

class TestDataModels:
    def test_track_creation(self):
        track = Track(number=1, title="Test Track", duration="3:45")
        
        assert track.number == 1
        assert track.title == "Test Track"
        assert track.duration == "3:45"
        
        track_dict = track.to_dict()
        assert track_dict['number'] == 1
        assert track_dict['title'] == "Test Track"
        assert track_dict['duration'] == "3:45"
    
    def test_album_creation(self):
        album = Album(
            name="Test Album",
            year=2020,
            label="Test Label",
            styles=["Rock", "Alternative"],
            url="https://www.discogs.com/release/12345-test-album"
        )
        
        assert album.name == "Test Album"
        assert album.year == 2020
        assert album.label == "Test Label"
        assert len(album.styles) == 2
        
        assert album.album_id == "discogs-release-12345"
    
    def test_album_id_fallback(self):
        album = Album(name="Test Album")
        
        assert album.album_id.startswith("hash-")
        assert len(album.album_id) > 5
    
    def test_artist_creation(self):
        artist = Artist(
            name="Test Artist",
            genre="Rock",
            url="https://www.discogs.com/artist/67890-test-artist"
        )
        
        assert artist.name == "Test Artist"
        assert artist.genre == "Rock"
        
        assert artist.artist_id == "discogs-artist-67890"
    
    def test_artist_id_fallback(self):
        artist = Artist(name="Test Artist", genre="Rock")
        
        assert artist.artist_id.startswith("hash-")
        assert len(artist.artist_id) > 5
    
    def test_artist_add_album(self):
        artist = Artist(name="Test Artist", genre="Rock")
        album1 = Album(name="Test Album")
        album2 = Album(name="Test Album")
        album3 = Album(name="Another Album")
        
        artist.add_album(album1)
        assert len(artist.albums) == 1

        artist.add_album(album2)
        assert len(artist.albums) == 1

        artist.add_album(album3)
        assert len(artist.albums) == 2
    
    def test_album_with_tracks(self):
        track1 = Track(number=1, title="Track 1", duration="3:45")
        track2 = Track(number=2, title="Track 2", duration="4:20")
        
        album = Album(
            name="Test Album",
            year=2020,
            tracks=[track1, track2]
        )
        
        assert len(album.tracks) == 2
        assert album.tracks[0].title == "Track 1"
        assert album.tracks[1].title == "Track 2"
    
    def test_artist_to_dict(self):
        track = Track(number=1, title="Track 1", duration="3:45")
        album = Album(
            name="Test Album",
            year=2020,
            label="Test Label",
            styles=["Rock"],
            tracks=[track]
        )
        artist = Artist(
            name="Test Artist",
            genre="Rock",
            websites=["http://example.com"],
            albums=[album]
        )
        
        artist_dict = artist.to_dict()
        
        assert artist_dict['name'] == "Test Artist"
        assert artist_dict['genre'] == "Rock"
        assert len(artist_dict['websites']) == 1
        assert len(artist_dict['albums']) == 1
        assert artist_dict['albums'][0]['name'] == "Test Album"
        assert len(artist_dict['albums'][0]['tracks']) == 1