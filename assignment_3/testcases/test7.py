goodAssignments = True
goodExamMarks = False
grade = 'A'
if(goodAssignments):
    if(goodExamMarks):
        grade = 'A'
    else:
        grade = 'B'
else:
    if(goodExamMarks):
        grade = 'B'
    else:
        grade = 'C'
print(grade)