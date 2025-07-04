from textnode import TextNode, TextType, Enum
import re
class BlockType(Enum):
    """
    Enum representing different types of Markdown blocks.
    """
    # Enum values for different Markdown block types
    PARAGRAPH = 'paragraph'
    HEADING = 'heading'
    CODE = 'code'
    QUOTE = 'quote'
    UNORDERED_LIST = 'unordered_list'
    ORDERED_LIST = 'ordered_list'

def block_to_block_type(block: str) -> BlockType:
    """
    Classifies a text block into a Markdown block type based on its syntax.

    Args:
        block (str): The input text block to classify.

    Returns:
        BlockType: The type of block (CODE, QUOTE, UNORDERED_LIST, HEADING,
                   ORDERED_LIST, or PARAGRAPH).
    """
    if not block.strip():
        return BlockType.PARAGRAPH
    
    lines_and_spaces_split_block = [line.split() for line in block.split('\n') if line.strip()]
    candidates = [tokens_lst[0] for tokens_lst in lines_and_spaces_split_block] 
    
    if not candidates:
        return BlockType.PARAGRAPH
        
    if lines_and_spaces_split_block[0][0].startswith('```') and block.endswith('```'):
        return BlockType.CODE
    
    if all(candidate == '>' for candidate in candidates):
        return BlockType.QUOTE
    
    if all(candidate == '-' for candidate in candidates):
        return BlockType.UNORDERED_LIST
    
    first_line_tokens = block.split()    
    
    if 1 <= len(first_line_tokens[0]) <= 6 and all(char == '#' for char in first_line_tokens[0]):
        return BlockType.HEADING
        
    if all(len(candidate.split('.')) == 2 and candidate.split('.')[0].isdigit() and candidate.split('.')[1] == '' for candidate in candidates):
        number_matches = [re.findall(r'(\d+)\.', candidate) for candidate in candidates]
        numbers = [int(match[0]) for match in number_matches if match]
        
        if numbers and numbers[0] > 0 and all(numbers[i] == numbers[i-1] + 1 for i in range(1, len(numbers))):
            return BlockType.ORDERED_LIST
    
    return BlockType.PARAGRAPH

def markdown_to_blocks(markdown: str) -> list[str]:
    """
    This function takes a string of text and splits it into blocks based on Markdown syntax.
    ### Args:
        text: A string of text to be split into blocks.
    ### Returns:
        A list of strings, each representing a block of text.
    ### Raises:
        ValueError: If the text is not a string or is empty.
    """
    if not isinstance(markdown, str):
        raise ValueError('markdown must be a string.')
    # Split the text into blocks based on double newlines
    # and remove leading/trailing whitespace from each block
    # Remove empty blocks
    # Remove leading/trailing whitespace from each line in the block
    # and remove empty lines
    # Join the lines back together
    # and return the cleaned blocks
    blocks = [block.strip() for block in markdown.split('\n\n') if block.strip()]
    clean_blocks = ['\n'.join(line.strip() for line in block.split('\n') if line.strip()) for block in blocks]    
    return clean_blocks

def text_to_textnodes(text: str) -> list[TextNode]:
    """
    This function takes a string of text and converts it into a list of TextNode objects.
    ### Args:
        text: A string of text to be converted.
    ### Returns:
        A list of TextNode objects representing the text.
    ### Raises:
        ValueError: If the text_type is not a valid TextType Enum.
    """
    # Initialize the list of TextNodes with the original text
    # Split the text into nodes based on delimiters
    # and assign the appropriate TextType
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, '`', TextType.CODE)
    nodes = split_nodes_delimiter(nodes, '**', TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, '_', TextType.ITALIC)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes 

def extract_markdown_images(text : str) -> list[tuple]:
    """Extracts the Alt Text and URL of Images from markdown texts"""
    image_regex = r'\!\[([^\]]*)\]\(([^\)]*)\)'
    image_links = re.findall(image_regex, text)
    return image_links
    
def extract_markdown_links(text: str) -> list[tuple]:
    """Extracts the Alt Text and URL of Links from markdown texts"""
    # Regex to match Markdown links
    # Matches [alt text](url) format
    # The negative lookbehind (?<!!) ensures that the link is not preceded by an exclamation mark
    # The regex captures the alt text and URL separately
    link_regex = r'(?<!!)\[([^\]]*)\]\(([^\)]*)\)'
    links = re.findall(link_regex, text)
    return links

def split_nodes_delimiter(old_nodes: list[TextNode], delimiter:  str| None, text_type :  TextType) -> list[TextNode]:
    """
    This function takes a list of TextNodes and splits them based on the provided delimiter.
    ### Args: 
        old_nodes: A list of TextNode objects.
        delimiter: The delimiter to split the text on. If None or an empty string, the text will not be split.
        text_type: The type of text to assign to the split parts. Must be a valid TextType Enum.
    ### Returns:
        A new list of TextNode objects with the text split based on the delimiter.
    ### Raises:
        ValueError: If the text_type is not a valid TextType Enum.
        ValueError: If the delimiter occurs an even number of times in the text, indicating a broken markdown format.
    """
    
    if not isinstance(text_type, TextType):
        raise ValueError(f'text_type must be a valid TextType.')
    new_nodes= []
    for node in old_nodes:
        # Pass through non-TEXT nodes or nodes without valid delimiter
        if node.text_type is not TextType.TEXT or not delimiter or delimiter not in node.text:
            new_nodes.append(node)
            continue
        split_text = node.text.split(delimiter)
        #Checks if the Delimiter occurs is of an even value, If so it raises a ValueError for a broken MD format
        if len(split_text) % 2 == 0:
            raise ValueError(f'Invalid Markdown: unmatched "{delimiter}" in "{node.text}".')
        # Create nodes: TEXT for non-empty even indices, text_type for odd
        new_nodes.extend(TextNode(snippet, TextType.TEXT if i % 2 == 0 else text_type) for i, snippet in enumerate(split_text) if snippet or i % 2 == 1)
    return new_nodes

def split_nodes_link(old_nodes:list[TextNode]) -> list[TextNode]:
    '''
    Takes a List Of TextNodes parses only the TEXT TextType Nodes;
    If an image is found in the TextNode's text the Image is Extracted;
    The fuction parses the rest of the TextNode's text looking for new images
    ### Args: 
        #### old_nodes: 
             A list of objects; Of type TextNodes; Of any TextType Enum.
    
    ### Returns:
        #### new_nodes: 
           A list of Potentianlly split TextNodes, if so the split is done base on MarkDown Links 
    '''    
    new_nodes = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT or not extract_markdown_links(node.text):
            new_nodes.append(node)
            continue
        
        alt_text, url = extract_markdown_links(node.text)[0]
        textnode_text_lst = node.text.split(f'[{alt_text}]({url})', maxsplit= 1)
        
        if textnode_text_lst[0]:
            new_nodes.append(TextNode(textnode_text_lst[0], TextType.TEXT))    
        
        new_nodes.append(TextNode(alt_text, TextType.LINK, url))
        
        if textnode_text_lst[1]:
            new_nodes.extend(split_nodes_link([TextNode(textnode_text_lst[1], TextType.TEXT)]))

    return new_nodes

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    '''
    Takes a List Of TextNodes parses only the TEXT TextType Nodes;
    If an image is found in the TextNode's text the Image is Extracted;
    The fuction parses the rest of the TextNode's text looking for new images
    ### Args: 
        #### old_nodes: 
             A list of objects; Of type TextNodes; Of any TextType Enum.
    
    ### Returns:
        #### new_nodes: 
           A list of TextNodes split
    '''
    new_nodes = []
    
    for node in old_nodes:
        
        if node.text_type is not TextType.TEXT or not extract_markdown_images(node.text):
            new_nodes.append(node)
            continue
        
        alt_text, url = extract_markdown_images(node.text)[0]
        text_for_textnode_lst = node.text.split(f'![{alt_text}]({url})', maxsplit = 1)
        
        if text_for_textnode_lst[0]:
            new_nodes.append(TextNode(text_for_textnode_lst[0], TextType.TEXT))    
        
        new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))    
        
        if text_for_textnode_lst[1]:
            new_nodes.extend(split_nodes_image([TextNode(text_for_textnode_lst[1], TextType.TEXT)]))
    
    return new_nodes