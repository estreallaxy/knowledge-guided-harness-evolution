from call_llm import call_llm

def get_metadata(sheet_strings: dict) -> dict:
    """
    Extracts metadata from LLM-compatible Excel tables with flexible hierarchy representation.

    Args:
        sheet_strings: Dictionary where keys are sheet names and values are strings
        call_llm: Function to interact with LLM (takes system_prompt and user_prompt)
        
    Returns:
        Dictionary containing extracted metadata with flexible structure
    """
    system_prompt = """You are an expert data analyst specializing in spreadsheet structure analysis. 
    Extract metadata from the provided markdown tables with this approach:

    1. Hierarchy Analysis:
    - Identify all header types (row, column, matrix, etc.)
    - For each header level document:
      * Header name and span (if merged)
      * Child relationships
      * Associated data fields
    - Describe relationships between headers

    2. Data Samples:
    - For each logical data section, provide representative values
    - Maintain connection to parent headers

    3. Sheet Summary:
    - Describe overall structure
    - Note any special patterns

    # Response Format
    {
        "sheet_name" : {
            "hierarchy": {
                "structure_type": "row_based|column_based|matrix|other",
                "levels": [
                    {
                        "header_type": "row|column|both|group",
                        "headers": [
                            {
                                "name": "header_name",
                                "span": [start, end],
                                "children": [...],
                                "data_fields": [...]
                            }
                        ]
                    }
                ],
                "relationships": ["description"]
            },
            "data_samples": {
                "header_path": ["sample1", ...]
            },
            "summary": "description",
            "statistics": {
                "row_count": int,
                "column_count": int,
                "merged_cells": int
            }
        },
        ...
    }""".strip()

    user_prompt = f"""Analyze these Excel sheets converted to markdown format:

    {sheet_strings}

    Follow these guidelines:
    1. Handle any header structure type
    2. Preserve hierarchical relationships
    3. Include span information for merged cells
    4. Provide 2-3 data samples per logical section
    5. Add basic statistics when available
    6. Return only valid JSON according to the "Response Format" Guidance.""".strip()

    try:
        # Get LLM response
        llm_response = call_llm(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            json_resp=True
        )

        llm_response = llm_response.strip().strip("```json").strip("```")

        # Parse and validate
        import json
        metadata = json.loads(llm_response)

        # Ensure consistent structure
        for sheet_data in metadata.values():
            # Initialize missing sections
            sheet_data.setdefault("hierarchy", {
                "structure_type": "unknown",
                "levels": [],
                "relationships": []
            })
            sheet_data.setdefault("data_samples", {})
            sheet_data.setdefault("summary", "")
            
            # Initialize statistics if not provided
            sheet_data.setdefault("statistics", {
                "row_count": "unknown",
                "column_count": "unknown",
                "merged_cells": "unknown"
            })

            # Normalize data samples to lists
            for header_path, samples in sheet_data["data_samples"].items():
                if not isinstance(samples, list):
                    sheet_data["data_samples"][header_path] = [str(samples)]

        return metadata

    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from LLM"}
    except Exception as e:
        return {"error": f"Metadata extraction failed: {str(e)}"}
