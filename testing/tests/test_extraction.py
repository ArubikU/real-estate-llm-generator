"""
Tests for PropertyExtractor.
"""

import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from core.llm.extraction import PropertyExtractor, ExtractionError


@pytest.fixture
def sample_html():
    return """
    <html>
        <body>
            <h1>Beautiful Villa in Tamarindo</h1>
            <div class="price">$450,000</div>
            <div class="details">
                <span>3 bedrooms</span>
                <span>2.5 bathrooms</span>
                <span>250 m²</span>
            </div>
            <div class="description">
                Stunning beachfront villa with ocean views
            </div>
        </body>
    </html>
    """


@pytest.fixture
def sample_extraction_response():
    return {
        "property_name": "Beautiful Villa in Tamarindo",
        "price_usd": 450000,
        "bedrooms": 3,
        "bathrooms": 2.5,
        "property_type": "villa",
        "location": "Tamarindo",
        "description": "Stunning beachfront villa with ocean views",
        "square_meters": 250,
        "extraction_confidence": 0.85,
        "field_confidence": {
            "property_name": 0.95,
            "price_usd": 0.90,
            "bedrooms": 0.85,
            "bathrooms": 0.85
        }
    }


@pytest.mark.django_db
class TestPropertyExtractor:
    
    def test_extract_from_html_success(self, sample_html, sample_extraction_response):
        """Test successful extraction from HTML."""
        
        with patch('core.llm.extraction.OpenAI') as mock_openai:
            # Mock OpenAI response
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(message=MagicMock(content=str(sample_extraction_response)))
            ]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            extractor = PropertyExtractor()
            result = extractor.extract_from_html(sample_html)
            
            assert result['property_name'] == "Beautiful Villa in Tamarindo"
            assert result['price_usd'] == Decimal('450000')
            assert result['bedrooms'] == 3
            assert result['bathrooms'] == Decimal('2.5')
            assert result['extraction_confidence'] >= 0.6
    
    def test_extract_from_html_missing_required_fields(self, sample_html):
        """Test extraction with missing required fields."""
        
        with patch('core.llm.extraction.OpenAI') as mock_openai:
            # Mock incomplete response
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(message=MagicMock(content='{"property_name": "Test"}'))
            ]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            extractor = PropertyExtractor()
            
            with pytest.raises(ExtractionError):
                extractor.extract_from_html(sample_html)
    
    def test_extract_with_retry(self, sample_html, sample_extraction_response):
        """Test retry logic on failure."""
        
        with patch('core.llm.extraction.OpenAI') as mock_openai:
            mock_client = MagicMock()
            
            # First call fails, second succeeds
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(message=MagicMock(content=str(sample_extraction_response)))
            ]
            
            mock_client.chat.completions.create.side_effect = [
                Exception("API Error"),
                mock_response
            ]
            mock_openai.return_value = mock_client
            
            extractor = PropertyExtractor()
            result = extractor.extract_with_retry(sample_html, max_retries=2)
            
            assert result['property_name'] == "Beautiful Villa in Tamarindo"
            assert mock_client.chat.completions.create.call_count == 2
    
    def test_decimal_conversion(self):
        """Test decimal field conversion."""
        
        extractor = PropertyExtractor()
        
        test_data = {
            'price_usd': 450000,
            'bathrooms': 2.5,
            'square_meters': 250
        }
        
        validated = extractor._validate_extraction(test_data)
        
        assert isinstance(validated['price_usd'], Decimal)
        assert isinstance(validated['bathrooms'], Decimal)
        assert isinstance(validated['square_meters'], Decimal)
        assert validated['price_usd'] == Decimal('450000')
