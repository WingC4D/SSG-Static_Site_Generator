from enum import Enum
class TextType(Enum):
    '''TextType Enum
    This Enum is used to represent the different types of text that can be used in the TextNode class.
    ### Attributes:
        TEXT: Regular text
        BOLD: Bold text
        ITALIC: Italic text
        IMAGE: Image text
        LINK: Link text
        CODE: Code text
    '''
    TEXT = 'Text'
    BOLD = 'Bold'
    ITALIC ="Italic"
    IMAGE ='Image'
    LINK = 'Link'
    CODE ='Code Text'

class TextNode():
    '''TextNode Class
    This class is used to represent a text node in the HTML tree.
    It is used to represent text that can be formatted in different ways.
    ### Attributes:
        text: The text to be displayed.
        text_type: The type of text (e.g. bold, italic, etc.)
        url: The URL to be used for links and images.
    '''
    def __init__(self, text:str, text_type:TextType, url:str  = None) -> None:
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other) -> None:
        if not self.text == other.text:
#print(f"The Texts don't match!:\nDesired Text: {self.text}\nOutput Text:{other.text}")
            return False
        if not self.text_type == other.text_type:
#print(f"The Text Types don't match!:\nDesired Text Type: {self.text_type}\nOutput Text Type:{other.text_type}")
            return False
        if not self.url == other.url:
#print(f"The Texts don't match!:\nDesired URL: {self.url}\nOutput URL:{other.url}")
            return False
        return True

    def __repr__(self) -> str:
        return f'TextNode(Text: {self.text}, Text Type: {self.text_type.value}, URl: {self.url})'