import asyncio


def main():
    print("Hello World")
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    finally:
        loop.close()


if __name__ == '__main__':
    main()