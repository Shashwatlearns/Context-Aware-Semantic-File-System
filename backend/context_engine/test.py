from classifier import classify

samples = [
    "Machine Learning Notes.pdf",
    "OS Process Scheduling.docx",
    "TCP IP Routing.pdf",
    "Python Lab Assignment.txt",
    "Project Report Final.docx",
    "Random Document.pdf"
]

for s in samples:
    print(f"{s}  -->  {classify(s)}")
