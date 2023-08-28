# dcpd_markdown.py

from markdown_it import MarkdownIt
from markdown_it.token import Token
import os
import argparse
import dcpd_log_debug
import dcpd_log_info

# Create an alias for convenience
logger_info = dcpd_log_info.logger
logger_debug = dcpd_log_debug.logger

# -------------------------------------------------------------------------
def generate_html_with_anchors(args):
    """
    Converts the local README.md to README.html with anchors added to h1 headers.

    Args:
    - args (object): An argument object with a 'verbose' attribute determining the verbosity.

    Notes:
    - Always logs function entry, exit, and important steps to the info log file.
    - Outputs to the console when 'args.verbose' is set to True.
    """
    
    entry_msg = "Starting the conversion of README.md to README.html."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)
    
    # Paths
    current_dir = os.path.dirname(os.path.realpath(__file__))
    md_file_path = os.path.join(current_dir, "..", "README.md")
    output_html_path = os.path.join(current_dir, "..", "README.html")

    try:
        # Read the original markdown content
        with open(md_file_path, "r") as f:
            original_md = f.read()
        
        # Process the content to generate HTML with anchors
        updated_html = process_content(original_md, args)

        # Save the generated HTML to the output file
        with open(output_html_path, "w") as f:
            f.write(updated_html)

        success_msg = "Conversion successful."
        logger_info.info(success_msg)
        if args.verbose:
            print(success_msg)
    except Exception as e:
        error_msg = f"Error during conversion: {str(e)}"
        logger_info.error(error_msg)
        if args.verbose:
            print(error_msg)
    
    exit_msg = "Exiting the conversion of README.md to README.html."
    logger_info.info(exit_msg)
    if args.verbose:
        print(exit_msg)

# -------------------------------------------------------------------------
def process_content(markdown_text, args):
    """
    Processes the provided markdown text to add anchors to h1 headers.

    Args:
    - markdown_text (str): The markdown content to process.
    - args (object): An argument object with a 'verbose' attribute determining the verbosity.

    Returns:
    str: The processed HTML content with anchors added to h1 headers.

    Notes:
    - Logs tokenization and important processing steps to the debug log file.
    - Outputs to the console when 'args.verbose' is set to True.
    """
    
    entry_msg = "Starting the tokenization and processing of the provided markdown content."
    logger_info.info(entry_msg)
    if args.verbose:
        print(entry_msg)
    
    # Initialize the markdown parser
    md = MarkdownIt()

    # Tokenize the markdown content
    tokens = md.parse(markdown_text)
    new_tokens = []

    for token in tokens:
        new_tokens.append(token)

        # Check if the token type is an h1 heading
        if token.type == 'heading_open' and token.tag == 'h1':
            # Extract the content of the heading from the next token
            heading_content = tokens[tokens.index(token) + 1].content
            heading_content = heading_content.replace("**", "")  # Remove markdown bold formatting
            anchor_name = heading_content.lower().replace(' ', '-')

            # Create and append an anchor token before the heading content
            anchor_token = Token(type='html_inline', tag='', nesting=0)
            anchor_token.content = f'<a id="{anchor_name}" href="#{anchor_name}"></a>'
            new_tokens.append(anchor_token)

    finished_msg = "Finished processing the markdown content."
    logger_debug.debug(finished_msg)
    if args.verbose:
        print(finished_msg)
    
    # Convert the modified tokens to HTML
    return md.renderer.render(new_tokens, md.options, {})