import os

class NoStudentException(Exception):
    pass

class NoSubjectException(Exception):
    pass

class GradeSystem:
    def __init__(self):
        self.student_grade = {}

    def search_grade(self, student_no, subject):
        if student_no in self.student_grade:
            student_data = self.student_grade[student_no]
            if subject in student_data:
                return student_data[subject]
            else:
                raise NoSubjectException("找不到學生的科目成績")
        else:
            raise NoStudentException("找不到學生學號")

    def search_all_grade(self, student_no):
        if student_no in self.student_grade:
            student_data = self.student_grade[student_no]
            return " ".join([f"{subject} {score}" for subject, score in student_data.items()])
        else:
            raise NoStudentException("找不到學生學號")

    def insert_grade(self, data):
        student_data = data.split()
        student_no = student_data[0]
        subjects = student_data[1:]
        subject_grade = {}
        for i in range(0, len(subjects), 2):
            subject = subjects[i]
            grade = int(subjects[i + 1])
            subject_grade[subject] = grade
        self.student_grade[student_no] = subject_grade

    def delete_grade(self, student_no):
        if student_no in self.student_grade:
            del self.student_grade[student_no]

class GradeSystemDriver:
    def __init__(self):
        self.grade_system = GradeSystem()
        self.file_path = "grade2.txt"

    def load_data(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                for line in file:
                    self.grade_system.insert_grade(line.strip())
            print(f"已從 {self.file_path} 匯入成績資料")

    def save_data(self):
        with open(self.file_path, 'w') as file:
            for student_no, subject_scores in self.grade_system.student_grade.items():
                data = [f"{student_no} {subject} {score}" for subject, score in subject_scores.items()]
                file.write(" ".join(data) + "\n")

    def run(self):
        self.load_data()

        while True:
            print("\n成績查詢程式")
            print("功能代號如下:")
            print("1.查詢學生單科成績")
            print("2.查詢學生所有成績")
            print("3.新增學生成績")
            print("4.刪除學生成績")
            print("5.離開系統")

            choice = input("請輸入功能代號:")

            if choice == '1':
                try:
                    student_id_subject = input("請輸入學生學號及科目 (例如：97501 DS): ")
                    student_id, subject = student_id_subject.split()
                    grade = self.grade_system.search_grade(student_id, subject)
                    print(f"{student_id} 的 {subject} 成績是 {grade}")
                except (NoSubjectException, NoStudentException) as e:
                    print(e)
            elif choice == '2':
                try:
                    student_id = input("請輸入學號:")
                    all_grades = self.grade_system.search_all_grade(student_id)
                    print(f"{student_id} 的所有成績如下:\n{all_grades}")
                except NoStudentException as e:
                    print(e)
            elif choice == '3':
                student_data = input("請輸入學生學號及科目成績 (例如：97531 DS 80 DM 80 LA 80): ")
                self.grade_system.insert_grade(student_data)
                print("新增成功!")
            elif choice == '4':
                student_id = input("請輸入學號:")
                self.grade_system.delete_grade(student_id)
                print(f"已刪除學號 {student_id} 的成績")
            elif choice == '5':
                print("=======結束======")
                self.save_data()
                break
            else:
                print("請輸入有效的選項。")

if __name__ == "__main__":
    driver = GradeSystemDriver()
    driver.run()
