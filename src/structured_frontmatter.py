"""
Structured Frontmatter System for Clean YAML Layout Authoring

This module provides clean, human-readable YAML structures that abstract away
PowerPoint placeholder names while maintaining full functionality. It includes:

1. Registry of structured patterns for different layout types
2. Bidirectional conversion between structured YAML and placeholder mappings
3. Validation system for structured frontmatter
4. Fallback handling when structured parsing fails

Based on the Template Discovery System specification (Option C).
"""

import re
from typing import Dict, List, Any, Optional, Union


class StructuredFrontmatterRegistry:
    """Registry of structured frontmatter patterns for different layout types"""
    
    def __init__(self, template_mapping: Optional[Dict] = None):
        """Initialize with template mapping from JSON file"""
        self.template_mapping = template_mapping or {}
    
    def get_structure_patterns(self):
        """Get structure patterns that define how to parse structured frontmatter"""
        return {
            "Four Columns": {
                "structure_type": "columns",
                "description": "Four-column comparison layout with individual titles and content",
                "yaml_pattern": {
                    "layout": "Four Columns",
                    "title": str,
                    "columns": [
                        {"title": str, "content": str}
                    ]
                },
                "validation": {
                    "min_columns": 1,
                    "max_columns": 4,
                    "required_fields": ["title", "columns"]
                },
                "example": """---
layout: Four Columns
title: Feature Comparison
columns:
  - title: Performance
    content: Fast processing with optimized algorithms
  - title: Security
    content: Enterprise-grade encryption and compliance
  - title: Usability
    content: Intuitive interface with minimal learning curve
  - title: Cost
    content: Competitive pricing with flexible plans
---"""
            },
        
        "Comparison": {
            "structure_type": "comparison",
            "description": "Side-by-side comparison layout for contrasting two options",
            "yaml_pattern": {
                "layout": "Comparison",
                "title": str,
                "comparison": {
                    "left": {"title": str, "content": str},
                    "right": {"title": str, "content": str}
                }
            },
            "mapping_rules": {
                "title": "semantic:title",
                "comparison.left.title": "Text Placeholder 2",
                "comparison.left.content": "Content Placeholder 3",
                "comparison.right.title": "Text Placeholder 4",
                "comparison.right.content": "Content Placeholder 5"
            },
            "validation": {
                "required_fields": ["title", "comparison"],
                "required_comparison_fields": ["left", "right"]
            },
            "example": """---
layout: Comparison
title: Solution Analysis
comparison:
  left:
    title: Traditional Approach
    content: Proven reliability with established workflows
  right:
    title: Modern Solution
    content: Advanced features with improved efficiency
---"""
        },
        
        "Two Content": {
            "structure_type": "sections",
            "description": "Side-by-side layout with two content areas",
            "yaml_pattern": {
                "layout": "Two Content",
                "title": str,
                "sections": [
                    {"title": str, "content": [str]}
                ]
            },
            "mapping_rules": {
                "title": "semantic:title",
                "sections[0].content": "Content Placeholder 2",
                "sections[1].content": "Content Placeholder 3"
            },
            "validation": {
                "required_fields": ["title", "sections"],
                "min_sections": 2,
                "max_sections": 2
            },
            "example": """---
layout: Two Content
title: Before and After
sections:
  - title: Current State
    content:
      - Manual processes
      - Time-consuming workflows
  - title: Future State
    content:
      - Automated systems
      - Streamlined operations
---"""
        },
        
        "Picture with Caption": {
            "structure_type": "media",
            "description": "Media slide with image placeholder and caption text",
            "yaml_pattern": {
                "layout": "Picture with Caption",
                "title": str,
                "media": {
                    "caption": str,
                    "description": str
                }
            },
            "mapping_rules": {
                "title": "semantic:title",
                "media.caption": "Text Placeholder 3",
                "media.description": "semantic:content"
            },
            "validation": {
                "required_fields": ["title", "media"]
            },
            "example": """---
layout: Picture with Caption
title: System Architecture
media:
  caption: High-level system architecture diagram
  description: |
    Main components include:
    • Frontend: React-based interface
    • API: RESTful services
    • Database: PostgreSQL with Redis
---"""
        }
    }
    
    def get_structure_definition(self, layout_name: str) -> Dict[str, Any]:
        """Get structure definition for a layout with dynamically built mapping rules"""
        patterns = self.get_structure_patterns()
        pattern = patterns.get(layout_name, {})
        
        if not pattern:
            return {}
        
        # Build mapping rules dynamically from template mapping
        mapping_rules = self._build_mapping_rules(layout_name)
        
        return {
            **pattern,
            "mapping_rules": mapping_rules
        }
    
    def _build_mapping_rules(self, layout_name: str) -> Dict[str, str]:
        """Build mapping rules dynamically from template JSON"""
        
        if not self.template_mapping:
            return {}
        
        layouts = self.template_mapping.get("layouts", {})
        layout_info = layouts.get(layout_name, {})
        placeholders = layout_info.get("placeholders", {})
        
        mapping_rules = {"title": "semantic:title"}  # Always use semantic for title
        
        if layout_name == "Four Columns":
            # Find column placeholders by looking for patterns in placeholder names
            col_title_placeholders = []
            col_content_placeholders = []
            
            for idx, placeholder_name in placeholders.items():
                name_lower = placeholder_name.lower()
                if "col" in name_lower and "title" in name_lower:
                    col_title_placeholders.append((idx, placeholder_name))
                elif "col" in name_lower and ("text" in name_lower or "content" in name_lower):
                    col_content_placeholders.append((idx, placeholder_name))
            
            # Sort by placeholder index to get correct order
            col_title_placeholders.sort(key=lambda x: int(x[0]))
            col_content_placeholders.sort(key=lambda x: int(x[0]))
            
            # Build mapping rules for each column
            for i, (idx, placeholder_name) in enumerate(col_title_placeholders):
                mapping_rules[f"columns[{i}].title"] = placeholder_name
            
            for i, (idx, placeholder_name) in enumerate(col_content_placeholders):
                mapping_rules[f"columns[{i}].content"] = placeholder_name
                
        elif layout_name == "Comparison":
            # Find comparison placeholders
            text_placeholders = []
            content_placeholders = []
            
            for idx, placeholder_name in placeholders.items():
                name_lower = placeholder_name.lower()
                if "text" in name_lower and "placeholder" in name_lower:
                    text_placeholders.append((int(idx), placeholder_name))
                elif "content" in name_lower and "placeholder" in name_lower:
                    content_placeholders.append((int(idx), placeholder_name))
            
            # Sort by index
            text_placeholders.sort()
            content_placeholders.sort()
            
            # Map to left/right structure
            if len(text_placeholders) >= 2:
                mapping_rules["comparison.left.title"] = text_placeholders[0][1]
                mapping_rules["comparison.right.title"] = text_placeholders[1][1]
            
            if len(content_placeholders) >= 2:
                mapping_rules["comparison.left.content"] = content_placeholders[0][1]
                mapping_rules["comparison.right.content"] = content_placeholders[1][1]
                
        elif layout_name == "Two Content":
            # Find content placeholders
            content_placeholders = []
            
            for idx, placeholder_name in placeholders.items():
                name_lower = placeholder_name.lower()
                if "content" in name_lower and "placeholder" in name_lower:
                    content_placeholders.append((int(idx), placeholder_name))
            
            content_placeholders.sort()
            
            # Map to sections
            for i, (idx, placeholder_name) in enumerate(content_placeholders[:2]):
                mapping_rules[f"sections[{i}].content"] = placeholder_name
                
        elif layout_name == "Picture with Caption":
            # Find text and content placeholders
            for idx, placeholder_name in placeholders.items():
                name_lower = placeholder_name.lower()
                if "text" in name_lower and "placeholder" in name_lower:
                    mapping_rules["media.caption"] = placeholder_name
                    break
            
            # Content uses semantic detection
            mapping_rules["media.description"] = "semantic:content"
        
        return mapping_rules
    
    def supports_structured_frontmatter(self, layout_name: str) -> bool:
        """Check if layout supports structured frontmatter"""
        patterns = self.get_structure_patterns()
        return layout_name in patterns
    
    def get_supported_layouts(self) -> List[str]:
        """Get list of layouts that support structured frontmatter"""
        patterns = self.get_structure_patterns()
        return list(patterns.keys())
    
    def get_example(self, layout_name: str) -> Optional[str]:
        """Get example structured frontmatter for a layout"""
        definition = self.get_structure_definition(layout_name)
        return definition.get("example")


class StructuredFrontmatterConverter:
    """Convert structured frontmatter to placeholder mappings (one-way only)"""
    
    def __init__(self, layout_mapping: Optional[Dict] = None):
        self.layout_mapping = layout_mapping or {}
        self.registry = StructuredFrontmatterRegistry(layout_mapping)
    
    def convert_structured_to_placeholders(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert structured frontmatter to placeholder field names"""
        
        layout_name = structured_data.get("layout")
        if not layout_name:
            return structured_data
            
        structure_def = self.registry.get_structure_definition(layout_name)
        if not structure_def:
            # No structured definition available, return as-is
            return structured_data
        
        result = {"type": layout_name}
        mapping_rules = structure_def["mapping_rules"]
        
        # Process each mapping rule
        for structured_path, placeholder_target in mapping_rules.items():
            value = self._extract_value_by_path(structured_data, structured_path)
            if value is not None:
                if placeholder_target.startswith("semantic:"):
                    # Use semantic field name directly
                    semantic_field = placeholder_target.split(":", 1)[1]
                    result[semantic_field] = value
                else:
                    # Use exact placeholder name
                    result[placeholder_target] = value
        
        return result
    
    
    def _extract_value_by_path(self, data: Dict[str, Any], path: str) -> Any:
        """Extract value from nested dict using dot notation path with array support"""
        
        # Handle array indexing like "columns[0].title"
        if "[" in path and "]" in path:
            return self._extract_array_value(data, path)
        
        # Handle simple dot notation like "comparison.left.title"
        keys = path.split(".")
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _extract_array_value(self, data: Dict[str, Any], path: str) -> Any:
        """Extract value from array using path like 'columns[0].title'"""
        
        # Parse "columns[0].title" into parts
        parts = self._parse_path_with_arrays(path)
        
        # Navigate through the data structure
        current = data
        for part in parts:
            if isinstance(part, int):
                if isinstance(current, list) and len(current) > part:
                    current = current[part]
                else:
                    return None
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def _set_value_by_path(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """Set value in nested dict using dot notation path with array support"""
        
        if "[" in path and "]" in path:
            self._set_array_value(data, path, value)
            return
        
        keys = path.split(".")
        current = data
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
    
    def _set_array_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """Set value in array structure, creating arrays as needed"""
        
        parts = self._parse_path_with_arrays(path)
        current = data
        
        # Navigate through all but the last part, creating structure as needed
        for i, part in enumerate(parts[:-1]):
            if isinstance(part, int):
                # Current should be a list, ensure it exists and has enough elements
                if not isinstance(current, list):
                    current = []
                while len(current) <= part:
                    current.append({})
                current = current[part]
            else:
                # Current should be a dict
                if part not in current:
                    # Look ahead to see if next part is an array index
                    next_part = parts[i + 1] if i + 1 < len(parts) else None
                    if isinstance(next_part, int):
                        current[part] = []
                    else:
                        current[part] = {}
                current = current[part]
        
        # Set the final value
        final_part = parts[-1]
        if isinstance(final_part, int):
            if not isinstance(current, list):
                current = []
            while len(current) <= final_part:
                current.append(None)
            current[final_part] = value
        else:
            current[final_part] = value
    
    def _parse_path_with_arrays(self, path: str) -> List[Union[str, int]]:
        """Parse path like 'columns[0].title' into ['columns', 0, 'title']"""
        
        parts = []
        current_part = ""
        i = 0
        
        while i < len(path):
            if path[i] == "[":
                # Add the current part if it exists
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                
                # Find the closing bracket and extract the index
                j = i + 1
                while j < len(path) and path[j] != "]":
                    j += 1
                
                if j < len(path):
                    index_str = path[i+1:j]
                    try:
                        index = int(index_str)
                        parts.append(index)
                    except ValueError:
                        # If it's not a number, treat as string key
                        parts.append(index_str)
                    
                    i = j + 1
                    # Skip the dot after the bracket if it exists
                    if i < len(path) and path[i] == ".":
                        i += 1
                else:
                    # Malformed path, just add the bracket as text
                    current_part += path[i]
                    i += 1
            elif path[i] == ".":
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                i += 1
            else:
                current_part += path[i]
                i += 1
        
        # Add any remaining part
        if current_part:
            parts.append(current_part)
        
        return parts


class StructuredFrontmatterValidator:
    """Validate structured frontmatter against layout requirements"""
    
    def __init__(self):
        self.registry = StructuredFrontmatterRegistry()
    
    def validate_structured_frontmatter(self, data: Dict[str, Any], layout_name: str) -> Dict[str, Any]:
        """Validate structured frontmatter against layout requirements"""
        
        structure_def = self.registry.get_structure_definition(layout_name)
        if not structure_def:
            return {"valid": True, "warnings": ["No validation rules available for this layout"]}
        
        validation_rules = structure_def.get("validation", {})
        result = {"valid": True, "warnings": [], "errors": []}
        
        # Check required fields
        required_fields = validation_rules.get("required_fields", [])
        for field in required_fields:
            if field not in data:
                result["valid"] = False
                result["errors"].append(f"Missing required field: '{field}'")
        
        # Layout-specific validation
        if layout_name == "Four Columns" and "columns" in data:
            self._validate_four_columns(data, validation_rules, result)
        elif layout_name == "Comparison" and "comparison" in data:
            self._validate_comparison(data, validation_rules, result)
        elif layout_name == "Two Content" and "sections" in data:
            self._validate_two_content(data, validation_rules, result)
        
        return result
    
    def _validate_four_columns(self, data: Dict[str, Any], rules: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Validate Four Columns specific structure"""
        columns = data.get("columns", [])
        
        min_cols = rules.get("min_columns", 1)
        max_cols = rules.get("max_columns", 4)
        
        if len(columns) < min_cols:
            result["valid"] = False
            result["errors"].append(f"Expected at least {min_cols} columns, got {len(columns)}")
        elif len(columns) > max_cols:
            result["warnings"].append(f"Expected at most {max_cols} columns, got {len(columns)} (extra columns will be ignored)")
        
        # Validate each column structure
        for i, column in enumerate(columns):
            if not isinstance(column, dict):
                result["errors"].append(f"Column {i+1} must be an object with 'title' and 'content'")
                continue
            
            if "title" not in column:
                result["warnings"].append(f"Column {i+1} missing 'title' field")
            if "content" not in column:
                result["warnings"].append(f"Column {i+1} missing 'content' field")
    
    def _validate_comparison(self, data: Dict[str, Any], rules: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Validate Comparison specific structure"""
        comparison = data.get("comparison", {})
        
        required_sides = rules.get("required_comparison_fields", ["left", "right"])
        for side in required_sides:
            if side not in comparison:
                result["valid"] = False
                result["errors"].append(f"Missing required comparison side: '{side}'")
            else:
                side_data = comparison[side]
                if not isinstance(side_data, dict):
                    result["errors"].append(f"Comparison '{side}' must be an object")
                else:
                    if "title" not in side_data:
                        result["warnings"].append(f"Comparison '{side}' missing 'title' field")
                    if "content" not in side_data:
                        result["warnings"].append(f"Comparison '{side}' missing 'content' field")
    
    def _validate_two_content(self, data: Dict[str, Any], rules: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Validate Two Content specific structure"""
        sections = data.get("sections", [])
        
        min_sections = rules.get("min_sections", 2)
        max_sections = rules.get("max_sections", 2)
        
        if len(sections) < min_sections:
            result["valid"] = False
            result["errors"].append(f"Expected at least {min_sections} sections, got {len(sections)}")
        elif len(sections) > max_sections:
            result["warnings"].append(f"Expected at most {max_sections} sections, got {len(sections)} (extra sections will be ignored)")


def get_structured_frontmatter_help(layout_name: str = None, template_mapping: Dict = None) -> Dict[str, Any]:
    """Get help information for structured frontmatter"""
    
    registry = StructuredFrontmatterRegistry(template_mapping)
    
    if layout_name:
        # Specific layout help
        definition = registry.get_structure_definition(layout_name)
        if not definition:
            return {
                "error": f"Layout '{layout_name}' does not support structured frontmatter",
                "supported_layouts": registry.get_supported_layouts()
            }
        
        return {
            "layout": layout_name,
            "description": definition["description"],
            "structure_type": definition["structure_type"],
            "example": definition["example"],
            "validation_rules": definition.get("validation", {}),
            "mapping_rules": definition["mapping_rules"]
        }
    else:
        # General help
        patterns = registry.get_structure_patterns()
        return {
            "supported_layouts": registry.get_supported_layouts(),
            "layout_info": {
                name: {
                    "description": definition["description"],
                    "structure_type": definition["structure_type"]
                }
                for name, definition in patterns.items()
            },
            "usage": "Use 'layout: <LayoutName>' in frontmatter, then follow the structured format for that layout"
        }