# app/services/metadata/artifact_metadata.py

from typing import Dict, Any, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ComponentType(str, Enum):
    """Supported visualization component types"""
    CHART = "Chart"
    TABLE = "Table"
    CARD = "Card"

class ChartType(str, Enum):
    """Supported chart types"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    RADAR = "radar"

class TableColumn(BaseModel):
    """Column definition for tables"""
    key: str
    label: str
    type: str = "string"
    format: Optional[str] = None
    sortable: bool = True
    filterable: bool = True

class CardMetric(BaseModel):
    """Metric definition for cards"""
    label: str
    value: Union[int, float, str]
    trend: Optional[str] = None
    change: Optional[float] = None
    description: Optional[str] = None

class VisualProperties(BaseModel):
    """Visual properties for components"""
    style: Dict[str, Any] = Field(
        default_factory=lambda: {
            "width": "800px",
            "height": "500px"
        }
    )
    theme: Optional[Dict[str, Any]] = None
    interactions: Optional[List[str]] = None

class DataSchema(BaseModel):
    """Schema definition for data structure"""
    type: str
    fields: Dict[str, Dict[str, Any]]
    metadata: Dict[str, Any]

class ArtifactConfig(BaseModel):
    """Configuration for artifacts"""
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    visual: VisualProperties = Field(default_factory=VisualProperties)

class ArtifactMetadata(BaseModel):
    """Complete artifact metadata model"""
    id: Optional[int] = None
    component_type: ComponentType
    title: str
    description: Optional[str] = None
    schema: DataSchema
    data: Dict[str, Any]
    config: ArtifactConfig
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    @classmethod
    def from_raw_data(
        cls, 
        raw_data: Dict[str, Any], 
        component_type: str, 
        title: Optional[str] = None
    ) -> 'ArtifactMetadata':
        """Create metadata instance from raw data"""
        try:
            # Initialize metadata generator
            generator = MetadataGenerator()
            
            # Generate metadata
            metadata = generator.generate(raw_data, component_type, title)
            
            # Create the artifact metadata instance
            return cls(
                component_type=ComponentType(component_type),
                title=metadata["title"],
                schema=DataSchema(**metadata["schema"]),
                data=metadata["transformed"],
                config=ArtifactConfig(
                    type=component_type,
                    visual=VisualProperties(**metadata["visual"])
                )
            )
            
        except Exception as e:
            logger.error(f"Error creating artifact metadata: {str(e)}")
            return cls._generate_fallback(component_type)

    @classmethod
    def _generate_fallback(cls, component_type: str) -> 'ArtifactMetadata':
        """Generate fallback metadata when creation fails"""
        return cls(
            component_type=ComponentType(component_type),
            title="Failed to Generate Artifact",
            schema=DataSchema(
                type="object",
                fields={},
                metadata={"error": "Failed to analyze data"}
            ),
            data={},
            config=ArtifactConfig(
                type=component_type,
                properties={"error": True},
                visual=VisualProperties()
            )
        )

    def get_presentation_data(self) -> Dict[str, Any]:
        """Get data formatted for presentation"""
        try:
            return {
                "type": self.component_type,
                "title": self.title,
                "data": self.data,
                "visual": self.config.visual.dict(),
                "config": self.config.properties
            }
        except Exception as e:
            logger.error(f"Error getting presentation data: {str(e)}")
            return {
                "type": self.component_type,
                "title": "Error in Presentation",
                "data": {},
                "visual": VisualProperties().dict(),
                "config": {}
            }

    @validator('data')
    def validate_data(cls, v):
        """Validate the data structure"""
        if not isinstance(v, dict):
            raise ValueError("Data must be a dictionary")
        return v


class DataTransformer(ABC):
    """Abstract base class for data transformers"""
    @abstractmethod
    def transform(self, data: Any) -> Dict[str, Any]:
        pass

    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

class TableTransformer(DataTransformer):
    def transform(self, data: Any) -> Dict[str, Any]:
        records = self._extract_records(data)
        if not records:
            return self._empty_table()

        # Extract headers from the first record
        headers = list(records[0].keys())
        
        # Transform records into rows
        rows = []
        for record in records:
            row = [self._format_value(record.get(header)) for header in headers]
            rows.append(row)

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
            "data": {"values": rows}
        }

    def validate(self, data: Any) -> bool:
        records = self._extract_records(data)
        return bool(records and all(isinstance(r, dict) for r in records))

    def _extract_records(self, data: Any) -> List[Dict[str, Any]]:
        if isinstance(data, list):
            return data if data and isinstance(data[0], dict) else []
        elif isinstance(data, dict):
            for value in data.values():
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    return value
        return []

    def _extract_headers(self, record: Dict[str, Any]) -> List[str]:
        return list(record.keys())

    def _format_rows(self, records: List[Dict[str, Any]], headers: List[str]) -> List[List[str]]:
        return [
            [self._format_value(record.get(header)) for header in headers]
            for record in records
        ]

    def _format_value(self, value: Any) -> str:
        if value is None:
            return ""
        elif isinstance(value, (int, float)):
            return self._format_number(value)
        return str(value)

    def _format_number(self, value: Union[int, float]) -> str:
        if abs(value) >= 1_000_000_000:
            return f"{value/1_000_000_000:.2f}B"
        elif abs(value) >= 1_000_000:
            return f"{value/1_000_000:.2f}M"
        elif abs(value) >= 1_000:
            return f"{value/1_000:.1f}K"
        elif isinstance(value, float):
            return f"{value:.2f}"
        return str(value)

    def _empty_table(self) -> Dict[str, Any]:
        return {
            "type": "table",
            "headers": [],
            "rows": [],
            "data": {"values": []}
        }

class SchemaAnalyzer:
    """Analyzes data structure and generates schema"""
    def analyze(self, data: Any) -> Dict[str, Any]:
        schema = {
            "type": self._get_type(data),
            "fields": self._analyze_fields(data),
            "metadata": self._extract_metadata(data)
        }
        return schema

    def _get_type(self, data: Any) -> str:
        if isinstance(data, dict):
            return "object"
        elif isinstance(data, list):
            return "array"
        elif isinstance(data, (int, float)):
            return "number"
        elif isinstance(data, bool):
            return "boolean"
        return "string"

    def _analyze_fields(self, data: Any) -> Dict[str, Any]:
        if isinstance(data, dict):
            return {
                key: {"type": self._get_type(value)}
                for key, value in data.items()
            }
        elif isinstance(data, list) and data:
            return self._analyze_fields(data[0])
        return {}

    def _extract_metadata(self, data: Any) -> Dict[str, Any]:
        return {
            "record_count": len(data) if isinstance(data, list) else 1,
            "nested_level": self._get_nesting_level(data),
            "has_arrays": self._contains_arrays(data)
        }

    def _get_nesting_level(self, data: Any, level: int = 0) -> int:
        if isinstance(data, dict):
            return max(
                (self._get_nesting_level(v, level + 1) for v in data.values()),
                default=level
            )
        elif isinstance(data, list) and data:
            return self._get_nesting_level(data[0], level + 1)
        return level

    def _contains_arrays(self, data: Any) -> bool:
        if isinstance(data, list):
            return True
        elif isinstance(data, dict):
            return any(self._contains_arrays(v) for v in data.values())
        return False

class MetadataGenerator:
    """Generates artifact metadata from raw data"""
    def __init__(self):
        self.analyzer = SchemaAnalyzer()
        self.transformers = {
            ComponentType.TABLE: TableTransformer(),
            # Add more transformers as needed
        }

    def generate(
        self,
        raw_data: Any,
        component_type: str,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            # Analyze data structure
            schema = self.analyzer.analyze(raw_data)
            
            # Transform data
            transformer = self.transformers.get(ComponentType(component_type))
            if not transformer:
                raise ValueError(f"Unsupported component type: {component_type}")
                
            transformed_data = transformer.transform(raw_data)
            
            # Generate metadata
            metadata = {
                "schema": schema,
                "transformed": transformed_data,
                "title": title or self._generate_title(schema, transformed_data),
                "visual": self._generate_visual_properties(schema, transformed_data)
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error generating metadata: {str(e)}")
            return self._generate_fallback_metadata(component_type)

    def _generate_title(
        self,
        schema: Dict[str, Any],
        transformed: Dict[str, Any]
    ) -> str:
        if "headers" in transformed:
            return f"Data Overview ({len(transformed['headers'])} columns)"
        return "Data Visualization"

    def _generate_visual_properties(
        self,
        schema: Dict[str, Any],
        transformed: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "style": {
                "width": "800px",
                "height": "500px"
            },
            "interactive": True
        }

    def _generate_fallback_metadata(self, component_type: str) -> Dict[str, Any]:
        return {
            "schema": {
                "type": "object",
                "fields": {},
                "metadata": {"record_count": 0}
            },
            "transformed": self.transformers[ComponentType(component_type)]._empty_table(),
            "title": "No Data Available",
            "visual": {
                "style": {
                    "width": "800px",
                    "height": "500px"
                }
            }
        }