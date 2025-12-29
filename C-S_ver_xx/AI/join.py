import os

def process_directory(directory_path, outfile):
    """Przetwarza katalog i jego podkatalogi, zapisując zawartość plików .py."""
    try:
        # Przechodzimy przez wszystkie elementy w katalogu
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            
            # Jeśli to katalog, przetwarzamy go rekurencyjnie
            if os.path.isdir(item_path):
                process_directory(item_path, outfile)
            
            # Jeśli to plik .py, przetwarzamy go
            elif item.endswith('.py'):
                process_python_file(item_path, item, outfile)
                
    except Exception as e:
        print(f'Wystąpił błąd podczas przetwarzania katalogu {directory_path}: {e}')

def process_python_file(file_path, filename, outfile):
    """Przetwarza pojedynczy plik Python i zapisuje jego zawartość."""
    try:
        with open(file_path, 'r', encoding='utf-8') as infile:
            content = infile.read()
            outfile.write(f'====================\n')
            outfile.write(f'FILE: {filename}\n')
            outfile.write(f'PATH: {file_path}\n')
            outfile.write(content + '\n\n')
    except Exception as e:
        print(f'Wystąpił błąd podczas przetwarzania pliku {file_path}: {e}')

def generate_text_file(source_directory, output_file):
    """Generuje plik tekstowy zawierający zawartość wszystkich plików .py w katalogu i podkatalogach."""
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            process_directory(source_directory, outfile)
        print(f'Plik tekstowy "{output_file}" został pomyślnie wygenerowany.')
    except Exception as e:
        print(f'Wystąpił błąd: {e}')

if __name__ == "__main__":
    source_directory = "C:/Users/cempa/Documents/CODE/.cursor-tutor/client-server_app/C_S_ver_0.4 _UT"
    output_file = "full.cr.txt"
    generate_text_file(source_directory, output_file) 