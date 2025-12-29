from usdb_downloader.parser import Parser


def main() -> None:
    parser = Parser()
    for file in parser.iter_files():
        parser.write_file(file)


if __name__ == "__main__":
    main()
