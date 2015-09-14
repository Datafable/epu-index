def main():
    with open('stopwords.txt') as f:
        print tuple([x.strip() for x in f.readlines()])

if __name__ == "__main__":
    main()
