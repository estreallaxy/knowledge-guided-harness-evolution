import argparse
from utils.data_pre_filter import handle_pre_filter
from utils.data_preview import handle_preview
from utils.data_construct import handle_construct
from utils.data_post_filter import handle_post_filter

def main():
    parser = argparse.ArgumentParser(description="Parquet Data Processing Toolkit")
    subparsers = parser.add_subparsers(title="Available Commands", dest="command", help="Choose an operation")

    # --- Pre-Filter Command ---
    parser_pre_filter = subparsers.add_parser('pre_filter', help='Filter and merge Parquet data based on turn count')
    parser_pre_filter.add_argument('--src', type=str, required=True, help='Source file or directory')
    parser_pre_filter.add_argument('--dst', type=str, default='.', help='Output directory')
    parser_pre_filter.add_argument('--name', type=str, default='filtered.parquet', help='Output filename')
    parser_pre_filter.add_argument('--min_turn', type=int, default=0, help='Minimum turn value')
    parser_pre_filter.add_argument('--shuffle', action='store_true', help='Shuffle the data before saving')
    parser_pre_filter.set_defaults(func=handle_pre_filter)

    # --- Preview Command ---
    parser_preview = subparsers.add_parser('preview', help='Quickly view the first few rows')
    parser_preview.add_argument('--src', type=str, required=True, help='Source file')
    parser_preview.add_argument('--rows', type=int, default=5, help='Number of rows to display')
    parser_preview.set_defaults(func=handle_preview)

    # --- Construct Final Command ---
    parser_construct = subparsers.add_parser('construct_final', help='Process dataset with LLM and save incrementally')
    parser_construct.add_argument('--src', type=str, required=True, help='Path to the source .parquet file')
    parser_construct.add_argument('--start', type=int, default=None, help='Starting index (overrides log file)')
    parser_construct.add_argument('--limit', type=int, default=None, help='Number of items to process in this run')
    parser_construct.add_argument('--prompt_file', type=str, default='prompt.txt', help='Path to prompt template file')
    parser_construct.add_argument('--log', type=str, default=None, help='Path to log file (overrides default)')
    parser_construct.add_argument('--mode', type=str, default="multi-turn", help='mode of processing: "single-turn" will process one conversation in one API call while "multi-turn" will process turn by turn')
    parser_construct.set_defaults(func=handle_construct)

    # --- Post-Filter Command ---
    parser_post_filter = subparsers.add_parser('post_filter', help='post-process filtered data')
    parser_post_filter.add_argument('--src', type=str, required=True, help='Source directory path containing .jsonl files')
    parser_post_filter.add_argument('--dst', type=str, required=True, help='Destination directory path for saving results')
    parser_post_filter.set_defaults(func=handle_post_filter)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()