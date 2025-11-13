import pytest
import tempfile
import os
import json
from src.utils.data_processor import DataProcessor
from src.scraper.data_models import Artist, Album, Track

class TestDataProcessor:
    @pytest.fixture
    def processor(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield DataProcessor(tmpdir)
    
    @pytest.fixture
    def sample_artists(self):
        track1 = Track(number=1, title="Track 1", duration="3:45")
        track2 = Track(number=2, title="Track 2", duration="4:20")
        
        album1 = Album(
            name="Album 1",
            year=2020,
            label="Label 1",
            styles=["Rock", "Alternative"],
            url="https://www.discogs.com/release/12345-album-1"
        )
        album1.tracks = [track1, track2]
        
        artist1 = Artist(
            name="Artist 1",
            genre="Rock",
            websites=["http://artist1.com"],
            url="https://www.discogs.com/artist/67890-artist-1"
        )
        artist1.add_album(album1)
        
        track3 = Track(number=1, title="Track 3", duration="2:30")
        
        album2 = Album(
            name="Album 2",
            year=2021,
            label="Label 2",
            styles=["Jazz"],
            url="https://www.discogs.com/release/54321-album-2"
        )
        album2.tracks = [track3]
        
        album3 = Album(
            name="Album 3",
            year=2022,
            label="Label 3",
            styles=["Blues"]
        )
        
        artist2 = Artist(
            name="Artist 2",
            genre="Jazz",
            websites=["http://artist2.com"],
            url="https://www.discogs.com/artist/11111-artist-2"
        )
        artist2.add_album(album2)
        artist2.add_album(album3)
        
        return [artist1, artist2]
    
    def test_artists_to_jsonl_structure(self, processor, sample_artists):
        output_file = processor.artists_to_jsonl(sample_artists, "test.jsonl")
        
        assert os.path.exists(output_file)
        
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            assert len(lines) == 2
            
            artist1_data = json.loads(lines[0])
            assert artist1_data['name'] == "Artist 1"
            assert artist1_data['genre'] == "Rock"
            assert artist1_data['id'] == "discogs-artist-67890"
            assert len(artist1_data['albums']) == 1
            assert artist1_data['albums'][0]['name'] == "Album 1"
            assert artist1_data['albums'][0]['id'] == "discogs-release-12345"
            assert len(artist1_data['albums'][0]['tracks']) == 2
            
            artist2_data = json.loads(lines[1])
            assert artist2_data['name'] == "Artist 2"
            assert artist2_data['genre'] == "Jazz"
            assert artist2_data['id'] == "discogs-artist-11111"
            assert len(artist2_data['albums']) == 2
    
    def test_artists_to_jsonl_filters_discogs(self, processor):
        artist = Artist(
            name="Test Artist",
            genre="Rock",
            websites=[
                "http://artist.com",
                "https://www.facebook.com/discogs",
                "https://discogs.com/artist/123",
                "http://example.com"
            ]
        )
        
        output_file = processor.artists_to_jsonl([artist], "test_filter.jsonl")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.loads(f.readline())
            
            assert len(data['websites']) == 2
            assert "http://artist.com" in data['websites']
            assert "http://example.com" in data['websites']
            
            for website in data['websites']:
                assert 'discogs' not in website.lower()
    
    def test_generate_summary_report(self, processor, sample_artists):
        report = processor.generate_summary_report(sample_artists)
        
        assert report['summary']['total_artists'] == 2
        assert report['summary']['total_albums'] == 3
        assert report['summary']['total_tracks'] == 3
        assert 'collection_date' in report['summary']
        
        assert len(report['artist_details']) == 2
        
        artist1_details = report['artist_details'][0]
        assert artist1_details['name'] == "Artist 1"
        assert artist1_details['albums_count'] == 1
        assert artist1_details['tracks_count'] == 2
        
        artist2_details = report['artist_details'][1]
        assert artist2_details['name'] == "Artist 2"
        assert artist2_details['albums_count'] == 2
        assert artist2_details['tracks_count'] == 1
    
    def test_empty_artists_list(self, processor):
        output_file = processor.artists_to_jsonl([], "empty.jsonl")
        
        assert os.path.exists(output_file)
        
        with open(output_file, 'r') as f:
            content = f.read()
            assert content == ""
        
        report = processor.generate_summary_report([])
        assert report['summary']['total_artists'] == 0
        assert report['summary']['total_albums'] == 0
        assert report['summary']['total_tracks'] == 0