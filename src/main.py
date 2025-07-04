from os import path, listdir, mkdir, makedirs
from shutil import copy, rmtree
from markdown_to_html_node import *
import sys

def main():
    basepath ='/'
    dest_dir = 'docs'
    
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
        #if not basepath.startswith('/'):
        #    basepath =  '.'+ basepath
        if not basepath.endswith('/'):
            basepath = basepath+'/'
    
    if path.exists(dest_dir):
        rmtree(dest_dir)
    makedirs(dest_dir)
    
    generate_pages_recursive('static','template.html' , dest_dir, basepath)
    generate_pages_recursive('content', 'template.html', dest_dir, basepath)
    
    
def generate_page(from_path: str, template_path: str, dst_path: str, basepath: str) -> None:
    print(f'Generating page from {from_path} to {dst_path} using {template_path}')
    with open(from_path, 'r') as rf, open(template_path, 'r') as tmp_f, open(dst_path,'w') as wf:
        md = rf.read()
        html_str = markdown_to_html_node(md).to_html()
        title = extract_title(md)
        
        tmp_contents = tmp_f.read().replace(
            r'{{ Title }}', title).replace(
                r'{{ Content }}',html_str).replace(
                    'href="/', f'href="{basepath}').replace(
                        'src="/', f'src="{basepath}')

        
        wf.write(str(tmp_contents))

def generate_pages_recursive(dir_path_content: str, template_path: str, dest_dir_path: str, basepath: str) -> None:
    dir_to_files(dir_path_content, dest_dir_path)
    content_items_lst = listdir(dir_path_content)
    print(f'parsing: {dir_path_content} to: {dest_dir_path} using: {template_path}')
    for item in content_items_lst:
        candidate_path = path.join(dir_path_content, item)
        dest_candidate_path = path.join(dest_dir_path, item)
        if path.isfile(candidate_path) and candidate_path.split('.')[1] == 'md':
            generate_page(candidate_path, template_path, f'{dest_candidate_path.rstrip('md')}html', basepath)
        elif path.isdir(candidate_path):
            generate_pages_recursive(candidate_path, template_path, dest_candidate_path, basepath)
        continue                
                                

def dir_to_files(dir_path: str, dst_path: str) -> None:
    dir_items = listdir(dir_path)
    for item in dir_items:
        source_path = path.join(dir_path, item)
        end_path = path.join(dst_path, item)
        if path.isfile(source_path):
            copy(source_path, end_path)
        elif path.isdir(source_path) and not path.isdir(end_path):
            mkdir(end_path)
            dir_to_files(source_path, end_path)


if __name__ == "__main__":
    main()