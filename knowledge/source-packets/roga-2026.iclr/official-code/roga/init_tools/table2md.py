from typing import Optional
from openpyxl.utils import get_column_letter
from openpyxl.utils.cell import range_boundaries
import pandas as pd

def table2md(workbook) -> dict:
    md_tables = {}
    for sheet in workbook.worksheets:
        sheet_md = sheet2md(sheet)
        md_tables[sheet.title] = sheet_md
    return md_tables

# def sheet2md(worksheet, range_str: Optional[str] = None) -> str:
#     if range_str is None:
#         pd_data = worksheet.values
#         df = pd.DataFrame(pd_data)
#     else:
#         min_col, min_row, max_col, max_row = range_boundaries(range_str)
        
#         data = []
#         for row in range(min_row, max_row + 1):
#             row_data = []
#             for col in range(min_col, max_col + 1):
#                 cell_value = worksheet.cell(row=row, column=col).value
#                 row_data.append(cell_value if cell_value is not None else "")
#             data.append(row_data)
        
#         df = pd.DataFrame(data)
#     if df.empty:
#         return "| No data available |"
#     df.fillna("", inplace=True)
#     md = df.to_markdown(index=False)
#     return md

def sheet2md(worksheet, range_str: Optional[str] = None) -> str:
    """
    Converts an openpyxl worksheet (or a specific range) to a markdown string with A1 position notation.
    Handles complex header structures including merged cells and multi-level headers.
    Each cell value is prefixed with its A1 position (e.g., A1,value).
    
    Args:
        worksheet: The openpyxl worksheet object
        range_str: Optional range string in A1 notation (e.g., "B6:I260"). 
                If None, processes the entire worksheet.
        
    Returns:
        Markdown string for the specified range/worksheet with A1 position notation
    """
    # Determine the range to process
    if range_str and range_str.strip():
        try:
            # Parse the specific range
            min_col, min_row, max_col, max_row = range_boundaries(range_str)
            
            if min_col is None or min_row is None:
                return "| Invalid range |"
                
        except Exception as e:
            return f"| Error parsing range {range_str}: {str(e)} |"
    else:
        # Use entire worksheet
        min_row, min_col = 1, 1
        max_row = worksheet.max_row
        max_col = worksheet.max_column
        
        if max_row == 0 or max_col == 0:
            return "| No data available |"
    
    # Create a grid for the specified range/worksheet
    cell_grid = {}
    merged_ranges = list(worksheet.merged_cells.ranges) if worksheet.merged_cells else []
    
    try:
        # First pass: extract cell values for the range
        for row_idx in range(min_row, max_row + 1):
            for col_idx in range(min_col, max_col + 1):
                cell = worksheet.cell(row=row_idx, column=col_idx)
                
                # Handle formula cells: show calculated value if available, otherwise show formula
                cell_value = ""
                if cell.data_type == 'f':  # Formula cell
                    if hasattr(cell, 'displayed_value') and cell.displayed_value is not None:
                        cell_value = str(cell.displayed_value).strip()

                if cell_value == "" and cell.value is not None:
                    try:
                        cell_value = str(cell.value).strip()
                    except Exception as e:
                        print(f"Error occurs when parsing single cell to markdown ({row_idx}, {col_idx})")
                
                cell_grid[(row_idx, col_idx)] = cell_value
        
        # Second pass: handle merged cells
        for merged_range in merged_ranges:
            # Only process merged ranges that intersect with our target range
            if (merged_range.min_row <= max_row and merged_range.max_row >= min_row and
                merged_range.min_col <= max_col and merged_range.max_col >= min_col):
                
                top_left_value = cell_grid.get((merged_range.min_row, merged_range.min_col), "")
                
                row_span = merged_range.max_row - merged_range.min_row + 1
                col_span = merged_range.max_col - merged_range.min_col + 1
                
                # Handle intersection of merged range with our target range
                intersect_min_row = max(merged_range.min_row, min_row)
                intersect_max_row = min(merged_range.max_row, max_row)
                intersect_min_col = max(merged_range.min_col, min_col)
                intersect_max_col = min(merged_range.max_col, max_col)
                
                for row_idx in range(intersect_min_row, intersect_max_row + 1):
                    for col_idx in range(intersect_min_col, intersect_max_col + 1):
                        if row_idx == merged_range.min_row and col_idx == merged_range.min_col:
                            # Keep the original value in the top-left cell, add span info if significant
                            if row_span > 1 or col_span > 1:
                                cell_grid[(row_idx, col_idx)] = f"{top_left_value} [MERGED {row_span}x{col_span}]" if top_left_value else f"[MERGED {row_span}x{col_span}]"
                        else:
                            # For other cells in the merge, use empty or a subtle indicator
                            cell_grid[(row_idx, col_idx)] = "~"
        
        # Build the markdown table for the range
        rows_with_data = []
        for row_idx in range(min_row, max_row + 1):
            row_values = []
            for col_idx in range(min_col, max_col + 1):
                col_letter = get_column_letter(col_idx)
                cell_reference = f"{col_letter}{row_idx}"
                
                cell_value = cell_grid.get((row_idx, col_idx), "")
                formatted_cell = f"{cell_reference},{cell_value}"
                row_values.append(formatted_cell)
            
            # Remove trailing empty cells
            while row_values and row_values[-1].endswith(","):
                row_values.pop()
            
            if row_values:  # Only add non-empty rows
                rows_with_data.append(row_values)
        
        if not rows_with_data:
            return "| No data in range |" if range_str else "| No data available |"
        
        # Ensure all rows have the same number of columns
        max_cols = max(len(row) for row in rows_with_data) if rows_with_data else 0
        for i, row in enumerate(rows_with_data):
            while len(row) < max_cols:
                col_idx = min_col + len(row)
                col_letter = get_column_letter(col_idx)
                row_idx = min_row + i
                cell_reference = f"{col_letter}{row_idx}"
                row.append(f"{cell_reference}, ")
        
        # Build markdown
        result = []
        for row in rows_with_data:
            result.append("| " + " | ".join(row) + " |")
        
        return "\n".join(result)
        
    except Exception as e:
        error_msg = f"| Error processing range {range_str}: {str(e)} |" if range_str else f"| Error processing worksheet: {str(e)} |"
        return error_msg