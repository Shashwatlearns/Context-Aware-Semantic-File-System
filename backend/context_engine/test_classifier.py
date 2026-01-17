from classifier import FileClassifier


def main():
    classifier = FileClassifier()

    text1 = "This document contains python and algorithm concepts"
    text2 = "Bank invoice and tax payment details"
    text3 = "University exam syllabus and lecture notes"

    print("Text 1 Category:", classifier.classify(text1))
    print("Text 2 Category:", classifier.classify(text2))
    print("Text 3 Category:", classifier.classify(text3))


if __name__ == "__main__":
    main()
