# backend/context_engine/classifier.py

class FileClassifier:
    """
    Classifies file content into semantic categories
    """

    def __init__(self):
        self.categories = {
            "education": ["exam", "syllabus", "lecture", "university", "college"],
            "finance": ["invoice", "salary", "tax", "bank", "payment"],
            "technology": ["python", "java", "algorithm", "database", "ai"],
            "general": []
        }

    def classify(self, text: str) -> str:
        text = text.lower()

        for category, keywords in self.categories.items():
            for word in keywords:
                if word in text:
                    return category

        return "general"
