from containers import Container


def main():
    container = Container()

    app_starter = container.app_starter()
    app_starter.start()
    app_starter.wait_to_finish()


if __name__ == "__main__":
    main()
