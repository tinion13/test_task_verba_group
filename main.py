from src.articles_from_query import get_articles_from_query
from src.articles_to_data import parse_articles_to_data
from src.json_to_xlsx import convert_json_to_xlsx_with_filtered


def run_get_articles() -> None:
    query = input("Введите query: ").strip()
    file_name = input("Введите путь к выходному JSON файлу: ").strip()
    get_articles_from_query(
        query=query, 
        file_name=file_name,
    )


def run_articles_to_data() -> None:
    articles_file_json = input("Введите путь к входному JSON файлу: ").strip()
    output_file_json = input("Введите путь к выходному JSON файлу: ").strip()
    limit_items = int(input("Введите limit_items (или оставьте пустым): ").strip())

    parse_articles_to_data(
        articles_file_json=articles_file_json,
        output_file_json=output_file_json,
        limit_items=limit_items,
    )


def run_json_to_xlsx() -> None:
    json_file = input("Введите путь к входному JSON файлу: ").strip()
    xlsx_file = input("Введите путь к выходному XLSX файлу: ").strip()
    xlsx_file_filtered = input("Введите путь к выходному отфильтрованному XLSX файлу: ").strip()
    convert_json_to_xlsx_with_filtered(
        json_filename=json_file, 
        xlsx_filename=xlsx_file,
        xlsx_filename_filtered=xlsx_file_filtered,
    )


def main() -> None:
    commands = {
        "1": {"name": "get_articles", "handler": run_get_articles, },
        "2": {"name": "articles_to_data", "handler": run_articles_to_data, },
        "3": {"name": "json_to_xlsx", "handler": run_json_to_xlsx, },
    }

    print("\nДоступные команды:")
    for number, command in commands.items():
        print(f"{number}. {command['name']}")

    choice = input("\nВведите номер команды: ").strip()
    command = commands.get(choice)
    if command is None:
        print("Неизвестная команда.")
        return

    try:
        command["handler"]()
        print("Готово.")
        return
    except NotImplementedError as error:
        print(f"Ошибка: {error}")
        return
    except Exception as error:
        print(f"Произошла ошибка: {error}")
        return


if __name__ == "__main__":
    main()
